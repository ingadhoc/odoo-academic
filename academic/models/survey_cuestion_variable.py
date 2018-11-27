##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields


class SurveyQuestionVariable(models.Model):

    _name = 'survey.question.variable'
    _description = 'Question Variable'

    name = fields.Char(
        required=True,
        translate=True,
    )
    performance_id = fields.Many2one(
        'survey.question.performance',
        string="Performance",
        required=True,
    )
    indicator_ids = fields.One2many(
        'survey.question.indicator',
        'variable_id',
        string="Indicators",
    )
