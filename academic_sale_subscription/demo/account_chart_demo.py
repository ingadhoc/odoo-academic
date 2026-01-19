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

    @api.model
    def _get_demo_data_move(self, company=False):
        data = super()._get_demo_data_move(company)

        if company.account_fiscal_country_id.code == "AR":
            # Only set document numbers if the invoices exist in the data
            # (they won't exist for branch companies where we skip demo data loading)
            if "demo_invoice_8" in data:
                data["demo_invoice_8"]["l10n_latam_document_number"] = "1-1"
            if "demo_invoice_equipment_purchase" in data:
                data["demo_invoice_equipment_purchase"]["l10n_latam_document_number"] = "1-2"
            if "demo_move_auto_reconcile_3" in data:
                data["demo_move_auto_reconcile_3"]["l10n_latam_document_number"] = "1-3"
            if "demo_move_auto_reconcile_4" in data:
                data["demo_move_auto_reconcile_4"]["l10n_latam_document_number"] = "1-4"
        return data
