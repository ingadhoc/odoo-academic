from odoo import models


class PaymentTransaction(models.Model):
    _inherit = "payment.transaction"

    def _post_process(self):
        return super(PaymentTransaction, self.with_context(from_payment_processing=True))._post_process()
