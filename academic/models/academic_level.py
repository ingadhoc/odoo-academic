##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import api, models, fields


class AcademicLevel(models.Model):

    _name = 'academic.level'
    _description = 'level'
    _order = 'sequence'
    _rec_names_search = ['name', 'section_id.name']

    sequence = fields.Integer(
        string='Sequence'
    )
    name = fields.Char(
        required=True,
        translate=True,
    )
    section_id = fields.Many2one(
        'academic.section',
        string='Section',
        required=True,
    )
    group_ids = fields.One2many(
        'academic.group',
        'level_id',
        string='Groups',
    )

    @api.depends('name', 'section_id.name')
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = rec.name + ' - ' + rec.section_id.name if rec.name else ''
