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
    'author': 'ADHOC SA',
    'category': 'Tools',
    'data': [
        'view/project_view.xml',
        'view/academic_menuitem.xml',
        'view/res_company.xml',
        'view/website_page_view.xml',
        'view/res_partner_view.xml',
        'security/ir.model.access.csv',

    ],
    'depends': [
        'academic',
        'website_security',
    ],
    'demo': [],
    'installable': False,
    'license': 'AGPL-3',
    'name': 'Academic Content',
    'test': [],
    'version': '11.0.1.1.0',
}
