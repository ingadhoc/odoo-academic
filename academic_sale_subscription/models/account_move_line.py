from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    student_id = fields.Many2one("res.partner", related="move_id.student_id", readonly=True)
    family_id = fields.Many2one("res.partner", related="student_id.parent_id", store=True, string="Family")
    ref = fields.Char(related=False, compute="_compute_ref")

    @api.depends("move_id.ref", "move_id.student_id", "move_id.student_id.name")
    def _compute_ref(self):
        for rec in self:
            rec.ref = " - ".join(filter(None, [rec.move_id.ref, rec.move_id.student_id.name]))
