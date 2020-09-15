##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import api, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    def _set_encrypted_password(self, uid, pw):
        """ Si es estudiante no limpiamos las password,
        solo guardamos la encriptada
        TODO deberiamos mejorar y solo guardar la password
        si venimos desde los groups, es decir forzando contraseña nosotros.
        Pero tendriamos que en ese caso ademas hacer que el init que borramos
        no limpie esas pass.
        """
        if self.has_group('academic.group_portal_student'):
            return self.env.cr.execute(
                "UPDATE res_users SET password=%s WHERE id=%s",
                (pw, uid))
        return super(ResUsers, self)._set_encrypted_password(uid, pw)

    def name_get(self):
        if self._context.get('show_login', False):
            return [(r.id, r.login) for r in self]
        return super().name_get()

    def _has_multiple_groups(self, group_ids):
        user_types_category = self.env.ref(
            'base.module_category_user_type', raise_if_not_found=False)
        # remove internal groups that inherit internal groups
        if user_types_category:
            internal_groups = self.env['res.groups'].search([
                ('category_id', '=', user_types_category.id),
                ('implied_ids.category_id', '=', user_types_category.id)])
            group_ids = list(set(group_ids) - set(internal_groups.ids))
        return super()._has_multiple_groups(group_ids)

    @api.model
    def systray_get_activities(self):
        """ We did this to avoid errors when use portal user when the module
        "Note" is not a depends of this module.
        Only apply this change if the user is portal.
        """
        if self.env.user.has_group('base.group_portal') \
            and self.env['ir.module.module'].sudo().search(
                [('name', '=', 'note')]).state == 'installed':
            self = self.sudo()
        return super(ResUsers, self).systray_get_activities()
