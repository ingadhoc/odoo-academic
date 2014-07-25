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

class survey_user_input(osv.Model):

	_inherit = 'survey.user_input'


	_columns = {
		'company_id': fields.related('group_evaluation_id', 'group_id','company_id',type='many2one',relation='res.company',string='Company', store=True, readonly=True),
		'group_id': fields.related('group_evaluation_id','group_id',type='many2one',relation='academic.group',string='Group', store=True, readonly=True),		
	}

	def force_closure(self, cr, uid, ids, context=None):
		for record in self.browse(cr, uid, ids, context=context):
			if not record.observation_category_id or not record.observation_category_id.name:
				raise osv.except_osv(_('Error!'), _("You can not force closure if you not set an observation category."))
		return self.write(cr, uid, ids, {'state':'done'}, context=context)

	def action_answer_survey(self, cr, uid, ids, context=None):
		''' Open the website page with the survey form into test mode'''
		user_input = self.browse(cr, uid, ids, context=context)[0]
		url = user_input.survey_id.public_url + '/' + user_input.token
		return {
			'type': 'ir.actions.act_url',
			'name': "Evaluation",
			'target': 'self',
			'url': url,
		}
