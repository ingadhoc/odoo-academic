##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from dateutil.relativedelta import relativedelta
from odoo import Command, fields
from odoo.addons.account_payment.tests.common import AccountPaymentCommon
from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestPortalPayment(AccountPaymentCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.today = fields.Date.today()
        cls.env["ir.config_parameter"].sudo().set_bool("account_payment.enable_portal_payment", True)
        cls.student = cls.env["res.partner"].create({"name": "Student"})
        cls.payer = cls.env["res.partner"].create({"name": "Payer"})

    def _create_posted_invoice(self, partner, invoice_date):
        # Without payment terms the due date is the invoice date.
        return self._create_invoice_one_line(
            price_unit=100.0,
            partner_id=partner,
            invoice_date=invoice_date,
            invoice_payment_term_id=False,
            post=True,
        )

    def test_only_oldest_invoice_can_be_paid(self):
        """Portal users can only pay the invoice with the oldest due date, when the company asks for it."""
        oldest = self._create_posted_invoice(self.student, self.today - relativedelta(days=20))
        newest = self._create_posted_invoice(self.student, self.today - relativedelta(days=10))
        company = oldest.company_id

        with self.subTest("option on: only the oldest invoice can be paid"):
            company.users_can_pay_only_oldest_invoice = True
            self.assertTrue(oldest._has_to_be_paid())
            self.assertFalse(newest._has_to_be_paid())

        with self.subTest("option off: every invoice can be paid"):
            company.users_can_pay_only_oldest_invoice = False
            self.assertTrue(oldest._has_to_be_paid())
            self.assertTrue(newest._has_to_be_paid())

        with self.subTest("option on, oldest paid: the next one can be paid"):
            company.users_can_pay_only_oldest_invoice = True
            self.env["account.payment.register"].with_context(
                active_model="account.move", active_ids=oldest.ids
            ).create({})._create_payments()
            self.assertFalse(oldest.amount_residual)
            self.assertTrue(newest._has_to_be_paid())

    def test_payment_by_other_partner_goes_to_invoice_partner(self):
        """A payment made from the portal by another contact is registered for the invoice partner."""
        invoice = self._create_posted_invoice(self.student, self.today)
        tx = self._create_transaction(
            "redirect",
            state="done",
            partner_id=self.payer.id,
            amount=invoice.amount_total,
            currency_id=invoice.currency_id.id,
            invoice_ids=[Command.set(invoice.ids)],
        )

        self._run_post_processing()
        payment = tx.payment_id

        self.assertTrue(payment)
        self.assertEqual(payment.partner_id, self.student)
        self.assertIn(payment.state, ("paid", "reconciled"))
        self.assertFalse(invoice.amount_residual)
        self.assertIn(invoice.payment_state, ("in_payment", "paid"))
