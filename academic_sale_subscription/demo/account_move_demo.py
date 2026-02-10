# pylint: disable=consider-merging-classes-inherited
from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def _init_academic_subscription_demo(self):
        """Initialize demo data for academic subscriptions: create invoices and payments."""
        try:
            # Obtener las suscripciones directamente sin usar browse
            subscription_refs = [
                "academic_sale_subscription.subscription_garcia_sofia",
                "academic_sale_subscription.subscription_lopez_martin",
                "academic_sale_subscription.subscription_rodriguez_valentina",
            ]

            subscriptions = self.env["sale.order"]
            for ref in subscription_refs:
                subscription = self.env.ref(ref, raise_if_not_found=False)
                if subscription:
                    subscriptions |= subscription

            if not subscriptions:
                return

            invoices_to_post = subscriptions.mapped("invoice_ids").filtered(lambda inv: inv.state == "draft")
            if invoices_to_post:
                self._ensure_invoice_accounts(invoices_to_post)

                # Solo postear facturas que tengan todas sus líneas con cuentas configuradas
                invoices_to_post = invoices_to_post.filtered(
                    lambda inv: all(
                        line.account_id or line.display_type in ("line_section", "line_note")
                        for line in inv.invoice_line_ids
                    )
                )

                if invoices_to_post:
                    try:
                        invoices_to_post.action_post()
                    except Exception:
                        return  # No crear pagos si las facturas fallan
                else:
                    return

            self._create_demo_payments(subscriptions)

        except Exception:
            return

    def _ensure_invoice_accounts(self, invoices):
        """Ensure all invoice lines have accounts configured."""
        for invoice in invoices:
            for line in invoice.invoice_line_ids:
                if line.display_type in (False, "product") and not line.account_id:
                    account = self._get_line_account(line, invoice)
                    if account:
                        line.account_id = account

    def _get_line_account(self, line, invoice):
        """Get the appropriate account for an invoice line."""
        # Intentar obtener la cuenta de ingresos del producto
        if line.product_id:
            accounts = line.product_id.product_tmpl_id._get_product_accounts()
            account = accounts.get("income")
            if account:
                return account

        # Si no hay cuenta del producto, usar la cuenta por defecto del journal
        if invoice.journal_id.default_account_id:
            return invoice.journal_id.default_account_id

        # Último recurso: buscar cualquier cuenta de ingresos
        return self.env["account.account"].search(
            [
                ("account_type", "=", "income"),
                ("company_id", "=", invoice.company_id.id),
            ],
            limit=1,
        )

    def _create_demo_payments(self, subscriptions):
        """Create demo payments for posted invoices."""

    def _create_demo_payments(self, subscriptions):
        """Create demo payments for posted invoices."""
        cash_journal = self._get_payment_journal()

        payment_data = [
            {
                "subscription_ref": "subscription_garcia_sofia",
                "amount": 18000,
                "memo": "Pago cuota + inscripción García Sofía",
            },
            {
                "subscription_ref": "subscription_lopez_martin",
                "amount": 15000,
                "memo": "Pago parcial cuota López Martín",
            },
        ]

        for data in payment_data:
            try:
                subscription = self.env.ref(
                    f"academic_sale_subscription.{data['subscription_ref']}", raise_if_not_found=False
                )
                if not subscription:
                    continue

                invoice = subscription.invoice_ids.filtered(lambda inv: inv.state == "posted")
                if invoice:
                    payment = self.env["account.payment"].create(
                        {
                            "payment_type": "inbound",
                            "partner_type": "customer",
                            "partner_id": subscription.partner_invoice_id.id,
                            "amount": data["amount"],
                            "journal_id": cash_journal.id,
                            "payment_method_id": self.env.ref("account.account_payment_method_manual_in").id,
                            "memo": data["memo"],
                        }
                    )
                    payment.action_post()

            except Exception:
                continue

    def _get_payment_journal(self):
        """Get a valid payment journal (cash or bank) with default account configured."""
        for journal_type in ["cash", "bank"]:
            journal = self.env["account.journal"].search(
                [
                    ("type", "=", journal_type),
                    ("default_account_id", "!=", False),
                ],
                limit=1,
            )
            if journal:
                return journal
        return False
