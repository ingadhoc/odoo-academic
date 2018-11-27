##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields


class AcademicSection(models.Model):

    _name = 'academic.section'
    _description = 'section'

    name = fields.Char(
        required=True,
    )
