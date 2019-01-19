from openerp import models, fields, api


class SurveyUserInputQuestionScore(models.Model):
    _inherit = 'survey.user_input_question_score'

    indicator_rel_score = fields.Float(
        'Indicator Relative Score',
        compute='_compute_indicator_rel_score', store=True)

    @api.multi
    @api.depends('score')
    # Los otros depends los sacamos y deben ser actualizados a mano con el
    # boton recompute desde una survey
    # @api.depends(
    #     'score',
    #     'question_id.max_indicator_rel_score',
    #     'question_id.max_indicator_score')
    def _compute_indicator_rel_score(self):
        for rec in self.filtered('question_id.max_indicator_score'):
            rec.indicator_rel_score = \
                rec.score / rec.question_id.max_indicator_score
