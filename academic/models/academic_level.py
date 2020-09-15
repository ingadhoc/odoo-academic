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
    survey_ids = fields.Many2many(
        'survey.survey',
        'academic_survey_ids_level_ids_rel',
        'level_id',
        'survey_id',
        string='Surveys',
    )

    @api.multi
    def name_get(self):
        # always return the full hierarchical name
        res = []
        for rec in self:
            name = rec.name
            name += ' - ' + rec.section_id.name
            res.append((rec.id, name))
        return res

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('name', operator, name),
                      ('section_id.name', operator, name)]
            result = self.search(args + domain, limit=limit).name_get()
        else:
            result = self.search(args, limit=limit).name_get()
        return result
