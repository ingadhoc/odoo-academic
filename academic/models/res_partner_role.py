##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields


class ResPartner(models.Model):

    _name = 'res.partner.role'
    _description = 'res.partner.role'

    name = fields.Char(required=True)
    # TODO tal vez agregar un selection de los tipos fuertes y permitir abm? por ahora vamos con los
    # external ids
    # name = fields.Char(required=True)
    color = fields.Integer('Color Index',)
