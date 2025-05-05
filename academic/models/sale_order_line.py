##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    group_id = fields.Many2one('academic.group')
    academic_product_type = fields.Selection(
        related='product_id.academic_product_type',
    )

