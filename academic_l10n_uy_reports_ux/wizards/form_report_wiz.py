from odoo import _, models


class FormReportWiz(models.TransientModel):
    _inherit = "form.report.wiz"

    def _get_form_3150_persons(self, moves):
        """Distinct students billed to the payment responsible during the year"""
        return len(moves.student_id) or super()._get_form_3150_persons(moves)

    def _get_form_3150_partner_problems(self, partner, moves):
        problems = super()._get_form_3150_partner_problems(partner, moves)
        if not moves.student_id:
            problems.append(_("none of its invoices of the year has a student"))
        return problems
