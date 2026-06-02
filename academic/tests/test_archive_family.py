##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestArchiveFamily(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Partner = cls.env["res.partner"]
        Link = cls.env["res.partner.link"]

        cls.rel = cls.env["res.partner.relationship"].create({"name": "Test Parent"})

        cls.family_a = Partner.create({"name": "Family A", "partner_type": "family"})
        cls.student_a = Partner.create({"name": "Student A", "partner_type": "student", "parent_id": cls.family_a.id})
        cls.relative_a = Partner.create({"name": "Relative A", "partner_type": "parent"})
        Link.create({"student_id": cls.family_a.id, "partner_id": cls.relative_a.id, "relationship_id": cls.rel.id})

        cls.family_b = Partner.create({"name": "Family B", "partner_type": "family"})
        cls.student_b = Partner.create({"name": "Student B", "partner_type": "student", "parent_id": cls.family_b.id})
        cls.relative_shared = Partner.create({"name": "Relative Shared", "partner_type": "parent"})
        Link.create(
            {"student_id": cls.family_a.id, "partner_id": cls.relative_shared.id, "relationship_id": cls.rel.id}
        )
        Link.create(
            {"student_id": cls.family_b.id, "partner_id": cls.relative_shared.id, "relationship_id": cls.rel.id}
        )

        cls.family_c = Partner.create({"name": "Family C", "partner_type": "family", "links_by_student": True})
        cls.student_c = Partner.create({"name": "Student C", "partner_type": "student", "parent_id": cls.family_c.id})
        cls.relative_c = Partner.create({"name": "Relative C", "partner_type": "parent"})
        Link.create({"student_id": cls.student_c.id, "partner_id": cls.relative_c.id, "relationship_id": cls.rel.id})

        cls.family_d = Partner.create({"name": "Family D", "partner_type": "family", "links_by_student": True})
        cls.student_d = Partner.create({"name": "Student D", "partner_type": "student", "parent_id": cls.family_d.id})
        cls.relative_cross = Partner.create({"name": "Relative Cross", "partner_type": "parent"})
        Link.create(
            {"student_id": cls.student_c.id, "partner_id": cls.relative_cross.id, "relationship_id": cls.rel.id}
        )
        Link.create(
            {"student_id": cls.student_d.id, "partner_id": cls.relative_cross.id, "relationship_id": cls.rel.id}
        )

    def test_01_archive_basic_mode_false(self):
        self.family_a.action_archive()
        self.assertFalse(self.family_a.active)
        self.assertFalse(self.student_a.active)
        self.assertFalse(self.relative_a.active)

    def test_02_shared_relative_not_archived(self):
        self.family_a.action_archive()
        self.assertTrue(self.relative_shared.active)

    def test_03_archive_mode_true(self):
        self.family_c.action_archive()
        self.assertFalse(self.family_c.active)
        self.assertFalse(self.student_c.active)
        self.assertFalse(self.relative_c.active)

    def test_04_unarchive_reactivates(self):
        self.family_a.action_archive()
        self.family_a.with_context(active_test=False).action_unarchive()
        self.assertTrue(self.family_a.active)
        self.assertTrue(self.student_a.active)
        self.assertTrue(self.relative_a.active)

        self.family_c.action_archive()
        self.family_c.with_context(active_test=False).action_unarchive()
        self.assertTrue(self.family_c.active)
        self.assertTrue(self.student_c.active)
        self.assertTrue(self.relative_c.active)

    def test_05_students_archive_with_family(self):
        self.family_b.action_archive()
        self.assertFalse(self.student_b.active)

    def test_06_relative_linked_to_active_student_other_family_not_archived(self):
        self.family_c.action_archive()
        self.assertTrue(self.relative_cross.active)

    def test_07_relative_portal_user_archived_with_family(self):
        """Portal user of a relative is archived before the relative so Odoo
        doesn't block the operation with 'cannot archive contacts linked to an
        active user'."""
        portal_user = self.env["res.users"].create(
            {
                "name": "Portal Relative A",
                "login": "portal_relative_a@test.com",
                "partner_id": self.relative_a.id,
                "group_ids": [(6, 0, [self.env.ref("base.group_portal").id])],
            }
        )
        self.assertTrue(portal_user.share)
        self.family_a.action_archive()
        self.assertFalse(self.relative_a.active)
        self.assertFalse(portal_user.active)

    def test_08_unarchive_reactivates_portal_user(self):
        """Unarchiving a family reactivates the relatives' portal users that
        were archived together with them."""
        portal_user = self.env["res.users"].create(
            {
                "name": "Portal Relative A 2",
                "login": "portal_relative_a2@test.com",
                "partner_id": self.relative_a.id,
                "group_ids": [(6, 0, [self.env.ref("base.group_portal").id])],
            }
        )
        self.family_a.action_archive()
        self.assertFalse(portal_user.active)
        self.family_a.with_context(active_test=False).action_unarchive()
        self.assertTrue(self.relative_a.active)
        self.assertTrue(portal_user.active)

    def test_09_internal_user_not_archived(self):
        """A relative with an active internal user is skipped entirely: the
        archive operation must not raise RedirectWarning and the internal user
        (and its partner) must remain active."""
        internal_user = self.env["res.users"].create(
            {
                "name": "Internal Relative A",
                "login": "internal_relative_a@test.com",
                "partner_id": self.relative_a.id,
                "group_ids": [(6, 0, [self.env.ref("base.group_user").id])],
            }
        )
        self.assertFalse(internal_user.share)
        self.family_a.action_archive()
        self.assertTrue(internal_user.active)
        self.assertTrue(self.relative_a.active)
