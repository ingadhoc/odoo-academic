# -*- coding: utf-8 -*-
from openerp import models, fields
# from openerp.exceptions import Warning


class company(models.Model):

    _inherit = 'res.company'

    academic_project_ids = fields.Many2many(
        'academic.project',
        'academic_project_company_ids_company_ids_rel',
        'company_id',
        'academic_project_id',
        string='Projects'
    )
