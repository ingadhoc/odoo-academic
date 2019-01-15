from odoo import fields, models


class WebsiteMenu(models.Model):
    _inherit = "website.menu"

    academic_project_id = fields.Many2one(
        'academic.project',
        string='Project',
    )
