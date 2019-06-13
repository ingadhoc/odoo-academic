##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import api, models, fields


class SurveyQuestion(models.Model):

    _inherit = 'survey.question'

    indicator_id = fields.Many2one(
        'survey.question.indicator',
        string='Indicator',
    )
    max_indicator_rel_score = fields.Float(
        'Indicator Score',
        compute='_compute_max_indicator_rel_score',
        store=True,
    )
    max_indicator_score = fields.Float(
        'Max Indicator Score',
        compute='_compute_max_indicator_rel_score',
        store=True,
    )

    @api.depends('page_id.survey_id.page_ids.question_ids.max_score')
    # @api.depends('max_score')
    def _compute_max_indicator_rel_score(self):
        '''Con esta funcion se calcula el valor porcentual maximo que
        se puede obtener en una pregunta
        para ese indicador en una evaluacion'''
        for rec in self:
            questions = self.search([
                ('survey_id', '=', rec.survey_id.id),
                ('indicator_id', '=', rec.indicator_id.id)])
            # max_indicator_score = max_score
            max_indicator_score = sum([x.max_score for x in questions])
            max_indicator_rel_score = 0.0
            if max_indicator_score:
                max_indicator_rel_score = rec.max_score * \
                    1.0 / max_indicator_score
            rec.update({
                'max_indicator_rel_score': max_indicator_rel_score,
                'max_indicator_score': max_indicator_score,
            })
