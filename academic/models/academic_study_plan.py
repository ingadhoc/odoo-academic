from odoo import fields, models


class StudyPlan(models.Model):
    _name = 'academic.study.plan'
    _description = 'Study Plan'

    name = fields.Char(string='Name')

    level_ids = fields.Many2many(
        'academic.level',
        'academic_study_plan_ids_level_ids_rel',
        'academic_study_plan_id',
        'level_id',
        string='Levels',
    )
