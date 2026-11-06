##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import Command
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestOrderWizard(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Partner = cls.env["res.partner"]

        family = Partner.create({"name": "Test Order Family", "partner_type": "family"})
        cls.student = Partner.create({"name": "Test Order Student", "partner_type": "student", "parent_id": family.id})
        cls.env["res.partner.link"].create(
            {
                "student_id": cls.student.id,
                "partner_id": Partner.create({"name": "Test Order Payer", "partner_type": "parent"}).id,
                "relationship_id": cls.env["res.partner.relationship"].create({"name": "Test Order Parent"}).id,
                "role_ids": [Command.set(cls.env.ref("academic.paying_role").ids)],
            }
        )

        cls.product = cls.env["product.product"].create({"name": "Test Order Colonia", "list_price": 100.0})
        cls.extra = cls.env["product.product"].create({"name": "Test Order Hora Extra", "list_price": 10.0})

        # the same products under two sections: what the summer camp templates look like
        cls.template = cls.env["sale.order.template"].create(
            {
                "name": "Test Order Colonia Verano",
                "sale_order_template_line_ids": [
                    Command.create({"sequence": 10, "display_type": "line_section", "name": "Diciembre"}),
                    Command.create({"sequence": 11, "name": "Diciembre", "product_id": cls.product.id}),
                    Command.create({"sequence": 12, "name": "Diciembre", "product_id": cls.extra.id}),
                    Command.create({"sequence": 13, "display_type": "line_section", "name": "Enero"}),
                    Command.create({"sequence": 14, "name": "Enero", "product_id": cls.product.id}),
                    Command.create({"sequence": 15, "name": "Enero", "product_id": cls.extra.id}),
                ],
            }
        )

    def _wizard(self):
        return self.env["academic.order.wizard"].create(
            {
                "student_ids": [Command.set(self.student.ids)],
                "template_id": self.template.id,
            }
        )

    def test_wizard_lines_mirror_the_template(self):
        lines = self._wizard().order_wizard_line_ids
        self.assertEqual(
            [(line.display_type, line.name, line.product_id) for line in lines],
            [
                ("line_section", "Diciembre", self.env["product.product"]),
                (False, "Diciembre", self.product),
                (False, "Diciembre", self.extra),
                ("line_section", "Enero", self.env["product.product"]),
                (False, "Enero", self.product),
                (False, "Enero", self.extra),
            ],
        )

    def test_order_keeps_sections_and_descriptions(self):
        wizard = self._wizard()
        wizard.order_wizard_line_ids.filtered("product_id").quantity = 2.0

        action = wizard.action_create_mass_subscription()
        orders = self.env["sale.order"].browse(action["domain"][0][2])

        self.assertEqual(len(orders), 1)
        self.assertEqual(
            [(line.display_type, line.name, line.product_id) for line in orders.order_line],
            [
                ("line_section", "Diciembre", self.env["product.product"]),
                (False, "Diciembre", self.product),
                (False, "Diciembre", self.extra),
                ("line_section", "Enero", self.env["product.product"]),
                (False, "Enero", self.product),
                (False, "Enero", self.extra),
            ],
        )
        self.assertEqual(orders.order_line.filtered("display_type").mapped("product_uom_qty"), [0.0, 0.0])
        self.assertEqual(orders.order_line.filtered("product_id").mapped("product_uom_qty"), [2.0] * 4)
