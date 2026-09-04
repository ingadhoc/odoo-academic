##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    current_main_group_id = fields.Many2one("academic.group", related="partner_id.current_main_group_id", store=True)
    show_update_end_date = fields.Boolean(store=False)

    partner_id = fields.Many2one(
        domain="[('type', '!=', 'private'), ('company_id', 'in', (False, company_id)), ('partner_type', '=', 'student')]"
    )
    partner_invoice_ids = fields.Many2many("res.partner", compute="_compute_partner_invoice")
    is_academic_sale = fields.Boolean(compute="_compute_is_academic_sale", readonly=False)

    @api.depends("partner_id")
    def _compute_is_academic_sale(self):
        for rec in self:
            rec.is_academic_sale = True if not rec.partner_id else rec.partner_id.partner_type == "student"

    @api.depends("partner_id", "partner_id.payment_responsible_ids")
    def _compute_partner_invoice(self):
        orders = self.filtered("partner_id")
        for rec in orders:
            if rec.partner_id.self_payment_responsible:
                rec.partner_invoice_ids = rec.partner_id
            else:
                student_links = rec.partner_id.student_link_ids.filtered(
                    lambda x: self.env.ref("academic.paying_role") in x.role_ids
                ).sorted("sequence")
                rec.partner_invoice_ids = student_links.mapped("partner_id")
        (self - orders).partner_invoice_ids = False

    @api.depends("partner_invoice_ids")
    def _compute_partner_invoice_id(self):
        # si bien en el dominio solo permitimos estudiantes, para no romper demo data de odoo ni tests, si no es un estudiante
        # dejamos compute by super
        students_orders = self.filtered("is_academic_sale")
        for order in students_orders:
            order.partner_invoice_id = order.partner_invoice_ids._origin[:1]
        super(SaleOrder, self - students_orders)._compute_partner_invoice_id()

    def _prepare_invoice(self):
        res = super()._prepare_invoice()
        if self.is_academic_sale:
            res["student_id"] = self.partner_id.id
        return res

    @api.model_create_multi
    def create(self, vals_list):
        orders = super().create(vals_list)
        for order in orders.filtered("is_academic_sale"):
            if order.partner_id:
                family_partners = order.partner_id.student_link_ids.mapped("partner_id")
                partners_to_subscribe = order.partner_invoice_id | family_partners
                to_subscribe = partners_to_subscribe - order.sudo().message_partner_ids
                if to_subscribe:
                    order.message_subscribe(partner_ids=to_subscribe.ids)
        return orders

    def _message_get_default_recipients(self):
        """Por defecto las plantillas mandan a partner_id pero para nosotros el partners es el estudiante.
        Cambiamos plantillas para que usen el campo "use_default_to" y luego cae en este método de python donde
        podemos ir mejorando a medida que nos pidan y modificar la logica de recipients.
        Por ahora lo mandamos solo al partner de facturación si está definido
        """
        default_recipients = super()._message_get_default_recipients()
        for record in self.filtered("is_academic_sale"):
            payment_responsible = record.partner_invoice_id | record.partner_invoice_ids
            if payment_responsible:
                default_recipients[record.id] = {
                    "email_cc": False,
                    "email_to": False,
                    "partner_ids": payment_responsible.ids,
                }
        return default_recipients

    def _get_invoice_grouping_keys(self):
        # Estas claves se evaluan sobre los valores de la factura y no sobre la orden: el alumno viaja en
        # student_id y el termino de pago en invoice_payment_term_id (el partner_id de la factura ya es el
        # responsable de pago).
        grouping_keys = super()._get_invoice_grouping_keys()
        if any(self.mapped("is_academic_sale")):
            grouping_keys = list(set(grouping_keys + ["student_id", "invoice_payment_term_id"]))
        return grouping_keys

    def _get_auto_invoice_grouping_keys(self):
        grouping_keys = super()._get_auto_invoice_grouping_keys() + [
            "partner_id",
            "partner_invoice_id",
            "payment_term_id",
        ]
        grouping_keys = list(set(grouping_keys))
        return grouping_keys

    def action_update_prices(self):
        if self.env.context.get("action_update_subscription_prices"):
            lines_no_recurring_pricing = self.order_line.filtered(
                lambda line: not bool(
                    line.product_id.product_tmpl_id._get_recurring_pricing(
                        line.order_id.pricelist_id, variant=line.product_id, plan_id=line.subscription_plan_id.id
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

    def _invoice_is_considered_free(self, invoiceable_lines):
        is_free, is_exception = super()._invoice_is_considered_free(invoiceable_lines)
        param_enabled = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("academic_sale_subscription.enable_zero_price_subscription_invoice")
        )
        if is_free and param_enabled:
            is_free = False
        return is_free, is_exception
