from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    enable_zero_price_subscription_invoice = fields.Boolean(
        config_parameter="academic_sale_subscription.enable_zero_price_subscription_invoice",
        string="Invoice subscriptions with zero total",
    )
