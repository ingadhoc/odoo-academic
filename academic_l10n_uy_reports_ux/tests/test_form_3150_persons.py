##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestForm3150Persons(TransactionCase):
    """Cuántos alumnos informa el formulario 3150 por cada responsable de pago"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Partner = cls.env["res.partner"]
        cls.wizard = cls.env["form.report.wiz"].create({"company_id": cls.env.company.id})
        cls.responsible = Partner.create({"name": "Responsable 3150", "partner_type": "parent"})
        cls.family = Partner.create({"name": "Familia 3150"})
        cls.family.write({"partner_type": "family"})
        cls.student_a = Partner.create({"name": "Alumno A 3150", "partner_type": "student", "parent_id": cls.family.id})
        cls.student_b = Partner.create({"name": "Alumno B 3150", "partner_type": "student", "parent_id": cls.family.id})

    @classmethod
    def _create_moves(cls, students):
        return cls.env["account.move"].create(
            [
                {
                    "move_type": "out_invoice",
                    "partner_id": cls.responsible.id,
                    "student_id": student.id if student else False,
                }
                for student in students
            ]
        )

    def test_counts_distinct_students(self):
        moves = self._create_moves([self.student_a, self.student_a, self.student_b])
        self.assertEqual(self.wizard._get_form_3150_persons(moves), 2)

    def test_without_students_reports_one_and_warns(self):
        moves = self._create_moves([None])
        self.assertEqual(self.wizard._get_form_3150_persons(moves), 1)
        problems = self.wizard._get_form_3150_partner_problems(self.responsible, moves)
        self.assertTrue(any("student" in problem for problem in problems), problems)

    def test_with_students_does_not_warn(self):
        moves = self._create_moves([self.student_a])
        problems = self.wizard._get_form_3150_partner_problems(self.responsible, moves)
        self.assertFalse([problem for problem in problems if "student" in problem], problems)
