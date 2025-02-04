##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    current_main_group_id = fields.Many2one("academic.group", related="partner_id.current_main_group_id", store=True)
    show_update_end_date = fields.Boolean(store=False)

    def _set_deferred_end_date_from_template(self):
        self.ensure_one()
        if (
            (not self.sale_order_template_id or self.sale_order_template_id.is_unlimited)
            and self.plan_id
            and not self.plan_id.is_unlimited
        ):
            self.write({"end_date": self.next_invoice_date + self.plan_id.duration - relativedelta(days=1)})
        else:
            super()._set_deferred_end_date_from_template()

    @api.constrains("sale_order_template_id", "plan_id")
    def _check_period(self):
        for rec in self:
            if (
                rec.sale_order_template_id
                and not rec.sale_order_template_id.is_unlimited
                and rec.plan_id
                and not rec.plan_id.is_unlimited
            ):
                raise UserError(
                    self.env._("There cannot be a sale order template and a recurring plan both with a defined period.")
                )

    def _get_auto_invoice_grouping_keys(self):
        grouping_keys = super()._get_auto_invoice_grouping_keys() + [
            "partner_id",
            "partner_invoice_id",
            "payment_term_id",
        ]
        grouping_keys = list(set(grouping_keys))
        return grouping_keys

    def action_update_prices(self):
        if self._context.get("action_update_subscription_prices"):
            lines_no_recurring_pricing = self.order_line.filtered(
                lambda line: not bool(
                    self.env["sale.subscription.pricing"]._get_first_suitable_recurring_pricing(
                        line.product_id, line.plan_id, line.order_id.pricelist_id
                    )
                )
            )
            # Voy a actualizar precios siempre y cuando haya líneas para actualizar, es decir, que tenga un precio
            # definido en recurring prices.
            # Si hay líneas para actualizar precios, entonces guardo el precio de las líneas que no se tienen que
            # actualizar para luego sobreescribir.
            if lines_no_recurring_pricing != self.order_line:
                lines_price_unit = {line: line.price_unit for line in lines_no_recurring_pricing}
                super().action_update_prices()
                for line, original_price in lines_price_unit.items():
                    line.price_unit = original_price
        else:
            super().action_update_prices()

    @api.onchange("next_invoice_date")
    def _onchange_next_invoice_date_show_update_end_date(self):
        self.show_update_end_date = True

    def set_deferred_end_date_from_button(self):
        for record in self:
            record._set_deferred_end_date_from_template()

    @api.model
    def get_duplicate_subscription_ids(self):
        # TODO: evaluar sacar feature
        grouped_subs = self.read_group(
            [("partner_id", "!=", False), ("order_line", "!=", False), ("subscription_state", "=", "3_progress")],
            ["partner_id"],
            ["partner_id"],
            lazy=False,
        )
        partner_ids = {group["partner_id"][0] for group in grouped_subs if group["__count"] > 1}

        if not partner_ids:
            return [("id", "in", [])]

        subscriptions = self.search(
            [
                ("partner_id", "in", list(partner_ids)),
                ("order_line", "!=", False),
                ("subscription_state", "=", "3_progress"),
            ]
        )

        grouped_by_products = {}
        duplicate_ids = set()

        for sub in subscriptions:
            product_ids = frozenset(sub.order_line.mapped("product_id.id"))
            key = (sub.partner_id.id, product_ids)

            if key in grouped_by_products:
                duplicate_ids.add(sub.id)
                duplicate_ids.update(grouped_by_products[key])
            grouped_by_products.setdefault(key, set()).add(sub.id)

        return [("id", "in", list(duplicate_ids))]

    def action_show_duplicate_subscriptions(self):
        # TODO: evaluac sacar feature
        return {
            "name": "Duplicated Subscriptions",
            "type": "ir.actions.act_window",
            "res_model": "sale.order",
            "view_mode": "list,form",
            "domain": self.get_duplicate_subscription_ids(),
            "context": "{'search_default_customer': 1}",
        }
