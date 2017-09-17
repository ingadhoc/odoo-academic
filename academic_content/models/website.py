# -*- coding: utf-8 -*-
from openerp import fields, models


class website_menu(models.Model):
    _inherit = "website.menu"

    academic_project_id = fields.Many2one(
        'academic.project',
        string='Project',
    )
