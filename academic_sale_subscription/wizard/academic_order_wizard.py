##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import Command, api, fields, models
from odoo.exceptions import UserError, ValidationError


class OrderWizard(models.TransientModel):
    _name = "academic.order.wizard"
    _description = "Academic Order Wizard"

    student_ids = fields.Many2many("res.partner", default=lambda self: self.env.context.get("active_ids", []))
    plan_id = fields.Many2one(
        "sale.subscription.plan", required=True, compute="_compute_plan", readonly=False, store=True
    )
    order_wizard_line_ids = fields.One2many(
        "academic.order.wizard.line",
        "academic_order_wizard_id",
        compute="_compute_order_wizard_line",
        readonly=False,
        store=True,
    )
    pricelist_id = fields.Many2one("product.pricelist")
    template_id = fields.Many2one("sale.order.template")
    next_invoice_date = fields.Date(string="Date of first invoice", required=True)
    status_sale = fields.Selection(
        [("draft", "Draft"), ("confirmed", "Confirmed")], default="draft", help="Status to be given to sales orders."
    )
    validity_date = fields.Date()
    payment_term_id = fields.Many2one("account.payment.term")

    def action_create_mass_subscription(self):
        if not self.student_ids:
            raise ValidationError(self.env._("No student has been selected."))

        if partners := self.student_ids.filtered(lambda x: x.partner_type != "student"):
            raise ValidationError(
                self.env._("The contacts must be of student type. The following do not meet this condition:\n%s")
                % "\n".join(partners.mapped("name"))
            )

        if partners := self.student_ids.filtered(
            lambda x: not x.payment_responsible_ids or not x.payment_responsible_ids.filtered("active")
        ):
            raise ValidationError(
                self.env._(
                    "The following students either have no payment responsible assigned or their payment responsible is archived:\n%s",
                    "\n".join(partners.mapped("name")),
                )
            )

        subscriptions = self._create_mass_subscription()

        action = self.env.ref("sale_subscription.sale_subscription_action").read()[0]
        action.update(
            {
                "domain": [("id", "in", subscriptions.ids)],
                "views": sorted(action["views"], key=lambda v: v[1] != "list"),  # show list view first
                "context": {"default_is_subscription": 1},
            }
        )
        return action

    def _create_mass_subscription(self, vals=None):
        subscriptions = self.env["sale.order"]
        for student in self.student_ids:
            subscription = self.env["sale.order"].create(
                {
                    "partner_id": student.id,
                    "plan_id": self.plan_id.id,
                    "pricelist_id": self.pricelist_id.id,
                    "start_date": self.next_invoice_date,
                    "sale_order_template_id": self.template_id.id,
                    "validity_date": self.validity_date if self.status_sale == "draft" else False,
                    **({"payment_term_id": self.payment_term_id.id} if self.payment_term_id else {}),
                    **(vals or {}),
                    "order_line": [
                        (
                            0,
                            0,
                            {
                                "product_id": line.product_id.id,
                                "product_uom_qty": line.quantity,
                                "price_unit": line.price,
                                **({"name": line.description} if line.description else {}),
                                **({"group_id": line.academic_group_id.id} if line.academic_group_id else {}),
                            },
                        )
                        for line in self.order_wizard_line_ids
                    ],
                }
            )

            if self.status_sale == "confirmed":
                subscription.action_confirm()

            subscriptions += subscription
        return subscriptions

    @api.depends("template_id")
    def _compute_plan(self):
        for rec in self:
            rec.plan_id = rec.template_id.plan_id or False

    @api.depends("template_id", "plan_id", "pricelist_id")
    def _compute_order_wizard_line(self):
        for rec in self:
            order_wizard_lines = []

            # deletion of lines created from another template
            lines_to_remove = rec.order_wizard_line_ids.filtered(
                lambda x: x.template_id and x.template_id != rec.template_id
            )
            for line in lines_to_remove:
                order_wizard_lines.append(Command.unlink(line.id))

            if rec.template_id:
                for line in rec.template_id.sale_order_template_line_ids:
                    existing_line = rec.order_wizard_line_ids.filtered(lambda l: l.product_id.id == line.product_id.id)

                    if existing_line:
                        pricing = existing_line.product_id.product_tmpl_id._get_recurring_pricing(
                            rec.pricelist_id, variant=existing_line.product_id, plan_id=rec.plan_id.id
                        )
                        price = 0.0
                        if pricing:
                            price = pricing._compute_price(
                                existing_line.product_id,
                                1.0,
                                existing_line.product_id.uom_id,
                                fields.Datetime.now(),
                                rec.pricelist_id.currency_id or self.env.company.currency_id,
                            )
                        order_wizard_line_vals = {
                            "price": price,
                        }
                        existing_line.write(order_wizard_line_vals)
                    else:
                        pricing = line.product_id.product_tmpl_id._get_recurring_pricing(
                            rec.pricelist_id, variant=line.product_id, plan_id=rec.plan_id.id
                        )
                        price = 0.0
                        if pricing:
                            price = pricing._compute_price(
                                line.product_id,
                                1.0,
                                line.product_id.uom_id,
                                fields.Datetime.now(),
                                rec.pricelist_id.currency_id or self.env.company.currency_id,
                            )
                        order_wizard_line_vals = {
                            "product_id": line.product_id.id,
                            "price": price,
                            "quantity": line.product_uom_qty,
                            "template_id": rec.template_id,
                        }
                        order_wizard_lines.append(Command.create(order_wizard_line_vals))

            rec.order_wizard_line_ids = order_wizard_lines

            products = rec.template_id.sale_order_template_line_ids.mapped("product_id")
            for wizard_line in rec.order_wizard_line_ids.filtered(lambda x: x.product_id not in products):
                pricing = wizard_line.product_id.product_tmpl_id._get_recurring_pricing(
                    rec.pricelist_id, variant=wizard_line.product_id, plan_id=rec.plan_id.id
                )
                price = 0.0
                if pricing:
                    price = pricing._compute_price(
                        wizard_line.product_id,
                        1.0,
                        wizard_line.product_id.uom_id,
                        fields.Datetime.now(),
                        rec.pricelist_id.currency_id or self.env.company.currency_id,
                    )
                wizard_line.write({"price": price})

    @api.constrains("next_invoice_date", "validity_date")
    def _check_validity_date(self):
        for rec in self.filtered(lambda x: x.status_sale == "draft"):
            if rec.next_invoice_date < rec.validity_date:
                raise UserError(self.env._("The date of the next invoice cannot be earlier than the validity date."))

    @api.constrains("order_wizard_line_ids")
    def _check_wizard_lines(self):
        for rec in self:
            if not rec.order_wizard_line_ids:
                raise ValidationError(self.env._("There must be product lines."))

    @api.onchange("order_wizard_line_ids")
    def _onchange_notification_price(self):
        for rec in self:
            if rec.order_wizard_line_ids.filtered(lambda x: x.price <= 0):
                return {
                    "warning": {
                        "title": self.env._("Warning"),
                        "message": self.env._("There are products with price 0."),
                        "type": "notification",
                    }
                }


