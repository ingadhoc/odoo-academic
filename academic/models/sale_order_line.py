##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    group_id = fields.Many2one("academic.group", compute="_compute_group_id", store=True, readonly=False)
    academic_product_type = fields.Selection(
        related="product_id.academic_product_type",
    )

    @api.depends("product_id")
    def _compute_group_id(self):
        for rec in self:
            if rec.product_id.academic_product_type and rec.order_id.opportunity_id.group_id:
                rec.group_id = rec.order_id.opportunity_id.group_id
            else:
                rec.group_id = False
