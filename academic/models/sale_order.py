##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import api, models, fields, _


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    partner_id = fields.Many2one(
        domain="[('type', '!=', 'private'), ('company_id', 'in', (False, company_id)), ('partner_type', '=', 'student')]")
    partner_invoice_ids = fields.Many2many('res.partner', compute='_compute_partner_invoice')

    @api.depends('partner_id.partner_link_ids.role_ids')
    def _compute_partner_invoice(self):
        for rec in self:
            rec.partner_invoice_ids = rec.partner_id.partner_link_ids.filtered(
                lambda x: self.env.ref('academic.paying_role') in x.role_ids).mapped('partner_id') if rec.partner_id else False

    @api.depends('partner_invoice_ids')
    def _compute_partner_invoice_id(self):
        for order in self:
            order.partner_invoice_id = order.partner_invoice_ids[:1]
