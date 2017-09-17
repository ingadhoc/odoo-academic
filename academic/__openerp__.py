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
    'category': u'base.module_category_knowledge_management',
    'data': [   u'security/academic_group.xml',
                u'view/division_view.xml',
                u'view/group_view.xml',
                u'view/level_view.xml',
                u'view/section_view.xml',
                u'view/partner_view.xml',
                u'view/promotion_view.xml',
                u'view/subject_view.xml',
                u'data/division_properties.xml',
                u'data/group_properties.xml',
                u'data/level_properties.xml',
                u'data/section_properties.xml',
                u'data/partner_properties.xml',
                u'data/promotion_properties.xml',
                u'data/subject_properties.xml',
                u'data/division_track.xml',
                u'data/group_track.xml',
                u'data/level_track.xml',
                u'data/section_track.xml',
                u'data/partner_track.xml',
                u'data/promotion_track.xml',
                u'data/subject_track.xml',
                # 'view/report_users.xml',
                # 'report/report_users.xml',
                'security/ir.model.access.csv',
                'security/security.xml',
                u'view/academic_menuitem.xml',
                'view/res_company.xml',
                u'view/academic_actions.xml'],
    'depends': [
        'base',
        'partner_person',
        ],
    'demo': [
        'data/demo/academic.subject.csv',
        'data/demo/academic.promotion.csv',
        'data/demo/academic.section.csv',
        'data/demo/academic.level.csv',
        'data/demo/res.partner.csv',
        'data/demo/res_company.xml',
        'data/demo/images/res_partner.xml',
        'data/demo/res_users.xml',
        'data/demo/academic.group.csv',
        ],
    'description': u'Academic',
    'installable': False,
    'license': 'AGPL-3',
    'name': u'Academic',
    'test': [],
    'version': '8.0.0.1.0',
    'website': 'www.adhoc.com.ar'}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
