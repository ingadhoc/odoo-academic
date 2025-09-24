##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from datetime import date

from odoo import api, fields, models


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
    subject_id = fields.Many2one("academic.subject", string="Subject/Course", required=False, index=True)
    teacher_id = fields.Many2one(
        "res.partner",
        string="Teacher",
        required=False,
        context={"default_partner_type": "teacher"},
        domain=[("partner_type", "=", "teacher")],
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
    name = fields.Char(compute="_compute_name", store=True)
    active = fields.Boolean(default=True)
    capacity = fields.Integer()
    student_count = fields.Integer(compute="_compute_student_count")

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

    def _compute_student_count(self):
        for group in self:
            group.student_count = len(group.student_ids)
