from odoo import models, fields


class ResPartnerRelationship(models.Model):

    _name = 'res.partner.relationship'
    _description = 'Contacts Relationship'

    name = fields.Char(
        required=True,
    )
