# -*- coding: utf-8 -*-

import re
from openerp import netsvc
from openerp.osv import osv, fields

class user_input(osv.osv):
    """"""
    
    _name = 'survey.user_input'
    _inherits = {  }
    _inherit = [ 'survey.user_input' ]



    _columns = {
        'apply_to_id': fields.many2one('res.partner', string='Apply To', readonly=True),
        'note': fields.text(string='Note', states={'done':[('readonly',True)]}),
        'observation_category_id': fields.many2one('academic.observation_category', string='Observation Category', states={'done':[('readonly',True)]}),
        'group_evaluation_id': fields.many2one('academic.group_evaluation', string='Group Evaluation', readonly=True), 
    }

    _defaults = {
    }


    _constraints = [
    ]




user_input()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
