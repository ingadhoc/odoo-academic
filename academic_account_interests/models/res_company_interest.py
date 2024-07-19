##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models


class ResCompanyInterest(models.Model):
    _inherit = 'res.company.interest'

    def _prepare_interest_invoice(self, line, to_date, journal):
        line = list(line)
        student = line[0]
        partner = line[1]
        line.pop(0)
        res = super()._prepare_interest_invoice(line, to_date, journal)
        if res:
            res.update({
                'student_id': student.id,
                'partner_id': partner.id,
            })
        return res

    def create_invoices(self, to_date, groupby=['student_id', 'partner_id']):
        return super().create_invoices(to_date, groupby=groupby)

    def _get_move_line_domains(self, to_date):
        res = super()._get_move_line_domains(to_date)
        res += [('journal_id.type', '=', 'sale'), ('move_id.state', '=', 'posted')]
        return res
