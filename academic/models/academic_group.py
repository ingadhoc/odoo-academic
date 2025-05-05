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
    academic_group_link_ids = fields.One2many(
        'academic.group.link',
        'group_id',
        string='Students',
    )
    active_link_ids = fields.One2many(
        'academic.group.link',
        'group_id',
        string='Active Students',
        domain=[('status','in', ['active', 'enrolled'])],
    )
    name = fields.Char(
        compute='_compute_name',
        store=True
    )
    active = fields.Boolean(default=True)
    active_student_count = fields.Integer(compute='_compute_student_count')
    enrolling_student_count = fields.Integer(compute='_compute_student_count')
    prospect_student_count = fields.Integer(compute='_compute_student_count')
    leave_student_count = fields.Integer(compute='_compute_student_count')
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

    # por ahora como a nivel ui nunca se necesita re comptuar en imsma vista
    # @api.depends('academic_group_link_ids')
    def _compute_student_count(self):
        # los estados lost y not_enrolled no los contamos, es basicamente que alguien no rematricula en un determinado grupo o no avanza la oportunidad.
        # para verlos usamos el boton correspondiente (enrolling / prospect) y luego filtro
        for group in self:
            group.active_student_count = len(group.academic_group_link_ids.filtered(lambda x: x.status in ['active', 'enrolled']))
            group.enrolling_student_count = len(group.academic_group_link_ids.filtered(lambda x: x.status in ['enrolling']))
            group.prospect_student_count = len(group.academic_group_link_ids.filtered(lambda x: x.status in ['prospect']))
            group.leave_student_count = len(group.academic_group_link_ids.filtered(lambda x: x.status in ['leave']))

    @api.depends('academic_group_link_ids.status', 'capacity')
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

    # @api.constrains('vacancies')
    # def _check_vacancies(self):
    #     if self.filtered(lambda x: x.vacancies < 0):
    #         raise ValidationError(_('There can be no negative vacancies. Increase group capacity.'))

    def open_leads(self):
        action = self.env["ir.actions.actions"]._for_xml_id("crm.crm_lead_action_pipeline")
        action.update({
            'domain': [('id', 'in', self.academic_group_link_ids.mapped('lead_id').ids)],
        })
        return action

    def open_enrolling_sales(self):
        action = self.env["ir.actions.actions"]._for_xml_id("sale.action_quotations_with_onboarding")
        action.update({
            'domain': [('id', 'in', self.academic_group_link_ids.filtered('registration_so_line_id').mapped('registration_so_line_id.order_id').ids)],
        })
        return action

    def open_students(self):
        action = self.env.ref('academic.action_academic_partner_students').read()[0]
        domain = [('academic_group_link_ids.group_id', '=', self.id)]
        domain += [('academic_group_link_ids.status', 'in', ['active', 'enrolled'])]
        action.update({
            'domain': domain,
            'views': [(False, 'list'), (False, 'form')],
            'context': {'from_open_student_view': True}
        })
        return action

    @api.constrains('academic_group_link_ids')
    def _check_unique_student_in_group(self):
        for rec in self:
            students = rec.academic_group_link_ids.mapped('student_id')
            if len(rec.academic_group_link_ids.filtered('student_id')) != len(students):
                raise ValidationError(_('There cannot be a repeated student in a group.'))
