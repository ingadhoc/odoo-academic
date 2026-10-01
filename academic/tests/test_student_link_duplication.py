##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestStudentLinkDuplication(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Partner = cls.env["res.partner"]
        cls.relationship = cls.env["res.partner.relationship"].create({"name": "Mother"})
        cls.family = Partner.create({"name": "Dup Family", "partner_type": "family"})
        cls.student = Partner.create({"name": "Dup Student", "partner_type": "student", "parent_id": cls.family.id})
        cls.relative = Partner.create({"name": "Dup Relative", "partner_type": "parent"})

    def _link_command(self):
        return [
            0,
            0,
            {
                "partner_id": self.relative.id,
                "relationship_id": self.relationship.id,
                "role_ids": [[6, False, []]],
                "sequence": 10,
            },
        ]

    def test_01_link_sent_for_family_and_student_at_once(self):
        """The form sends the link the onchange propagated, the compute adds its own."""
        self.family.write(
            {
                "student_link_ids": [self._link_command()],
                "student_ids": [[1, self.student.id, {"student_link_ids": [self._link_command()]}]],
            }
        )
        self.env.flush_all()
        self.assertEqual(self.student.student_link_ids.partner_id, self.relative)
        self.assertEqual(len(self.student.student_link_ids), 1)

    def test_02_link_only_on_the_family_still_propagates(self):
        self.family.write({"student_link_ids": [self._link_command()]})
        self.env.flush_all()
        self.assertEqual(self.student.student_link_ids.partner_id, self.relative)
        self.assertEqual(len(self.student.student_link_ids), 1)

    def test_03_existing_link_is_not_created_twice(self):
        Link = self.env["res.partner.link"]
        vals = {
            "student_id": self.student.id,
            "partner_id": self.relative.id,
            "relationship_id": self.relationship.id,
        }
        first = Link.create(vals)
        second = Link.create(vals)
        self.env.flush_all()
        self.assertEqual(first, second)
        self.assertEqual(len(self.student.student_link_ids), 1)

    def test_04_repeated_pair_in_the_same_batch(self):
        Link = self.env["res.partner.link"]
        vals = {
            "student_id": self.student.id,
            "partner_id": self.relative.id,
            "relationship_id": self.relationship.id,
        }
        links = Link.create([dict(vals), dict(vals)])
        self.env.flush_all()
        self.assertEqual(len(links), 1)

    def test_05_different_students_keep_their_own_link(self):
        other_student = self.env["res.partner"].create(
            {"name": "Other Student", "partner_type": "student", "parent_id": self.family.id}
        )
        self.family.write({"student_link_ids": [self._link_command()]})
        self.env.flush_all()
        self.assertEqual(self.student.student_link_ids.partner_id, self.relative)
        self.assertEqual(other_student.student_link_ids.partner_id, self.relative)
