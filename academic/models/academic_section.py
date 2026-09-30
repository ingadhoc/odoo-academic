##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import Command, api, fields, models


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
        string="Next Study Plans",
        help="Study plans a student continues into after finishing this one, used by the"
        " re-enrollment wizard. With more than one the destination is picked by hand.",
    )
    level_line_ids = fields.One2many(
        "academic.section.level",
        "section_id",
        string="Levels Sequence",
        help="Levels of the study plan, in the order the student goes through them.",
    )
    level_ids = fields.Many2many(
        "academic.level",
        string="Levels",
        compute="_compute_level_ids",
        inverse="_inverse_level_ids",
    )
    sequence = fields.Integer(
        default=10,
    )

    @api.depends("level_line_ids.level_id")
    def _compute_level_ids(self):
        for rec in self:
            rec.level_ids = rec.level_line_ids.level_id

    def _inverse_level_ids(self):
        """Keeps level_ids usable as a plain m2m (data files, imports, existing views)."""
        for rec in self:
            lines = rec.level_line_ids
            commands = [Command.unlink(line.id) for line in lines if line.level_id not in rec.level_ids]
            sequence = max(lines.mapped("sequence"), default=0)
            for level in rec.level_ids - lines.level_id:
                sequence += 10
                commands.append(Command.create({"level_id": level.id, "sequence": sequence}))
            rec.level_line_ids = commands

    def _get_sorted_level_lines(self):
        # sorted explicitly: the o2m order can be stale in cache right after writing the sequence
        self.ensure_one()
        return self.level_line_ids.sorted(lambda x: (x.sequence, x.id))

    def _is_last_level(self, level):
        """True only when the plan has its sequence configured and `level` closes it, as
        opposed to a plan with no sequence at all, where nothing can be told apart."""
        lines = self._get_sorted_level_lines()
        return bool(lines) and lines[-1].level_id == level

    def _get_first_level(self):
        """Where a student coming from another plan starts. Empty without a sequence."""
        lines = self._get_sorted_level_lines()
        return lines[0].level_id if lines else self.env["academic.level"]

    def _get_next_level(self, level):
        lines = self._get_sorted_level_lines()
        for line, next_line in zip(lines, lines[1:]):
            if line.level_id == level:
                return next_line.level_id
        return self.env["academic.level"]
