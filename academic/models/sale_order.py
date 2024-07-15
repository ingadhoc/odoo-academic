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

    # dejamos solo depends a partner_id para que si cambia algo de la asignación no se re-calculen todas las ventas existentes
    @api.depends('partner_id')
    def _compute_partner_invoice(self):
        for rec in self:
            rec.partner_invoice_ids = rec.partner_id.student_link_ids.filtered(
                lambda x: self.env.ref('academic.paying_role') in x.role_ids).mapped('partner_id') if rec.partner_id else False

    @api.depends('partner_invoice_ids')
    def _compute_partner_invoice_id(self):
        for order in self:
            order.partner_invoice_id = order.partner_invoice_ids[:1]

    def _prepare_invoice(self):
        res = super()._prepare_invoice()
        res["student_id"] = self.partner_id.id
        return res
