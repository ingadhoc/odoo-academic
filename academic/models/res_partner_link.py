##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api
from odoo.exceptions import UserError


class ResPartner(models.Model):

    _name = 'res.partner.link'
    _description = 'res.partner.link'

    student_id = fields.Many2one('res.partner', 'Student or Family', required=True, ondelete='cascade')
    # student_id = fields.Many2one('res.partner', 'Student', ondelete='cascade')
    # family_id = fields.Many2one('res.partner', 'Family', ondelete='cascade')
    relationship_id = fields.Many2one('res.partner.relationship', required=True, ondelete='restrict')
    role_ids = fields.Many2many('res.partner.role', string='Roles')
    partner_id = fields.Many2one('res.partner', required=True, ondelete='restrict')
    note = fields.Text(string="Notas")

    # @api.constrains('student_id', 'family_id')
    # def _check_student_or_family(self):
    #     recs = self.filtered(lambda x: not x.student_id and not x.family_id)
    #     if recs:
    #         raise UserError('Los contactos y roles deben estar vinculados a una famila o a un estudiante')

    _sql_constraints = [
        ('link_unique',
         'unique(student_id, partner_id)',
         'El contacto debe ser agregado por unica vez en cada familia o estudiante')]
