##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields


class AcademicObservationCategory(models.Model):

    _name = 'academic.observation_category'
    _description = 'observation_category'

    name = fields.Char(
        required=True,
        translate=True,
    )
    dont_consider = fields.Boolean(
        string='Don not Consider?',
    )
