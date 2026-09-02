##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from datetime import date

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class AcademicGroup(models.Model):
    _name = "academic.group"
    _description = "group"
    _order = "year desc, name"

    _group_unique = models.Constraint(
        "unique(subject_id, company_id, level_id, year, division_id, section_id)",
        "Group should be unique per Institution, Study Plan, Subject, Course-Division and Year",
    )

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
    employee_teacher_id = fields.Many2one(
        "hr.employee",
        string="Docente a cargo",
        required=False,
        check_company=True,
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
    student_count = fields.Integer(compute="_compute_student_count", store=True)

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

    def _get_next_year_group(self, level=None):
        """`level` overrides the level to search for, to follow the study plan sequence."""
        self.ensure_one()
        # active_test=False: the unique constraint ignores `active`, so an archived group
        # that is not found here makes the copy below crash on a unique violation
        return (
            self.env["academic.group"]
            .with_context(active_test=False)
            .search(
                [
                    ("year", "=", self.year + 1),
                    ("company_id", "=", self.company_id.id),
                    ("section_id", "=", self.section_id.id),
                    ("level_id", "=", (level or self.level_id).id),
                    ("division_id", "=", self.division_id.id),
                    ("subject_id", "=", self.subject_id.id),
                ],
                limit=1,
            )
        )

    def _create_next_year_group(self, level=None):
        self.ensure_one()
        return self.copy(
            default={
                "year": self.year + 1,
                "level_id": (level or self.level_id).id,
                "student_ids": False,
            }
        )

    def _get_or_create_next_year_group(self, level=None):
        self.ensure_one()
        return self._get_next_year_group(level=level) or self._create_next_year_group(level=level)

    def _get_groups_action(self):
        action = self.env["ir.actions.actions"]._for_xml_id("academic.action_academic_group_groups")
        action.update({"domain": [("id", "in", self.ids)], "context": {}})
        return action

    def _get_next_year_level(self):
        """Next level in the study plan. Empty when the group closes the plan (its students
        are not re-enrolled), the same level when the plan has no sequence configured."""
        self.ensure_one()
        if self.section_id._is_last_level(self.level_id):
            return self.env["academic.level"]
        return self.section_id._get_next_level(self.level_id) or self.level_id

    def create_next_year_groups(self):
        # estamos pasando de un año a otro sin usar study plan por lo siguiente:
        # a) hay muchos colegios que no lo tienen bien implmentado
        # b) los study plan no pueden reflejar todos los casos todavia (por )
        existing = next_groups = self.env["academic.group"]
        for rec in self:
            found = rec._get_next_year_group()
            existing |= found
            next_groups |= found or rec._create_next_year_group()

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "type": "success",
                "message": self.env._(
                    "%(created)s next year group(s) created, %(existing)s already existed.",
                    created=len(next_groups - existing),
                    existing=len(existing),
                ),
                "next": next_groups._get_groups_action(),
            },
        }

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

    @api.depends("student_ids")
    def _compute_student_count(self):
        for group in self:
            group.student_count = len(group.student_ids)

    @api.constrains("employee_teacher_id", "company_id")
    def _check_employee_teacher_company(self):
        for group in self.filtered("employee_teacher_id"):
            if group.employee_teacher_id.company_id != group.company_id:
                raise ValidationError(self.env._("The teacher in charge must belong to the same company as the group."))
