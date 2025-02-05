##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import fields, models


class AcademicPromotion(models.Model):
    _name = "academic.promotion"
    _description = "promotion"

    name = fields.Char(
        required=True,
    )
