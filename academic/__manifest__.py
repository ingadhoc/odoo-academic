##############################################################################
#
#    Copyright (C) 2015  ADHOC SA  (http://www.adhoc.com.ar)
#    All Rights Reserved.
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
{
    'name': 'Academic',
    'version': '11.0.1.0.0',
    'sequence': 14,
    'summary': '',
    'author': 'ADHOC SA',
    'website': 'www.adhoc.com.ar',
    'license': 'AGPL-3',
    'images': [
    ],
    'depends': [
        'mail',
        'survey',
        'evaluation',
        'board',
        'decimal_precision',
    ],
    'data': [
        'security/academic_security.xml',
        'security/ir.model.access.csv',
        'views/academic_menuitem.xml',
        'views/res_partner_views.xml',
        'views/academic_group_views.xml',
        'views/academic_group_evaluation_views.xml',
        'views/survey_user_input_views.xml',
        'views/academic_division_views.xml',
        'views/academic_observation_category_views.xml',
        'views/academic_level_views.xml',
        'views/academic_period_views.xml',
        'views/survey_survey_views.xml',
        'views/academic_promotion_views.xml',
        'views/academic_section_views.xml',
        'views/academic_subject_views.xml',
        'views/res_company_views.xml',
        'views/survey_question_views.xml',
        'views/survey_question_indicator_views.xml',
        'views/survey_question_variable_views.xml',
        'views/survey_question_performance_views.xml',
        'views/login_page.xml',
        'views/res_user_template.xml',
        'report/division_analysis_views.xml',
        'report/evaluation_report_views.xml',
        'report/evaluation_analysis_views.xml',
        'report/group_evaluation_report_users.xml',
        'report/report_users.xml',
        'wizards/division_analysis_wizard_views.xml',
        'data/academic_data.xml',
        'data/academic_mail_template.xml',
    ],
    'demo': [
        'demo/academic.subject.csv',
        'demo/academic.promotion.csv',
        'demo/academic.section.csv',
        'demo/academic.level.csv',
        'demo/academic.observation_category.csv',
        'demo/res.partner.csv',
        'demo/res_partner_demo.xml',
        'demo/res_company_demo.xml',
        'demo/res_users_demo.xml',
        'demo/academic.group.csv',
        'demo/evaluation/survey.survey.csv',
        'demo/evaluation/survey.page.csv',
        'demo/evaluation/survey.question.objective.csv',
        'demo/evaluation/survey.question.level.csv',
        'demo/evaluation/survey.objective.csv',
        'demo/evaluation/survey.question.csv',
        'demo/evaluation/survey.label.csv',
        'demo/evaluation/survey.matrix_answer_score.csv',
        'demo/evaluation/survey.question.score.range.csv',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
