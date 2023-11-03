from odoo import models, fields


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    student_id = fields.Many2one(related="move_id.student_id", store=True)
