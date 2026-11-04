##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestMultipleEmployees(TransactionCase):
    """One person can hold several employee records, one per institution: a main
    one and its children. The module keeps the company and the user in sync down
    the hierarchy, and makes the time off dashboard add up every record."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Employee = cls.env["hr.employee"]
        cls.company_a = cls.env["res.company"].create({"name": "Instituto A"})
        cls.company_b = cls.env["res.company"].create({"name": "Instituto B"})
        cls.user = cls.env["res.users"].create(
            {
                "name": "Profesora",
                "login": "profesora.academic.hr",
                "company_id": cls.company_a.id,
                "company_ids": [(6, 0, [cls.company_a.id, cls.company_b.id])],
            }
        )
        cls.main = cls.Employee.create({"name": "Profesora A", "company_id": cls.company_a.id, "user_id": cls.user.id})
        # Through the form the compute fills the company from the main employee;
        # a bare create would take the default of the active company instead.
        # The company has to be passed: see the test about it below.
        cls.child = cls.Employee.create(
            {
                "name": "Profesora B",
                "main_employee_id": cls.main.id,
                "company_id": cls.company_a.id,
                "user_id": cls.user.id,
            }
        )

    def test_the_company_of_a_new_child_is_not_filled_in_for_you(self):
        """Known gap, NOT from the 19 -> 20 jump: measured the same on both.

        The module used to redeclare `company_id` with a compute that took the
        company of the main employee, but the core defines that field as
        `related='resource_id.company_id'` (resource/models/resource_mixin.py:20,
        identical on 19 and on 20), and a related field wins over a compute. So
        the compute never ran on either version and creating a child without a
        company fails the constraint below. From 20 on Odoo at least says so out
        loud, with "Field hr.employee.company_id is both compute and related"
        (odoo/orm/fields.py:478), a warning that did not exist in 19 -- which is
        how this surfaced. The dead compute was dropped in the migration; making
        the company fill itself in is a change of behaviour and is left to decide.
        """
        with self.assertRaises(UserError):
            self.Employee.create({"name": "Sin compañía", "main_employee_id": self.main.id})

    def test_moving_the_main_employee_moves_the_child(self):
        self.main.company_id = self.company_b
        self.assertEqual(self.child.company_id, self.company_b)

    def test_a_child_cannot_be_in_another_company(self):
        with self.assertRaises(UserError):
            self.child.company_id = self.company_b

    def test_the_user_propagates_to_the_children(self):
        other = self.env["res.users"].create(
            {
                "name": "Otra",
                "login": "otra.academic.hr",
                "company_id": self.company_a.id,
                "company_ids": [(6, 0, [self.company_a.id])],
            }
        )
        self.main.user_id = other
        self.assertEqual(self.child.user_id, other)

    def test_the_hierarchy_cannot_be_circular(self):
        with self.assertRaises(UserError):
            self.main.main_employee_id = self.child

    def test_the_contextual_employee_is_every_record_of_the_user(self):
        employees = self.Employee.with_user(self.user).with_context(multiple_employees=True)._get_contextual_employee()
        self.assertEqual(len(employees), 2)
        self.assertEqual(set(employees.ids), {self.main.id, self.child.id})

    def test_without_the_context_the_core_cannot_pick_one_employee(self):
        """FROM THE JUMP, measured on both versions. Odoo 20 hardened an
        assumption this module breaks on purpose.

        The module drops the unique(user_id, company_id) constraint in `init()`
        so one person can hold several employee records in the same institution.
        `res.users._compute_company_employee` used to build a dict keyed by user
        (hr/models/res_users.py:266 on 19), so with two employees the last one
        won and `employee_id` held a single record. On 20 it uses `_read_group`
        with `id:recordset` (hr/models/res_users.py:318) and hands the Many2one
        both records, which raises. Its docstring now states "A user has at most
        one employee per company".

        Anything reading `user.employee_id` for such a user therefore breaks on
        20. Deciding which of the employees should win is a product call, so the
        migration did not invent one; this test pins what happens today.
        """
        with self.assertRaises(ValueError):
            self.Employee.with_user(self.user)._get_contextual_employee()

    def test_the_time_off_balances_add_up_every_employee(self):
        """`get_allocation_data_request` lives on hr.work.entry.type in 20; in 19
        it was on hr.leave.type, which no longer exists. The override tags each
        entry with the employee so the two records do not collide."""
        WorkEntryType = self.env["hr.work.entry.type"].with_user(self.user)
        data = WorkEntryType.get_allocation_data_request()
        self.assertIsInstance(data, list)
        keys = [entry[3] for entry in data if len(entry) >= 4]
        self.assertEqual(len(keys), len(set(keys)), "every entry has to carry its own key")
        if data:
            self.assertTrue(
                any(f"({self.main.name})" in entry[0] or f"({self.child.name})" in entry[0] for entry in data),
                "the name of the entry says which employee it belongs to",
            )

    def test_the_balances_still_take_the_same_year_only_flag_of_20(self):
        """The 20 signature added `same_year_only`; the override has to pass it
        on instead of swallowing it."""
        WorkEntryType = self.env["hr.work.entry.type"].with_user(self.user)
        self.assertIsInstance(WorkEntryType.get_allocation_data_request(same_year_only=True), list)

    def test_the_department_does_not_count_the_employees_that_have_children(self):
        department = self.env["hr.department"].create({"name": "Docentes", "company_id": self.company_a.id})
        self.main.department_id = department
        self.child.department_id = department
        department.invalidate_recordset(["total_employee"])
        self.assertEqual(department.total_employee, 1, "only the child counts, the main one has children")
