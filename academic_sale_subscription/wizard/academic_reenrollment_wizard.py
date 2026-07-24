##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import Command, api, fields, models
from odoo.exceptions import ValidationError


class AcademicReenrollmentWizard(models.TransientModel):
    _name = "academic.reenrollment.wizard"
    _inherit = ["academic.order.params"]
    _description = "Academic Re-enrollment Wizard"

    line_ids = fields.One2many(
        "academic.reenrollment.wizard.line",
        "wizard_id",
        string="Groups to Re-enroll",
        default=lambda self: [
            Command.create({"source_group_id": group_id}) for group_id in self.env.context.get("active_ids", [])
        ],
    )
    is_recurring_mode = fields.Boolean(compute="_compute_is_recurring_mode")
    requires_sale_data = fields.Boolean(compute="_compute_requires_sale_data")
    student_count = fields.Integer(compute="_compute_student_count")

    @api.depends("template_id")
    def _compute_is_recurring_mode(self):
        for rec in self:
            rec.is_recurring_mode = rec._is_recurring_products(rec.template_id.sale_order_template_line_ids.product_id)

    @api.depends("line_ids.manage_sale_workflow", "line_ids.student_ids")
    def _compute_requires_sale_data(self):
        """Groups without the sales workflow get no order, so they need no sale data."""
        for rec in self:
            rec.requires_sale_data = any(line.manage_sale_workflow and line.student_ids for line in rec.line_ids)

    @api.depends("line_ids.student_ids")
    def _compute_student_count(self):
        for rec in self:
            rec.student_count = len(rec.line_ids.student_ids)

    def action_reenroll(self):
        self.ensure_one()
        lines = self.line_ids.filtered("student_ids")
        if not lines:
            raise ValidationError(self.env._("No selected group has students to re-enroll into a next year group."))
        if self.requires_sale_data and not self.template_id:
            raise ValidationError(self.env._("A quotation template is required to create the re-enrollment orders."))

        orders = self.env["sale.order"]
        created_groups = self.env["academic.group"]
        enrolled_count = 0
        for line in lines:
            students = line.student_ids
            target_group = line.target_group_id
            if not target_group:
                target_group = line.source_group_id._get_or_create_next_year_group(level=line.target_level_id)
                line.target_group_id = target_group
                created_groups |= target_group
            if line.manage_sale_workflow:
                orders |= line._create_orders(target_group, students)
            else:
                target_group.student_ids = [Command.link(student.id) for student in students]
                enrolled_count += len(students)

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "type": "success",
                "message": self.env._(
                    "%(orders)s re-enrollment order(s) created and %(enrolled)s student(s) enrolled directly"
                    " in %(groups)s group(s) (%(created_groups)s new next year group(s)).",
                    orders=len(orders),
                    enrolled=enrolled_count,
                    groups=len(lines),
                    created_groups=len(created_groups),
                ),
                "next": self._get_result_action(orders, lines.target_group_id),
            },
        }

    def _get_result_action(self, orders, target_groups):
        # no order created at all: land on the target groups instead
        return self._get_orders_action(orders) if orders else target_groups._get_groups_action()


