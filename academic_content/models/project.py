from odoo import models, fields


class AcademicProject(models.Model):

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
    website_page_ids = fields.One2many(
        'website.page',
        'academic_project_id',
        string='Website Pages',
    )
