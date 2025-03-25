##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import api, fields, models


class CrmLead(models.Model):
    _inherit = "crm.lead"

    group_id = fields.Many2one('academic.group', compute='_compute_group', inverse='_inverse_group')

    def _compute_group(self):
        for rec in self:
            rec.group_id = rec.env['academic.group.link'].search([('lead_id', '=', rec.id)], limit=1).group_id

    def _inverse_group(self):
        for rec in self:
            if not rec.group_id:
                rec.env['academic.group.link'].search([('lead_id', '=', rec.id)], limit=1).unlink()

            if not rec.partner_id:
                continue

            if rec.group_id:
                link = rec.env['academic.group.link'].search([('group_id', '=', rec.group_id.id), ('student_id', '=', rec.partner_id.id)], limit=1)
                if link:
                    link.group_id = rec.group_id.id
                else:
                    rec.group_id.academic_group_link_ids = [(0, 0, {'student_id': rec.partner_id.id, 'lead_id': rec.id})]

    @api.ondelete(at_uninstall=False)
    def _prevent_unlink_if_group_link_protected(self):
        """ Al eliminar un lead, se intenta desvincular el group link asociado.
        Si el vínculo con el grupo (group link) ya avanzó a un estado protegido
        (por ejemplo, con suscripciones activas u otras restricciones), el propio
        modelo `academic.group.link` bloqueará el borrado gracias a sus restricciones
        """
        self.filtered('group_id').group_id = False
