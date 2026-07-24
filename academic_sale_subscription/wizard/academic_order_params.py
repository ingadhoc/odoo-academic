##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import api, fields, models


class AcademicOrderParams(models.AbstractModel):
    _name = "academic.order.params"
    _description = "Academic Order Parameters"

    template_id = fields.Many2one("sale.order.template")
    plan_id = fields.Many2one("sale.subscription.plan", compute="_compute_plan", readonly=False, store=True)
    pricelist_id = fields.Many2one("product.pricelist")
    next_invoice_date = fields.Date(string="Date of first invoice")
    status_sale = fields.Selection(
        [("draft", "Draft"), ("confirmed", "Confirmed")], default="draft", help="Status to be given to sales orders."
    )
    validity_date = fields.Date()
    payment_term_id = fields.Many2one("account.payment.term")

    @api.depends("template_id")
    def _compute_plan(self):
        for rec in self:
            rec.plan_id = rec.template_id.plan_id or False

    def _is_recurring_products(self, products):
        """Nothing configured yet counts as recurring: the wizards default to subscriptions."""
        return not products or any(products.mapped("recurring_invoice"))

    def _get_orders_action(self, orders):
        if self.is_recurring_mode:
            action = self.env["ir.actions.actions"]._for_xml_id("sale_subscription.sale_subscription_action")
            action.update(
                {
                    "domain": [("id", "in", orders.ids)],
                    "views": sorted(action["views"], key=lambda v: v[1] != "list"),
                    "context": {"default_is_subscription": 1},
                }
            )
            return action
        return {
            "type": "ir.actions.act_window",
            "name": self.env._("Orders"),
            "res_model": "sale.order",
            "view_mode": "list,form",
            "domain": [("id", "in", orders.ids)],
        }
