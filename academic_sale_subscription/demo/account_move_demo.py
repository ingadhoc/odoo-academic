# pylint: disable=consider-merging-classes-inherited
from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def _init_academic_subscription_demo(self):
        subscriptions = self.browse(
            [
                self.env.ref("academic_sale_subscription.subscription_garcia_sofia").id,
                self.env.ref("academic_sale_subscription.subscription_lopez_martin").id,
                self.env.ref("academic_sale_subscription.subscription_rodriguez_valentina").id,
            ]
        )

        invoices_to_post = subscriptions.mapped("invoice_ids").filtered(lambda inv: inv.state == "draft")
        if invoices_to_post:
            invoices_to_post.action_post()

        cash_journal = self.env["account.journal"].search([("type", "=", "cash")], limit=1)
        if not cash_journal:
            cash_journal = self.env["account.journal"].search([("type", "=", "bank")], limit=1)

        garcia_subscription = self.env.ref("academic_sale_subscription.subscription_garcia_sofia")
        garcia_invoice = garcia_subscription.invoice_ids.filtered(lambda inv: inv.state == "posted")
        if garcia_invoice and cash_journal:
            payment_garcia = self.env["account.payment"].create(
                {
                    "payment_type": "inbound",
                    "partner_type": "customer",
                    "partner_id": garcia_subscription.partner_invoice_id.id,
                    "amount": 18000,
                    "journal_id": cash_journal.id,
                    "payment_method_id": self.env.ref("account.account_payment_method_manual_in").id,
                    "memo": "Pago cuota + inscripción García Sofía",
                }
            )
            payment_garcia.action_post()

        lopez_subscription = self.env.ref("academic_sale_subscription.subscription_lopez_martin")
        lopez_invoice = lopez_subscription.invoice_ids.filtered(lambda inv: inv.state == "posted")
        if lopez_invoice and cash_journal:
            payment_lopez = self.env["account.payment"].create(
                {
                    "payment_type": "inbound",
                    "partner_type": "customer",
                    "partner_id": lopez_subscription.partner_invoice_id.id,
                    "amount": 15000,
                    "journal_id": cash_journal.id,
                    "payment_method_id": self.env.ref("account.account_payment_method_manual_in").id,
                    "memo": "Pago parcial cuota López Martín",
                }
            )
            payment_lopez.action_post()
