# -*- coding: utf-8 -*-

import re
from openerp import netsvc
from openerp.osv import osv, fields

class promotion(osv.osv):
    """"""
    
    _name = 'academic.promotion'
    _description = 'promotion'



    _columns = {
        'name': fields.char(string='Name', required=True),
    }

    _defaults = {
    }


    _constraints = [
    ]




promotion()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
