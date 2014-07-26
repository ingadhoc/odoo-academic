from openerp import osv, models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning

class survey_user_input_question_score(models.Model):
    _inherit = 'survey.user_input_question_score'

        # 'question_id': fields.many2one('survey.question', 'Question', ondelete='cascade', required=True,),
        # 'user_input_id': fields.many2one('survey.user_input', 'User Input', ondelete='cascade', required=True,),
        # 'score': fields.integer('Score', required=True,),
        # 'score_percentage': fields.integer('Score %', required=True,),    
    # indicator_rel_score = fields.Float('Indicator Relative Score')
    indicator_rel_score = fields.Float('Indicator Relative Score',compute='_get_indicator_rel_score', store=True)
    
    @api.one
    @api.depends('score','question_id.max_indicator_rel_score')
    def _get_indicator_rel_score(self):
        # questions = self.env['survey.question'].search([('survey_id','=',self.question_id.survey_id.id),
        #     ('indicator_id','=',self.question_id.indicator_id.id)])
        # print 'questions', len(questions)
        
        # max_indicator_questions_score = sum([x.max_score for x in questions])        
        # print 'max_indicator_questions_score', max_indicator_questions_score

        indicator_rel_score = 0.0
        if self.question_id.max_indicator_score:
            indicator_rel_score = self.score / self.question_id.max_indicator_score
        print 'self.question_id.max_indicator_score', self.id, indicator_rel_score
        self.indicator_rel_score = indicator_rel_score

class survey_survey(models.Model):
    _inherit = 'survey.survey'
    question_ids = fields.One2many('survey.question','survey_id','Questions')

class survey_question(models.Model):
    
    _inherit = 'survey.question'

    max_indicator_rel_score = fields.Float('Indicator Score',compute='_get_max_indicator_rel_score', store=True)
    max_indicator_score = fields.Float('Max Indicator Score',compute='_get_max_indicator_rel_score', store=True)
    max_score = fields.Integer('Max Score',compute='_get_max_score', store=True, help='Max score an answer of this question can get')

    @api.one
    # TODO seguramente el max_score tenga que modificarse en una funcion 'store'
    @api.depends('max_score')
    # @api.depends('max_score','survey_id.question_ids')
    def _get_max_indicator_rel_score(self):
        '''Con esta funcion se calcula el valor porcentual maximo que se puede obtener en una pregunta 
        para ese indicador en una evaluacion'''

        questions = self.search([('survey_id','=',self.survey_id.id),('indicator_id','=',self.indicator_id.id)])
        max_indicator_score = sum([x.max_score for x in questions])        
        max_indicator_rel_score = 0.0
        if max_indicator_score:
            max_indicator_rel_score = self.max_score * 1.0 / max_indicator_score
        print 'Changing max_indicator_rel_score and max_indicator_score'
        self.max_indicator_rel_score = max_indicator_rel_score
        self.max_indicator_score = max_indicator_score

    @api.one
    @api.depends('type')
    # @api.depends('score_ranges_ids','score_calc_method','type','copy_labels_ids','matrix_subtype','labels_ids_2')
    def _get_max_score(self):
        max_score = 0
        question = self 
        if question.type == 'simple_choice':
            scores = [answer.score for answer in question.copy_labels_ids]
            max_score = max(scores if scores else [0])

        elif question.type == 'multiple_choice' and question.score_calc_method == 'direct_sum':
            max_score = sum([answer.score for answer in question.copy_labels_ids if answer.score > 0])
        elif question.type == 'multiple_choice' and question.score_calc_method == 'ranges':
            scores = [score_range.score for score_range in question.score_ranges_ids]
            max_score = max(scores if scores else [0])
        
        elif question.type == 'numerical_box' and question.score_calc_method == 'direct_sum':
            max_score = question.validation_max_float_value
        elif question.type == 'numerical_box' and question.score_calc_method == 'ranges':
            scores = [score_range.score for score_range in question.score_ranges_ids]
            max_score = max(scores if scores else [0])              
        
        elif question.type == 'matrix' and question.matrix_subtype == 'simple' and question.score_calc_method == 'direct_sum':
            for matrix_question in question.labels_ids_2:
                scores = [matrix_score.score for matrix_score in matrix_question.matrix_answer_score_ids]
                max_score += max(scores if scores else [0])
        elif question.type == 'matrix' and question.matrix_subtype == 'multiple' and question.score_calc_method == 'direct_sum':
            for matrix_question in question.labels_ids_2:
                max_score += sum([matrix_score.score for matrix_score in matrix_question.matrix_answer_score_ids if matrix_score.score > 0])
        elif question.type == 'matrix' and question.score_calc_method == 'ranges':
            scores = [score_range.score for score_range in question.score_ranges_ids]
            max_score = max(scores if scores else [0])
        print 'Changing max_score'
        self.max_score = max_score