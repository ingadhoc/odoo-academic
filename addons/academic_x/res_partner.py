# -*- coding: utf-8 -*-
from openerp import fields, models


class partner(models.Model):

    """"""
    _inherit = 'res.partner'

    partner_type = fields.Selection([(u'student', u'Student'), (u'teacher', u'Teacher'), (
        u'administrator', u'Administrator'),(u'gral_administrator', u'Gral. Administrator'), ], string='partner_type', change_default=True,)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
