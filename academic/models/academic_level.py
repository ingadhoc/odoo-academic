##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import fields, models


class AcademicLevel(models.Model):
    _name = "academic.level"
    _description = "level"
    _unique_level_name = models.Constraint(
        "UNIQUE(name)",
        "The level name must be unique.",
    )

    name = fields.Char(required=True)
