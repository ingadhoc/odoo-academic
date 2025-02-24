from odoo import models


class ResPartner(models.Model):

    _inherit = 'res.partner'

    def _get_first_residual_invoice(self):
        self.ensure_one()
        return self.env['account.move'].search(
            [('amount_residual', '>', 0),
             ('state', '=', 'posted'),
             ('move_type', '=', 'out_invoice'),
             ('partner_id', '=', self.id)],
        limit=1, order="invoice_date_due ASC")
