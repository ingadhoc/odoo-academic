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

class survey(osv.osv):
    """"""
    
    _name = 'survey.survey'
    _inherits = {  }
    _inherit = [ 'survey.survey' ]

    _columns = {
        'apply_to': fields.selection([(u'student', u'Student'), (u'teacher', u'Teacher'), (u'administrator', u'Administrator')], string='Apply to'),
        'answered_by': fields.selection([(u'student', u'Student'), (u'teacher', u'Teacher'), (u'administrator', u'Administrator')], string='Answered By'),
        'level_id': fields.many2one('academic.level', string='Level'),
        'subject_id': fields.many2one('academic.subject', string='Subject'),
        'checked_by': fields.selection([(u'student', u'Student'), (u'teacher', u'Teacher'), (u'administrator', u'Administrator')], string='Checked By'),
        'evaluation_subtype': fields.selection([(u'student_evaluation', u'Student Evaluation'), (u'poll_survey', u'Poll Survey')], string='Subtype'),
        'period_id': fields.many2one('academic.period', string='period_id'),
        'is_diagnosis': fields.boolean(string='Is Diagnosis?'),
        'group_evaluation_ids': fields.one2many('academic.group_evaluation', 'survey_id', string='Groups', context={'from_survey':True}), 
        'level_ids': fields.many2many('academic.level', 'academic_survey_ids_level_ids_rel', 'survey_id', 'level_id', string='Levels'), 
        'subject_ids': fields.many2many('academic.subject', 'academic_survey_ids_subject_ids_rel', 'survey_id', 'subject_id', string='Subjects'), 
    }

    _defaults = {
    }


    _constraints = [
    ]




survey()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
