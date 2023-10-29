##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields
# from odoo.exceptions import UserError


class ResPartner(models.Model):

    _name = 'res.partner.link'
    _description = 'res.partner.link'

    student_id = fields.Many2one('res.partner', 'Student', required=True, ondelete='cascade')
    relationship_id = fields.Many2one('res.partner.relationship', required=True, ondelete='restrict')
    role_ids = fields.Many2many('res.partner.role', string='Roles')
    partner_id = fields.Many2one('res.partner', required=True, ondelete='restrict')
    note = fields.Text(string="Notas")
