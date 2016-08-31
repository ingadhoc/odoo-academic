# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning


class ResPartner(models.Model):
    _inherit = 'res.partner'

    academic_project_ids = fields.Many2many(
        related='company_id.academic_project_ids',
        store=True,
    )
