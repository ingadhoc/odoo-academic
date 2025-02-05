##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import fields, models


class ResPartnerCategory(models.Model):
    _inherit = "res.partner.category"
    _check_company_domain = models.check_company_domain_parent_of

    company_id = fields.Many2one("res.company", "Company", index=True)
