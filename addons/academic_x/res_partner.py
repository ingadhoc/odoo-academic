# -*- coding: utf-8 -*-
##############################################################################
#
#    Academic
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


import re
from openerp import netsvc
from openerp.osv import osv
# from openerp.osv import osv, fields
from openerp import fields

class partner(osv.osv):
    """"""
    
    _inherit = 'res.partner'

    partner_type = fields.Selection([(u'student', u'Student'), (u'teacher', u'Teacher'), (u'administrator', u'Administrator'),], string='partner_type', change_default=True,)
    # Estos tres campos no existen mas, si se quieren tendria que ir en res.company
    # administrator_ids = fields.One2many('res.partner','company_id', string='Administrators', domain=[('partner_type','=','administrator')], context={'default_partner_type':'administrator'},)
    # teacher_ids = fields.One2many('res.partner','company_id', string='Teachers', domain=[('partner_type','=','teacher')], context={'default_partner_type':'teacher'},)
    # student_ids = fields.One2many('res.partner','company_id', string='Students', domain=[('partner_type','=','student')], context={'default_partner_type':'student'},)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
