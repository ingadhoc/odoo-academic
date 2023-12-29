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
    'version': "16.0.1.4.0",
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
        'contacts',
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
        'views/res_users_views.xml',
        'views/res_company_views.xml',
        'views/login_page.xml',
        'views/sale_order_views.xml',
        'views/res_partner_link_views.xml',
        'views/res_partner_relationship_views.xml',
        'data/res_users_data.xml',
        'data/res_partner_role_data.xml',
    ],
    'demo': [
        'demo/res_partner_relationship_demo.xml',
        'demo/res_partner_demo.xml',
        'demo/academic.subject.csv',
        'demo/academic.section.csv',
        'demo/academic.level.csv',
        'demo/academic.promotion.csv',
        'demo/res.partner.csv',
        'demo/res_company_demo.xml',
        'demo/res_users_demo.xml',
        'demo/academic.group.csv',
        'demo/res.partner.link.csv',
    ],
    'installable': False,
    'auto_install': False,
    'application': False,
}
