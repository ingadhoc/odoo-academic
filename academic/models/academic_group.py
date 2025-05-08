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
    main_so_line_ids = fields.One2many(
        "sale.order.line",
        "group_id",
        string="Main SO Line",
        domain=[("product_id.academic_product_type", "=", "main")],
    )
    enrollment_so_line_ids = fields.One2many(
        "sale.order.line",
        "group_id",
        string="Enrollment SO Line",
        domain=[("product_id.academic_product_type", "=", "registration")],
    )
    lead_ids = fields.One2many(
        "crm.lead",
        "group_id",
        string="Leads",
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
    active_student_count = fields.Integer(compute="_compute_active_student_count")
    enrolling_student_count = fields.Integer(compute="_compute_enrolling_student_count")
    prospect_student_count = fields.Integer(compute="_compute_prospect_student_count")
    capacity = fields.Integer()
    vacancies = fields.Integer(compute="_compute_vacancies", store=True)

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

    def _compute_active_student_count(self):
        for group in self:
            group.active_student_count = len(group.main_so_line_ids.mapped("order_id.partner_id"))

    def _compute_enrolling_student_count(self):
        for group in self:
            group.enrolling_student_count = len(
                group.enrollment_so_line_ids.mapped("order_id.partner_id")
                - group.main_so_line_ids.mapped("order_id.partner_id")
            )

    def _compute_prospect_student_count(self):
        for group in self:
            group.prospect_student_count = len(
                group.lead_ids.filtered(
                    lambda x: x.active
                    and x.partner_id not in group.enrollment_so_line_ids.mapped("order_id.partner_id")
                    and x.partner_id not in group.main_so_line_ids.mapped("order_id.partner_id")
                )
            )

    @api.depends("main_so_line_ids.order_id.state", "capacity")
    def _compute_vacancies(self):
        for group in self:
            group.vacancies = group.capacity - group.active_student_count

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

    def open_leads(self):
        action = self.env["ir.actions.actions"]._for_xml_id("crm.crm_lead_action_pipeline")
        action.update(
            {
                "context": {"search_default_group_id": self.id},
            }
        )
        return action

    def open_enrolling_sales(self):
        action = self.env["ir.actions.actions"]._for_xml_id("sale.action_quotations_with_onboarding")
        action.update({"domain": [("id", "in", self.enrollment_so_line_ids.mapped("order_id").ids)], "context": {}})
        return action

    def open_active_sales(self):
        action = self.env["ir.actions.actions"]._for_xml_id("sale.action_quotations_with_onboarding")
        action.update({"domain": [("id", "in", self.main_so_line_ids.mapped("order_id").ids)], "context": {}})
        return action

    def open_students(self):
        action = self.env.ref("academic.action_academic_partner_students").read()[0]
        action.update(
            {
                "domain": [("id", "in", self.main_so_line_ids.mapped("order_id.partner_id").ids)],
                "views": [(False, "list"), (False, "form")],
                "context": {"from_open_student_view": True},
            }
        )
        return action

    @api.depends("subject_id", "main_so_line_ids.order_id.state", "main_so_line_ids.order_id.partner_id")
    def _compute_student_ids(self):
        for group in self.filtered(lambda x: not x.subject_id):
            confirmed_lines = group.main_so_line_ids.filtered(lambda l: l.order_id.state == "sale")
            group.student_ids = confirmed_lines.mapped("order_id.partner_id")
