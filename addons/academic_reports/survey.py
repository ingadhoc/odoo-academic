from openerp import models, fields, api


class survey_user_input_question_score(models.Model):
    _inherit = 'survey.user_input_question_score'

    indicator_rel_score = fields.Float(
        'Indicator Relative Score',
        compute='_get_indicator_rel_score', store=True)

    @api.one
    @api.depends(
        'score',
        'question_id.max_indicator_rel_score',
        'question_id.max_indicator_score')
    def _get_indicator_rel_score(self):

        indicator_rel_score = 0.0
        if self.question_id.max_indicator_score:
            indicator_rel_score = self.score / \
                self.question_id.max_indicator_score
        print 'question_id.max_indicator_score', self.id, indicator_rel_score
        self.indicator_rel_score = indicator_rel_score


class survey_survey(models.Model):
    _inherit = 'survey.survey'
    question_ids = fields.One2many(
        'survey.question', 'stored_survey_id', 'Questions')


class survey_question(models.Model):

    _inherit = 'survey.question'

    # Tuve que agregar este campo stored survey id porque empezo a dar error
    # en el search de questions de mas abajo y no me sobreescribia el survey_id
    # agregando simplemente store
    # tal vez la solucion mas elegante sea hacer un calcular en un write o algo
    # desde las surveys
    stored_survey_id = fields.Many2one(
        'survey.survey',
        related='page_id.survey_id',
        store=True,
        string='Stored Survey Id')
    max_indicator_rel_score = fields.Float(
        'Indicator Score',
        compute='_get_max_indicator_rel_score', store=True)
    max_indicator_score = fields.Float(
        'Max Indicator Score',
        compute='_get_max_indicator_rel_score', store=True)

    @api.one
    @api.depends('max_score', 'survey_id.question_ids')
    def _get_max_indicator_rel_score(self):
        '''Con esta funcion se calcula el valor porcentual maximo que
        se puede obtener en una pregunta
        para ese indicador en una evaluacion'''
        questions = self.search(
            [('stored_survey_id', '=', self.survey_id.id),
             ('indicator_id', '=', self.indicator_id.id)])
        max_indicator_score = sum([x.max_score for x in questions])
        max_indicator_rel_score = 0.0
        if max_indicator_score:
            max_indicator_rel_score = self.max_score * \
                1.0 / max_indicator_score
        print 'Changing max_indicator_rel_score and max_indicator_score'
        self.max_indicator_rel_score = max_indicator_rel_score
        self.max_indicator_score = max_indicator_score
