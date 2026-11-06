from odoo import api, models


class AccountChartTemplate(models.AbstractModel):
    _inherit = "account.chart.template"

    @api.model
    def _install_demo(self, companies):
        # Do not load generic demo data on the academic company: the standard
        # Odoo invoices may come with a missing account_id.
        if not isinstance(companies, models.BaseModel):
            companies = self.env["res.company"].browse(companies)
        academic_company = self.env.ref("academic.res_company_los_arroyos", raise_if_not_found=False)
        if academic_company:
            companies -= academic_company
        return super()._install_demo(companies)
