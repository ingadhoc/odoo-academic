# -*- coding: utf-8 -*-

import re
from openerp import netsvc
from openerp.osv import osv, fields

class subject(osv.osv):
    """"""
    
    _name = 'academic.subject'
    _description = 'subject'



    _columns = {
        'name': fields.char(string='Name', required=True, translate=True),
        'group_ids': fields.one2many('academic.group', 'subject_id', string='Groups'), 
        'survey_ids': fields.many2many('survey.survey', 'academic_survey_ids_subject_ids_rel', 'subject_id', 'survey_id', string='Surveys'), 
    }

    _defaults = {
    }


    _constraints = [
    ]




subject()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
