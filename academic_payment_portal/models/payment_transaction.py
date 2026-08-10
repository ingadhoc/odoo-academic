from odoo import models


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    def _create_payment(self, **extra_create_values):
        self.ensure_one()

        partner_id = self.super().mapped("invoice_ids.partner_id")
        if len(partner_id) == 1 and self.partner_id.commercial_partner_id != partner_id[0].commercial_partner_id:
            return super(PaymentTransaction, self.with_context(transaction_force_partner_id=partner_id))._create_payment(**extra_create_values)
        return super()._create_payment(**extra_create_values)
