##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import api, models, fields, _
from odoo.exceptions import UserError


class SurveySurvey(models.Model):

    _inherit = 'survey.survey'

    apply_to = fields.Selection(
        [('student', 'Student'),
         ('teacher', 'Teacher'),
         ('administrator', 'Administrator')],
    )
    answered_by = fields.Selection(
        [('student', 'Student'),
         ('teacher', 'Teacher'),
         ('administrator', 'Administrator')],
    )
    level_id = fields.Many2one(
        'academic.level',
        string='Level',
    )
    subject_id = fields.Many2one(
        'academic.subject',
        string='Subject',
    )
    checked_by = fields.Selection(
        [('student', 'Student'),
         ('teacher', 'Teacher'),
         ('administrator', 'Administrator')],
    )
    evaluation_subtype = fields.Selection(
        [('student_evaluation', 'Student Evaluation'),
         ('poll_survey', 'Poll Survey')],
        string='Subtype',
    )
    period_id = fields.Many2one(
        'academic.period',
    )
    is_diagnosis = fields.Boolean(
        string='Is Diagnosis?',
    )
    group_evaluation_ids = fields.One2many(
        'academic.group_evaluation',
        'survey_id',
        string='Groups',
        context={'from_survey': True},
    )
    level_ids = fields.Many2many(
        'academic.level',
        'academic_survey_ids_level_ids_rel',
        'survey_id',
        'level_id',
        string='Levels',
    )
    subject_ids = fields.Many2many(
        'academic.subject',
        'academic_survey_ids_subject_ids_rel',
        'survey_id',
        'subject_id',
        string='Subjects',
    )
    # group_year': fields.Many2many(
    # 'academic.group',
    #  'academic_survey_ids_year_rel',
    #  'survey_id',
    #  'year',
    #  string='Years')
    group_year = fields.Integer(
        string='Year',
    )

    def get_user_input(self, token):
        user_input_obj = self.env['survey.user_input']
        user_input_ids = user_input_obj.search(
            [('token', '=', token)])
        if user_input_ids:
            return user_input_obj.browse(
                user_input_ids[0])
        return False

    def set_invisible(self):
        group_evaluation_obj = self.env['academic.group_evaluation']
        group_evaluation_ids = group_evaluation_obj.search(
            [('survey_id', 'in', self.ids)])
        group_evaluation_ids.set_invisible()

    def set_visible(self):
        group_evaluation_obj = self.env['academic.group_evaluation']
        group_evaluation_ids = group_evaluation_obj.search(
            [('survey_id', 'in', self.ids)])
        group_evaluation_ids.set_visible()

    def set_closed(self):
        group_evaluation_obj = self.env['academic.group_evaluation']
        group_evaluation_ids = group_evaluation_obj.search(
            [('survey_id', 'in', self.ids)])
        group_evaluation_ids.set_closed()

    def action_send_survey(self):
        group_evaluation_obj = self.env['academic.group_evaluation']
        group_evaluation_ids = group_evaluation_obj.search(
            [('survey_id', 'in', self.ids)])
        group_evaluation_ids.action_send_survey()

    def autom_add_groups(self):
        for survey in self.read(
                self.ids, ['level_ids', 'subject_ids', 'group_year'],
        ):
            level_ids = survey.get('level_ids', False)
            subject_ids = survey.get('subject_ids', False)
            survey_id = survey.get('id', False)
            group_year = survey.get('group_year', False)

            if not level_ids or not subject_ids:
                raise UserError(_(
                    'Automatically Add Groups Error!\n'
                    'To automatically add Groups you should set level,'
                    ' subject and year!'))
            group_ids = self.env['academic.group'].search(
                [('level_id', 'in', level_ids),
                 ('subject_id', 'in', subject_ids),
                 ('year', '=', group_year)],
            )
            survey = self.browse(survey_id)
            actual_group_ids = [x.group_id.id
                                for x in survey.group_evaluation_ids]
            new_group_ids = list(set(group_ids) - set(actual_group_ids))
            for i in new_group_ids:
                self.env['academic.group_evaluation'].create(
                    {'survey_id': survey.id,
                     'group_id': i,
                     })

    @api.multi
    def copy(self, default=None):
        new_survey_id = super(SurveySurvey, self).copy(default)
        question_obj = self.env['survey.question']
        question_ids = question_obj.search(
            [('page_id.survey_id', '=', new_survey_id)])
        question_obj._get_max_score(question_ids)
        return new_survey_id
