##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
import psycopg2
from odoo.tests.common import TransactionCase, tagged
from odoo.tools import mute_logger


@tagged("post_install", "-at_install")
class TestPartnerCode(TransactionCase):
    """The module gives every family an academic code out of a sequence, and
    keeps it unique within the company."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Partner = cls.env["res.partner"]

    def test_a_family_gets_a_code_from_the_sequence(self):
        family = self.Partner.create({"name": "García", "partner_type": "family"})
        self.assertTrue(family.academic_code)
        self.assertEqual(len(family.academic_code), 4, "the sequence is padded to four digits")

    def test_two_families_get_different_codes(self):
        first = self.Partner.create({"name": "García", "partner_type": "family"})
        second = self.Partner.create({"name": "López", "partner_type": "family"})
        self.assertNotEqual(first.academic_code, second.academic_code)

    def test_a_contact_that_is_not_a_family_gets_no_code(self):
        family = self.Partner.create({"name": "García", "partner_type": "family"})
        student = self.Partner.create({"name": "Sofía García", "partner_type": "student", "parent_id": family.id})
        other = self.Partner.create({"name": "Proveedor SA"})
        self.assertFalse(student.academic_code)
        self.assertFalse(other.academic_code)

    def test_duplicating_a_family_gives_it_a_new_code(self):
        """The field is copy=False, so the duplicate does not carry the code; it
        goes through create as a family and takes the next one."""
        family = self.Partner.create({"name": "García", "partner_type": "family"})
        copy = family.copy()
        self.assertTrue(copy.academic_code)
        self.assertNotEqual(copy.academic_code, family.academic_code)

    @mute_logger("odoo.sql_db")
    def test_two_families_cannot_share_a_code_in_the_same_company(self):
        family = self.Partner.create({"name": "García", "partner_type": "family"})
        other = self.Partner.create({"name": "López", "partner_type": "family"})
        with self.assertRaises(psycopg2.errors.UniqueViolation):
            with self.cr.savepoint():
                other.academic_code = family.academic_code
                other.flush_recordset()

    @mute_logger("odoo.sql_db")
    def test_the_constraint_does_not_reach_the_families_with_no_company(self):
        """The constraint is UNIQUE (academic_code, company_id), and Postgres
        does not make two NULLs collide: two families without a company can
        share a code, and so can one without a company and one with it. It is
        how it already behaved in 19 -- pinned here so nobody reads the
        constraint as a global uniqueness."""
        first = self.Partner.create({"name": "García", "partner_type": "family", "company_id": False})
        second = self.Partner.create({"name": "López", "partner_type": "family", "company_id": False})
        second.academic_code = first.academic_code
        second.flush_recordset()
        self.assertEqual(second.academic_code, first.academic_code)

        with_company = self.Partner.create(
            {"name": "Ortiz", "partner_type": "family", "company_id": self.env.company.id}
        )
        with_company.academic_code = first.academic_code
        with_company.flush_recordset()
        self.assertEqual(with_company.academic_code, first.academic_code)
