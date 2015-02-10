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
    'demo_xml': [
        ],
    'depends': [
                'academic', 
                'disable_openerp_online',
                'academic_clean_views',
                'academic_fixes_and_customizations',
                # TODO: portal_academic deberia instalarse automaticamente
                # 'reports'????
                ],
    'description': 'Academic Project',
    'init_xml': [],
    'installable': True,
    'license': 'AGPL-3',
    'name': u'Academic Project',
    'test': [],
    'update_xml': [
        'data/academic_data.xml',   
    ],
    'version': '1.1',
    'application': True,
    'website': ''}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
