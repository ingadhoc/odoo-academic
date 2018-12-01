##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields


class AcademicDivision(models.Model):
    _name = 'academic.division'
    _description = 'division'

    name = fields.Char(
        required=True,
    )
