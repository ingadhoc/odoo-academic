from odoo.http import request

try:
    from odoo.addons.account_payment_multi.controllers.portal import PaymentPortal

    class PaymentPortal(PaymentPortal):
        def _get_selected_invoices_domain(self, due_date, partner_id=None):
            if not partner_id:
                invoice_id = request.params.get('invoice_id')
                if invoice_id:
                    invoice = request.env['account.move'].sudo().browse(int(invoice_id))
                    partner_id = invoice.partner_id.id
            return super()._get_selected_invoices_domain(due_date, partner_id=partner_id)

except ImportError:
    pass
