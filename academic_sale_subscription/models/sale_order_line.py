##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    plan_id = fields.Many2one('sale.subscription.plan', related='order_id.plan_id')
    next_invoice_date = fields.Date(related='order_id.next_invoice_date', store=True)
    partner_invoice_id = fields.Many2one(related='order_id.partner_invoice_id', store=True)
    payment_term_id = fields.Many2one(related='order_id.payment_term_id', store=True)

    def open_subscription_form(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'target': 'current',
            'view_mode': 'form',
            'res_id': self.order_id.id,
            'context': dict(self._context),
        }
