# -*- coding: utf-8 -*-
from openerp import tools
from openerp import models, fields, api, _

class academic_evaluation_report(models.Model):
    _name = "academic.evaluation.report"
    _description = "Academic Evaluation Report"
    _auto = False

    # Survey Fields
    is_evaluation = fields.Boolean('Is Evaluation?', readonly=True,)
    survey_id = fields.Many2one('survey.survey', 'Survey', readonly=True,)
    survey_stage_id = fields.Many2one('survey.stage', string="Stage", readonly=True,)
    period_id =  fields.Many2one('academic.period', string='Period', readonly=True,)
    
    # Group evaluation
    group_evaluation_state = fields.Selection([(u'invisible', u'Invisible'), (u'visible', u'Visible'), (u'open', u'Open'), (u'closed', u'Closed')], 'Group Ev. Status', readonly=True)
    
    # # Partner
    disabled_person = fields.Boolean('Disabled Person?')
    
    # User Input
    question_id =  fields.Many2one('survey.question', string='Question',)
    dont_consider = fields.Boolean('Don not Consider?')
    input_state = fields.Selection([('done', 'Finished '),('skip', 'Not Finished')], 'Status', readonly=True)
    group_id = fields.Many2one('academic.group', 'Group', readonly=True,)
    partner_id = fields.Many2one('res.partner', 'Partner', readonly=True,)
    company_id = fields.Many2one('res.company', 'Company', readonly=True,)
    input_avg_score = fields.Float('Avg Score', readonly=True, group_operator='avg',)
    input_min_score = fields.Float('Min Score', readonly=True, group_operator='min',)
    input_max_score = fields.Float('Max Score', readonly=True, group_operator='max',)

    # Question fields
    objective_id = fields.Many2one('survey.objective', string='Objective', readonly=True)
    level_id = fields.Many2one('survey.level', string='Level', readonly=True) 
    content_id = fields.Many2one('survey.content', string='Content', readonly=True)

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'academic_evaluation_report')
        cr.execute("""
            create or replace view academic_evaluation_report as (
SELECT
        survey_user_input_question_score.id as id,
        survey_user_input_question_score.question_id as question_id,
        survey_user_input_question_score.score_percentage as input_avg_score,
        survey_user_input_question_score.score_percentage as input_min_score,
        survey_user_input_question_score.score_percentage as input_max_score,
        survey_question.objective_id as objective_id,
        survey_question.level_id as level_id,
        survey_question.content_id as content_id,
        survey_user_input.survey_id as survey_id,
        survey_user_input.partner_id as partner_id,
        survey_user_input.state as input_state,
        res_partner.disabled_person as disabled_person,
        academic_group_evaluation.group_id as group_id,
        academic_group_evaluation.state as group_evaluation_state,
        academic_group.company_id,
        academic_observation_category.dont_consider as dont_consider,
        survey_survey.is_evaluation as is_evaluation,
        survey_survey.stage_id as survey_stage_id,
        survey_survey.period_id as period_id  
    FROM survey_user_input_question_score
    INNER JOIN survey_user_input
        on survey_user_input_question_score.user_input_id = survey_user_input.id
    INNER JOIN survey_survey
    on survey_user_input.survey_id = survey_survey.id
    FULL JOIN academic_group_evaluation
        on survey_user_input.group_evaluation_id = academic_group_evaluation.id  
    FULL JOIN academic_group
        on academic_group_evaluation.group_id = academic_group.id  
    INNER JOIN survey_question
        on survey_user_input_question_score.question_id = survey_question.id
    LEFT JOIN academic_observation_category
    on survey_user_input.observation_category_id = academic_observation_category.id        
    INNER JOIN res_partner
    on survey_user_input.partner_id = res_partner.id            
    WHERE survey_survey.evaluation_subtype = 'student_evaluation'
        )
        """)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
