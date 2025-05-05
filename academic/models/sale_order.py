##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    partner_id = fields.Many2one(
        domain="[('type', '!=', 'private'), ('company_id', 'in', (False, company_id)), ('partner_type', '=', 'student')]"
    )
    partner_invoice_ids = fields.Many2many("res.partner", compute="_compute_partner_invoice")
    group_id = fields.Many2one(related='order_line.group_id')
    enolling_group_id = fields.Many2one(related='order_line.group_id', domain="[('order_line.product_id.academic_product_type', '=', 'registration')]")

    # dejamos solo depends a partner_id para que si cambia algo de la asignación no se re-calculen todas las ventas existentes
    @api.depends("partner_id")
    def _compute_partner_invoice(self):
        orders = self.filtered("partner_id")
        for rec in orders:
            rec.partner_invoice_ids = rec.partner_id.payment_responsible_ids
        (self - orders).partner_invoice_ids = False

    @api.depends("partner_invoice_ids")
    def _compute_partner_invoice_id(self):
        # si bien en el dominio solo permitimos estudiantes, para no romper demo data de odoo ni tests, si no es un estudiante
        # dejamos compute by super
        students_orders = self.filtered(lambda x: x.partner_id.partner_type == "student")
        for order in students_orders:
            order.partner_invoice_id = order.partner_invoice_ids._origin[:1]
        super(SaleOrder, self - students_orders)._compute_partner_invoice_id()

    def _prepare_invoice(self):
        res = super()._prepare_invoice()
        res["student_id"] = self.partner_id.id
        return res

    def action_confirm(self):
        for rec in self:
            rec.message_subscribe(
                [
                    payment_responsible.id
                    for payment_responsible in rec.partner_invoice_id | rec.partner_invoice_ids
                    if payment_responsible not in rec.sudo().message_partner_ids
                ]
            )
        return super().action_confirm()

    def _message_get_default_recipients(self):
        """Por defecto las plantillas mandan a partner_id pero para nosotros el partners es el estudiante.
        Cambiamos plantillas para que usen el campo "use_default_to" y luego cae en este método de python donde
        podemos ir mejorando a medida que nos pidan y modificar la logica de recipients.
        Por ahora lo mandamos solo al partner de facturación si está definido
        """
        default_recipients = super()._message_get_default_recipients()
        for record in self:
            payment_responsible = record.partner_invoice_id | record.partner_invoice_ids
            if payment_responsible:
                default_recipients[record.id] = {
                    "email_cc": False,
                    "email_to": False,
                    "partner_ids": payment_responsible.ids,
                }
        return default_recipients
