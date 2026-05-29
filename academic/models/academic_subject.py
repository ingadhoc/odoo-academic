##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class AcademicSubject(models.Model):
    _name = "academic.subject"
    _description = "subject"

    _subject_template_unique = models.Constraint(
        "UNIQUE(template_id, state_id, company_id)",
        "There is already a subject for this template, jurisdiction and company.",
    )

    name = fields.Char(
        required=True,
    )
    company_id = fields.Many2one(
        "res.company",
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    state_id = fields.Many2one(
        "res.country.state",
        related="company_id.state_id",
        index=True,
        readonly=True,
        store=True,
    )
    template_id = fields.Many2one(
        "academic.subject.template",
        required=True,
        ondelete="restrict",
        index=True,
    )
    code = fields.Char(
        related="template_id.code",
        readonly=True,
        store=True,
    )
    group_ids = fields.One2many(
        "academic.group",
        "subject_id",
        string="Groups",
    )
    employees_asignatures_ids = fields.One2many(comodel_name="hr.employee.asignatures", inverse_name="subject_id")

    @api.constrains("company_id", "state_id")
    def _check_company_state_consistency(self):
        for rec in self:
            if rec.company_id.state_id and rec.state_id != rec.company_id.state_id:
                raise ValidationError(self.env._("The subject jurisdiction must match the company jurisdiction."))
