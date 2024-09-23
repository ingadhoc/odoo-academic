##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    current_subscription_ids = fields.One2many(
        'sale.order',
        compute='_compute_current_subscription',
    )

    def _compute_current_subscription(self):
        for rec in self:
            rec.current_subscription_ids = self.env['sale.order'].search([
                ('partner_id', '=', rec.id),
                ("subscription_state", "=", "3_progress")
            ])
