##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models


class AccountMoveSend(models.TransientModel):
    _inherit = 'account.move.send'

    def _get_default_mail_partner_ids(self, move, mail_template, mail_lang):
        partners_invoice = move.student_id.get_payment_responsible() if move.student_id else self.env['res.partner']
        return super()._get_default_mail_partner_ids(move, mail_template, mail_lang) | partners_invoice
