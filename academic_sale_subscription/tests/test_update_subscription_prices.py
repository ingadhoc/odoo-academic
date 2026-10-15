##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import fields
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestUpdateSubscriptionPrices(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.plan = cls.env["sale.subscription.plan"].create({"name": "Monthly Academic"})
        cls.product = cls.env["product.product"].create(
            {"name": "Academic Fee", "recurring_invoice": True, "invoice_policy": "order", "list_price": 100.0}
        )
        family = cls.env["res.partner"].create({"name": "Family Prices"})
        family.write({"partner_type": "family"})
        responsible = cls.env["res.partner"].create(
            {"name": "Responsible Prices", "partner_type": "parent", "vat": "20-22222222-2"}
        )
        cls.env["res.partner.link"].create(
            {
                "student_id": family.id,
                "partner_id": responsible.id,
                "relationship_id": cls.env["res.partner.relationship"].create({"name": "Test Prices"}).id,
                "role_ids": [(6, 0, [cls.env.ref("academic.paying_role").id])],
            }
        )
        cls.student = cls.env["res.partner"].create(
            {"name": "Student Prices", "partner_type": "student", "parent_id": family.id}
        )

    def test_update_prices_with_note_line(self):
        subscription = self.env["sale.order"].create(
            {
                "partner_id": self.student.id,
                "order_line": [
                    (0, 0, {"product_id": self.product.id, "product_uom_qty": 1}),
                    (0, 0, {"display_type": "line_note", "name": "Family discount"}),
                ],
            }
        )
        today = fields.Date.today()
        subscription.write(
            {
                "plan_id": self.plan.id,
                "state": "sale",
                "subscription_state": "3_progress",
                "start_date": today,
                "next_invoice_date": today,
            }
        )
        subscription.action_update_subscription_prices()
        self.assertEqual(subscription.order_line.filtered("product_id").price_unit, 100.0)
