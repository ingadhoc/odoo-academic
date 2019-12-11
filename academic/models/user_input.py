##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, _
from odoo.exceptions import UserError


class SurveyUserInput(models.Model):

    _name = 'survey.user_input'
    _inherit = 'survey.user_input'

    apply_to_id = fields.Many2one(
        'res.partner',
        string='Apply To',
        readonly=True,
    )
    note = fields.Text(
        states={'done': [('readonly', True)]},
    )
    observation_category_id = fields.Many2one(
        'academic.observation_category',
        string='Observation Category',
        states={'done': [('readonly', True)]},
    )
    group_evaluation_id = fields.Many2one(
        'academic.group_evaluation',
        string='Group Evaluation',
        readonly=True,
        ondelete='cascade',
    )
    company_id = fields.Many2one(
        'res.company',
        related='group_evaluation_id.company_id',
        string='Company',
        store=True,
    )
    group_id = fields.Many2one(
        'academic.group',
        related='group_evaluation_id.group_id',
        string='Group',
        store=True,
    )

    def force_closure(self):
        for record in self:
            if not record.observation_category_id\
                    or not record.observation_category_id.name:
                raise UserError(_(
                    "You can not force closure if you not set"
                    " an observation category."))
        return self.write({'state': 'done'})

    def action_answer_survey(self):
        ''' Open the website page with the survey form into test mode'''
        # user_input = self.browse(cr, uid, id)[0]

        # TODO mejorar este fix que hicimos, es porque algunas veces daba error
        # al re abrir una survey
        self.write({'state': 'new'})

        url = self.survey_id.public_url + '/' + self.token
        return {
            'type': 'ir.actions.act_url',
            'name': "Evaluation",
            'target': 'self',
            'url': url,
        }
