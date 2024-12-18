from odoo import models, api


class BaseLanguageInstall(models.TransientModel):
    _inherit = "base.language.install"

    @api.model
    def _init_demo_base(self):
        lang_ids = self.env['res.lang'].with_context(active_test=False).search([('code', 'in', ['es_AR', 'es_UY', 'es_CL'])]).ids
        installer = self.env['base.language.install'].create({'lang_ids': [(6, 0, lang_ids)]})
        installer.lang_install()
        for company in self.env['res.company'].search([('id', '!=', self.env.ref('base.main_company').id)]):
            self.env['ir.default'].set('res.partner', 'lang', 'es_AR', company_id = company.id)
        self.env['res.partner'].with_context(active_test=False).search(
            [('id', 'not in', [self.env.ref('base.partner_root').id])]).write({'lang': 'es_AR'})
