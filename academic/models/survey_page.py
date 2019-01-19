##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields


class SurveyPage(models.Model):
    _inherit = 'survey.page'

    description = fields.Html(
        translate=False,
    )

    title = fields.Char(
        translate=False,
    )

    def get_user_input(self, token):
        user_input_obj = self.env['survey.user_input']
        user_input_ids = user_input_obj.search(
            [('token', '=', token)])
        if user_input_ids:
            return user_input_obj.browse(
                user_input_ids[0])
        return False
