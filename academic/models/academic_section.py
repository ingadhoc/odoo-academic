##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import fields, models


class AcademicSection(models.Model):
    _name = "academic.section"
    _description = "section"
    _order = "sequence"

    name = fields.Char(
        required=True,
    )
    correlative_ids = fields.Many2many(
        "academic.section",
        "academic_section_correlative_ids_rel",
        "section_id",
        "correlative_id",
        string="Correlative Study Plans",
    )
    level_ids = fields.Many2many(
        "academic.level",
        "academic_section_level_ids_rel",
        "section_id",
        "level_id",
        string="Levels",
    )
    sequence = fields.Integer(
        default=10,
    )
