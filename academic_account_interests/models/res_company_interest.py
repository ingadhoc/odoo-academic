##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models
from odoo.tools.safe_eval import safe_eval


class ResCompanyInterest(models.Model):
    _inherit = "res.company.interest"

    def _prepare_interest_invoice(self, partner, debt, to_date, journal):
        student = partner
        partner = debt["partner_id"]
        res = super()._prepare_interest_invoice(partner, debt, to_date, journal)
        if res:
            res.update(
                {
                    "student_id": student.id,
                    "partner_id": partner.id,
                }
            )
        return res

    def _calculate_debts(self, from_date, to_date, groupby=None):
        if groupby is None:
            groupby = ["student_id", "partner_id"]

        deuda = {}

        interest_rate = {
            "daily": 1,
            "weekly": 7,
            "monthly": 30,
            "yearly": 360,
        }

        # Deudas de períodos anteriores
        previous_grouped_lines = self.env["account.move.line"]._read_group(
            domain=self._get_move_line_domains()
            + [("full_reconcile_id", "=", False), ("date_maturity", "<", from_date)],
            groupby=groupby,
            aggregates=["amount_residual:sum"],
        )
        for x in previous_grouped_lines:
            self._update_deuda(
                deuda,
                x[0],
                "Deuda periodos anteriores",
                x[2] * self.with_context(debt_past_period=True)._calculate_rate() * self.interval,
            )
            deuda[x[0]]["partner_id"] = x[1]

        # Intereses por el último período
        last_period_lines = self.env["account.move.line"].search(
            self._get_move_line_domains()
            + [("amount_residual", ">", 0), ("date_maturity", ">=", from_date), ("date_maturity", "<", to_date)]
        )
        for student, amls in last_period_lines.grouped("student_id").items():
            interest = sum(
                move.amount_residual
                * ((to_date - move.invoice_date_due).days)
                * (self._calculate_rate() / interest_rate[self.rule_type])
                for move, lines in amls.grouped("move_id").items()
            )
            self._update_deuda(deuda, student, "Deuda último periodo", interest)
            deuda[student]["partner_id"] = amls[0].partner_id

        # Intereses por pagos tardíos
        if self.late_payment_interest:
            partial_domain = [
                # lo dejamos para NTH
                # debit_move_id. safe eval domain
                ("debit_move_id.partner_id.active", "=", True),
                ("debit_move_id.parent_state", "=", "posted"),
                ("debit_move_id.account_id", "in", self.receivable_account_ids.ids),
                ("credit_move_id.date", ">=", from_date),
                ("credit_move_id.date", "<", to_date),
            ]

            if self.domain:
                partial_domain.append(("debit_move_id", "any", safe_eval(self.domain)))

            partials = (
                self.env["account.partial.reconcile"]
                .search(partial_domain)
                .filtered(lambda x: x.credit_move_id.date > x.debit_move_id.date_maturity)
                .grouped("debit_move_id")
            )

            for move_line, parts in partials.items():
                due_date = max(from_date, parts.debit_move_id.date_maturity)

                days = (parts.credit_move_id.date - due_date).days
                interest = parts.amount * days * (self._calculate_rate() / interest_rate[self.rule_type])
                # Se debe actualiza la deuda del partner, por ello se llama al cliente metodo para su actualizacion
                self._update_deuda(deuda, move_line.student_id, "Deuda pagos vencidos", interest)
                deuda[move_line.student_id]["partner_id"] = move_line.partner_id

        return deuda

    def _get_move_line_domains(self):
        res = super()._get_move_line_domains()
        res += [("journal_id.type", "=", "sale")]
        return res
