##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import Command
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestStudentLinksPropagation(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.paying_role = cls.env.ref("academic.paying_role")
        cls.relationship = cls.env["res.partner.relationship"].create({"name": "Test Propagation Relationship"})
        cls.payer = cls.env["res.partner"].create(
            {"name": "Test Propagation Payer", "partner_type": "parent", "vat": "20111111112"}
        )
        cls.family = cls.env["res.partner"].create({"name": "Test Propagation Family", "partner_type": "family"})
        cls.student = cls.env["res.partner"].create(
            {"name": "Test Propagation Student", "partner_type": "student", "parent_id": cls.family.id}
        )

    def _add_family_link(self, roles=None):
        self.family.write(
            {
                "student_link_ids": [
                    Command.create(
                        {
                            "partner_id": self.payer.id,
                            "relationship_id": self.relationship.id,
                            "role_ids": [Command.set(roles.ids if roles else [])],
                        }
                    )
                ]
            }
        )
        # read the student links before editing the family one, so the compute is
        # already materialized: that is the state in which the bug showed up
        self.assertEqual(len(self.student.student_link_ids), 1)
        return self.family.student_link_ids

    def test_01_role_added_on_an_existing_family_link_reaches_the_student(self):
        """Ticking the paying role on a link the family already has must reach the student."""
        family_link = self._add_family_link()
        self.assertFalse(self.student.student_link_ids.role_ids)

        family_link.role_ids = [Command.set(self.paying_role.ids)]

        self.assertEqual(self.student.student_link_ids.role_ids, self.paying_role)
        self.assertEqual(self.student.payment_responsible_ids, self.payer)

    def test_02_relationship_changed_on_an_existing_family_link_reaches_the_student(self):
        family_link = self._add_family_link(self.paying_role)
        other_relationship = self.env["res.partner.relationship"].create({"name": "Test Propagation Other"})

        family_link.write({"relationship_id": other_relationship.id, "sequence": 99})

        self.assertEqual(self.student.student_link_ids.relationship_id, other_relationship)
        self.assertEqual(self.student.student_link_ids.sequence, 99)

    def test_03_family_links_do_not_override_a_student_that_keeps_its_own(self):
        """With links_by_student the family is no longer the source: the student keeps its links."""
        family_link = self._add_family_link(self.paying_role)
        self.family.links_by_student = True
        other_payer = self.env["res.partner"].create(
            {"name": "Test Propagation Other Payer", "partner_type": "parent", "vat": "20222222223"}
        )

        family_link.partner_id = other_payer

        self.assertEqual(self.student.student_link_ids.partner_id, self.payer)
