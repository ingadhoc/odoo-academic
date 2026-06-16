##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestArchiveFamilyDebt(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Partner = cls.env["res.partner"]
        Link = cls.env["res.partner.link"]

        cls.rel = cls.env["res.partner.relationship"].create({"name": "Test Debt Parent"})
        cls.paying_role = cls.env.ref("academic.paying_role")

        cls.family = Partner.create({"name": "Family Debt"})
        cls.family.write({"partner_type": "family"})
        cls.student = Partner.create({"name": "Student Debt", "partner_type": "student", "parent_id": cls.family.id})
        cls.responsible = Partner.create({"name": "Responsible Debt", "partner_type": "parent", "vat": "20-11111111-1"})
        Link.create(
            {
                "student_id": cls.family.id,
                "partner_id": cls.responsible.id,
                "relationship_id": cls.rel.id,
                "role_ids": [(6, 0, [cls.paying_role.id])],
            }
        )

        cls.family_no_debt = Partner.create({"name": "Family No Debt"})
        cls.family_no_debt.write({"partner_type": "family"})
        cls.student_no_debt = Partner.create(
            {"name": "Student No Debt", "partner_type": "student", "parent_id": cls.family_no_debt.id}
        )
        cls.relative_no_debt = Partner.create({"name": "Relative No Debt", "partner_type": "parent"})
        Link.create(
            {
                "student_id": cls.family_no_debt.id,
                "partner_id": cls.relative_no_debt.id,
                "relationship_id": cls.rel.id,
            }
        )

    def _create_posted_invoice(self, partner):
        """Create a minimal posted customer invoice for the given partner."""
        journal = self.env["account.journal"].search(
            [("type", "=", "sale"), ("company_id", "=", self.env.company.id)], limit=1
        )
        account = self.env["account.account"].search(
            [("account_type", "=", "income"), ("company_ids", "in", [self.env.company.id])], limit=1
        )
        move = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": partner.id,
                "journal_id": journal.id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Test line",
                            "quantity": 1,
                            "price_unit": 100.0,
                            "account_id": account.id,
                        },
                    )
                ],
            }
        )
        move.action_post()
        return move

    def test_01_archive_with_debt_returns_wizard(self):
        """Archiving a family with unpaid invoices returns the debt-warning
        wizard action instead of archiving immediately."""
        self._create_posted_invoice(self.responsible)
        result = self.family.action_archive()
        self.assertEqual(result.get("type"), "ir.actions.act_window")
        self.assertEqual(result.get("res_model"), "archive.family.debt.wizard")
        self.assertTrue(self.family.active)

    def test_02_archive_without_debt_proceeds_directly(self):
        """Archiving a family with no unpaid invoices archives immediately
        (no wizard returned)."""
        result = self.family_no_debt.action_archive()
        if result:
            self.assertNotEqual(result.get("res_model"), "archive.family.debt.wizard")
        self.assertFalse(self.family_no_debt.active)
        self.assertFalse(self.student_no_debt.active)

    def test_03_wizard_confirm_archives_family_and_cascade(self):
        """Confirming the wizard archives the family, its students and relatives."""
        self._create_posted_invoice(self.responsible)
        result = self.family.action_archive()
        self.assertEqual(result.get("res_model"), "archive.family.debt.wizard")

        wizard = self.env["archive.family.debt.wizard"].create({"family_ids": [(6, 0, [self.family.id])]})
        wizard.action_confirm()

        self.assertFalse(self.family.active)
        self.assertFalse(self.student.active)
        self.assertFalse(self.responsible.active)
