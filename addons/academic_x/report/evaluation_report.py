# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import tools
from openerp.osv import fields, osv

class academic_evaluation_report(osv.osv):
    _name = "academic.evaluation.report"
    _description = "Academic Evaluation Report"
    _auto = False
    # _rec_name = 'date'
    _columns = {
    # Survey Fields
        'is_evaluation': fields.boolean('Is Evaluation?', readonly=True, ),
        'survey_id' : fields.many2one('survey.survey', 'Survey', readonly=True,),
        'survey_stage_id': fields.many2one('survey.stage', string="Stage", readonly=True,),
    # User Input Fields / answer
        'input_score': fields.float('Score', readonly=True, group_operator='sum', ),
        'input_min_score': fields.float('Min. Score', readonly=True, group_operator='min', ),
        'input_max_score': fields.float('Max. Score', readonly=True, group_operator='max', ),
        'input_avg_score': fields.float('Avg. Score', readonly=True, group_operator='avg', ),
        'input_state' : fields.selection([('done', 'Finished '),('skip', 'Not Finished')], 'Status', readonly=True),        
        'group_id' : fields.many2one('academic.group', 'Group', readonly=True,),
        'partner_id' : fields.many2one('res.partner', 'Partner', readonly=True,),
        'company_id' : fields.many2one('res.partner', 'Company', readonly=True,),
    # User Input Question Fields
        # 'question_score': fields.float('Score', readonly=True, group_operator='avg', ),
        'question_avg_score': fields.float('Score', readonly=True, group_operator='avg', ),
    # Question fields
        'objective_id': fields.many2one('survey.question.objective', string='Objective', readonly=True),
        'level_id': fields.many2one('survey.question.level', string='Level', readonly=True),        
        'content_id': fields.many2one('survey.question.content', string='Content', readonly=True),        
        'indicator_id': fields.many2one('survey.question.indicator', string='Indicator', readonly=True),        
        'variable_id': fields.many2one('survey.question.variable', string='Variable', readonly=True),        
        'performance_id': fields.many2one('survey.question.performance', string='Performance', readonly=True),
        # TODO to bring max_score it should be a stored functional field
        # 'max_score': fields.integer('Max Score', readonly=True),
    # Not used fields / to analize
        # 'date_create' : fields.datetime('Create Date', readonly=True, ),
    }

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'academic_evaluation_report')
        cr.execute("""
            create or replace view academic_evaluation_report as (
SELECT
        survey_user_input_question_score.id as id,
        survey_user_input_question_score.score as question_avg_score,
        survey_question.objective_id as objective_id,
        survey_question.level_id as level_id,
        survey_question.content_id as content_id,
        survey_question.indicator_id as indicator_id,
        survey_question_indicator.variable_id as variable_id,
    survey_question_variable.performance_id as performance_id,        
        survey_user_input.score as input_score,
        survey_user_input.score as input_min_score,
        survey_user_input.score as input_max_score,
        survey_user_input.score as avg_score,
        survey_user_input.survey_id as survey_id,
        survey_user_input.date_create as date_create,
        survey_user_input.partner_id as partner_id,
        survey_user_input.state as input_state,
        academic_group_evaluation.group_id as group_id,
        academic_group.company_id,
        survey_survey.is_evaluation as is_evaluation,
        survey_survey.stage_id as survey_stage_id        
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
    FULL JOIN survey_question_indicator
        on survey_question.indicator_id = survey_question_indicator.id      
    FULL JOIN survey_question_variable
        on survey_question_indicator.variable_id = survey_question_variable.id
        )
        """)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
