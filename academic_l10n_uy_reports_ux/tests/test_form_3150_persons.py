##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo.addons.l10n_uy_reports_ux.tests.test_form_3150 import TestForm3150
from odoo.tests.common import tagged


@tagged("post_install_l10n", "post_install", "-at_install")
class TestForm3150Persons(TestForm3150):
    """How many students the form 3150 reports for each payment responsible.

    It runs over the same data as the declaration itself: the invoices have to pass the filter of
    l10n_uy_reports_ux (posted, of the year, accepted by the DGI) to be counted here.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.family = cls.env["res.partner"].create({"name": "Familia 3150", "partner_type": "family"})
        cls.student_a = cls._create_student("Alumno A 3150")
        cls.student_b = cls._create_student("Alumno B 3150")
        cls.student_c = cls._create_student("Alumno C 3150")

    @classmethod
    def _create_student(cls, name):
        return cls.env["res.partner"].create(
            {
                "name": name,
                "partner_type": "student",
                "parent_id": cls.family.id,
            }
        )

    def _persons_of(self, content, name):
        """The persons field of the line E of the record of this payment responsible"""
        return self._record_of(content, name)[4][40:].split(";")[-1]

    def test_counts_distinct_students_on_the_file(self):
        """Two invoices of the same student are one person, and the responsible without students reports one"""
        partner = self._create_responsible("Lopez Maria", "11111111", "Ejido 1495")
        self._create_move(partner, 400000, student_id=self.student_a.id)
        self._create_move(partner, 400000, student_id=self.student_a.id)
        self._create_move(partner, 400000, student_id=self.student_b.id)

        content = self._get_file(self._get_wizard())
        self.assertEqual(self._persons_of(content, "Lopez Maria"), "0002")
        self.assertEqual(self._persons_of(content, "Perez Juan"), "0001", "It has no students at all")

    def test_credit_notes_do_not_add_students(self):
        """A student billed and credited for the same amount was not billed, as the amount of the record"""
        partner = self._create_responsible("Diaz Jorge", "22222222", "Ejido 1495")
        self._create_move(partner, 900000, student_id=self.student_a.id)
        self._create_move(partner, 300000, student_id=self.student_b.id)
        self._create_move(partner, 300000, move_type="out_refund", student_id=self.student_b.id)
        # Only on a credit note, it was never billed either
        self._create_move(partner, 100000, move_type="out_refund", student_id=self.student_c.id)

        content = self._get_file(self._get_wizard())
        self.assertEqual(self._persons_of(content, "Diaz Jorge"), "0001")

    def test_without_students_the_record_is_listed(self):
        """Billing a student to a responsible that had none takes one problem off its list"""
        wizard = self._get_wizard()
        moves = self.env["account.move"].search([("partner_id", "=", self.over.id)])
        before = wizard._get_form_3150_partner_problems(self.over, moves)

        moves[0].student_id = self.student_a
        after = wizard._get_form_3150_partner_problems(self.over, moves)
        self.assertEqual(len(after), len(before) - 1, before)
