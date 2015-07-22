# -*- coding: utf-8 -*-

import re
from openerp import netsvc
from openerp.osv import osv, fields

class group_evaluation(osv.osv):
    """"""
    
    _name = 'academic.group_evaluation'
    _description = 'group_evaluation'
    _inherits = {  }
    _inherit = [ 'mail.thread' ]

    _track = {
    }


    _columns = {
        'date_open': fields.datetime(string='Date Open', readonly=True),
        'date_close': fields.datetime(string='Date Close', readonly=True),
        'observation': fields.text(string='Observations', states={'closed':[('readonly',True)]}),
        'contingencies': fields.boolean(string='Contingencies?', states={'closed':[('readonly',True)]}),
        'state': fields.selection([(u'invisible', u'Invisible'), (u'visible', u'Visible'), (u'open', u'Open'), (u'closed', u'Closed')], string='State', readonly=True, required=True),
        'group_id': fields.many2one('academic.group', string='Group', readonly=True, required=True, states={'invisible':[('readonly',False)]}, ondelete='cascade'), 
        'survey_id': fields.many2one('survey.survey', string='Evaluation', readonly=True, required=True, states={'invisible':[('readonly',False)]}, context={'default_is_evaluation':True}, domain=[('is_evaluation','=',True)], ondelete='cascade'), 
        'user_input_ids': fields.one2many('survey.user_input', 'group_evaluation_id', string='Users Inputs', states={'closed':[('readonly',True)]}), 
    }

    _defaults = {
        'state': 'invisible',
        'group_id': lambda self, cr, uid, context=None: context and context.get('group_id', False),
        'survey_id': lambda self, cr, uid, context=None: context and context.get('survey_id', False),
    }


    _constraints = [
    ]




group_evaluation()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
