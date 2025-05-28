##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from datetime import date

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AcademicGroup(models.Model):
    _name = "academic.group"
    _description = "group"
    _order = "year desc, name"

    _sql_constraints = [
        (
            "group_unique",
            "unique(subject_id, company_id, level_id, year, division_id)",
            "Group should be unique per Institution, Subject," " Course-Division and Year",
        )
    ]

    type = fields.Selection(
        [
            ("student", "Student"),
            ("teacher", "Teacher"),
            ("administrator", "Administrator"),
            ("gral_administrator", "gral_administrator"),
            ("parent", "Relative"),
        ]
    )
    year = fields.Integer(required=True, default=date.today().year, index=True)
    division_id = fields.Many2one(
        "academic.division",
        string="Division",
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        context={"default_is_company": True},
        default=lambda self: self.env.company,
    )
    section_ids = fields.Many2many("academic.section", related="company_id.section_ids")
    section_id = fields.Many2one(
        "academic.section",
        string="Study Plan",
        required=True,
        domain="[('id', 'in', section_ids)]",
    )
    level_ids = fields.Many2many(related="section_id.level_ids")
    level_id = fields.Many2one(
        "academic.level",
        string="Level",
        required=True,
        domain="[('id', 'in', level_ids)]",
    )
    subject_id = fields.Many2one("academic.subject", string="Subject", required=False, index=True)
    teacher_id = fields.Many2one(
        "res.partner",
        string="Teacher",
        required=False,
        context={"default_partner_type": "teacher"},
        domain=[("partner_type", "=", "teacher")],
    )
    fee_so_line_ids = fields.One2many(
        "sale.order.line",
        "group_id",
        string="Main SO Line",
        domain=[("product_id.academic_product_type", "=", "fee")],
    )
    registration_so_line_ids = fields.One2many(
        "sale.order.line",
        "group_id",
        string="Registration SO Line",
        domain=[("product_id.academic_product_type", "=", "registration")],
    )
    opportunities_ids = fields.One2many(
        "crm.lead",
        "group_id",
        string="Opportunities",
    )
    student_ids = fields.Many2many(
        "res.partner",
        "academic_student_group_ids_student_ids_rel",
        "group_id",
        "partner_id",
        string="Student",
        context={"default_partner_type": "student"},
        domain=[("partner_type", "=", "student")],
        compute="_compute_student_ids",
        store=True,
        readonly=False,
    )
    name = fields.Char(compute="_compute_name", store=True)
    active = fields.Boolean(default=True)
    fee_student_count = fields.Integer(compute="_compute_fee_student_count")
    no_fee_student_count = fields.Integer(compute="_compute_no_fee_student_count")
    registration_student_count = fields.Integer(compute="_compute_registration_student_count")
    opportunities_student_count = fields.Integer(compute="_compute_opportunities_student_count")
    capacity = fields.Integer()
    vacancies = fields.Integer(compute="_compute_vacancies", store=True)
    manage_sale_workflow = fields.Boolean(compute="_compute_manage_sale_workflow", store=True, readonly=False)

    @api.depends("company_id", "level_id", "division_id", "year")
    def _compute_name(self):
        for line in self:
            name_parts = [
                line.company_id.name,
                line.section_id.name,
                line.level_id.name,
                line.division_id.name if line.division_id else None,
                self.env._("Year: %s", line.year),
            ]
            line.name = " - ".join(filter(None, name_parts))

    # TODO mejorar todos estos compute, read group? podemos simplificar calculos? query?
    def _compute_fee_student_count(self):
        for group in self:
            group.fee_student_count = len(
                group.fee_so_line_ids.filtered(lambda x: x.state == "sale").mapped("order_id.partner_id")
            )

    def _compute_no_fee_student_count(self):
        for group in self:
            group.no_fee_student_count = len(
                group.registration_so_line_ids.filtered(lambda x: x.state in ["sale"]).mapped("order_id.partner_id")
                - group.fee_so_line_ids.mapped("order_id.partner_id")
            )

    def _compute_registration_student_count(self):
        # TODO tal vez deberiamos hacer una constraint que no pueda permitir dos lineas de venta "activas" para mismo academic_product_type, student y grupo
        # luego el mapped no seria necesario
        for group in self:
            group.registration_student_count = len(
                group.registration_so_line_ids.filtered(lambda x: x.state in ["draft", "sent"]).mapped(
                    "order_id.partner_id"
                )
            )

    def _compute_opportunities_student_count(self):
        for group in self:
            group.opportunities_student_count = len(
                group.opportunities_ids.filtered(
                    lambda x: x.active
                    and x.partner_id
                    not in group.registration_so_line_ids.mapped("order_id.partner_id")
                    | group.fee_so_line_ids.mapped("order_id.partner_id")
                )
            )

    @api.depends("fee_so_line_ids.order_id.state", "capacity", "manage_sale_workflow")
    def _compute_vacancies(self):
        for group in self:
            if group.manage_sale_workflow:
                group.vacancies = group.capacity - len(
                    group.registration_so_line_ids.filtered(lambda x: x.order_id.state == "sale").mapped(
                        "order_id.partner_id"
                    )
                )
            else:
                group.vacancies = group.capacity - len(group.student_ids)

    def create_next_year_groups(self):
        # estamos pasando de un año a otro sin usar study plan por lo siguiente:
        # a) hay muchos colegios que no lo tienen bien implmentado
        # b) los study plan no pueden reflejar todos los casos todavia (por )

        for rec in self:
            next_group = rec.env["academic.group"].search(
                [
                    ("year", "=", rec.year + 1),
                    ("company_id", "=", rec.company_id.id),
                    ("level_id", "=", rec.level_id.id),
                    ("division_id", "=", rec.division_id.id),
                ],
                limit=1,
            )

            if not next_group:
                next_group = rec.copy(
                    default={
                        "year": rec.year + 1,
                        "student_ids": False,
                    }
                )

    def open_student_view(self):
        action = self.env.ref("academic.action_academic_partner_students").read()[0]
        action.update(
            {
                "domain": [("current_main_group_id", "=", self.id)],
                "views": [(False, "list")],
                "context": {"from_open_student_view": True},
            }
        )
        return action

    @api.constrains("vacancies")
    def _check_vacancies(self):
        if self.filtered(lambda x: x.vacancies < 0):
            raise ValidationError(_("There can be no negative vacancies. Increase group capacity."))

    def open_opportunities(self):
        action = self.env["ir.actions.actions"]._for_xml_id("crm.crm_lead_action_pipeline")
        action.update(
            {
                "context": {"search_default_group_id": self.id},
            }
        )
        return action

    def open_registration_sales(self):
        action = self.env["ir.actions.actions"]._for_xml_id("sale.action_quotations_with_onboarding")
        action.update({"domain": [("id", "in", self.registration_so_line_ids.mapped("order_id").ids)], "context": {}})
        return action

    def open_no_fee_students(self):
        action = self.env.ref("academic.action_academic_partner_students").read()[0]
        action.update(
            {
                "domain": [
                    (
                        "id",
                        "in",
                        (
                            self.registration_so_line_ids.filtered(lambda x: x.state in ["sale"]).mapped(
                                "order_id.partner_id"
                            )
                            - self.fee_so_line_ids.mapped("order_id.partner_id")
                        ).ids,
                    )
                ],
                "views": [(False, "list"), (False, "form")],
                "context": {"from_open_student_view": True},
            }
        )
        return action

    def open_fee_sales(self):
        action = self.env["ir.actions.actions"]._for_xml_id("sale.action_quotations_with_onboarding")
        action.update(
            {
                "domain": [
                    ("id", "in", self.fee_so_line_ids.filtered(lambda x: x.state == "sale").mapped("order_id").ids)
                ],
                "context": {},
            }
        )
        return action

    def open_students(self):
        action = self.env.ref("academic.action_academic_partner_students").read()[0]
        action.update(
            {
                "domain": [("id", "in", self.student_ids.ids)],
                "views": [(False, "list"), (False, "form")],
                "context": {"from_open_student_view": True},
            }
        )
        return action

    @api.depends("manage_sale_workflow", "registration_so_line_ids.state", "fee_so_line_ids.state")
    def _compute_student_ids(self):
        for group in self.filtered("manage_sale_workflow"):
            group.student_ids = group.fee_so_line_ids.filtered(lambda x: x.order_id.state == "sale").mapped(
                "order_id.partner_id"
            ) | group.registration_so_line_ids.filtered(lambda x: x.order_id.state == "sale").mapped(
                "order_id.partner_id"
            )

    @api.constrains("capacity")
    def _check_capacity(self):
        if self.filtered(lambda x: x.capacity <= 0):
            raise ValidationError(self.env._("The capacity must be greater than 0."))

    @api.depends("subject_id")
    def _compute_manage_sale_workflow(self):
        groups_with_subject = self.filtered("subject_id")
        groups_with_subject.manage_sale_workflow = False
        (self - groups_with_subject).manage_sale_workflow = True

    def write(self, vals):
        if "manage_sale_workflow" in vals and not (
            self.env.user.has_group("academic.group_manager") or self.env.user._is_admin()
        ):
            raise ValidationError(_("You are not allowed to modify the sale workflow setting."))
        return super().write(vals)
