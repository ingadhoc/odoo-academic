# -*- coding: utf-8 -*-
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
    'author': 'ADHOC SA.',
    'category': 'Tools',
    'data': [
        'security/academic_group.xml',
        'view/division_view.xml',
        'view/group_view.xml',
        'view/level_view.xml',
        'view/section_view.xml',
        'view/partner_view.xml',
        'view/promotion_view.xml',
        'view/subject_view.xml',
        'security/ir.model.access.csv',
        'security/security.xml',
        'view/academic_menuitem.xml',
        'view/res_company.xml',
        'view/res_users_view.xml',
    ],
    'depends': [
        'base',
    ],
    'demo': [
        'demo/academic.subject.csv',
        'demo/academic.promotion.csv',
        'demo/academic.section.csv',
        'demo/academic.level.csv',
        'demo/res.partner.csv',
        'demo/res_company.xml',
        'demo/images/res_partner.xml',
        'demo/res_users.xml',
        'demo/academic.group.csv',
    ],
    'description': 'Academic',
    'installable': True,
    'license': 'AGPL-3',
    'name': 'Academic',
    'version': '9.0.1.2.0',
    'website': 'www.adhoc.com.ar'
}
