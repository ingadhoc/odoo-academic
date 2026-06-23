##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import api, fields, models


class ArchiveFamilyDebtWizard(models.TransientModel):
    _name = "archive.family.debt.wizard"
    _description = "Archive Family — Debt Warning"

    family_ids = fields.Many2many(
        "res.partner",
        string="Families",
        domain=[("partner_type", "=", "family")],
    )
    student_debt_info = fields.Html(
        string="Students with pending debt",
        readonly=True,
        compute="_compute_student_debt_info",
    )

    @api.depends("family_ids")
    def _compute_student_debt_info(self):
        for wizard in self:
            families = self.env["res.partner"].browse(wizard.family_ids.ids)
            students_with_debt = families.student_ids._get_students_with_debt()
            if not students_with_debt:
                wizard.student_debt_info = False
                continue
            items = "".join(f"<li>{s.name}</li>" for s in students_with_debt)
            wizard.student_debt_info = (
                "<p>"
                + self.env._(
                    "The following students have unpaid invoices. "
                    "Their payment responsibles will be archived and "
                    "will no longer receive mass communications."
                )
                + f"</p><ul>{items}</ul>"
                + "<p>"
                + self.env._(
                    "The debt remains recorded in accounting and is visible in the "
                    "Partner Ledger and Aged Receivable reports."
                )
                + "</p>"
            )

    def action_confirm(self):
        self.family_ids.with_context(skip_debt_check=True).action_archive()
        return {"type": "ir.actions.act_window_close"}
