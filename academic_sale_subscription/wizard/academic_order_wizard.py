##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api, _, Command
from odoo.exceptions import ValidationError, UserError
from odoo.exceptions import UserError, ValidationError


class OrderWizard(models.TransientModel):
    _name = 'academic.order.wizard'

    student_ids = fields.Many2many('res.partner', default=lambda self: self.env.context.get('active_ids', []))
    plan_id = fields.Many2one('sale.subscription.plan', required=True, compute="_compute_plan", readonly=False, store=True)
    order_wizard_line_ids = fields.One2many('academic.order.wizard.line', 'academic_order_wizard_id', compute="_compute_order_wizard_line", readonly=False, store=True)
    pricelist_id = fields.Many2one('product.pricelist')
    template_id = fields.Many2one('sale.order.template')
    next_invoice_date = fields.Date(required=True)
    status_sale = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed')],
        default='draft', help='Status to be given to sales orders.'
    )
    validity_date = fields.Date()
    payment_term_id = fields.Many2one('account.payment.term',)

    def action_create_mass_subscription(self):
        if not self.student_ids:
            raise ValidationError(_("No student has been selected."))

        if partners := self.student_ids.filtered(lambda x: x.partner_type != 'student'):
            raise ValidationError(_("The contacts must be of student type. The following do not meet this condition:\n%s") % "\n".join(partners.mapped('name')))

        subscriptions = self._create_mass_subscription()

        action = self.env.ref('sale_subscription.sale_subscription_action').read()[0]
        action.update({
            'domain': [('id', 'in', subscriptions.ids)],
            'views': sorted(action['views'], key=lambda v: v[1] != 'tree'),  # show tree view first
            'context': {'default_is_subscription': 1}
        })
        return action

    def _create_mass_subscription(self):
        subscriptions = self.env['sale.order']
        academic_paying_role = self.env.ref('academic.paying_role')
        for student in self.student_ids:
            paying_role = student.student_link_ids.filtered(lambda x: academic_paying_role in x.role_ids)
            if not paying_role:
                raise ValidationError(
                        _("The student %s has no payment responsible for the payment set." % student.name)
                    )
            subscription = self.env['sale.order'].create({
                'partner_id': student.id,
                'partner_invoice_id': paying_role[0].partner_id.id,
                'plan_id': self.plan_id.id,
                'pricelist_id': self.pricelist_id.id,
                'next_invoice_date': self.next_invoice_date,
                'sale_order_template_id': self.template_id.id,
                'validity_date': self.validity_date if self.status_sale == 'draft' else False,
                **({'payment_term_id': self.payment_term_id.id} if self.payment_term_id else {}),
                'order_line': [
                    (0, 0, {
                        'product_id': line.product_id.id,
                        'product_uom_qty': 1,
                        'price_unit': line.price,
                        **({'name': line.description} if line.description else {}),
                    }) for line in self.order_wizard_line_ids
                ]
            })

            if self.status_sale == 'confirmed':
                subscription.action_confirm()

            subscriptions += subscription
        return subscriptions

    @api.depends('template_id')
    def _compute_plan(self):
        for rec in self:
            rec.plan_id = rec.template_id.plan_id or False

    @api.model
    def _get_product_price(self, product_id, plan_id, pricelist_id):
        if not plan_id:
            return 1.0

        lines = plan_id.product_subscription_pricing_ids.filtered(
            lambda x: x.product_template_id.id == product_id.product_tmpl_id.id
            and (not x.product_variant_ids or product_id.id in x.product_variant_ids.mapped('id'))
        )

        if pricelist_id:
            lines = lines.filtered(lambda x: x.pricelist_id.id == pricelist_id.id)

        lines = lines.sorted(key=lambda x: bool(x.product_variant_ids), reverse=True)

        return lines[0].price if lines else 1.0

    @api.depends('template_id', 'plan_id', 'pricelist_id')
    def _compute_order_wizard_line(self):
        for rec in self:
            order_wizard_lines = []

            if rec.template_id:
                for line in rec.template_id.sale_order_template_line_ids:
                    existing_line = rec.order_wizard_line_ids.filtered(lambda l: l.product_id.id == line.product_id.id)

                    if existing_line:
                        order_wizard_line_vals = {
                            'price': self._get_product_price(existing_line.product_id, rec.plan_id, rec.pricelist_id)
                        }
                        existing_line.write(order_wizard_line_vals)
                    else:
                        order_wizard_line_vals = {
                            'product_id': line.product_id.id,
                            'price': self._get_product_price(line.product_id, rec.plan_id, rec.pricelist_id)
                        }
                        order_wizard_lines.append(Command.create(order_wizard_line_vals))

            rec.order_wizard_line_ids = order_wizard_lines

            products = rec.template_id.sale_order_template_line_ids.mapped('product_id')
            for wizard_line in rec.order_wizard_line_ids.filtered(lambda x: x.product_id not in products):
                wizard_line.write({
                    'price': self._get_product_price(wizard_line.product_id, rec.plan_id, rec.pricelist_id)
                })

    @api.constrains('next_invoice_date', 'validity_date')
    def _check_validity_date(self):
        for rec in self.filtered(lambda x: x.status_sale == 'draft'):
            if rec.next_invoice_date < rec.validity_date:
                raise UserError(_("The date of the next invoice cannot be earlier than the validity date."))

    @api.constrains('order_wizard_line_ids')
    def _check_price(self):
        for rec in self:
            if not rec.order_wizard_line_ids:
                raise ValidationError(_("There must be product lines."))

            if rec.order_wizard_line_ids.filtered(lambda x: x.price <= 0):
                raise ValidationError(_("The product price should not be equal to or less than 0."))


class AcademicOrderWizardLine(models.TransientModel):
    _name = 'academic.order.wizard.line'

    academic_order_wizard_id = fields.Many2one('academic.order.wizard')
    product_id = fields.Many2one('product.product', required=True)
    price = fields.Monetary(default=1.0)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    description = fields.Text()