class AcademicReenrollmentWizardLine(models.TransientModel):
    _name = "academic.reenrollment.wizard.line"
    _description = "Academic Re-enrollment Wizard Line"

    wizard_id = fields.Many2one("academic.reenrollment.wizard", required=True, ondelete="cascade")
    source_group_id = fields.Many2one("academic.group", required=True, string="Current Group")
    manage_sale_workflow = fields.Boolean(compute="_compute_manage_sale_workflow")
    company_id = fields.Many2one(related="source_group_id.company_id")
    section_id = fields.Many2one(related="source_group_id.section_id")
    subject_id = fields.Many2one(related="source_group_id.subject_id")
    level_ids = fields.Many2many(related="source_group_id.level_ids")
    target_year = fields.Integer(compute="_compute_target_year")
    target_level_id = fields.Many2one(
        "academic.level",
        string="Next Level",
        compute="_compute_target_level_id",
        readonly=False,
        store=True,
        domain="[('id', 'in', level_ids)]",
        help="Level of the group to create, suggested from the study plan sequence.",
    )
    target_group_id = fields.Many2one(
        "academic.group",
        string="Next Year Group",
        compute="_compute_target_group_id",
        readonly=False,
        store=True,
        domain="[('year', '=', target_year), ('company_id', '=', company_id),"
        " ('section_id', '=', section_id), ('subject_id', '=', subject_id)]",
        help="Group the students are re-enrolled into. Leave it empty to create it"
        " on the fly on the level set next to it.",
    )
    is_last_level = fields.Boolean(
        compute="_compute_is_last_level",
        string="Last Level",
        help="The group closes its study plan, so no next level is suggested and it is left out of the"
        " re-enrollment. Set a level or a group by hand to re-enroll it anyway.",
    )
    will_create_group = fields.Boolean(compute="_compute_will_create_group", string="New Group")
    student_ids = fields.Many2many(
        "res.partner",
        string="Students to Re-enroll",
        compute="_compute_students",
    )
    student_count = fields.Integer(compute="_compute_students")
    excluded_no_responsible_ids = fields.Many2many(
        "res.partner",
        string="Without Payment Responsible",
        compute="_compute_students",
        help="Students excluded because they have no active payment responsible.",
    )
    excluded_enrolled_ids = fields.Many2many(
        "res.partner",
        string="Already Enrolled",
        compute="_compute_students",
        help="Students excluded because they are already enrolled in the next year group.",
    )

    @api.depends("source_group_id")
    def _compute_target_year(self):
        for rec in self:
            rec.target_year = rec.source_group_id.year + 1

    @api.depends("source_group_id", "target_group_id")
    def _compute_manage_sale_workflow(self):
        """The target group decides: that is where the students land, and where student_ids
        is either computed from the orders or set by hand."""
        for rec in self:
            group = rec.target_group_id or rec.source_group_id
            rec.manage_sale_workflow = group.manage_sale_workflow

    @api.depends("source_group_id")
    def _compute_target_level_id(self):
        for rec in self:
            group = rec.source_group_id._origin
            rec.target_level_id = group._get_next_year_level() if group else False

    @api.depends("source_group_id")
    def _compute_is_last_level(self):
        """Own compute method: `store` and `compute_sudo` must not be mixed within one."""
        for rec in self:
            group = rec.source_group_id._origin
            rec.is_last_level = bool(group) and group.section_id._is_last_level(group.level_id)

    @api.depends("source_group_id", "target_level_id")
    def _compute_target_group_id(self):
        for rec in self:
            group = rec.source_group_id._origin
            rec.target_group_id = (
                group._get_next_year_group(level=rec.target_level_id) if group and rec.target_level_id else False
            )

    def _has_target(self):
        """A line only re-enrolls when it has somewhere to go: the last level of a study
        plan leaves both empty unless the user fills one by hand."""
        self.ensure_one()
        return bool(self.target_group_id or self.target_level_id)

    @api.depends("target_group_id", "target_level_id")
    def _compute_will_create_group(self):
        for rec in self:
            rec.will_create_group = rec._has_target() and not rec.target_group_id

    @api.depends("source_group_id", "target_group_id", "target_level_id")
    def _compute_students(self):
        """Always recomputed from the groups: the client does not send readonly values back.
        A line without a target re-enrolls nobody, so the whole preview stays empty and it
        drags no student count nor sale data requirement with it."""
        for rec in self:
            group = rec.source_group_id._origin
            students = group.student_ids if rec._has_target() else self.env["res.partner"]
            # without the sales workflow there is no order, so no payment responsible
            no_responsible = (
                students._filter_without_payment_responsible() if rec.manage_sale_workflow else self.env["res.partner"]
            )
            already_enrolled = (students - no_responsible) & rec._get_enrolled_students()
            rec.student_ids = students - no_responsible - already_enrolled
            rec.student_count = len(rec.student_ids)
            rec.excluded_no_responsible_ids = no_responsible
            rec.excluded_enrolled_ids = already_enrolled

    def _get_enrolled_students(self):
        """Students of the target group plus its pending quotations, so re-running never duplicates."""
        self.ensure_one()
        target_group = self.target_group_id._origin
        return target_group.student_ids | target_group._get_pending_registration_students()

    def _create_orders(self, target_group, students):
        self.ensure_one()
        wizard = self.wizard_id
        # the order belongs to the group's school company, not the one active in the session
        order_wizard = (
            self.env["academic.order.wizard"]
            .with_company(self.source_group_id.company_id)
            .with_context(academic_group_id=target_group.id)
            .create(
                {
                    "student_ids": [Command.set(students.ids)],
                    "template_id": wizard.template_id.id,
                    "plan_id": wizard.plan_id.id,
                    "pricelist_id": wizard.pricelist_id.id,
                    "next_invoice_date": wizard.next_invoice_date,
                    "status_sale": wizard.status_sale,
                    "validity_date": wizard.validity_date,
                    "payment_term_id": wizard.payment_term_id.id,
                }
            )
        )
        return order_wizard._create_mass_subscription(vals={"company_id": self.source_group_id.company_id.id})
