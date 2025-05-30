##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import fields, models


class AcademicYear(models.Model):
    _name = "academic.year"
    _description = "Academic Year"
    _order = "date_start desc"

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    date_start = fields.Date(required=True)
    date_end = fields.Date(required=True)
    group_ids = fields.One2many(
        "academic.group",
        "year_id",
    )

    _sql_constraints = [
        ("name_unique", "unique(name)", "Name must be unique!"),
        ("date_check", "check(date_start <= date_end)", "The start date must be before or equal to the end date!"),
    ]
