##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import _, models


class FormReportWiz(models.TransientModel):
    _inherit = "form.report.wiz"

    def _get_form_3150_students(self, moves):
        """Students with something billed to the payment responsible during the year.

        The amount of the record is reported net of credit notes, and so is this count: a student whose
        invoices were all credited was not billed anything, and one that only shows up on a credit note
        was not billed either.
        """
        amount_per_student = {}
        for move in moves.filtered("student_id"):
            student = move.student_id
            amount_per_student[student] = amount_per_student.get(student, 0.0) + move.amount_total_signed
        currency = self.company_id.currency_id
        return [student for student, amount in amount_per_student.items() if not currency.is_zero(amount)]

    def _get_form_3150_persons(self, moves):
        return len(self._get_form_3150_students(moves)) or super()._get_form_3150_persons(moves)

    def _get_form_3150_partner_problems(self, partner, moves):
        problems = super()._get_form_3150_partner_problems(partner, moves)
        if not self._get_form_3150_students(moves):
            problems.append(_("none of its invoices of the year bills a student, so the record reports one person"))
        return problems
