# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning


class level(models.Model):
    """"""

    _name = 'academic.level'
    _description = 'level'

    name = fields.Char(
        string='Name',
        required=True,
        translate=True
        )
    section_id = fields.Many2one(
        'academic.section',
        string='Section',
        required=True
        )
    group_ids = fields.One2many(
        'academic.group',
        'level_id',
        string='Groups'
        )

    _constraints = [
    ]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
