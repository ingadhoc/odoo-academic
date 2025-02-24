# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    users_can_pay_only_oldest_invoice = fields.Boolean(
        related="company_id.users_can_pay_only_oldest_invoice", readonly=False
    )
