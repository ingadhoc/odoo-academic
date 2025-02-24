from odoo import models, fields


class ResCompany(models.Model):

    _inherit = 'res.company'

    users_can_pay_only_oldest_invoice = fields.Boolean(default=True)
