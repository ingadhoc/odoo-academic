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
    survey_ids = fields.Many2many(
        'survey.survey',
        'academic_survey_ids_subject_ids_rel',
        'subject_id',
        'survey_id',
        string='Surveys',
    )
