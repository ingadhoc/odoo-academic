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
    graduating_count = fields.Integer(compute="_compute_graduating_count")
    mixed_plans_warning = fields.Char(compute="_compute_mixed_plans_warning")
    pending_warning = fields.Char(compute="_compute_pending_warning")

    @api.depends("template_id")
    def _compute_is_recurring_mode(self):
        for rec in self:
            rec.is_recurring_mode = rec._is_recurring_products(rec.template_id.sale_order_template_line_ids.product_id)

    @api.depends("line_ids.manage_sale_workflow", "line_ids.student_ids", "line_ids.move_ids.target_group_id")
    def _compute_requires_sale_data(self):
        for rec in self:
            rec.requires_sale_data = any(line._requires_sale_data() for line in rec.line_ids)

    @api.depends("line_ids.student_ids")
    def _compute_student_count(self):
        for rec in self:
            rec.student_count = len(rec.line_ids.student_ids)

    @api.depends("line_ids.graduating_count")
    def _compute_graduating_count(self):
        for rec in self:
            rec.graduating_count = sum(rec.line_ids.mapped("graduating_count"))

    @api.depends("line_ids.student_ids", "line_ids.target_section_id", "line_ids.move_ids.target_group_id")
    def _compute_mixed_plans_warning(self):
        for rec in self:
            sections = rec.line_ids.filtered(lambda x: x._requires_sale_data())._get_target_sections()
            rec.mixed_plans_warning = False
            if len(sections) > 1:
                rec.mixed_plans_warning = self.env._(
                    "The groups of this re-enrollment go to %(count)s different study plans (%(plans)s). The"
                    " quotation template and the pricelist below are the same for all of them: re-enroll one"
                    " study plan at a time if they need different ones.",
                    count=len(sections),
                    plans=", ".join(sections.mapped("name")),
                )

    @api.depends("line_ids.is_pending")
    def _compute_pending_warning(self):
        for rec in self:
            pending = rec.line_ids.filtered("is_pending")
            rec.pending_warning = (
                self.env._(
                    "Some groups still have students and no destination for next year: %(groups)s."
                    " Set a study plan or a next year group on them, or take them out of this"
                    " re-enrollment.",
                    groups=", ".join(pending.source_group_id.mapped("display_name")),
                )
                if pending
                else False
            )

    def action_reenroll(self):
        self.ensure_one()
        # before the emptiness check: a run mixing pending and ready lines went through and
        # left the pending ones behind without saying a word
        if self.pending_warning:
            raise ValidationError(self.pending_warning)
        lines = self.line_ids.filtered("student_ids")
        if not lines:
            raise ValidationError(self.env._("No selected group has students to re-enroll into a next year group."))
        if self.requires_sale_data and not self.template_id:
            raise ValidationError(self.env._("A quotation template is required to create the re-enrollment orders."))

        orders = self.env["sale.order"]
        existing_groups = lines.target_group_id | lines.move_ids.target_group_id
        target_groups = self.env["academic.group"]
        enrolled_count = 0
        for line in lines:
            for target_group, students in line._get_destinations().items():
                target_groups |= target_group
                if target_group.manage_sale_workflow:
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
                    groups=len(target_groups),
                    created_groups=len(target_groups - existing_groups),
                ),
                "next": self._get_result_action(orders, target_groups),
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
    section_ids = fields.Many2many(related="source_group_id.section_ids")
    subject_id = fields.Many2one(related="source_group_id.subject_id")
    target_year = fields.Integer(compute="_compute_target_year")
    target_section_id = fields.Many2one(
        "academic.section",
        string="Next Study Plan",
        compute="_compute_target_section_id",
        readonly=False,
        store=True,
        domain="[('id', 'in', section_ids)]",
        help="Study plan of the group to create. It is the current one until the group closes it,"
        " where the plan set as next on the study plan is suggested.",
    )
    target_level_ids = fields.Many2many(related="target_section_id.level_ids")
    target_level_id = fields.Many2one(
        "academic.level",
        string="Next Level",
        compute="_compute_target_level_id",
        readonly=False,
        store=True,
        domain="[('id', 'in', target_level_ids)]",
        help="Level of the group to create, suggested from the study plan sequence.",
    )
    target_division_id = fields.Many2one(
        "academic.division",
        string="Next Division",
        compute="_compute_target_division_id",
        readonly=False,
        store=True,
        help="Division of the group to create. On a change of study plan it is only kept when the"
        " target plan already uses it, so no division is invented.",
    )
    target_group_id = fields.Many2one(
        "academic.group",
        string="Next Year Group",
        compute="_compute_target_group_id",
        readonly=False,
        store=True,
        domain="[('year', '=', target_year), ('company_id', '=', company_id), ('subject_id', '=', subject_id)]",
        help="Group the students are re-enrolled into. Leave it empty to create it"
        " on the fly on the study plan, level and division set next to it.",
    )
    is_last_level = fields.Boolean(
        compute="_compute_is_last_level",
        string="Last Level",
        help="The group closes its study plan, so the destination is looked up on the plans set as next."
        " With more than one it cannot be guessed, and it is picked by hand.",
    )
    is_graduating = fields.Boolean(
        compute="_compute_is_graduating",
        string="Graduating",
        help="The group closes its study plan and no single plan follows it, so its students finish"
        " their studies. Set a study plan or a group by hand to re-enroll them anyway.",
    )
    graduating_count = fields.Integer(compute="_compute_is_graduating", string="Graduating Students")
    is_pending = fields.Boolean(compute="_compute_is_pending", string="Pending Destination")
    pending_count = fields.Integer(
        compute="_compute_is_pending",
        string="Without Destination",
        help="Students of the group that have nowhere to go yet. Set a study plan or a next"
        " year group on the line to re-enroll them.",
    )
    will_create_group = fields.Boolean(compute="_compute_will_create_group", string="New Group")
    student_ids = fields.Many2many(
        "res.partner",
        "academic_reenrollment_line_student_rel",
        "line_id",
        "partner_id",
        string="Students to Re-enroll",
        compute="_compute_students",
        readonly=False,
        store=True,
        help="Remove a student to leave them out of this re-enrollment, for instance when they"
        " are leaving the school or repeating the level.",
    )
    student_count = fields.Integer(compute="_compute_student_count", store=True)
    move_ids = fields.One2many(
        "academic.reenrollment.wizard.move",
        "line_id",
        string="Students Sent to Another Group",
    )
    excluded_no_responsible_ids = fields.Many2many(
        "res.partner",
        "academic_reenrollment_line_no_responsible_rel",
        "line_id",
        "partner_id",
        string="Without Payment Responsible",
        compute="_compute_students",
        store=True,
        help="Students excluded because they have no active payment responsible.",
    )
    excluded_enrolled_ids = fields.Many2many(
        "res.partner",
        "academic_reenrollment_line_enrolled_rel",
        "line_id",
        "partner_id",
        string="Already Enrolled",
        compute="_compute_students",
        store=True,
        help="Students excluded because they are already enrolled in the next year group.",
    )

    @api.depends("source_group_id")
    def _compute_target_year(self):
        for rec in self:
            rec.target_year = rec.source_group_id.year + 1

    @api.depends("source_group_id", "target_group_id")
    def _compute_manage_sale_workflow(self):
        """The target group decides: that is where student_ids is either computed from the
        orders or set by hand."""
        for rec in self:
            group = rec.target_group_id or rec.source_group_id
            rec.manage_sale_workflow = group.manage_sale_workflow

    @api.depends("source_group_id")
    def _compute_target_section_id(self):
        for rec in self:
            group = rec.source_group_id._origin
            rec.target_section_id = group._get_next_year_section() if group else False

    @api.depends("source_group_id", "target_section_id")
    def _compute_target_level_id(self):
        for rec in self:
            group = rec.source_group_id._origin
            rec.target_level_id = group._get_next_year_level(rec.target_section_id) if group else False

    @api.depends("source_group_id", "target_section_id")
    def _compute_target_division_id(self):
        """Falls back to the plan of the source group so that a level set by hand, with no
        plan to change to, keeps the division as it did before."""
        for rec in self:
            group = rec.source_group_id._origin
            rec.target_division_id = (
                group._get_next_year_division(rec.target_section_id or group.section_id) if group else False
            )

    @api.depends("source_group_id")
    def _compute_is_last_level(self):
        """Own compute method: `store` and `compute_sudo` must not be mixed within one."""
        for rec in self:
            group = rec.source_group_id._origin
            rec.is_last_level = bool(group) and group.section_id._is_last_level(group.level_id)

    @api.depends("source_group_id", "target_section_id", "target_level_id", "target_division_id")
    def _compute_target_group_id(self):
        for rec in self:
            group = rec.source_group_id._origin
            rec.target_group_id = (
                group._get_next_year_group(
                    level=rec.target_level_id,
                    section=rec.target_section_id,
                    division=rec.target_division_id,
                )
                if group and rec.target_section_id and rec.target_level_id
                else False
            )

    def _has_target(self):
        """A line only re-enrolls when it has somewhere to go."""
        self.ensure_one()
        return bool(self.target_group_id or self.target_level_id)

    @api.depends(
        "target_group_id",
        "target_level_id",
        "source_group_id.student_count",
        "source_group_id.section_id.correlative_ids",
    )
    def _compute_is_graduating(self):
        """A plan with several plans after it is a different case: nobody graduates there,
        the destination is just pending."""
        for rec in self:
            group = rec.source_group_id._origin
            rec.is_graduating = bool(group) and group._is_graduating() and not rec._has_target()
            rec.graduating_count = rec.source_group_id.student_count if rec.is_graduating else 0

    @api.depends(
        "target_group_id",
        "target_level_id",
        "source_group_id.student_ids",
        "source_group_id.section_id.correlative_ids",
    )
    def _compute_is_pending(self):
        """Students to place and nowhere to place them. Not a graduation: there the plan ends
        on purpose, here the destination is only missing."""
        for rec in self:
            group = rec.source_group_id._origin
            pending = self.env["res.partner"]
            if group and not rec._has_target() and not group._is_graduating():
                pending = group.student_ids - rec._get_enrolled_students()
            rec.pending_count = len(pending)
            rec.is_pending = bool(pending)

    @api.depends("target_group_id", "target_level_id")
    def _compute_will_create_group(self):
        for rec in self:
            rec.will_create_group = rec._has_target() and not rec.target_group_id

    @api.depends("source_group_id", "target_group_id", "target_level_id")
    def _compute_students(self):
        """Recomputed from the groups on every change of destination, and editable so the user
        can leave students out. A line without a target re-enrolls nobody."""
        for rec in self:
            group = rec.source_group_id._origin
            students = group.student_ids if rec._has_target() else self.env["res.partner"]
            # without the sales workflow there is no order, so no payment responsible
            no_responsible = (
                students._filter_without_payment_responsible() if rec.manage_sale_workflow else self.env["res.partner"]
            )
            already_enrolled = (students - no_responsible) & rec._get_enrolled_students()
            rec.student_ids = students - no_responsible - already_enrolled
            rec.excluded_no_responsible_ids = no_responsible
            rec.excluded_enrolled_ids = already_enrolled

    @api.depends("student_ids")
    def _compute_student_count(self):
        # own compute: the count follows the students removed by hand, which leave the rest as it is
        for rec in self:
            rec.student_count = len(rec.student_ids)

    def _get_enrolled_students(self):
        """Students already placed for next year, plus the pending quotations, so re-running
        never duplicates. Every group of next year counts, not only the one of the line: a
        student sent to another division was proposed again, and the second order only failed
        on confirmation."""
        self.ensure_one()
        groups = self.env["academic.group"].search(
            [
                ("year", "=", self.target_year),
                ("company_id", "=", self.company_id.id),
                ("subject_id", "=", self.subject_id.id),
            ]
        )
        return groups.student_ids | groups._get_pending_registration_students()

    def _get_target_sections(self):
        return (
            self.target_group_id.section_id
            | self.filtered(lambda x: not x.target_group_id).target_section_id
            | self.move_ids.target_group_id.section_id
        )

    def _requires_sale_data(self):
        """Any destination of the line under the sales workflow needs the order data."""
        self.ensure_one()
        return bool(self.student_ids) and (
            self.manage_sale_workflow or any(self.move_ids.target_group_id.mapped("manage_sale_workflow"))
        )

    def _get_destinations(self):
        """Group each student lands in: the one of the line, plus the group picked one by one
        for those sent somewhere else. Creates the group of the line if it does not exist."""
        self.ensure_one()
        moves = self.move_ids.filtered(lambda x: x.student_id in self.student_ids)
        destinations = {group: move.student_id for group, move in moves.grouped("target_group_id").items()}
        staying = self.student_ids - moves.student_id
        if staying:
            target_group = self.target_group_id or self.source_group_id._create_next_year_group(
                level=self.target_level_id,
                section=self.target_section_id,
                division=self.target_division_id,
            )
            destinations[target_group] = destinations.get(target_group, self.env["res.partner"]) | staying
        return destinations

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


class AcademicReenrollmentWizardMove(models.TransientModel):
    _name = "academic.reenrollment.wizard.move"
    _description = "Academic Re-enrollment Student Move"

    _student_unique = models.Constraint(
        "unique(line_id, student_id)",
        "Each student can only be sent to one group.",
    )

    line_id = fields.Many2one("academic.reenrollment.wizard.line", required=True, ondelete="cascade")
    company_id = fields.Many2one(related="line_id.company_id")
    subject_id = fields.Many2one(related="line_id.subject_id")
    target_year = fields.Integer(related="line_id.target_year")
    student_ids = fields.Many2many(related="line_id.student_ids")
    student_id = fields.Many2one(
        "res.partner",
        string="Student",
        required=True,
        domain="[('id', 'in', student_ids)]",
    )
    target_group_id = fields.Many2one(
        "academic.group",
        string="Group",
        required=True,
        domain="[('year', '=', target_year), ('company_id', '=', company_id), ('subject_id', '=', subject_id)]",
        help="Group this student is re-enrolled into, instead of the one of the line.",
    )
