##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields
import datetime


class ResCompany(models.Model):

    _inherit = 'res.company'

    company_group_ids = fields.One2many(
        'academic.group',
        'company_id',
        string='Groups',
    )
    study_plan_id = fields.Many2one(
        comodel_name='academic.study.plan',
        string='Plan de Estudio'
    )
    family_required = fields.Boolean()

    def create_study_plan_groups(self):
        for rec in self:
            for level in rec.study_plan_id.level_ids:
                year = fields.Date.add(fields.Date.today(), years=1).year
                existing_groups_levels = self.env['academic.group'].search(
                    [('year', '=', year), ('level_id', '=', level.id), ('company_id', '=', rec.id), ('parent_id', '=', False)]).mapped('level_id')
                if level in existing_groups_levels:
                    continue
                self.env['academic.group'].create({
                    'year': year,
                    'level_id': level.id,
                    'company_id': rec.id,
                })

    def create_groups_next_year(self):
        self.create_study_plan_groups()
        for rec in self:
            year = fields.Date.today().year
            for group in self.env['academic.group'].search([('year', '=', year), ('company_id', '=', rec.id), ('parent_id', '!=', False)]):
                if group.level_id not in group.study_plan_level_ids:
                    # TODO ver que hacemos con groups que no estan en plan de estudio
                    continue
                current_index = group.study_plan_level_ids.ids.index(group.level_id.id)
                # este seria el ultimo año del plan de estudios
                if current_index + 1 < len(group.study_plan_level_ids):
                    next_level = group.study_plan_level_ids[current_index + 1]
                    parent_group = self.env['academic.group'].search(
                        [('year', '=', year + 1), ('level_id', '=', next_level.id), ('company_id', '=', rec.id), ('parent_id', '=', False)])
                    group.copy({
                        'year': year + 1,
                        'level_id': next_level.id,
                        'parent_id': parent_group.id,
                        # por ahora nos pidieron que no copiemos estudiantes
                        'student_ids': [(5, 0, 0)],
                    })
                # existing_groups_levels = self.env['academic.group'].search(
                #     [('year', '=', year), ('level_id', '=', level.id), ('company_id', '=', rec.id), ('parent_id', '=', False)]).mapped('level_id')
            # for group in rec.company_group_ids:
            #         if current_index + 1 < len(group.study_plan_level_ids):
            #             next_level = group.study_plan_level_ids[current_index + 1]
