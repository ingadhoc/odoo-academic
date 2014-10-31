# -*- coding: utf-8 -*-

import re
from openerp import netsvc
from openerp.osv import osv, fields

class period(osv.osv):
    """"""
    
    _name = 'academic.period'
    _description = 'period'



    _columns = {
        'name': fields.char(string='Name', required=True),
        'year': fields.integer(string='Year', required=True),
    }

    _defaults = {
    }


    _constraints = [
    ]




period()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
