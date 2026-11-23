from odoo.http import request
from odoo.addons.account_payment_multi.controllers.portal import PaymentPortal

class PaymentPortal(PaymentPortal):
    def _get_selected_invoices_domain(self, due_date, partner_id=None):
        # En contexto académico, el usuario logueado debe ser responsable de pago del estudiante
        # No usamos el partner_id de la factura porque este es el estudiante, no el responsable
        if not partner_id:
            partner_id = request.env.user.partner_id.id
        
        # Construimos dominio base
        domain = [
            ('state', 'not in', ('cancel', 'draft')),
            ('move_type', 'in', ('out_invoice', 'out_receipt')),
            ('payment_state', 'not in', ('in_payment', 'paid')),
            ('invoice_date_due', '<=', due_date),
        ]
        
        # Filtramos por facturas donde el usuario es responsable de pago del estudiante
        # o donde el usuario es el partner directo de la factura
        domain.append('|')
        domain.append(('student_id.payment_responsible_ids', 'in', partner_id))
        domain.append(('partner_id', '=', partner_id))
        
        return domain
