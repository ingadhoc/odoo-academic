##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestPaymentResponsibleRole(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Partner = cls.env["res.partner"]
        Link = cls.env["res.partner.link"]

        cls.rel = cls.env["res.partner.relationship"].create({"name": "Test Responsible Parent"})
        cls.paying_role = cls.env.ref("academic.paying_role")

        cls.family = Partner.create({"name": "Family Responsible"})
        cls.family.write({"partner_type": "family"})
        cls.student = Partner.create(
            {"name": "Student Responsible", "partner_type": "student", "parent_id": cls.family.id}
        )
        cls.old_responsible = Partner.create(
            {"name": "Old Responsible", "partner_type": "parent", "vat": "20-22222222-2"}
        )
        cls.new_responsible = Partner.create(
            {"name": "New Responsible", "partner_type": "parent", "vat": "20-33333333-3"}
        )

        cls.old_link = Link.create(
            {
                "student_id": cls.family.id,
                "partner_id": cls.old_responsible.id,
                "relationship_id": cls.rel.id,
                "role_ids": [(6, 0, [cls.paying_role.id])],
            }
        )
        cls.new_link = Link.create(
            {
                "student_id": cls.family.id,
                "partner_id": cls.new_responsible.id,
                "relationship_id": cls.rel.id,
                "role_ids": [(6, 0, [cls.paying_role.id])],
            }
        )

    def _create_posted_invoice(self, partner, student):
        """Create a minimal posted customer invoice for the given partner and student."""
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
                "student_id": student.id,
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

    def test_01_remove_role_with_debt_of_another_responsible(self):
        """The previous responsible can lose the role when the student's unpaid
        invoices belong to the new responsible."""
        self._create_posted_invoice(self.new_responsible, self.student)
        self.old_link.write({"role_ids": [(3, self.paying_role.id)]})
        self.assertNotIn(self.paying_role, self.old_link.role_ids)

    def test_02_remove_role_blocked_by_own_debt(self):
        """The responsible keeps the role while their own invoices are unpaid."""
        self._create_posted_invoice(self.old_responsible, self.student)
        with self.assertRaises(ValidationError):
            self.old_link.write({"role_ids": [(3, self.paying_role.id)]})

    def test_03_unlink_with_debt_of_another_responsible(self):
        """Same as test_01 but deleting the link instead of removing the role."""
        self._create_posted_invoice(self.new_responsible, self.student)
        self.old_link.unlink()
        self.assertFalse(self.old_link.exists())
