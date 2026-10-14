##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import Command
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestReenrollmentWizard(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Partner = cls.env["res.partner"]

        cls.level_1 = cls.env["academic.level"].create({"name": "Test Reenroll Level 1"})
        cls.level_2 = cls.env["academic.level"].create({"name": "Test Reenroll Level 2"})
        cls.division = cls.env["academic.division"].create({"name": "Test Reenroll Division"})
        cls.section = cls.env["academic.section"].create(
            {
                "name": "Test Reenroll Plan",
                "level_line_ids": [
                    Command.create({"level_id": cls.level_1.id, "sequence": 10}),
                    Command.create({"level_id": cls.level_2.id, "sequence": 20}),
                ],
            }
        )
        cls.next_level = cls.env["academic.level"].create({"name": "Test Reenroll Next Plan Level"})
        cls.next_section = cls.env["academic.section"].create(
            {
                "name": "Test Reenroll Next Plan",
                "level_line_ids": [Command.create({"level_id": cls.next_level.id, "sequence": 10})],
            }
        )
        cls.company = cls.env.company
        cls.company.section_ids = [Command.link(cls.section.id), Command.link(cls.next_section.id)]

        relationship = cls.env["res.partner.relationship"].create({"name": "Test Reenroll Parent"})
        paying_role = cls.env.ref("academic.paying_role")
        family = Partner.create({"name": "Test Reenroll Family", "partner_type": "family"})

        def student(name):
            return Partner.create({"name": name, "partner_type": "student", "parent_id": family.id})

        def pay_link(student_record, payer):
            return cls.env["res.partner.link"].create(
                {
                    "student_id": student_record.id,
                    "partner_id": payer.id,
                    "relationship_id": relationship.id,
                    "role_ids": [Command.set(paying_role.ids)],
                }
            )

        cls.student_ok = student("Test Reenroll Student Payable")
        pay_link(cls.student_ok, Partner.create({"name": "Test Reenroll Payer", "partner_type": "parent"}))

        # no payment responsible at all
        cls.student_no_payer = student("Test Reenroll Student Without Payer")

        # has one, but archived: the wizard must treat it as no responsible
        cls.student_archived_payer = student("Test Reenroll Student Archived Payer")
        archived_payer = Partner.create({"name": "Test Reenroll Archived Payer", "partner_type": "parent"})
        pay_link(cls.student_archived_payer, archived_payer)
        archived_payer.action_archive()

    def _group(self, level=None, manage_sale_workflow=True, students=None, section=None, year=2026, division=None):
        students = students or self.env["res.partner"]
        division = self.division if division is None else division
        return self.env["academic.group"].create(
            {
                "year": year,
                "company_id": self.company.id,
                "section_id": (section or self.section).id,
                "level_id": (level or self.level_1).id,
                "division_id": division.id if division else False,
                # explicit: the compute would derive it from subject_id, and capacity has
                # to cover the students or the vacancies constraint rejects the create
                "manage_sale_workflow": manage_sale_workflow,
                "capacity": 10,
                "student_ids": [Command.set(students.ids)],
            }
        )

    def _wizard(self, groups):
        return self.env["academic.reenrollment.wizard"].with_context(active_ids=groups.ids).create({})

    def _next_year_groups(self, level=None, section=None):
        domain = [("year", "=", 2027), ("section_id", "=", (section or self.section).id)]
        if level:
            domain.append(("level_id", "=", level.id))
        return self.env["academic.group"].search(domain)

    def assertSameRecords(self, actual, expected, msg=None):
        self.assertEqual(sorted(actual.ids), sorted(expected.ids), msg)

    def test_01_reenrolling_twice_duplicates_neither_groups_nor_students(self):
        """Groups outside the sales workflow carry their students over directly, so a
        second run must find them already enrolled and have nothing left to do."""
        students = self.student_ok + self.student_no_payer
        group = self._group(manage_sale_workflow=False, students=students)

        self._wizard(group).action_reenroll()

        target = self._next_year_groups()
        self.assertEqual(len(target), 1)
        self.assertEqual(target.level_id, self.level_2, "the plan sequence decides the target level")
        self.assertSameRecords(target.student_ids, students)

        second_run = self._wizard(group)
        self.assertFalse(second_run.line_ids.student_ids, "students already enrolled must not be offered a second time")
        self.assertSameRecords(second_run.line_ids.excluded_enrolled_ids, students)
        with self.assertRaises(ValidationError):
            second_run.action_reenroll()

        self.assertEqual(len(self._next_year_groups()), 1, "the second run duplicated the next year group")
        self.assertSameRecords(self._next_year_groups().student_ids, students)

    def test_02_student_without_active_payment_responsible_is_excluded(self):
        """Excluded in the preview instead of aborting the whole run, and the students
        that can be billed keep going through."""
        group = self._group(
            manage_sale_workflow=True,
            students=self.student_ok + self.student_no_payer + self.student_archived_payer,
        )

        wizard = self._wizard(group)
        line = wizard.line_ids

        self.assertSameRecords(line.student_ids, self.student_ok)
        self.assertSameRecords(line.excluded_no_responsible_ids, self.student_no_payer + self.student_archived_payer)
        self.assertEqual(wizard.student_count, 1, "the payable student must still be counted")
        self.assertTrue(wizard.requires_sale_data, "the line still needs the sale data for the payable student")

    def test_03_group_closing_the_plan_is_left_out_of_the_preview(self):
        """No target means no re-enrollment: the line must not claim students, promise a
        new group, nor drag a quotation template requirement with it."""
        group = self._group(level=self.level_2, manage_sale_workflow=True, students=self.student_ok)

        wizard = self._wizard(group)
        line = wizard.line_ids

        self.assertTrue(line.is_last_level)
        self.assertFalse(line.target_level_id)
        self.assertFalse(line.target_group_id)
        self.assertFalse(line.student_ids, "a line with nowhere to go must not offer students")
        self.assertFalse(line.will_create_group)
        self.assertFalse(wizard.requires_sale_data, "a no-op line must not force a quotation template")
        with self.assertRaises(ValidationError):
            wizard.action_reenroll()

    def test_04_setting_a_level_by_hand_brings_a_closing_group_back(self):
        """Repeaters and non-linear institutions: the user overrides the suggestion."""
        group = self._group(level=self.level_2, manage_sale_workflow=False, students=self.student_ok)
        wizard = self._wizard(group)
        line = wizard.line_ids
        self.assertFalse(line.student_ids)

        line.target_level_id = self.level_2

        self.assertTrue(line.will_create_group)
        self.assertSameRecords(line.student_ids, self.student_ok)

        wizard.action_reenroll()

        target = self._next_year_groups(level=self.level_2)
        self.assertEqual(len(target), 1)
        self.assertSameRecords(target.student_ids, self.student_ok)

    def test_05_last_level_continues_into_the_next_study_plan(self):
        """7th grade of Primary goes on to 1st year of Secondary: another study plan, and
        the group of the new plan is created when it does not exist yet."""
        self.section.correlative_ids = [Command.link(self.next_section.id)]
        group = self._group(level=self.level_2, manage_sale_workflow=False, students=self.student_ok)

        wizard = self._wizard(group)
        line = wizard.line_ids

        self.assertTrue(line.is_last_level)
        self.assertFalse(line.is_graduating, "the plan has a plan after it, so nobody graduates")
        self.assertEqual(line.target_section_id, self.next_section)
        self.assertEqual(line.target_level_id, self.next_level, "the student starts at the first level")
        self.assertFalse(line.target_division_id, "the target plan does not use the division of the source group")
        self.assertTrue(line.will_create_group)
        self.assertSameRecords(line.student_ids, self.student_ok)

        wizard.action_reenroll()

        target = self._next_year_groups(section=self.next_section)
        self.assertEqual(len(target), 1)
        self.assertEqual(target.level_id, self.next_level)
        self.assertSameRecords(target.student_ids, self.student_ok)
        self.assertFalse(self._next_year_groups(), "nothing must be created in the plan being left behind")

    def test_06_existing_group_of_the_next_plan_is_reused(self):
        """Schools create next year groups ahead of time, so the re-enrollment has to land
        on the group that is already there instead of creating a second one."""
        self.section.correlative_ids = [Command.link(self.next_section.id)]
        existing = self._group(
            level=self.next_level, section=self.next_section, year=2027, division=False, manage_sale_workflow=False
        )
        group = self._group(level=self.level_2, manage_sale_workflow=False, students=self.student_ok)

        wizard = self._wizard(group)

        self.assertEqual(wizard.line_ids.target_group_id, existing)
        self.assertFalse(wizard.line_ids.will_create_group)

        wizard.action_reenroll()

        self.assertSameRecords(existing.student_ids, self.student_ok)
        self.assertEqual(len(self._next_year_groups(section=self.next_section)), 1)

    def test_07_two_next_study_plans_leave_the_destination_to_the_user(self):
        """Ambiguous destination: the user picks any group of next year, from any plan."""
        other_section = self.env["academic.section"].create({"name": "Test Reenroll Other Next Plan"})
        self.section.correlative_ids = [Command.set((self.next_section + other_section).ids)]
        group = self._group(level=self.level_2, manage_sale_workflow=False, students=self.student_ok)

        wizard = self._wizard(group)
        line = wizard.line_ids

        self.assertTrue(line.is_last_level)
        self.assertFalse(line.target_section_id, "two plans follow, so no destination can be guessed")
        self.assertFalse(line.is_graduating, "a pending destination is not a graduation")
        self.assertFalse(line.student_ids)

        line.target_section_id = self.next_section

        self.assertEqual(line.target_level_id, self.next_level)
        self.assertFalse(line.is_graduating)
        self.assertSameRecords(line.student_ids, self.student_ok)

        wizard.action_reenroll()

        self.assertSameRecords(self._next_year_groups(section=self.next_section).student_ids, self.student_ok)

    def test_08_group_closing_a_plan_that_leads_nowhere_graduates(self):
        """Graduating is a result, not a group left out: it is reported and it must not
        block the rest of the run."""
        graduating = self._group(level=self.level_2, manage_sale_workflow=False, students=self.student_ok)
        continuing = self._group(
            level=self.level_1, manage_sale_workflow=False, students=self.student_no_payer, division=False
        )

        wizard = self._wizard(graduating + continuing)
        graduating_line = wizard.line_ids.filtered(lambda x: x.source_group_id == graduating)

        self.assertTrue(graduating_line.is_graduating)
        self.assertEqual(graduating_line.graduating_count, 1)
        self.assertEqual(wizard.graduating_count, 1)
        self.assertFalse(graduating_line.student_ids)

        wizard.action_reenroll()

        self.assertSameRecords(
            self._next_year_groups(level=self.level_2).student_ids,
            self.student_no_payer,
            "the group that continues must be re-enrolled anyway",
        )

    def test_09_a_group_of_another_plan_can_be_picked_by_hand(self):
        """No next plan configured at all: the user picks any group of next year of the
        same company, whatever its study plan."""
        target = self._group(
            level=self.next_level, section=self.next_section, year=2027, division=False, manage_sale_workflow=False
        )
        group = self._group(level=self.level_2, manage_sale_workflow=False, students=self.student_ok)
        wizard = self._wizard(group)
        line = wizard.line_ids
        self.assertFalse(line.student_ids)

        line.target_group_id = target

        self.assertSameRecords(line.student_ids, self.student_ok)

        wizard.action_reenroll()

        self.assertSameRecords(target.student_ids, self.student_ok)

    def test_10_students_can_be_removed_and_sent_to_another_group(self):
        """Divisions that open, merge or lose students: the preview is where that is
        settled, one student at a time."""
        leaving = self.student_no_payer
        moving = self.student_archived_payer
        students = self.student_ok + leaving + moving
        group = self._group(manage_sale_workflow=False, students=students)
        other_division = self.env["academic.division"].create({"name": "Test Reenroll Division B"})
        other_group = self._group(level=self.level_2, year=2027, division=other_division, manage_sale_workflow=False)

        wizard = self._wizard(group)
        line = wizard.line_ids
        self.assertSameRecords(line.student_ids, students)

        line.student_ids = [Command.unlink(leaving.id)]
        line.move_ids = [Command.create({"student_id": moving.id, "target_group_id": other_group.id})]

        self.assertEqual(line.student_count, 2, "the count must follow the students removed by hand")
        self.assertEqual(wizard.student_count, 2)

        wizard.action_reenroll()

        target = self._next_year_groups(level=self.level_2) - other_group
        self.assertSameRecords(target.student_ids, self.student_ok, "only the students left on the line")
        self.assertSameRecords(other_group.student_ids, moving)
        self.assertNotIn(leaving, target.student_ids | other_group.student_ids)

    def test_11_destinations_in_different_plans_warn_about_the_shared_sale_data(self):
        """One template and one pricelist for the whole run: mixing plans is allowed, but
        the user has to know before confirming."""
        self.section.correlative_ids = [Command.link(self.next_section.id)]
        continuing = self._group(level=self.level_1, manage_sale_workflow=True, students=self.student_ok)
        changing_plan = self._group(
            level=self.level_2, manage_sale_workflow=True, students=self.student_ok, division=False
        )

        wizard = self._wizard(continuing + changing_plan)

        self.assertTrue(wizard.requires_sale_data)
        self.assertTrue(wizard.mixed_plans_warning, "two study plans in one run must be warned about")
        self.assertIn(self.next_section.name, wizard.mixed_plans_warning)

        self.assertFalse(self._wizard(continuing).mixed_plans_warning, "a single plan needs no warning")

    def test_12_a_group_without_destination_holds_the_whole_run(self):
        """Mixed with a group that does have a destination, the one without it used to be
        dropped in silence: nobody re-enrolled and nothing said."""
        other_section = self.env["academic.section"].create({"name": "Test Reenroll Other Next Plan"})
        self.section.correlative_ids = [Command.set((self.next_section + other_section).ids)]
        pending = self._group(level=self.level_2, manage_sale_workflow=False, students=self.student_ok)
        ready = self._group(
            level=self.level_1, manage_sale_workflow=False, students=self.student_no_payer, division=False
        )

        wizard = self._wizard(pending + ready)
        pending_line = wizard.line_ids.filtered(lambda x: x.source_group_id == pending)

        self.assertTrue(pending_line.is_pending, "two next plans and no pick: the destination is pending")
        self.assertEqual(pending_line.pending_count, 1)
        self.assertFalse(pending_line.is_graduating, "a pending destination is not a graduation")
        self.assertTrue(wizard.pending_warning)
        self.assertIn(pending.display_name, wizard.pending_warning)

        with self.assertRaises(ValidationError):
            wizard.action_reenroll()

        self.assertFalse(self._next_year_groups(), "nothing may be re-enrolled while a line is pending")

        pending_line.target_section_id = self.next_section

        self.assertFalse(pending_line.is_pending)
        self.assertFalse(wizard.pending_warning)

        wizard.action_reenroll()

        self.assertSameRecords(self._next_year_groups(section=self.next_section).student_ids, self.student_ok)
        self.assertSameRecords(self._next_year_groups(level=self.level_2).student_ids, self.student_no_payer)

    def test_13_a_student_sent_to_another_group_is_not_proposed_again(self):
        """The already enrolled check looks at every group of next year: looking only at the
        group of the line proposed the student again and duplicated their order."""
        moving = self.student_no_payer
        students = self.student_ok + moving
        group = self._group(manage_sale_workflow=False, students=students)
        other_division = self.env["academic.division"].create({"name": "Test Reenroll Division C"})
        other_group = self._group(level=self.level_2, year=2027, division=other_division, manage_sale_workflow=False)

        first_run = self._wizard(group)
        first_run.line_ids.move_ids = [Command.create({"student_id": moving.id, "target_group_id": other_group.id})]
        first_run.action_reenroll()

        self.assertSameRecords(other_group.student_ids, moving)

        second_run = self._wizard(group)
        line = second_run.line_ids

        self.assertFalse(line.student_ids, "both students are already placed for next year")
        self.assertSameRecords(line.excluded_enrolled_ids, students)
        with self.assertRaises(ValidationError):
            second_run.action_reenroll()

        self.assertSameRecords(other_group.student_ids, moving, "the moved student must not be enrolled twice")

    def test_14_a_group_whose_students_are_all_placed_is_not_pending(self):
        """Pending means students left to place. Re-opening the wizard on a group with an
        ambiguous destination, already re-enrolled by hand, must not block anything."""
        other_section = self.env["academic.section"].create({"name": "Test Reenroll Other Next Plan"})
        self.section.correlative_ids = [Command.set((self.next_section + other_section).ids)]
        group = self._group(level=self.level_2, manage_sale_workflow=False, students=self.student_ok)

        first_run = self._wizard(group)
        first_run.line_ids.target_section_id = self.next_section
        first_run.action_reenroll()

        second_run = self._wizard(group)

        self.assertFalse(second_run.line_ids.target_section_id, "two next plans still leave the pick to the user")
        self.assertFalse(second_run.line_ids.is_pending, "nobody is left to place, so nothing is pending")
        self.assertFalse(second_run.pending_warning)
