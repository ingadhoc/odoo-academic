##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    company_group_ids = fields.One2many(
        "academic.group",
        "company_id",
        string="Groups",
    )
    section_ids = fields.Many2many("academic.section", string="Study Plans")
    family_required = fields.Boolean(default=True)  # Falta revisar la implementación con ese booleano en False
