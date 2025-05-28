##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import api, fields, models
from odoo.exceptions import UserError


class ResCompany(models.Model):
    _inherit = "res.company"

    require_student_on_invoices = fields.Boolean(default=True)

    @api.constrains("require_student_on_invoices")
    def _check_invoices_with_student(self):
        cia_require_students = self.filtered("require_student_on_invoices")
        if cia_require_students:
            invoices = self.env["account.move"].search(
                [
                    ("company_id", "in", cia_require_students.ids),
                    ("move_type", "in", ["out_invoice", "out_refund"]),
                    ("student_id", "=", False),
                ],
                limit=1,
            )
            if invoices:
                raise UserError(
                    self.env._(
                        "You cannot mark require student on invoices if there are already invoices without students."
                    )
                )
