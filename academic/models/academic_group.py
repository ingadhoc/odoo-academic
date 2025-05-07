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
    study_plan_level_ids = fields.Many2many(related="company_id.study_plan_id.level_ids")
    level_id = fields.Many2one(
        "academic.level",
        string="Level",
        required=True,
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
        'sale.order.line',
        'group_id',
        string='Main SO Line',
        domain=[('product_id.academic_product_type', '=', 'main')],
    )
    enrollment_so_line_ids = fields.One2many(
        'sale.order.line',
        'group_id',
        string='Enrollment SO Line',
        domain=[('product_id.academic_product_type', '=', 'registration')],
    )
    lead_ids = fields.One2many(
        'crm.lead',
        'group_id',
        string='Leads',
    )
    student_ids = fields.Many2many(
        "res.partner",
        "academic_student_group_ids_student_ids_rel",
        "group_id",
        "partner_id",
        string="Student",
        context={"default_partner_type": "student"},
        domain=[("partner_type", "=", "student")],
    )
    name = fields.Char(
        compute='_compute_name',
        store=True
    )
    active = fields.Boolean(default=True)
    active_student_count = fields.Integer(compute='_compute_active_student_count')
    enrolling_student_count = fields.Integer(compute='_compute_enrolling_student_count')
    prospect_student_count = fields.Integer(compute='_compute_prospect_student_count')
    capacity = fields.Integer()
    vacancies = fields.Integer(compute="_compute_vacancies", store=True)

    @api.depends("company_id", "level_id", "division_id", "year")
    def _compute_name(self):
        for line in self:
            name_parts = [
                line.company_id.name,
                line.level_id.name if line.level_id else None,
                line.division_id.name if line.division_id else None,
                line.level_id.section_id.name if line.level_id and line.level_id.section_id else None,
                self.env._("Year: %s", line.year),
            ]
            line.name = " - ".join(filter(None, name_parts))

    def _compute_active_student_count(self):
        for group in self:
            group.active_student_count = len(group.main_so_line_ids.filtered(lambda x: x.order_id.state == "sale"))

    def _compute_enrolling_student_count(self):
        for group in self:
            group.enrolling_student_count = len(group.enrollment_so_line_ids.filtered(lambda x: not x.order_id.state == "sale"))

    def _compute_prospect_student_count(self):
        for group in self:
            group.prospect_student_count = len(group.lead_ids.filtered(lambda x: x.active and not x.stage_id.is_won))

    @api.depends('main_so_line_ids.order_id.subscription_state', 'capacity')
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
                next_group = rec.copy(default={
                    'year': rec.year + 1,
                    "student_ids": False,
                })

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

    @api.constrains('vacancies')
    def _check_vacancies(self):
        if self.filtered(lambda x: x.vacancies < 0):
            raise ValidationError(_('There can be no negative vacancies. Increase group capacity.'))

    def open_leads(self):
        action = self.env["ir.actions.actions"]._for_xml_id("crm.crm_lead_action_pipeline")
        action.update({
            'context': {'search_default_group_id': self.id},
        })
        return action

    def open_enrolling_sales(self):
        action = self.env["ir.actions.actions"]._for_xml_id("sale.action_quotations_with_onboarding")
        action.update({
            'domain': [('id', 'in', self.enrollment_so_line_ids.mapped('order_id').ids)],
        })
        return action

    def open_students(self):
        action = self.env.ref('academic.action_academic_partner_students').read()[0]
        action.update({
            'domain': [('id', 'in', self.main_so_line_ids.mapped('order_id.partner_id').ids)],
            'views': [(False, 'list'), (False, 'form')],
            'context': {'from_open_student_view': True}
        })
        return action

    # TODO ver si se hace en base a suscripciones
    # @api.constrains('academic_group_link_ids')
    # def _check_unique_student_in_group(self):
    #     for rec in self:
    #         students = rec.academic_group_link_ids.mapped('student_id')
    #         if len(rec.academic_group_link_ids.filtered('student_id')) != len(students):
    #             raise ValidationError(_('There cannot be a repeated student in a group.'))
