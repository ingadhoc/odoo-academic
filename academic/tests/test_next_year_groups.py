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
        cls.next_level_1 = cls.env["academic.level"].create({"name": "Test Next Year Next Plan Level 1"})
        cls.next_section = cls.env["academic.section"].create(
            {
                "name": "Test Next Year Next Plan",
                "level_line_ids": [Command.create({"level_id": cls.next_level_1.id, "sequence": 10})],
            }
        )
        cls.company = cls.env.company
        cls.company.section_ids = [Command.link(cls.section.id), Command.link(cls.next_section.id)]
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

    def test_04_last_level_of_a_plan_leading_nowhere_suggests_no_target(self):
        self.assertEqual(self.group._get_next_year_section(), self.section)
        self.assertEqual(self.group._get_next_year_level(self.section), self.level_2)

        closing_group = self.group.copy({"level_id": self.level_2.id})
        self.assertFalse(
            closing_group._get_next_year_section(),
            "a group closing a plan that leads nowhere must not suggest a destination",
        )
        self.assertTrue(closing_group._is_graduating())

    def test_05_plan_without_sequence_keeps_the_same_level(self):
        """Schools that never configured the plan must behave exactly as before."""
        self.section.level_line_ids.unlink()

        self.assertFalse(self.section._is_last_level(self.level_1))
        self.assertEqual(self.group._get_next_year_level(self.section), self.level_1)

    def test_06_last_level_continues_into_the_next_study_plan(self):
        """The whole point of the next study plan: 7th grade of Primary goes on to
        1st year of Secondary, which is another plan."""
        self.section.correlative_ids = [Command.link(self.next_section.id)]
        closing_group = self.group.copy({"level_id": self.level_2.id})

        self.assertEqual(closing_group._get_next_year_section(), self.next_section)
        self.assertEqual(closing_group._get_next_year_level(self.next_section), self.next_level_1)
        self.assertFalse(closing_group._is_graduating(), "a plan that continues is not a graduation")

    def test_07_two_next_study_plans_suggest_nothing(self):
        """Ambiguous destination: WinWin has two Secondary paths in one plan, and guessing
        one of them would send students to the wrong school."""
        other_section = self.env["academic.section"].create({"name": "Test Next Year Other Plan"})
        self.section.correlative_ids = [Command.set((self.next_section + other_section).ids)]
        closing_group = self.group.copy({"level_id": self.level_2.id})

        self.assertFalse(closing_group._get_next_year_section())
        self.assertFalse(
            closing_group._is_graduating(), "two plans follow: the destination is pending, not a graduation"
        )

    def test_08_division_is_only_kept_when_the_target_plan_uses_it(self):
        """A Secondary without divisions must not get an invented "A" from Primary."""
        self.assertFalse(
            self.group._get_next_year_division(self.next_section),
            "the target plan does not use the division yet, so none is proposed",
        )

        self.env["academic.group"].create(
            {
                "year": 2026,
                "company_id": self.company.id,
                "section_id": self.next_section.id,
                "level_id": self.next_level_1.id,
                "division_id": self.division.id,
                "capacity": 10,
            }
        )

        self.assertEqual(self.group._get_next_year_division(self.next_section), self.division)

    def test_09_group_of_the_next_plan_is_reused_instead_of_created(self):
        """Schools create next year groups ahead of time: the re-enrollment has to land
        on the group that is already there."""
        self.section.correlative_ids = [Command.link(self.next_section.id)]
        closing_group = self.group.copy({"level_id": self.level_2.id})
        existing = self.env["academic.group"].create(
            {
                "year": 2027,
                "company_id": self.company.id,
                "section_id": self.next_section.id,
                "level_id": self.next_level_1.id,
                "capacity": 10,
            }
        )

        target = closing_group._get_next_year_group(section=self.next_section, level=self.next_level_1)

        self.assertEqual(target, existing)

    def test_10_created_group_of_the_next_plan_carries_plan_and_drops_division(self):
        self.section.correlative_ids = [Command.link(self.next_section.id)]
        closing_group = self.group.copy({"level_id": self.level_2.id})

        target = closing_group._create_next_year_group(section=self.next_section, level=self.next_level_1)

        self.assertEqual(target.section_id, self.next_section, "the created group must live in the target plan")
        self.assertEqual(target.level_id, self.next_level_1)
        self.assertFalse(target.division_id, "the target plan does not use the division of the source group")
        self.assertEqual(target.year, 2027)
