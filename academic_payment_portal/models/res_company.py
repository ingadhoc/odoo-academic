from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    users_can_pay_only_oldest_invoice = fields.Boolean(default=True)
