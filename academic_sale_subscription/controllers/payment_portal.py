from odoo.addons.payment.controllers import portal as payment_portal


class PaymentPortal(payment_portal.PaymentPortal):
    def _get_subscription_domain(self, partner):
        res = super()._get_subscription_domain(partner)
        for domain_tuple in res:
            if len(domain_tuple) == 3 and domain_tuple[0] == "subscription_state" and domain_tuple[1] == "in":
                states = list(domain_tuple[2])
                if "1_draft" not in states:
                    states.append("1_draft")
                index = res.index(domain_tuple)
                res[index] = ("subscription_state", "in", states)
                break
        return res
