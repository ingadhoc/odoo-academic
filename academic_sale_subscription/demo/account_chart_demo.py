from odoo import api, models


class AccountChartTemplate(models.AbstractModel):
    _inherit = "account.chart.template"

    @api.model
    def _get_demo_data(self, company=False):
        demo_data = super()._get_demo_data(company)
        # Get academic company
        academic_company = self.env.ref("academic.res_company_los_arroyos", raise_if_not_found=False)

        if company == academic_company:
            # Do not load generic demo data on academic company
            # This prevents loading standard Odoo invoices that may have missing account_id
            return {}
        return demo_data

    def _post_load_demo_data(self, company=False):
        # Get academic company
        academic_company = self.env.ref("academic.res_company_los_arroyos", raise_if_not_found=False)

        if company == academic_company:
            # Skip generic demo data post-processing for academic company
            return

        return super()._post_load_demo_data(company)
