##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestInvoiceGrouping(TransactionCase):
    """Facturar a mano no junta en una misma factura ventas de distinto alumno ni de distinto termino
    de pago, aunque compartan el responsable de pago."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Partner = cls.env["res.partner"]

        cls.relationship = cls.env["res.partner.relationship"].create({"name": "Test Grouping Relationship"})
        cls.paying_role = cls.env.ref("academic.paying_role")

        cls.family = Partner.create({"name": "Family Grouping"})
        cls.family.write({"partner_type": "family"})
        cls.responsible = Partner.create(
            {"name": "Responsible Grouping", "partner_type": "parent", "vat": "20-22222222-2"}
        )
        cls.env["res.partner.link"].create(
            {
                "student_id": cls.family.id,
                "partner_id": cls.responsible.id,
                "relationship_id": cls.relationship.id,
                "role_ids": [(6, 0, [cls.paying_role.id])],
            }
        )
        cls.student = Partner.create(
            {"name": "Student Grouping", "partner_type": "student", "parent_id": cls.family.id}
        )
        cls.sibling = Partner.create(
            {"name": "Sibling Grouping", "partner_type": "student", "parent_id": cls.family.id}
        )

        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Grouping Fee",
                "type": "service",
                "invoice_policy": "order",
                "list_price": 100.0,
            }
        )
        cls.payment_term_a = cls.env.ref("account.account_payment_term_immediate")
        cls.payment_term_b = cls.env.ref("account.account_payment_term_30days")

    @classmethod
    def _create_order(cls, student, payment_term):
        order = cls.env["sale.order"].create(
            {
                "partner_id": student.id,
                "payment_term_id": payment_term.id,
                "order_line": [(0, 0, {"product_id": cls.product.id, "product_uom_qty": 1})],
            }
        )
        order.action_confirm()
        return order

    def test_different_payment_terms_are_not_merged(self):
        """El caso del ticket: un alumno con dos cuotas que vencen distinto dia."""
        orders = self._create_order(self.student, self.payment_term_a) | self._create_order(
            self.student, self.payment_term_b
        )

        invoices = orders._create_invoices()

        self.assertEqual(len(invoices), 2)
        self.assertEqual(invoices.mapped("invoice_payment_term_id"), self.payment_term_a | self.payment_term_b)

    def test_same_payment_term_is_merged(self):
        """Sin diferencia de termino de pago ni de alumno, la consolidacion sigue siendo la de siempre."""
        orders = self._create_order(self.student, self.payment_term_a) | self._create_order(
            self.student, self.payment_term_a
        )

        invoices = orders._create_invoices()

        self.assertEqual(len(invoices), 1)

    def test_different_students_are_not_merged(self):
        """Dos hermanos comparten responsable de pago pero cada uno factura por separado."""
        orders = self._create_order(self.student, self.payment_term_a) | self._create_order(
            self.sibling, self.payment_term_a
        )

        invoices = orders._create_invoices()

        self.assertEqual(len(invoices), 2)
        self.assertEqual(invoices.mapped("student_id"), self.student | self.sibling)
