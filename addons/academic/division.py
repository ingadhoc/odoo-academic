# -*- coding: utf-8 -*-

import re
from openerp import netsvc
from openerp.osv import osv, fields

class division(osv.osv):
    """"""
    
    _name = 'academic.division'
    _description = 'division'



    _columns = {
        'name': fields.char(string='Name', required=True),
    }

    _defaults = {
    }


    _constraints = [
    ]




division()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
