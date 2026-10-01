##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import Command
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestNextYearGroups(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.level_1 = cls.env["academic.level"].create({"name": "Test Next Year Level 1"})
        cls.level_2 = cls.env["academic.level"].create({"name": "Test Next Year Level 2"})
        cls.division = cls.env["academic.division"].create({"name": "Test Next Year Division"})
        cls.section = cls.env["academic.section"].create(
            {
                "name": "Test Next Year Plan",
                "level_line_ids": [
                    Command.create({"level_id": cls.level_1.id, "sequence": 10}),
                    Command.create({"level_id": cls.level_2.id, "sequence": 20}),
                ],
            }
        )
        cls.company = cls.env.company
        cls.company.section_ids = [Command.link(cls.section.id)]
        cls.group = cls.env["academic.group"].create(
            {
                "year": 2026,
                "company_id": cls.company.id,
                "section_id": cls.section.id,
                "level_id": cls.level_1.id,
                "division_id": cls.division.id,
                # academic_sale_subscription constrains capacity > 0, and the copy of the
                # next year group carries it along, so it cannot be left at the default
                "capacity": 10,
            }
        )

    def _next_year_groups(self, level=None, active_test=True):
        domain = [("year", "=", 2027), ("section_id", "=", self.section.id)]
        if level:
            domain.append(("level_id", "=", level.id))
        return self.env["academic.group"].with_context(active_test=active_test).search(domain)

    def test_01_running_the_mass_action_twice_creates_one_group(self):
        """The dedup search is the whole point of the action: re-running it must reuse."""
        self.group.create_next_year_groups()
        self.assertEqual(len(self._next_year_groups()), 1)

        self.group.create_next_year_groups()
        self.assertEqual(len(self._next_year_groups()), 1, "the second run duplicated the next year group")

    def test_02_subject_group_does_not_reuse_the_commercial_group(self):
        """A subject group and the commercial group of the same level are different
        records for the unique constraint, so they need one next year group each."""
        template = self.env["academic.subject.template"].create({"name": "Test Next Year Subject", "code": "TSTNY"})
        subject = self.env["academic.subject"].create(
            {"name": "Test Next Year Subject", "company_id": self.company.id, "template_id": template.id}
        )
        subject_group = self.group.copy({"subject_id": subject.id})

        (self.group + subject_group).create_next_year_groups()

        next_groups = self._next_year_groups()
        self.assertEqual(len(next_groups), 2)
        self.assertEqual(len(next_groups.filtered("subject_id")), 1)
        self.assertEqual(len(next_groups.filtered(lambda x: not x.subject_id)), 1)

    def test_03_archived_next_year_group_is_reused(self):
        """The unique constraint ignores `active`: not finding an archived group would
        make the copy blow up on a unique violation and abort the whole batch."""
        self.group.create_next_year_groups()
        self._next_year_groups().action_archive()

        self.group.create_next_year_groups()

        self.assertEqual(len(self._next_year_groups(active_test=False)), 1)

    def test_04_last_level_of_the_plan_suggests_no_level(self):
        self.assertEqual(self.group._get_next_year_level(), self.level_2)

        closing_group = self.group.copy({"level_id": self.level_2.id})
        self.assertFalse(closing_group._get_next_year_level(), "a group closing the plan must not suggest a next level")

    def test_05_plan_without_sequence_keeps_the_same_level(self):
        """Schools that never configured the plan must behave exactly as before."""
        self.section.level_line_ids.unlink()

        self.assertFalse(self.section._is_last_level(self.level_1))
        self.assertEqual(self.group._get_next_year_level(), self.level_1)
