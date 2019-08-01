from odoo import fields, models, api


class Page(models.Model):
    _inherit = "website.page"

    academic_project_id = fields.Many2one(
        'academic.project',
        string='Project',
    )

    @api.one
    def _compute_visible(self):
        user = self.env['res.users'].browse(
            self._context.get('uid', False)) or self.env.user
        self.is_visible = self.website_published and (
            not self.date_publish
            or self.date_publish < fields.Datetime.now()) and (
            not self.groups_id
            or user.groups_id & self.groups_id) and (
                not self.academic_project_id or
            user.company_id & self.academic_project_id.
            academic_project_company_ids)
