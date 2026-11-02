##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import Command, api, fields, models
from odoo.exceptions import UserError, ValidationError


class OrderWizard(models.TransientModel):
    _name = "academic.order.wizard"
    _inherit = ["academic.order.params"]
    _description = "Academic Order Wizard"

    student_ids = fields.Many2many("res.partner", default=lambda self: self.env.context.get("active_ids", []))
    order_wizard_line_ids = fields.One2many(
        "academic.order.wizard.line",
        "academic_order_wizard_id",
        compute="_compute_order_wizard_line",
        readonly=False,
        store=True,
    )
    is_recurring_mode = fields.Boolean(
        compute="_compute_is_recurring_mode",
        store=True,
    )

    @api.depends("order_wizard_line_ids.product_id")
    def _compute_is_recurring_mode(self):
        for rec in self:
            rec.is_recurring_mode = rec._is_recurring_products(
                rec.order_wizard_line_ids.filtered("product_id").product_id
            )

    def action_create_mass_subscription(self):
        if not self.student_ids:
            raise ValidationError(self.env._("No student has been selected."))

        if partners := self.student_ids.filtered(lambda x: x.partner_type != "student"):
            raise ValidationError(
                self.env._("The contacts must be of student type. The following do not meet this condition:\n%s")
                % "\n".join(partners.mapped("name"))
            )

        if partners := self.student_ids._filter_without_payment_responsible():
            raise ValidationError(
                self.env._(
                    "The following students either have no payment responsible assigned or their payment responsible is archived:\n%s",
                    "\n".join(partners.mapped("name")),
                )
            )

        orders = self._create_mass_subscription()
        return self._get_orders_action(orders)

    def _create_mass_subscription(self, vals=None):
        orders = self.env["sale.order"]
        for student in self.student_ids:
            order_vals = {
                "partner_id": student.id,
                "pricelist_id": self.pricelist_id.id,
                "validity_date": self.validity_date if self.status_sale == "draft" else False,
                **({"payment_term_id": self.payment_term_id.id} if self.payment_term_id else {}),
                **(vals or {}),
                "order_line": [
                    Command.create(line._prepare_order_line_values()) for line in self.order_wizard_line_ids
                ],
            }
            if self.is_recurring_mode:
                order_vals.update(
                    {
                        "plan_id": self.plan_id.id,
                        "start_date": self.next_invoice_date,
                        "sale_order_template_id": self.template_id.id,
                    }
                )
            order = self.env["sale.order"].create(order_vals)

            if self.status_sale == "confirmed":
                order.action_confirm()

            orders += order
        return orders

    def _get_recurring_price(self, product):
        """Price of a product under this wizard's plan and pricelist."""
        self.ensure_one()
        pricing = product.product_tmpl_id._get_recurring_pricing(
            self.pricelist_id, variant=product, plan_id=self.plan_id.id
        )
        if not pricing:
            return 0.0
        return pricing._compute_price(
            product,
            1.0,
            product.uom_id,
            date=fields.Datetime.now(),
            currency=self.pricelist_id.currency_id or self.env.company.currency_id,
        )

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
                # one wizard line per template line, so a product repeated under several
                # sections keeps one row per section instead of collapsing into one
                for line in rec.template_id.sale_order_template_line_ids:
                    existing_line = rec.order_wizard_line_ids.filtered(lambda l: l.template_line_id == line)

                    if existing_line:
                        if not line.display_type:
                            existing_line.write({"price": rec._get_recurring_price(existing_line.product_id)})
                        continue

                    order_wizard_line_vals = {
                        "sequence": line.sequence,
                        "name": line.name,
                        "display_type": line.display_type,
                        "template_id": rec.template_id.id,
                        "template_line_id": line.id,
                    }
                    if not line.display_type:
                        order_wizard_line_vals.update(
                            {
                                "product_id": line.product_id.id,
                                "price": rec._get_recurring_price(line.product_id),
                                "quantity": line.product_uom_qty,
                            }
                        )
                    order_wizard_lines.append(Command.create(order_wizard_line_vals))

            rec.order_wizard_line_ids = order_wizard_lines

            products = rec.template_id.sale_order_template_line_ids.product_id
            for wizard_line in rec.order_wizard_line_ids.filtered(
                lambda x: x.product_id and x.product_id not in products
            ):
                if wizard_line.product_id.recurring_invoice:
                    pricing = wizard_line.product_id.product_tmpl_id._get_recurring_pricing(
                        rec.pricelist_id, variant=wizard_line.product_id, plan_id=rec.plan_id.id
                    )
                    price = 0.0
                    if pricing:
                        price = pricing._compute_price(
                            wizard_line.product_id,
                            1.0,
                            wizard_line.product_id.uom_id,
                            date=fields.Datetime.now(),
                            currency=rec.pricelist_id.currency_id or self.env.company.currency_id,
                        )
                    wizard_line.write({"price": price})
                else:
                    pricelist = rec.pricelist_id
                    if pricelist:
                        price = pricelist._get_product_price(
                            wizard_line.product_id,
                            1.0,
                            currency=pricelist.currency_id,
                            date=fields.Datetime.now(),
                        )
                    else:
                        price = wizard_line.product_id.lst_price
                    wizard_line.write({"price": price})

    @api.constrains("next_invoice_date", "validity_date")
    def _check_validity_date(self):
        for rec in self.filtered(lambda x: x.status_sale == "draft" and x.next_invoice_date and x.validity_date):
            if rec.next_invoice_date < rec.validity_date:
                raise UserError(self.env._("The date of the next invoice cannot be earlier than the validity date."))

    @api.constrains("order_wizard_line_ids")
    def _check_wizard_lines(self):
        for rec in self:
            if not rec.order_wizard_line_ids.filtered("product_id"):
                raise ValidationError(self.env._("There must be product lines."))

    @api.constrains("plan_id", "next_invoice_date", "order_wizard_line_ids")
    def _check_recurring_fields_required(self):
        for rec in self:
            lines_with_product = rec.order_wizard_line_ids.filtered("product_id")
            if not lines_with_product:
                continue
            is_recurring = all(line.product_id.recurring_invoice for line in lines_with_product)
            if not is_recurring:
                continue
            if not rec.plan_id:
                raise ValidationError(self.env._("A subscription plan is required when creating recurring orders."))
            if not rec.next_invoice_date:
                raise ValidationError(self.env._("The date of first invoice is required for recurring orders."))

    @api.onchange("order_wizard_line_ids")
    def _onchange_notification_price(self):
        for rec in self:
            if rec.order_wizard_line_ids.filtered(lambda x: x.product_id and x.price <= 0):
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
    _order = "sequence, id"

    academic_order_wizard_id = fields.Many2one("academic.order.wizard")
    sequence = fields.Integer(default=10)
    display_type = fields.Selection(
        [("line_section", "Section"), ("line_note", "Note")],
        help="Technical field for UX purpose.",
    )
    product_id = fields.Many2one("product.product")
    price = fields.Monetary(compute="_compute_price", readonly=False, store=True)
    currency_id = fields.Many2one("res.currency", default=lambda self: self.env.company.currency_id)
    name = fields.Text(string="Description")
    quantity = fields.Float(default=1.0)
    template_id = fields.Many2one("sale.order.template")
    template_line_id = fields.Many2one("sale.order.template.line")
    academic_group_id = fields.Many2one(
        "academic.group", compute="_compute_academic_group_id", store=True, readonly=False
    )
    academic_product_type = fields.Selection(
        related="product_id.academic_product_type",
    )

    @api.constrains("product_id", "display_type")
    def _check_product_required(self):
        for rec in self:
            if not rec.display_type and not rec.product_id:
                raise ValidationError(self.env._("A line that is not a section or a note needs a product."))

    def _prepare_order_line_values(self):
        """Values for the sale order line this wizard line creates."""
        self.ensure_one()
        if self.display_type:
            return {
                "sequence": self.sequence,
                "display_type": self.display_type,
                "name": self.name or "",
                "product_uom_qty": 0.0,
                "price_unit": 0.0,
            }
        return {
            "sequence": self.sequence,
            "product_id": self.product_id.id,
            "product_uom_qty": self.quantity,
            "price_unit": self.price,
            **({"name": self.name} if self.name else {}),
            **({"group_id": self.academic_group_id.id} if self.academic_group_id else {}),
        }

    @api.depends("product_id", "academic_order_wizard_id.plan_id", "academic_order_wizard_id.pricelist_id")
    def _compute_price(self):
        for rec in self.filtered("product_id"):
            if rec.product_id.recurring_invoice:
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
                        date=fields.Datetime.now(),
                        currency=rec.academic_order_wizard_id.pricelist_id.currency_id or self.env.company.currency_id,
                    )
                else:
                    rec.price = 0.0
            else:
                pricelist = rec.academic_order_wizard_id.pricelist_id
                if pricelist:
                    rec.price = pricelist._get_product_price(
                        rec.product_id,
                        1.0,
                        currency=pricelist.currency_id,
                        date=fields.Datetime.now(),
                    )
                else:
                    rec.price = rec.product_id.lst_price

    @api.depends("academic_product_type")
    def _compute_academic_group_id(self):
        if academic_group := self.env.context.get("academic_group_id"):
            academic_products = self.filtered("academic_product_type")
            academic_products.academic_group_id = academic_group
            (self - academic_products).academic_group_id = False
