from odoo.http import request

try:
    from odoo.addons.account_payment_multi.controllers.portal import PaymentPortal

    class PaymentPortal(PaymentPortal):
        def _get_selected_invoices_domain(self, due_date, partner_id=None):
            if not partner_id:
                partner_id = request.env.user.partner_id.id
            domain = super()._get_selected_invoices_domain(due_date, partner_id=partner_id)

            domain = [leaf for leaf in domain if not (isinstance(leaf, tuple) and leaf[0] == "partner_id")]
            domain += [
                "|",
                ("partner_id", "=", partner_id),
                ("message_partner_ids", "in", [partner_id]),
            ]
            return domain

        def _selected_invoices_get_page_view_values(self, selected_invoices, **kwargs):
            selected_invoices = selected_invoices.with_context(skip_selected_invoices_validation=True)
            return super()._selected_invoices_get_page_view_values(selected_invoices, **kwargs)

except ImportError:
    pass
