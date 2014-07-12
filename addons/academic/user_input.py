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
