from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class EmployeeAsignatures(models.Model):
    _name = 'hr.employee.asignatures'
    _description = 'Employee Asignatures'
    _rec_name = 'teacher_id'

    name = fields.Char(compute='_compute_name')

    teacher_id = fields.Many2one(
        'hr.employee',
        required=True,
        ondelete='cascade'
    )
    subject_id = fields.Many2one(
        comodel_name='academic.subject',
    )
    level_ids = fields.Many2many(
        'academic.level',
        'hr_employee_asignatures_ids_level_ids_rel',
        'hr_employee_asignature_id',
        'level_id',
    )

    @api.constrains('teacher_id', 'subject_id')
    def _check_repeated_subject_teacher(self):
        for record in self:
            if self.env['hr.employee.asignatures'].search_count([
                    ('id', '!=', record.id),
                    ('subject_id', '=', record.subject_id.id),
                    ('teacher_id', '=', record.teacher_id.id)]):
                raise ValidationError(_(
                    'There is another record that contains the same subject \
                        and teacher'))

    @api.constrains('subject_id')
    def _check_level_ids(self):
        for record in self:
            if not record.level_ids:
                raise ValidationError(_(
                    'You have to add at least a level for that subject'))


class Employee(models.Model):
    _inherit = 'hr.employee'

    asignatures_ids = fields.One2many(
        comodel_name='hr.employee.asignatures',
        inverse_name='teacher_id',
        )

    study_plan_level_ids = fields.Many2many(related='company_id.study_plan_id.level_ids')
