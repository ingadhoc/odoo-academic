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
        cls.company = cls.env.company
        cls.company.section_ids = [Command.link(cls.section.id)]

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

    def _group(self, level=None, manage_sale_workflow=True, students=None):
        students = students or self.env["res.partner"]
        return self.env["academic.group"].create(
            {
                "year": 2026,
                "company_id": self.company.id,
                "section_id": self.section.id,
                "level_id": (level or self.level_1).id,
                "division_id": self.division.id,
                # explicit: the compute would derive it from subject_id, and capacity has
                # to cover the students or the vacancies constraint rejects the create
                "manage_sale_workflow": manage_sale_workflow,
                "capacity": 10,
                "student_ids": [Command.set(students.ids)],
            }
        )

    def _wizard(self, groups):
        return self.env["academic.reenrollment.wizard"].with_context(active_ids=groups.ids).create({})

    def _next_year_groups(self, level=None):
        domain = [("year", "=", 2027), ("section_id", "=", self.section.id)]
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
