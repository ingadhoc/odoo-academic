##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import Command
from odoo.exceptions import AccessError
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestGroupAccess(TransactionCase):
    """Accesses add up in 20: an unfiltered one must not widen the portal filter."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.level = cls.env["academic.level"].create({"name": "Test Access Level"})
        cls.section = cls.env["academic.section"].create(
            {
                "name": "Test Access Plan",
                "level_line_ids": [Command.create({"level_id": cls.level.id, "sequence": 10})],
            }
        )
        cls.company = cls.env.company
        cls.company.section_ids = [Command.link(cls.section.id)]
        cls.teacher = cls.env["res.partner"].create({"name": "Test Access Teacher", "partner_type": "teacher"})
        cls.own_group = cls._create_group("Test Access Own", teacher=cls.teacher)
        cls.other_group = cls._create_group("Test Access Other")
        cls.internal_teacher = cls.env["res.users"].create(
            {
                "name": "Test Access Internal Teacher",
                "login": "test_access_internal_teacher",
                "partner_id": cls.teacher.id,
                "company_id": cls.company.id,
                "company_ids": [Command.set([cls.company.id])],
                "group_ids": [
                    Command.set(
                        [
                            cls.env.ref("base.group_user").id,
                            cls.env.ref("academic.group_user").id,
                            cls.env.ref("academic.group_portal_teacher").id,
                        ]
                    )
                ],
            }
        )

    @classmethod
    def _create_group(cls, name, teacher=None):
        return cls.env["academic.group"].create(
            {
                "name": name,
                "year": 2026,
                "company_id": cls.company.id,
                "section_id": cls.section.id,
                "level_id": cls.level.id,
                "teacher_id": teacher.id if teacher else False,
                # academic_sale_subscription constrains capacity > 0
                "capacity": 10,
            }
        )

    def test_01_internal_teacher_only_reads_own_groups(self):
        """An internal user holding Teacher's Portal keeps the portal filter."""
        groups = self.env["academic.group"].with_user(self.internal_teacher).search([])
        self.assertEqual(groups, self.own_group)

    def test_02_internal_teacher_cannot_touch_other_groups(self):
        other = self.other_group.with_user(self.internal_teacher)
        with self.assertRaises(AccessError):
            other.check_access("read")
        with self.assertRaises(AccessError):
            other.check_access("write")

    def test_03_internal_teacher_still_writes_own_groups(self):
        own = self.own_group.with_user(self.internal_teacher)
        own.check_access("write")
        own.write({"name": "Test Access Own Renamed"})

    def test_04_internal_user_without_portal_group_reads_every_group(self):
        """The filter must not reach users who hold no portal group."""
        internal = self.env["res.users"].create(
            {
                "name": "Test Access Internal",
                "login": "test_access_internal",
                "company_id": self.company.id,
                "company_ids": [Command.set([self.company.id])],
                "group_ids": [Command.set([self.env.ref("base.group_user").id])],
            }
        )
        groups = self.env["academic.group"].with_user(internal).search([])
        self.assertIn(self.other_group, groups)
