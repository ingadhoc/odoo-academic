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


{   
    'author': 'Sistemas ADHOC',
    'auto_install': True,
    'installable': True,
    'category': 'Tools',
    'demo': [
        'data/demo/res_users.xml',
        'data/demo/res.partner.csv',
        ],
    'depends': ['portal', 'academic_x'],
    'description': 'Academic Portal',
    'init_xml': [],
    'license': 'AGPL-3',
    'name': u'Academic Portal',
    'test': [],
    'data': [   
        'security/portal_academic_security.xml',
        'security/ir.model.access.csv',
        'data/data.xml',
        'portal_evaluation_view.xml',
    ],
    'version': '8.0.1.2.0',
    'website': ''}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
