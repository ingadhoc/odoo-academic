# -*- coding: utf-8 -*-
from openerp import models, fields


class project(models.Model):
    """"""

    _name = 'academic.project'
    _description = 'Project'

    name = fields.Char(
        string='Name',
        required=True
        )
    academic_project_company_ids = fields.Many2many(
        'res.company',
        'academic_project_company_ids_company_ids_rel',
        'academic_project_id',
        'company_id',
        string='Companies'
        )
    website_menu_ids = fields.One2many(
        'website.menu',
        'academic_project_id',
        string='Website Menus',
        )
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
