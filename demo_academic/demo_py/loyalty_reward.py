##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import api, models


class LoyaltyReward(models.Model):
    _inherit = 'loyalty.reward'

    @api.model
    def _init_demo_base(self):
        self.env['loyalty.reward'].create({
            'discount': 10,
            'discount_applicability': 'specific',
            'discount_product_domain': str([
                "&",
                ("recurring_invoice", "=", True),
                ('product_variant_ids.name', 'in', ['Tuition', 'Arancel']),
            ]),
            'description': "10% discount",
            'discount_line_product_id': self.env.ref('demo_academic.product_template_discount_sibling').product_variant_id.id,
            'program_id': self.env.ref('demo_academic.loyalty_program_discount_sibling').id
        })

        self.env['loyalty.reward'].create({
            'discount': 20,
            'discount_applicability': 'specific',
            'discount_product_domain': str([
                "&",
                ("recurring_invoice", "=", True),
                ('product_variant_ids.name', 'in', ['Tuition', 'Arancel']),
            ]),
            'description': "20% discount",
            'discount_line_product_id': self.env.ref('demo_academic.product_template_official_discount').product_variant_id.id,
            'program_id': self.env.ref('demo_academic.loyalty_program_discount_official').id
        })
