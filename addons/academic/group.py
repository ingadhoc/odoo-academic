# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning


class group(models.Model):
    """"""

    _name = 'academic.group'
    _description = 'group'

    type = fields.Selection(
        [(u'student', u'Student'), (u'teacher', u'Teacher'), (u'administrator', u'Administrator'), (u'gral_administrator', u'Gral. Administrator')],
        string='type'
        )
    year = fields.Integer(
        string='Year',
        required=True
        )
    division_id = fields.Many2one(
        'academic.division',
        string='Division',
        copy=False
        )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        context={'default_is_company':True},
        default=lambda s, cr, uid, c: s.pool.get('res.company')._company_default_get(cr, uid, 'academic.group', context=c)
        )
    level_id = fields.Many2one(
        'academic.level',
        string='Level',
        required=True
        )
    subject_id = fields.Many2one(
        'academic.subject',
        string='Subject',
        required=True
        )
    teacher_id = fields.Many2one(
        'res.partner',
        string='Teacher',
        required=True,
        context={'default_partner_type':'teacher'},
        domain=[('partner_type','=','teacher')]
        )
    student_ids = fields.Many2many(
        'res.partner',
        'academic_student_group_ids_student_ids_rel',
        'group_id',
        'partner_id',
        string='Student',
        context={'default_partner_type':'student'},
        domain=[('partner_type','=','student')]
        )

    _constraints = [
    ]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