class AcademicOrderWizardLine(models.TransientModel):
    _name = "academic.order.wizard.line"
    _description = "Academic Order Wizard Lines"

    academic_order_wizard_id = fields.Many2one("academic.order.wizard")
    product_id = fields.Many2one("product.product", required=True)
    price = fields.Monetary(compute="_compute_price", readonly=False, store=True)
    currency_id = fields.Many2one("res.currency", default=lambda self: self.env.company.currency_id)
    description = fields.Text()
    quantity = fields.Float(default=1.0)
    template_id = fields.Many2one("sale.order.template", store=False)
    academic_group_id = fields.Many2one(
        "academic.group", compute="_compute_academic_group_id", store=True, readonly=False
    )
    academic_product_type = fields.Selection(
        related="product_id.academic_product_type",
    )

    @api.depends("product_id")
    def _compute_price(self):
        for rec in self.filtered("product_id"):
            pricing = rec.product_id.product_tmpl_id._get_recurring_pricing(
                rec.academic_order_wizard_id.pricelist_id,
                variant=rec.product_id,
                plan_id=rec.academic_order_wizard_id.plan_id.id,
            )
            if pricing:
                rec.price = pricing._compute_price(
                    rec.product_id,
                    1.0,
                    rec.product_id.uom_id,
                    fields.Datetime.now(),
                    rec.academic_order_wizard_id.pricelist_id.currency_id or self.env.company.currency_id,
                )
            else:
                rec.price = 0.0

    @api.depends("academic_product_type")
    def _compute_academic_group_id(self):
        if academic_group := self.env.context.get("academic_group_id"):
            academic_products = self.filtered("academic_product_type")
            academic_products.academic_group_id = academic_group
            (self - academic_products).academic_group_id = False
