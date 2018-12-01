##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields


class SurveyQuestionPerformance(models.Model):

    _name = 'survey.question.performance'
    _description = 'Question Performance'

    name = fields.Char(
        required=True,
        translate=True,
    )
    variable_ids = fields.One2many(
        'survey.question.variable',
        'performance_id',
        string="Variables",
    )
