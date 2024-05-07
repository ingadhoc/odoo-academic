##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import api, models, fields


class AcademicLevel(models.Model):

    _name = 'academic.level'
    _description = 'level'
    _order = 'sequence'

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
            rec.display_name = rec.name + ' - ' + rec.section_id.name

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('name', operator, name),
                      ('section_id.name', operator, name)]
            res = super().name_search(name=name, args=args + domain, operator=operator, limit=limit)
        else:
            res = super().name_search(name=name, args=args, operator=operator, limit=limit)
        return res
