from odoo.addons.sale_subscription.controllers.portal import CustomerPortal
from odoo.http import request, route


class AcademicPortal(CustomerPortal):
    def _get_subscription_domain(self, partner):
        domain = super()._get_subscription_domain(partner)
        students = partner.sudo().partner_link_ids.student_id
        if not students:
            return domain
        rest = [leaf for leaf in domain if leaf[0] != "partner_id"]
        return [
            "|",
            ("partner_id", "child_of", partner.commercial_partner_id.id),
            ("partner_id", "in", students.ids),
        ] + rest

    @route()
    def subscription(
        self, order_id, access_token=None, message="", message_class="", report_type=None, download=False, **kw
    ):
        response = super().subscription(
            order_id=order_id,
            access_token=access_token,
            message=message,
            message_class=message_class,
            report_type=report_type,
            download=download,
            **kw,
        )
        if "enable_token_management" not in response.qcontext:
            return response

        if not response.qcontext["enable_token_management"]:
            order_sudo, _ = self._get_subscription(access_token, order_id)
            response.qcontext["enable_token_management"] = (
                order_sudo.partner_id.partner_type == "student"
                and request.env.user.partner_id in order_sudo.partner_id.payment_responsible_ids
            )

        return response
