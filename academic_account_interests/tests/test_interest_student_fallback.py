##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from dateutil.relativedelta import relativedelta
from odoo import fields
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestInterestStudentFallback(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        Partner = cls.env["res.partner"]

        cls.sale_journal = cls.env["account.journal"].search(
            [("type", "=", "sale"), ("company_id", "=", cls.company.id)], limit=1
        )
        cls.income_account = cls.env["account.account"].search(
            [("account_type", "=", "income"), ("company_ids", "in", [cls.company.id])], limit=1
        )
        cls.receivable_accounts = cls.env["account.account"].search(
            [("account_type", "=", "asset_receivable"), ("company_ids", "in", [cls.company.id])]
        )

        cls.interest_product = cls.env["product.product"].create({"name": "Interest 70280", "type": "service"})
        cls.interest = cls.env["res.company.interest"].create(
            {
                "company_id": cls.company.id,
                "receivable_account_ids": [(6, 0, cls.receivable_accounts.ids)],
                "interest_product_id": cls.interest_product.id,
                "rate": 0.08,
                "rule_type": "monthly",
                "interval": 1,
            }
        )

        cls.customer = Partner.create({"name": "Customer 70280"})
        cls.family = Partner.create({"name": "Family 70280", "partner_type": "family"})
        cls.student = Partner.create({"name": "Student 70280", "partner_type": "student", "parent_id": cls.family.id})

        cls.from_date = fields.Date.today()
        cls.to_date = cls.from_date + relativedelta(months=1)
        cls.overdue_date = cls.from_date - relativedelta(days=60)

    def _create_overdue_invoice(self, partner, student=None):
        vals = {
            "move_type": "out_invoice",
            "partner_id": partner.id,
            "journal_id": self.sale_journal.id,
            "invoice_date": self.overdue_date,
            "invoice_date_due": self.overdue_date,
            "invoice_line_ids": [
                (
                    0,
                    0,
                    {
                        "name": "Line 70280",
                        "quantity": 1,
                        "price_unit": 100.0,
                        "account_id": self.income_account.id,
                    },
                )
            ],
        }
        if student:
            vals["student_id"] = student.id
        move = self.env["account.move"].create(vals)
        move.action_post()
        return move

    def test_debt_included_when_no_student(self):
        move = self._create_overdue_invoice(self.customer)
        self.assertFalse(move.student_id)

        deuda = self.interest.with_company(self.company)._calculate_debts(self.from_date, self.to_date)

        self.assertIn(self.customer, deuda)
        self.assertGreater(deuda[self.customer]["values"].get("Deuda periodos anteriores", 0), 0)
        self.assertEqual(deuda[self.customer]["values"].get("partner_id"), self.customer)

    def test_debt_grouped_by_student_when_present(self):
        move = self._create_overdue_invoice(self.family, student=self.student)
        self.assertEqual(move.student_id, self.student)

        deuda = self.interest.with_company(self.company)._calculate_debts(self.from_date, self.to_date)

        self.assertIn(self.student, deuda)
        self.assertNotIn(self.family, deuda)
        self.assertEqual(deuda[self.student]["values"].get("partner_id"), self.family)
