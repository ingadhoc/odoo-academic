# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import fields, api, models


class PortalWizard(models.TransientModel):
    _inherit = 'portal.wizard'

    @api.model
    def _default_portal(self):
        self._context
        active_model = self._context.get('active_model')
        active_id = self._context.get('active_id')
        if active_model == 'res.partner' and active_id:
            partner_type = self.env[
                active_model].browse(active_id).partner_type
            # template_user_id = self.env[active_model].with_context(
            # partner_type=partner_type)._default_template_user_id()
            groups = self.env['res.groups']
            if partner_type == 'gral_administrator':
                groups = self.env.ref(
                    'portal_academic.group_portal_gral_administrator')
            elif partner_type == 'administrator':
                groups = self.env.ref(
                    'portal_academic.group_portal_administrator')
            elif partner_type == 'teacher':
                groups = self.env.ref(
                    'portal_academic.group_portal_teacher')
            elif partner_type == 'parent':
                groups = self.env.ref(
                    'portal_academic.group_portal_parent')
            elif partner_type == 'student':
                groups = self.env.ref(
                    'portal_academic.group_portal_student')
            return groups.id
        return super(PortalWizard, self)._default_portal()

    portal_id = fields.Many2one(
        default=_default_portal)
