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
from openerp.osv import osv, fields

class group(osv.osv):
    """"""
    
    _name = 'academic.group'
    _description = 'group'

    _columns = {
        'type': fields.selection([(u'student', u'Student'), (u'teacher', u'Teacher'), (u'administrator', u'Administrator')], string='type'),
        'year': fields.integer(string='Year', required=True),
        'division_id': fields.many2one('academic.division', string='Division'),
        'company_id': fields.many2one('res.company', string='Company', required=True, context={'default_is_company':True}),
        'level_id': fields.many2one('academic.level', string='Level', required=True), 
        'subject_id': fields.many2one('academic.subject', string='Subject', required=True), 
        'teacher_id': fields.many2one('res.partner', string='Teacher', required=True, context={'default_partner_type':'teacher'}, domain=[('partner_type','=','teacher')]), 
        'student_ids': fields.many2many('res.partner', 'academic_student_group_ids_student_ids_rel', 'group_id', 'partner_id', string='Student', context={'default_partner_type':'student'}, domain=[('partner_type','=','student')]), 
        'group_evaluation_ids': fields.one2many('academic.group_evaluation', 'group_id', string='Evaluations', context={'from_group':True}), 
    }

    _defaults = {
        'company_id': lambda s, cr, uid, c: s.pool.get('res.company')._company_default_get(cr, uid, 'academic.group', context=c),
    }


    _constraints = [
    ]




group()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
