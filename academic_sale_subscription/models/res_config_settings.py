from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    enable_zero_price_subscription_invoice = fields.Boolean(
        config_parameter="academic_sale_subscription.enable_zero_price_subscription_invoice",
        string="Invoice subscriptions with zero total",
    )
    academic_grouped_invoice_notice = fields.Boolean(
        related="company_id.academic_grouped_invoice_notice",
        readonly=False,
    )
    academic_grouped_invoice_notice_template_id = fields.Many2one(
        related="company_id.academic_grouped_invoice_notice_template_id",
        readonly=False,
    )
