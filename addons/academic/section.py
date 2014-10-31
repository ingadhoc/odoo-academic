# -*- coding: utf-8 -*-

import re
from openerp import netsvc
from openerp.osv import osv, fields

class section(osv.osv):
    """"""
    
    _name = 'academic.section'
    _description = 'section'



    _columns = {
        'name': fields.char(string='Name', required=True, translate=True),
    }

    _defaults = {
    }


    _constraints = [
    ]




section()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
