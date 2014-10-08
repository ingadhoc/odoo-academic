# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-TODAY OpenERP S.A. <http://www.openerp.com>
#
#    This program is free software: you can redistribute it and / or modify
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

from openerp.osv import fields, osv
from openerp.tools.translate import _


class survey_page(osv.Model):
    _inherit = 'survey.page'

    def get_user_input(self, cr, uid, ids, token, context=None):
        user_input_obj = self.pool['survey.user_input']
        user_input_ids = user_input_obj.search(
            cr, uid, [('token', '=', token)], context=context)
        if user_input_ids:
            return user_input_obj.browse(cr, uid, user_input_ids[0], context=context)
        return False


class survey_survey(osv.Model):

    _inherit = 'survey.survey'

    _columns = {
        # 'group_id': fields.many2one('academic.group',string='Group', ),
        # 'apply_to': fields.selection([(u'student', 'student'), (u'teacher', 'teacher'), (u'administrator', 'administrator')], string='Apply To'),
        # 'answered_by': fields.selection([(u'student', 'student'), (u'teacher', 'teacher'), (u'administrator', 'administrator')], string='Answered by'),
    }

    def get_user_input(self, cr, uid, ids, token, context=None):
        user_input_obj = self.pool['survey.user_input']
        user_input_ids = user_input_obj.search(
            cr, uid, [('token', '=', token)], context=context)
        if user_input_ids:
            return user_input_obj.browse(cr, uid, user_input_ids[0], context=context)
        return False

    def set_invisible(self, cr, uid, ids, context=None):
        group_evaluation_obj = self.pool['academic.group_evaluation']
        group_evaluation_ids = group_evaluation_obj.search(
            cr, uid, [('survey_id', 'in', ids)], context=context)
        return group_evaluation_obj.set_invisible(cr, uid, group_evaluation_ids, context=context)

    def set_visible(self, cr, uid, ids, context=None):
        group_evaluation_obj = self.pool['academic.group_evaluation']
        group_evaluation_ids = group_evaluation_obj.search(
            cr, uid, [('survey_id', 'in', ids)], context=context)
        return group_evaluation_obj.set_visible(cr, uid, group_evaluation_ids, context=context)

    def set_closed(self, cr, uid, ids, context=None):
        group_evaluation_obj = self.pool['academic.group_evaluation']
        group_evaluation_ids = group_evaluation_obj.search(
            cr, uid, [('survey_id', 'in', ids)], context=context)
        return group_evaluation_obj.set_closed(cr, uid, group_evaluation_ids, context=context)

    def action_send_survey(self, cr, uid, ids, context=None):
        group_evaluation_obj = self.pool['academic.group_evaluation']
        group_evaluation_ids = group_evaluation_obj.search(
            cr, uid, [('survey_id', 'in', ids)], context=context)
        return group_evaluation_obj.action_send_survey(cr, uid, group_evaluation_ids, context=context)

    def autom_add_groups(self, cr, uid, ids, context=None):
        new_record_ids = []
        for survey in self.read(cr, uid, ids, ['level_ids', 'subject_ids'], context=context):
            level_ids = survey.get('level_ids', False)
            subject_ids = survey.get('subject_ids', False)
            survey_id = survey.get('id', False)
            if not level_ids or not subject_ids:
                raise osv.except_osv(_('Atuomatically Add Groups Error!'), _(
                    'To auotmatically add Groups you should set level and subject!'))
            group_ids = self.pool['academic.group'].search(cr, uid, [(
                'level_id', 'in', level_ids), ('subject_id', 'in', subject_ids)], context=context)
            survey = self.browse(cr, uid, survey_id, context=context)
            actual_group_ids = [
                x.group_id.id for x in survey.group_evaluation_ids]
            new_group_ids = list(set(group_ids) - set(actual_group_ids))
            for i in new_group_ids:
                new_record_ids.append(self.pool['academic.group_evaluation'].create(cr, uid, {
                    'survey_id': survey.id,
                    'group_id': i,
                }, context=context))
        return new_record_ids


class survey_question_performance(osv.Model):

    _name = 'survey.question.performance'
    _description = 'Question Performance'

    _columns = {
        'name': fields.char(string="Name", required=True, translate=True),
        'variable_ids': fields.one2many('survey.question.variable', 'performance_id', string="Variables",),
    }


class survey_question_variable(osv.Model):

    _name = 'survey.question.variable'
    _description = 'Question Variable'

    _columns = {
        'name': fields.char(string="Name", required=True, translate=True),
        'performance_id': fields.many2one('survey.question.performance', string="Performance", required=True,),
        'indicator_ids': fields.one2many('survey.question.indicator', 'variable_id', string="Indicators",),
    }


class survey_question_indicator(osv.Model):

    _name = 'survey.question.indicator'
    _description = 'Question Indicator'

    _columns = {
        'name': fields.char(string="Name", required=True, translate=True),
        'calc_type': fields.selection([('group_average', 'Group Average'), ('group_max', 'Group Max Value')], string="Calculation Type", required=True,),
        'variable_id': fields.many2one('survey.question.variable', string="Variable", required=True,),
        'question_ids': fields.one2many('survey.question', 'indicator_id', string="Questions",),
    }

    _defaults = {
        'calc_type': 'group_average',
    }


class survey_question(osv.Model):

    _inherit = 'survey.question'

    _columns = {
        'indicator_id': fields.many2one('survey.question.indicator', string='Indicator', ),
    }
