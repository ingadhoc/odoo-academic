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
from datetime import datetime
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
import uuid

class group_evaluation(osv.osv):
    """"""
    
    _inherit = 'academic.group_evaluation'

    def _get_time_used(self, cr, uid, ids, names, arg, context=None):
        res = {}
        for record in self.browse(cr, uid, ids, context=context):
            if record.date_open:
                date_open = datetime.strptime(record.date_open, DEFAULT_SERVER_DATETIME_FORMAT)            
            if record.date_close:
                date_close = datetime.strptime(record.date_close, DEFAULT_SERVER_DATETIME_FORMAT)
            time_used = False
            if date_open and date_close:
                time_used = date_close - date_open
                res[record.id] = time_used
        return res

    _columns = {
        'company_id': fields.related('group_id','company_id',type='many2one',relation='res.company',string='Company', store=False, readonly=True),
        # 'answered_by': fields.related('survey_id','answered_by', type='selection', selection=[(u'student', 'student'), (u'teacher', 'teacher'), (u'administrator', 'administrator')], string='Answered by', store=True, readonly=True),
        # 'apply_to': fields.related('survey_id','apply_to', type='selection', selection=[(u'student', 'student'), (u'teacher', 'teacher'), (u'administrator', 'administrator')], string='Appy To', store=True, readonly=True),
        'time_used': fields.function(_get_time_used, string='Time Used', type='float', ),
    }

    _sql_constraints = [
        ('group_uniq', 'unique(group_id, survey_id)', 'There can not be two groups for the same evaluation.'),
    ]    

    def set_invisible(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'invisible'}, context=context)

    def set_visible(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'visible'}, context=context)

    def set_closed(self, cr, uid, ids, context=None):
        # for record in self.browse(cr, uid, ids, context=context):
        if isinstance(ids, (int, long)):
            ids = [ids]
        user_input_obj = self.pool['survey.user_input']
        user_input_ids = user_input_obj.search(cr, uid, [('group_evaluation_id','in',ids)], context=context)
        for user_input_state in user_input_obj.read(cr, uid, user_input_ids, ['state']):
            if user_input_state['state'] != 'done':
                raise osv.except_osv(_('Error!'), _("You can not close a Group Evaluation with user inputs not done. First you should close each user input."))
        return self.write(cr, uid, ids, {'state':'closed','date_close':datetime.now()}, context=context)       

    def print_users(self, cr, uid, ids, context=None):
        '''
        This function prints a report with users login and password. 
        '''
        # TODO: print students, teachers or administrators depending on the type of evaluation group
        
        assert len(ids) == 1, 'This option should only be used for a single id at a time'
        print 'ids', ids
        group_ids = [self.browse(cr, uid, ids[0], context=context).group_id.id]
        print 'group_ids', group_ids
        self.pool['academic.group'].create_students_users(cr, uid, group_ids, context=context)        
        # return self.pool['report'].get_action(cr, uid, group_ids, 'academic_x.template_group_ev_report_users', context=context)
        return self.pool['report'].get_action(cr, uid, ids, 'academic_x.template_group_ev_report_users', context=context)

    def action_send_survey(self, cr, uid, ids, context=None):
        survey_response_obj = self.pool.get('survey.user_input')
        partner_obj = self.pool['res.partner']
                
        def create_response(survey_id, answered_by, apply_to, group_evaluation_id):
            response_ids = survey_response_obj.search(cr, uid, [
                ('survey_id', '=', survey_id),
                ('partner_id', '=', answered_by),
                ('apply_to_id', '=', apply_to),
                ('group_evaluation_id', '=', group_evaluation_id),
                ], context=context)
            if not response_ids:
                token = uuid.uuid4().__str__()
                return survey_response_obj.create(cr, uid, {
                    'survey_id': survey_id,
                    'date_create': datetime.now(),
                    'type': 'link',
                    'state': 'new',
                    'token': token,
                    'partner_id': answered_by,
                    'apply_to_id': apply_to,
                    'group_evaluation_id': group_evaluation_id})
            return False

        for group_evaluation in self.browse(cr, uid, ids, context=context):
            survey_id = group_evaluation.survey_id.id
            # group_id = group_evaluation.group_id.id
            group_evaluation_id = group_evaluation.id
            administrator_ids = partner_obj.search(cr, uid, [
                ('partner_type','=','administrator'),
                ('company_id','=',group_evaluation.group_id.company_id.id),
                ('section_id','=',group_evaluation.group_id.level_id.section_id.id),
                ], context=context)

            if group_evaluation.survey_id.apply_to == 'teacher':
                apply_to = group_evaluation.group_id.teacher_id.id
            elif group_evaluation.survey_id.apply_to == 'administrator':
                if not administrator_ids:
                    raise osv.except_osv(_('Error!'), _('There is no administrator set up for ' + group_evaluation.group_id.company_id.name))
                apply_to = administrator_ids[0]
            else:
                apply_to = False                
            
            if group_evaluation.survey_id.answered_by == 'teacher':
                answered_by = group_evaluation.group_id.teacher_id.id
            elif group_evaluation.survey_id.answered_by == 'administrator':
                if not administrator_ids:
                    raise osv.except_osv(_('Error!'), _('There is no administrator set up for ' + group_evaluation.group_id.company_id.name))
                answered_by = administrator_ids[0]
            else:
                answered_by = False

            if group_evaluation.survey_id.apply_to == 'student' or group_evaluation.survey_id.answered_by == 'student':
            # if group_evaluation.survey_id.answered_by == 'student':               
                for student in group_evaluation.group_id.student_ids:
                    if group_evaluation.survey_id.apply_to == 'student':
                        apply_to = student.id
                    if group_evaluation.survey_id.answered_by == 'student':
                        answered_by = student.id                   
                    create_response(survey_id,
                                    answered_by, 
                                    apply_to,
                                    group_evaluation_id)
            else:
                create_response(survey_id,
                                answered_by, 
                                apply_to,
                                group_evaluation_id)
        self.write(cr, uid, ids, {'state':'open','date_open':datetime.now()}, context=context)
        return True
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
