from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _has_to_be_paid(self):
        self.ensure_one()
        if (
            self.company_id.users_can_pay_only_oldest_invoice
            and self.partner_id.sudo()._get_first_residual_invoice() != self
        ):
            return False
        return super()._has_to_be_paid()
