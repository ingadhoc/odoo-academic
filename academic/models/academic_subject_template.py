##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import api, fields, models


class AcademicSubjectTemplate(models.Model):
    _name = "academic.subject.template"
    _description = "Subject Template"
    _rec_name = "display_name"

    _code_unique = models.Constraint(
        "UNIQUE(code)",
        "The canonical code must be unique.",
    )

    name = fields.Char(required=True)
    code = fields.Char(required=True, index=True)
    area = fields.Char()
    subject_ids = fields.One2many("academic.subject", "template_id")
    display_name = fields.Char(compute="_compute_display_name", store=True)

    @api.depends("code", "name")
    def _compute_display_name(self):
        for rec in self:
            if rec.code and rec.name:
                rec.display_name = f"[{rec.code}] {rec.name}"
            else:
                rec.display_name = rec.name or rec.code or False
