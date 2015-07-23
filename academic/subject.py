# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, api, _
from openerp.exceptions import Warning


class subject(models.Model):
    """"""

    _name = 'academic.subject'
    _description = 'subject'

    name = fields.Char(
        string='Name',
        required=True,
        translate=True
        )
    group_ids = fields.One2many(
        'academic.group',
        'subject_id',
        string='Groups'
        )

    _constraints = [
    ]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
