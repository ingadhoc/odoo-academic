# -*- coding: utf-8 -*-

import re
from openerp import netsvc
from openerp.osv import osv, fields

class observation_category(osv.osv):
    """"""
    
    _name = 'academic.observation_category'
    _description = 'observation_category'



    _columns = {
        'name': fields.char(string='Name', required=True, translate=True),
        'dont_consider': fields.boolean(string='Don not Consider?'),
    }

    _defaults = {
    }


    _constraints = [
    ]




observation_category()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
