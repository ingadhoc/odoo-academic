# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, api, _
from openerp.exceptions import Warning


class partner(models.Model):
    """"""

    _name = 'res.partner'
    _inherits = {}
    _inherit = ['res.partner']

    partner_type = fields.Selection(
        [(u'student', u'Student'), (u'teacher', u'Teacher'), (u'administrator', u'Administrator'), (u'gral_administrator', u'Gral. Administrator')],
        change_default=True,
        string='Partner Type'
        )
    section_id = fields.Many2one(
        'academic.section',
        string='Section'
        )
    promotion_id = fields.Many2one(
        'academic.promotion',
        string='Promotion'
        )
    teacher_group_ids = fields.One2many(
        'academic.group',
        'teacher_id',
        string='Groups'
        )
    student_group_ids = fields.Many2many(
        'academic.group',
        'academic_student_group_ids_student_ids_rel',
        'partner_id',
        'group_id',
        string='Groups'
        )

    _constraints = [
    ]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
