##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields


class ResCompany(models.Model):

    _inherit = 'res.company'

    company_group_ids = fields.One2many(
        'academic.group',
        'company_id',
        string='Groups',
    )
