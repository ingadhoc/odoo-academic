from odoo.addons.account.controllers.portal import PortalAccount
from odoo.http import request
from odoo.osv import expression


class PortalAccount(PortalAccount):
    def _prepare_my_invoices_values(
        self, page, date_begin, date_end, sortby, filterby, domain=None, url="/my/invoices"
    ):
        values = super()._prepare_my_invoices_values(page, date_begin, date_end, sortby, filterby, domain, url)
        domain = expression.AND(
            [
                domain or [],
                self._get_invoices_domain(),
            ]
        )
        searchbar_filters = self._get_account_searchbar_filters()
        if not filterby:
            filterby = "all"
        domain += searchbar_filters[filterby]["domain"]
        invoices = request.env["account.move"].search(domain)
        total_amount_due = (
            sum(invoices.mapped(lambda x: -x.amount_residual if x.move_type == "out_refund" else x.amount_residual))
            if invoices
            else 0.0
        )
        values.update({"total_amount_due": total_amount_due})
        return values
