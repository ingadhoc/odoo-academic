# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, api, _
from openerp.exceptions import Warning


class section(models.Model):
    """"""

    _name = 'academic.section'
    _description = 'section'

    name = fields.Char(
        string='Name',
        required=True,
        translate=True
        )

    _constraints = [
    ]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
