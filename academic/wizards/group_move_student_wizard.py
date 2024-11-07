##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AcademicGroupMoveStudentWizard(models.TransientModel):
    _name = 'academic.group.move.student.wizard'
    _description = 'Wizard para mover estudiante'

    parent_group_id = fields.Many2one('academic.group', readonly=True, default=lambda self: self.env.context.get('active_id', []))
    student_to_move = fields.Many2many('res.partner', compute="_compute_student_to_move")
    student_ids = fields.Many2many('res.partner', domain="[('id', 'in', student_to_move)]", compute="_compute_student_to_move", readonly=False)
    child_group_id = fields.Many2one('academic.group', domain="[('parent_id', '=', parent_group_id)]", required=True)

    def move_students(self):
        self.ensure_one()

        if not self.student_ids:
            raise UserError(_("Please select at least one student to move."))

        self.parent_group_id.write({'student_ids': [(3, student.id) for student in self.student_ids]})
        self.child_group_id.write({'student_ids': [(4, student.id) for student in self.student_ids]})

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'academic.group',
            'view_mode': 'form',
            'res_id': self.child_group_id.id,
            'target': 'current',
        }

    @api.depends('parent_group_id')
    def _compute_student_to_move(self):
        records = self.filtered('parent_group_id')
        for rec in records:
            existing_student_ids = rec.child_group_id.student_ids.ids if rec.child_group_id else []
            available_student_ids = rec.parent_group_id.student_ids.filtered(lambda s: s.id not in existing_student_ids).ids
            rec.student_to_move = [(6, 0, available_student_ids)]
            rec.student_ids = [(6, 0, available_student_ids)]
        (self - records).student_to_move = [(6, 0, [])]
        (self - records).student_ids = [(6, 0, [])]
