from odoo import models, fields, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    # student_id = fields.Many2one(related="move_id.student_id", store=True)
    ref = fields.Char(related=False, compute="_compute_ref")

    @api.depends('move_id.ref', 'move_id.student_id', 'move_id.student_id.name')
    def _compute_ref(self):
        for rec in self:
            rec.ref = '- '.join(filter(None, [rec.move_id.ref, rec.move_id.student_id.name]))
