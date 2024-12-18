##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import api, models


class SaleOrderTemplate(models.Model):
    _inherit = 'sale.order.template'

    @api.model
    def _init_demo_base(self):
        products = {
            'product_template_enrollment_pink_room': self.env.ref('demo_academic.product_template_enrollment_pink_room').product_variant_id,
            'product_template_tuition_pink_room': self.env.ref('demo_academic.product_template_tuition_pink_room').product_variant_id,
            'product_template_enrollment_blue_room': self.env.ref('demo_academic.product_template_enrollment_blue_room').product_variant_id,
            'product_template_tuition_blue_room': self.env.ref('demo_academic.product_template_tuition_blue_room').product_variant_id,
            'product_template_enrollment_primary_level': self.env.ref('demo_academic.product_template_enrollment_primary_level').product_variant_id,
            'product_template_tuition_primary_level': self.env.ref('demo_academic.product_template_tuition_primary_level').product_variant_id,
            'product_template_enrollment_secondary_level': self.env.ref('demo_academic.product_template_enrollment_secondary_level').product_variant_id,
            'product_template_tuition_secondary_level': self.env.ref('demo_academic.product_template_tuition_secondary_level').product_variant_id,
        }

        templates_data = [
            {
                'name': 'Pink Room - Initial Level',
                'plan_id': self.env.ref('sale_subscription.subscription_plan_month').id,
                'sale_order_template_line_ids': [
                    (0, 0, {'product_id': products['product_template_enrollment_pink_room'].id}),
                    (0, 0, {'product_id': products['product_template_tuition_pink_room'].id}),
                ],
            },
            {
                'name': 'Blue Room - Initial Level',
                'plan_id': self.env.ref('sale_subscription.subscription_plan_month').id,
                'sale_order_template_line_ids': [
                    (0, 0, {'product_id': products['product_template_enrollment_blue_room'].id}),
                    (0, 0, {'product_id': products['product_template_tuition_blue_room'].id}),
                ],
            },
            {
                'name': '1st Grade Primary Level - Primary Level',
                'plan_id': self.env.ref('sale_subscription.subscription_plan_month').id,
                'sale_order_template_line_ids': [
                    (0, 0, {'product_id': products['product_template_enrollment_primary_level'].id}),
                    (0, 0, {'product_id': products['product_template_tuition_primary_level'].id}),
                ],
            },
            {
                'name': '1st Year Secondary Level - Secondary Level',
                'plan_id': self.env.ref('sale_subscription.subscription_plan_month').id,
                'sale_order_template_line_ids': [
                    (0, 0, {'product_id': products['product_template_enrollment_secondary_level'].id}),
                    (0, 0, {'product_id': products['product_template_tuition_secondary_level'].id}),
                ],
            },
        ]

        self.create(templates_data)
