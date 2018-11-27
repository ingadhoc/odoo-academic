##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields


class SurveyQuestionIndicator(models.Model):

    _name = 'survey.question.indicator'
    _description = 'Question Indicator'

    name = fields.Char(
        required=True,
        translate=True,
    )
    calc_type = fields.Selection(
        [('group_average', 'Group Average'),
         ('group_max', 'Group Max Value')],
        string="Calculation Type",
        required=True,
        default='group_average',
    )
    variable_id = fields.Many2one(
        'survey.question.variable',
        string="Variable",
        required=True,
    )
    question_ids = fields.One2many(
        'survey.question',
        'indicator_id',
        string="Questions",
    )
