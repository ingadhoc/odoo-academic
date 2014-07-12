# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

from openerp import tools
from openerp.osv import fields, osv

class academic_evaluation_report(osv.osv):
    _name = "academic.evaluation.report"
    _description = "Academic Evaluation Report"
    _auto = False
    # _rec_name = 'date'
    _columns = {
        'score': fields.float('Score', readonly=True, group_operator='avg', ),
        'min_score': fields.float('Min. Score', readonly=True, group_operator='min', ),
        'max_score': fields.float('Max. Score', readonly=True, group_operator='max', ),
        'is_evaluation': fields.boolean('Is Evaluation?', readonly=True, ),
        'survey_id' : fields.many2one('survey', 'Survey', readonly=True,),
        'date_create' : fields.datetime('Create Date', readonly=True, ),
        'user_id' : fields.many2one('res.users', 'User', readonly=True,),
        'state' : fields.selection([('done', 'Finished '),('skip', 'Not Finished')], \
                            'Status', readonly=True),        
        # 'title': fields.char('Survey Title', size=128, readonly=True, ),
        'date_open': fields.datetime('Survey Open Date', readonly=True, ),
        'date_close': fields.datetime('Survey Close Date', readonly=True, ),
        'survey_state': fields.selection([('open', 'Open'), ('cancel', 'Cancelled'),('close', 'Closed') ], 'Status', readonly=True, ),
        # 'responsible_id': fields.many2one('res.users', 'Responsible', help="User responsible for survey", readonly=True, ),
        # 'tot_start_survey': fields.integer("Total Started Survey", readonly=1),
        # 'tot_comp_survey': fields.integer("Total Completed Survey", readonly=1),
        # 'color': fields.integer('Color Index', readonly=True),
    }
    # _order = 'date desc'
        
        # Cosas que saque de la consulta
        # survey.title as title,
        # survey.responsible_id as responsible_id,

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'academic_evaluation_report')
        cr.execute("""
            create or replace view academic_evaluation_report as (
    SELECT
        survey_user_input.id as id,
        survey_user_input.score as score,
        survey_user_input.score as min_score,
        survey_user_input.score as max_score,
        survey_user_input.survey_id as survey_id,
        survey_user_input.date_create as date_create,
        survey_user_input.partner_id as user_id,
        survey_user_input.state as state,
        survey.is_evaluation as is_exam,
        survey.date_open as date_open, 
        survey.date_close as date_close,
        survey.state as survey_state, 
        survey.tot_start_survey as tot_start_survey,
        survey.tot_comp_survey as tot_comp_survey,
    FROM survey 
    INNER JOIN survey_user_input
        on survey.id = survey_user_input.survey_id
        )
        """)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
