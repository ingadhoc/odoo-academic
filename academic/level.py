# -*- coding: utf-8 -*-

import re
from openerp import netsvc
from openerp.osv import osv, fields

class level(osv.osv):
    """"""
    
    _name = 'academic.level'
    _description = 'level'



    _columns = {
        'name': fields.char(string='Name', required=True, translate=True),
        'section_id': fields.many2one('academic.section', string='Section', required=True),
        'group_ids': fields.one2many('academic.group', 'level_id', string='Groups'), 
        'survey_ids': fields.many2many('survey.survey', 'academic_survey_ids_level_ids_rel', 'level_id', 'survey_id', string='Surveys'), 
    }

    _defaults = {
    }


    _constraints = [
    ]




level()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
