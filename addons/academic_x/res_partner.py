# -*- coding: utf-8 -*-
from openerp import fields, api, models

class partner(models.Model):
    """"""
    
    _inherit = 'res.partner'

    partner_type = fields.Selection([(u'student', u'Student'), (u'teacher', u'Teacher'), (u'administrator', u'Administrator'),], string='partner_type', change_default=True,)
    # Estos tres campos no existen mas, si se quieren tendria que ir en res.company
    # administrator_ids = fields.One2many('res.partner','company_id', string='Administrators', domain=[('partner_type','=','administrator')], context={'default_partner_type':'administrator'},)
    # teacher_ids = fields.One2many('res.partner','company_id', string='Teachers', domain=[('partner_type','=','teacher')], context={'default_partner_type':'teacher'},)
    # student_ids = fields.One2many('res.partner','company_id', string='Students', domain=[('partner_type','=','student')], context={'default_partner_type':'student'},)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
