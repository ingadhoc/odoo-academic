from odoo.addons.sale_subscription.controllers.portal import CustomerPortal
from odoo.http import request, route


class AcademicPortal(CustomerPortal):
    @route()
    def subscription(self, order_id, access_token=None, message='', message_class='', report_type=None, download=False, **kw):
        response = super().subscription(order_id=order_id, access_token=access_token, message=message, message_class=message_class, report_type=report_type, download=download, **kw)
        if 'enable_token_management' not in response.qcontext:
            return response

        if not response.qcontext['enable_token_management']:
            order_sudo, _ = self._get_subscription(access_token, order_id)
            response.qcontext['enable_token_management'] = order_sudo.partner_id.partner_type == 'student' and request.env.user.partner_id in order_sudo.partner_id.payment_responsible_ids

        return response
