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
    'auto_install': False,
    'installable': True,
    'category': 'Tools',
    'demo': [
        ],
    'depends': ['base','survey','academic_x','web'],
    'description': 'Academic Fixes and Customizations',
    'init_xml': [],
    'license': 'AGPL-3',
    'name': u'Academic Fixes and Customizations',
    'test': [],
    'data': [   
        'security/security.xml',
        'data/mail.xml', 
        'views/login_page.xml',
        'security/ir.model.access.csv',
    ],
    'version': '8.0.1.1.0',
    'website': ''}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
