##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields


class AcademicShift(models.Model):
    _name = 'academic.shift'
    _description = 'shift'

    name = fields.Char(
        required=True,
    )
