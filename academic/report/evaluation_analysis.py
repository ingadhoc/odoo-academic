##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, tools


class AcademicEvaluationAnalysis(models.Model):
    _name = "academic.evaluation.analysis"
    _description = "Evaluation Analysis"
    _auto = False

    # Survey Fields
    is_evaluation = fields.Boolean(
        'Is Evaluation?',
        readonly=True,)
    survey_id = fields.Many2one(
        'survey.survey',
        'Survey',
        readonly=True,
    )
    survey_stage_id = fields.Many2one(
        'survey.stage',
        string="Stage",
        readonly=True,)
    period_id = fields.Many2one(
        'academic.period',
        string='Period',
        readonly=True,)

    # Group evaluation
    group_evaluation_state = fields.Selection(
        [('invisible', 'Invisible'),
         ('visible', 'Visible'),
         ('open', 'Open'),
         ('closed', 'Closed')],
        'Group Ev. Status', readonly=True)

    # Partner
    disabled_person = fields.Boolean(
        'Disabled Person?',
    )

    # User Input
    dont_consider = fields.Boolean(
        'Don not Consider?',
    )
    input_state = fields.Selection(
        [('done', 'Finished '),
         ('skip', 'Not Finished')],
        'Status',
        readonly=True,
    )
    group_id = fields.Many2one(
        'academic.group',
        'Group',
        readonly=True,
    )
    course_level_id = fields.Many2one(
        'academic.level',
        'Course Level',
        readonly=True,
    )
    partner_id = fields.Many2one(
        'res.partner',
        'Partner',
        readonly=True,
    )
    company_id = fields.Many2one(
        'res.company',
        'Company',
        readonly=True,
    )
    avg_score = fields.Float(
        'Avg Score',
        readonly=True,
        group_operator='avg',
    )
    min_score = fields.Float(
        'Min Score',
        readonly=True,
        group_operator='min',
    )
    max_score = fields.Float(
        'Max Score',
        readonly=True,
        group_operator='max',
    )

    def init(self):
        tools.drop_view_if_exists(self._cr, 'academic_evaluation_analysis')
        self._cr.execute("""
            create or replace view academic_evaluation_analysis as (
SELECT
        survey_user_input_question_score.id as id,
        survey_user_input.score as avg_score,
        survey_user_input.score as min_score,
        survey_user_input.score as max_score,
        survey_user_input.survey_id as survey_id,
        survey_user_input.partner_id as partner_id,
        survey_user_input.state as input_state,
        academic_observation_category.dont_consider as dont_consider,
        academic_group_evaluation.group_id as group_id,
        academic_group.level_id as course_level_id,
        academic_group_evaluation.state as group_evaluation_state,
        academic_group.company_id,
        res_partner.disabled_person as disabled_person,
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
    LEFT JOIN academic_observation_category
    on survey_user_input.observation_category_id =
     academic_observation_category.id
    INNER JOIN res_partner
    on survey_user_input.partner_id = res_partner.id
    LEFT JOIN academic_level
    on academic_group.level_id = academic_level.id)
        """)
