##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields


class ResPartner(models.Model):

    _name = 'res.partner.family'
    _description = 'res.partner.family'

    name = fields.Char(required=True)
    student_ids = fields.One2many('res.partner', 'family_id', 'Students')
    contact_ids = fields.One2many('res.partner', 'family_id', 'Students')
    student_link_ids = fields.One2many('res.partner.link', 'student_id', string='Contactos y Roles')

    # TODO tal vez agregar un selection de los tipos fuertes y permitir abm? por ahora vamos con los
    # external ids
    # name = fields.Char(required=True)
