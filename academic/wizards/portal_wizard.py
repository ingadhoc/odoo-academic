from odoo import fields, api, models


class PortalWizard(models.TransientModel):
    _inherit = 'portal.wizard'

    @api.model
    def _default_portal(self):
        active_model = self._context.get('active_model')
        active_id = self._context.get('active_id')
        if active_model == 'res.partner' and active_id:
            partner_type = self.env[
                active_model].browse(active_id).partner_type
            groups = self.env['res.groups']
            if partner_type == 'gral_administrator':
                groups = self.env.ref(
                    'academic.group_portal_gral_administrator')
            elif partner_type == 'administrator':
                groups = self.env.ref(
                    'academic.group_portal_administrator')
            elif partner_type == 'teacher':
                groups = self.env.ref(
                    'academic.group_portal_teacher')
            elif partner_type == 'parent':
                groups = self.env.ref(
                    'academic.group_portal_parent')
            elif partner_type == 'student':
                groups = self.env.ref(
                    'academic.group_portal_student')
            return groups.id
        return super(PortalWizard, self)._default_portal()

    portal_id = fields.Many2one('res.groups', default=_default_portal)

    def action_grant_access_all(self):
        for wizard_user in self.user_ids:
            if not wizard_user.is_portal and not wizard_user.is_internal and wizard_user.email_state == 'ok':
                wizard_user.action_grant_access()
        return self._action_open_modal()
