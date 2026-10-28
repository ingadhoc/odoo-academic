##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from unittest.mock import patch

from odoo import Command
from odoo.tests.common import TransactionCase, new_test_user, tagged
from odoo.tools import mute_logger


@tagged("post_install", "-at_install")
class TestBackgroundOrders(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Partner = cls.env["res.partner"]
        cls.company = cls.env.company
        cls.user = new_test_user(
            cls.env,
            login="test_batch_manager",
            groups="academic.group_manager,sales_team.group_sale_manager",
            company_id=cls.company.id,
        )

        cls.level_1 = cls.env["academic.level"].create({"name": "Test Batch Level 1"})
        cls.level_2 = cls.env["academic.level"].create({"name": "Test Batch Level 2"})
        cls.section = cls.env["academic.section"].create(
            {
                "name": "Test Batch Plan",
                "level_line_ids": [
                    Command.create({"level_id": cls.level_1.id, "sequence": 10}),
                    Command.create({"level_id": cls.level_2.id, "sequence": 20}),
                ],
            }
        )
        cls.company.section_ids = [Command.link(cls.section.id)]

        relationship = cls.env["res.partner.relationship"].create({"name": "Test Batch Parent"})
        paying_role = cls.env.ref("academic.paying_role")
        family = Partner.create({"name": "Test Batch Family", "partner_type": "family"})
        payer = Partner.create({"name": "Test Batch Payer", "partner_type": "parent"})
        cls.students = Partner.create(
            [{"name": f"Test Batch Student {i}", "partner_type": "student", "parent_id": family.id} for i in range(4)]
        )
        cls.env["res.partner.link"].create(
            [
                {
                    "student_id": student.id,
                    "partner_id": payer.id,
                    "relationship_id": relationship.id,
                    "role_ids": [Command.set(paying_role.ids)],
                }
                for student in cls.students
            ]
        )

        cls.plan = cls.env["sale.subscription.plan"].create(
            {"name": "Test Batch Monthly", "billing_period_value": 1, "billing_period_unit": "month"}
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Batch Registration",
                "type": "service",
                "recurring_invoice": True,
                "academic_product_type": "registration",
                "list_price": 100.0,
            }
        )
        cls.template = cls.env["sale.order.template"].create(
            {
                "name": "Test Batch Template",
                "plan_id": cls.plan.id,
                "sale_order_template_line_ids": [Command.create({"product_id": cls.product.id})],
            }
        )

    def setUp(self):
        super().setUp()
        # only the jobs of the test: the runner below would also pick the ones left in the database
        self.env["bg.job"].search([("state", "in", ["enqueued", "waiting"])]).state = "canceled"

    def _set_threshold(self, value):
        self.env["ir.config_parameter"].sudo().set_param("academic_sale_subscription.background_order_threshold", value)

    def _group(self, students):
        return self.env["academic.group"].create(
            {
                "year": 2026,
                "company_id": self.company.id,
                "section_id": self.section.id,
                "level_id": self.level_1.id,
                "manage_sale_workflow": True,
                "capacity": 10,
                "student_ids": [Command.set(students.ids)],
            }
        )

    def _reenroll(self, group, status_sale="confirmed"):
        wizard = (
            self.env["academic.reenrollment.wizard"]
            .with_user(self.user)
            .with_context(active_ids=group.ids)
            .create(
                {
                    "template_id": self.template.id,
                    "next_invoice_date": "2027-03-01",
                    "validity_date": "2027-02-01",
                    "status_sale": status_sale,
                }
            )
        )
        return wizard.action_reenroll()

    def _orders(self, students):
        return self.env["sale.order"].search([("partner_id", "in", students.ids)])

    def _jobs(self):
        return self.env["bg.job"].search(
            [("method", "=", "_create_academic_orders"), ("create_uid", "=", self.user.id)]
        )

    def _run_jobs(self):
        """Run the queued jobs as the base_bg runner would, returning the messages sent."""
        Job = self.env["bg.job"]
        # base_bg commits around each job, which a test cursor refuses
        with patch.object(self.env.cr, "commit"), patch.object(type(Job), "_notify_user") as notify:
            while job := Job.search([("method", "=", "_create_academic_orders"), ("state", "=", "enqueued")], limit=1):
                job.state = "running"
                job.run()
        return [call.args[0] for call in notify.call_args_list]

    def test_01_under_the_threshold_orders_are_created_right_away(self):
        self._set_threshold(10)
        self._reenroll(self._group(self.students))

        self.assertFalse(self._jobs(), "few students must keep the immediate flow")
        orders = self._orders(self.students)
        self.assertEqual(len(orders), 4)
        self.assertEqual(set(orders.mapped("state")), {"sale"})

    def test_02_over_the_threshold_orders_go_to_a_background_job(self):
        self._set_threshold(2)
        self._reenroll(self._group(self.students))

        jobs = self._jobs()
        self.assertEqual(len(jobs), 2, "4 students in jobs of 2")
        self.assertEqual(jobs.create_uid, self.user, "base_bg runs the jobs as who queued them")
        self.assertFalse(self._orders(self.students), "no order may be created within the request")
        target = self.env["academic.group"].search([("year", "=", 2027), ("section_id", "=", self.section.id)])
        self.assertEqual(target.level_id, self.level_2, "the next year group is created right away")

        messages = self._run_jobs()

        orders = self._orders(self.students)
        self.assertEqual(len(orders), 4)
        self.assertEqual(set(orders.mapped("state")), {"sale"})
        self.assertEqual(orders.order_line.group_id, target)
        self.assertEqual(orders.user_id, self.user, "the orders belong to who ran the wizard, not to the cron")
        self.assertEqual(orders.create_uid, self.user)
        self.assertEqual(len(messages), 2, "one message per job")
        self.assertIn("2 academic order(s) created", messages[0])

    def test_03_queued_students_are_not_proposed_again(self):
        """Between the queueing and the job run, a second wizard must not duplicate them."""
        self._set_threshold(2)
        group = self._group(self.students)
        self._reenroll(group)

        second = (
            self.env["academic.reenrollment.wizard"].with_user(self.user).with_context(active_ids=group.ids).create({})
        )
        self.assertFalse(second.line_ids.student_ids)
        self.assertEqual(sorted(second.line_ids.excluded_enrolled_ids.ids), sorted(self.students.ids))

    @mute_logger("odoo.sql_db", "odoo.addons.academic_sale_subscription.models.res_partner")
    def test_04_a_failing_student_does_not_stop_the_rest(self):
        self._set_threshold(2)
        # an order of this company can not take a contact of another one
        other_company = self.env["res.company"].create({"name": "Test Background Other Company"})
        Partner = self.env["res.partner"]
        family = Partner.create(
            {"name": "Test Background Other Family", "partner_type": "family", "company_id": other_company.id}
        )
        broken = Partner.create(
            {"name": "Test Background Broken Student", "partner_type": "student", "parent_id": family.id}
        )
        self.env["res.partner.link"].create(
            {
                "student_id": broken.id,
                "partner_id": Partner.create(
                    {"name": "Test Background Other Payer", "partner_type": "parent", "company_id": other_company.id}
                ).id,
                "relationship_id": self.students.student_link_ids.relationship_id[:1].id,
                "role_ids": [Command.set(self.env.ref("academic.paying_role").ids)],
            }
        )
        self._reenroll(self._group(self.students | broken), status_sale="draft")

        messages = self._run_jobs()

        self.assertFalse(self._orders(broken))
        self.assertEqual(len(self._orders(self.students)), 4)
        self.assertEqual(set(self._jobs().mapped("state")), {"done"}, "the failure must not cancel the next job")
        summary = next(m for m in messages if broken.name in m)
        self.assertIn("academic order(s) created", summary)

    def test_05_mass_order_wizard_also_goes_to_the_background(self):
        self._set_threshold(2)
        group = self._group(self.students)
        wizard = (
            self.env["academic.order.wizard"]
            .with_user(self.user)
            .with_context(active_ids=self.students.ids)
            .create({"template_id": self.template.id, "next_invoice_date": "2027-03-01", "validity_date": "2027-02-01"})
        )
        # opened from the students, not from a group: the group is set on the line
        wizard.order_wizard_line_ids.academic_group_id = group
        wizard.action_create_mass_subscription()

        self.assertFalse(self._orders(self.students))
        self.assertEqual(group._get_pending_registration_students(), self.students)
        self._run_jobs()
        orders = self._orders(self.students)
        self.assertEqual(len(orders), 4)
        self.assertEqual(orders.plan_id, self.plan)
        self.assertEqual(set(orders.mapped("state")), {"draft"})

    def test_06_a_group_is_readable_without_access_to_jobs(self):
        reader = new_test_user(self.env, login="test_bg_reader", groups="base.group_user")
        self._set_threshold(2)
        group = self._group(self.students)
        self._reenroll(group)
        target = self.env["academic.group"].search([("year", "=", 2027), ("section_id", "=", self.section.id)])
        self.assertEqual(target.with_user(reader).registration_student_count, 4)

    def test_07_the_threshold_defaults_to_fifty(self):
        Wizard = self.env["academic.order.wizard"]
        self.env["ir.config_parameter"].sudo().search(
            [("key", "=", "academic_sale_subscription.background_order_threshold")]
        ).unlink()
        self.assertEqual(Wizard._get_background_threshold(), 50, "without the parameter")
        self._set_threshold("fifty")
        self.assertEqual(Wizard._get_background_threshold(), 50, "with a wrong value")
