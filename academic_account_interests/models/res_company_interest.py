##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import _, models
from odoo.tools.safe_eval import safe_eval


class ResCompanyInterest(models.Model):
    _inherit = "res.company.interest"

    def _search_last_journal_for_partner(self, partner, debt):
        partner = debt["partner_id"]
        res = super()._search_last_journal_for_partner(partner=partner, debt=debt)
        return res

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
        previous_lines = self.env["account.move.line"].search(
            self._get_move_line_domains()
            + [
                ("full_reconcile_id", "=", False),
                ("amount_residual", ">", 0),
                ("date_maturity", "<", from_date),
            ]
        )
        past_due_rate = self.with_context(debt_past_period=True)._calculate_rate()
        for line in previous_lines:
            student = line[groupby[0]] if groupby else line.student_id
            partner = line[groupby[1]] if groupby and len(groupby) > 1 else line.partner_id
            if not student or not partner:
                continue

            residual_amount = line.amount_residual
            interest = residual_amount * past_due_rate * self.interval
            detail = _(
                "- Invoice %(invoice_name)s: Residual %(residual)s x %(interval)s periods -> Interest: %(interest)s"
            ) % {
                "invoice_name": line.move_id.name or line.move_name or "-",
                "residual": round(residual_amount, 2),
                "interval": self.interval,
                "interest": round(interest, 2),
            }
            self._update_deuda(deuda, student, "Deuda periodos anteriores", interest, detail)
            deuda[student]["values"]["partner_id"] = partner

        # Intereses por el último período
        last_period_lines = self.env["account.move.line"].search(
            self._get_move_line_domains()
            + [("amount_residual", ">", 0), ("date_maturity", ">=", from_date), ("date_maturity", "<", to_date)]
        )
        for student, amls in last_period_lines.grouped("student_id").items():
            if not student:
                continue
            partner = amls[:1].partner_id
            if not partner:
                continue

            for move, lines in amls.grouped("move_id").items():
                due_date = move.invoice_date_due or lines[:1].date_maturity
                if not due_date:
                    continue
                days = max((to_date - due_date).days, 0)
                residual_amount = move.amount_residual
                interest = residual_amount * days * (self._calculate_rate() / interest_rate[self.rule_type])
                detail = _(
                    "- Invoice %(invoice_name)s: Due %(due_date)s | Residual %(residual)s x %(days)s days -> Interest: %(interest)s"
                ) % {
                    "invoice_name": move.name or lines[:1].move_name or "-",
                    "due_date": due_date,
                    "residual": round(residual_amount, 2),
                    "days": days,
                    "interest": round(interest, 2),
                }
                self._update_deuda(deuda, student, "Deuda último periodo", interest, detail)

            if student in deuda:
                deuda[student]["values"]["partner_id"] = partner

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
                partial_domain.append(("debit_move_id", "any", safe_eval(self.domain, self._get_eval_context())))

            partials = (
                self.env["account.partial.reconcile"]
                .search(partial_domain)
                .filtered(
                    lambda x: x.debit_move_id.date_maturity and x.credit_move_id.date > x.debit_move_id.date_maturity
                )
                .grouped("debit_move_id")
            )

            for move_line, parts in partials.items():
                student = move_line.student_id
                partner = move_line.partner_id
                if not student or not partner:
                    continue
                for part in parts:
                    due_date = max(from_date, part.debit_move_id.date_maturity)

                    days = (part.credit_move_id.date - due_date).days
                    interest = part.amount * days * (self._calculate_rate() / interest_rate[self.rule_type])
                    detail = _(
                        "- Payment %(payment_name)s applied to %(invoice_name)s on %(payment_date)s -> Interest: %(interest)s"
                    ) % {
                        "payment_name": part.credit_move_id.move_id.name or part.credit_move_id.name or "-",
                        "invoice_name": part.debit_move_id.move_id.name or part.debit_move_id.name or "-",
                        "payment_date": part.credit_move_id.date,
                        "interest": round(interest, 2),
                    }
                    self._update_deuda(deuda, student, "Deuda pagos vencidos", interest, detail)

                if student in deuda:
                    deuda[student]["values"]["partner_id"] = partner

        return deuda

    def _get_move_line_domains(self):
        res = super()._get_move_line_domains()
        res += [("journal_id.type", "=", "sale")]
        return res
