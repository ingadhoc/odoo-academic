# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning


class division(models.Model):
    """"""

    _name = 'academic.division'
    _description = 'division'

    name = fields.Char(
        string='Name',
        required=True
        )

    _constraints = [
    ]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
