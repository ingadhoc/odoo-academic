##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import fields, models


class AcademicSectionLevel(models.Model):
    _name = "academic.section.level"
    _description = "Study Plan Level"
    _order = "sequence, id"
    _rec_name = "level_id"

    _level_unique = models.Constraint(
        "unique(section_id, level_id)",
        "Each level can only be added once per study plan.",
    )

    section_id = fields.Many2one(
        "academic.section",
        string="Study Plan",
        required=True,
        ondelete="cascade",
        index=True,
    )
    level_id = fields.Many2one("academic.level", string="Level", required=True)
    sequence = fields.Integer(default=10)
