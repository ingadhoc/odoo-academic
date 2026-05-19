from odoo.addons.account.controllers.portal import PortalAccount
from odoo.fields import Domain
from odoo.http import request


class PortalAccount(PortalAccount):
    def _get_account_searchbar_filters(self):
        filters = super()._get_account_searchbar_filters()
        filters = {k: v for k, v in filters.items() if k == "all"}
        paying_role_id = request.env.ref("academic.paying_role").id
        student_links = (
            request.env["res.partner.link"]
            .sudo()
            .search(
                [
                    ("partner_id", "=", request.env.user.partner_id.id),
                    ("role_ids", "in", paying_role_id),
                ]
            )
        )
        students = student_links.mapped("student_id")
        for student in students:
            filters[f"student_{student.id}"] = {"label": student.name, "domain": [("student_id", "=", student.id)]}
        return filters

    def _prepare_my_invoices_values(
        self, page, date_begin, date_end, sortby, filterby, domain=None, url="/my/invoices"
    ):
        searchbar_filters = self._get_account_searchbar_filters()
        if filterby not in searchbar_filters:
            filterby = "all"
        values = super()._prepare_my_invoices_values(page, date_begin, date_end, sortby, filterby, domain, url)

        partner = request.env.user.partner_id
        AccountInvoice = request.env["account.move"].sudo()

        domain = Domain.AND(
            [
                domain or [],
                self._get_invoices_domain(),
                [
                    "|",
                    ("partner_id", "child_of", [partner.commercial_partner_id.id]),
                    ("message_partner_ids", "in", [partner.id]),
                ],
            ]
        )
        domain += searchbar_filters[filterby]["domain"]

        order = self._get_account_searchbar_sortings().get(sortby or "date", {}).get("order", "invoice_date desc")

        invoices = AccountInvoice.search(domain)
        total = len(invoices)
        total_amount_due = (
            sum(invoices.mapped(lambda x: -x.amount_residual if x.move_type == "out_refund" else x.amount_residual))
            if invoices
            else 0.0
        )
        values.update(
            {
                "total_amount_due": total_amount_due,
                "invoices": lambda pager_offset: [
                    invoice._get_invoice_portal_extra_values()
                    for invoice in AccountInvoice.search(
                        domain, order=order, limit=self._items_per_page, offset=pager_offset
                    )
                ],
                "pager": {**values["pager"], "total": total},
            }
        )
        return values
