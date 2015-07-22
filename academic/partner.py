# -*- coding: utf-8 -*-

import re
from openerp import netsvc
from openerp.osv import osv, fields

class partner(osv.osv):
    """"""
    
    _name = 'res.partner'
    _inherits = {  }
    _inherit = [ 'res.partner' ]



    _columns = {
        'partner_type': fields.selection([(u'student', u'Student'), (u'teacher', u'Teacher'), (u'administrator', u'Administrator'), (u'gral_administrator', 'gral_administrator')], string='Partner Type'),
        'section_id': fields.many2one('academic.section', string='Section'),
        'promotion_id': fields.many2one('academic.promotion', string='Promotion'),
        'teacher_group_ids': fields.one2many('academic.group', 'teacher_id', string='Groups'), 
        'student_group_ids': fields.many2many('academic.group', 'academic_student_group_ids_student_ids_rel', 'partner_id', 'group_id', string='Groups'), 
    }

    _defaults = {
    }


    _constraints = [
    ]




partner()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
