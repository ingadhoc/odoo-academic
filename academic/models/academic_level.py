##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import fields, models


class AcademicLevel(models.Model):
    _name = "academic.level"
    _description = "level"
    _sql_constraints = [
        (
            "unique_level_name",
            "UNIQUE(name)",
            "The level name must be unique.",
        )
    ]

    name = fields.Char(required=True)
