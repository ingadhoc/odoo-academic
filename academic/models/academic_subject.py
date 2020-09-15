##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields


class AcademicSubject(models.Model):

    _name = 'academic.subject'
    _description = 'subject'

    name = fields.Char(
        required=True,
    )
    group_ids = fields.One2many(
        'academic.group',
        'subject_id',
        string='Groups',
    )
    employees_asignatures_ids = fields.One2many(
        comodel_name='hr.employee.asignatures',
        inverse_name='subject_id')
