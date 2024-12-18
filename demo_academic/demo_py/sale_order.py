##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    active = fields.Boolean(default=True)

    @api.model
    def _init_demo_base(self):
        if self.env['ir.module.module'].search([('name', '=', 'sale_exception'), ('state', '=', 'installed')], limit=1):
            self.env['exception.rule'].search([('active', '=', True)]).write({'active': False})

        self.search([]).active = False

        student = self.env.ref('demo_academic.res_partner_student_1')

        product_enrollment = self.env.ref('demo_academic.product_template_enrollment_secondary_level')
        product_tuition = self.env.ref('demo_academic.product_template_tuition_secondary_level')
        product_english = self.env.ref('demo_academic.product_template_extracurricular_english')

        plan = self.env.ref('sale_subscription.subscription_plan_month')

        orders = self.create([
            {
                'partner_id': student.id,
                'plan_id': plan.id,
                'order_line': [
                    (0, 0, {'product_id': product_enrollment.product_variant_id.id, 'product_uom_qty': 1}),
                ],
            },
            {
                'partner_id': student.id,
                'plan_id': plan.id,
                'order_line': [
                    (0, 0, {'product_id': product_tuition.product_variant_id.id, 'product_uom_qty': 1}),
                ],
            },
            {
                'partner_id': student.id,
                'plan_id': plan.id,
                'order_line': [
                    (0, 0, {'product_id': product_english.product_variant_id.id, 'product_uom_qty': 1}),
                ],
            },
        ])

        for order in orders:
            order.action_confirm()
            order._create_invoices()
        invoices = orders.mapped('invoice_ids')

        invoices[0].action_post()
        self._create_payment(invoices[0], invoices[0].amount_total)

        invoices[1].action_post()
        self._create_payment(invoices[1], invoices[1].amount_total / 2)

        invoices[2].action_post()

    def _create_payment(self, invoice, amount):
        register_wizard = self.env['account.payment.register'].with_context({
                            'active_model': 'account.move',
                            'active_ids': [invoice.id],
                        })
        register_wizard_obj = register_wizard.create({
            'journal_id': self.env['account.journal'].search([('type', '=', 'bank')], limit=1).id,
            'amount': amount
        })
        register_wizard_obj.action_create_payments()
