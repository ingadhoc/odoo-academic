from odoo import Command, api, fields, models


class PaymentTransactionRetryLines(models.TransientModel):
    _inherit = "payment.transaction.retry.lines"

    partner_ids = fields.Many2many("res.partner", compute="_compute_res_partner", string="Partners")

    @api.depends("invoice_id")
    def _compute_res_partner(self):
        for rec in self:
            rec.partner_ids = [Command.set(rec.invoice_id._get_suggested_responsible()[1])]

    @api.depends("partner_ids")
    def _compute_payment_token_id(self):
        for rec in self:
            token_list = self.env["payment.token"].search(
                [
                    ("company_id", "=", rec.retry_id.company_id.id),
                    ("partner_id", "in", rec.partner_ids.ids),
                ]
            )
            if token_list:
                rec.payment_token_id = token_list.sorted(lambda x: x.create_date)[-1]
            else:
                rec.payment_token_id = False
