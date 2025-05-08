from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    academic_product_type = fields.Selection(
        selection=[
            ("main", "Main"),
            ("registration", "Registration"),
        ],
    )
