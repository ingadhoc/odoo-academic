from odoo import fields, models


class SurveyLabel(models.Model):

    _inherit = 'survey.label'

    value = fields.Char(
        translate=False,
    )
