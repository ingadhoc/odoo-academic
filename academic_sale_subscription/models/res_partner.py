##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    current_subscription_ids = fields.One2many(
        'sale.order.line',
        compute='_compute_current_subscription',
    )

    def _compute_current_subscription(self):
        for rec in self:
            rec.current_subscription_ids = self.env['sale.order.line'].search([
                ('order_partner_id', '=', rec.id),
                ('order_id.subscription_state', '=', '3_progress')
            ]).filtered(
                lambda line: not line.order_id.end_date or line.order_id.next_invoice_date < line.order_id.end_date
            )
