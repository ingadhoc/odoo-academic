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
    'version': '13.0.1.8.0',
    'sequence': 14,
    'summary': '',
    'author': 'ADHOC SA',
    'website': 'www.adhoc.com.ar',
    'license': 'AGPL-3',
    'images': [
    ],
    'depends': [
        'portal_backend',
        'board',
        'hr',
        'website',
        'board',
        'sale_management',
        'account',
    ],
    'data': [
        'security/academic_security.xml',
        'security/ir.model.access.csv',
        'views/academic_menuitem.xml',
        'views/res_partner_views.xml',
        'views/academic_group_views.xml',
        'views/academic_division_views.xml',
        'views/academic_level_views.xml',
        'views/academic_study_plan_views.xml',
        'views/academic_promotion_views.xml',
        'views/academic_section_views.xml',
        'views/academic_subject_views.xml',
        'views/hr_views.xml',
        'views/res_company_views.xml',
        'views/res_users_views.xml',
        'views/login_page.xml',
        'data/academic_mail_template.xml',
        'data/res_users_data.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
