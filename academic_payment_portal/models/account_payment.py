from odoo import api,  models


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    @api.model_create_multi
    def create(self, vals_list):
        transaction_force_partner_id = self.env.context.get('transaction_force_partner_id')
        for vals in vals_list:
            if vals.get('payment_transaction_id') and transaction_force_partner_id:
                vals['partner_id'] = transaction_force_partner_id.commercial_partner_id.id
        return super().create(vals_list)
