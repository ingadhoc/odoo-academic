# -*- coding: utf-8 -*-
##############################################################################
#
#    School
#    Copyright (C) 2014 No author.
#    No email
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


{   'active': False,
    'author': 'Sistemas ADHOC',
    'category': 'base.module_category_knowledge_management',
    'demo': [
        'data/demo/academic.subject.csv',
        'data/demo/academic.promotion.csv',
        'data/demo/academic.section.csv',
        'data/demo/academic.level.csv',
        'data/demo/academic.observation_category.csv',
        'data/demo/res.partner.csv',
        'data/demo/res_company.xml',
        'data/demo/images/res_partner.xml',
        'data/demo/res_users.xml',
        'data/demo/academic.group.csv',
        'data/demo/evaluation/survey.survey.csv',
        'data/demo/evaluation/survey.page.csv',
        'data/demo/evaluation/survey.question.objective.csv',
        'data/demo/evaluation/survey.question.level.csv',
        'data/demo/evaluation/survey.objective.csv',
        'data/demo/evaluation/survey.question.csv',
        'data/demo/evaluation/survey.label.csv',
        'data/demo/evaluation/survey.matrix_answer_score.csv',
        # TODO: llevar las imagenes de una manera en que si las levante
        # 'data/demo/evaluation/ir.attachment.csv',
        ],
    'depends': [
        'academic',
        'evaluation',
        'partner_user',
        'partner_person',
        ],
    'description': 'Academic General Modifications',
    'init_xml': [],
    'installable': True,
    'license': 'AGPL-3',
    'name': u'Academic General Modifications',
    'test': [],
    'qweb': [
        ],
    'data': [   
        'view/partner_view.xml',
        'view/group_view.xml',
        'view/survey_view.xml',
        'view/group_evaluation_view.xml',
        'view/user_input_view.xml',
        'view/survey_indicator_view.xml',
        'security/ir.model.access.csv',
        'security/security.xml',
        'report/report_users.xml',
        'report/group_evaluation_report_users.xml',
        'view/res_company.xml',
        'view/survey_templates.xml',
    ],
    'version': '1.1',
    'website': ''}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
