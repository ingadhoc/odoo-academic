##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields
from odoo.addons.auth_crypt.models.res_users import ResUsers


class ResUsers(models.Model):
    _inherit = 'res.users'

    def _set_encrypted_password(self, encrypted):
        """ Si es estudiante no limpiamos las password, solo guardamos la encriptada
        TODO deberiamos mejorar y solo guardar la password si venimos desde los groups, es decir
        forzando contraseña nosotros. Pero tendriamos que en ese caso ademas hacer que el init que borramos
        no limpie esas pass.
        """
        if self.has_group('academic.group_portal_student'):
            return self.env.cr.execute(
                "UPDATE res_users SET password_crypt=%s WHERE id=%s",
                (encrypted, self.id))
        return super(ResUsers, self)._set_encrypted_password(encrypted)

    def name_get(self):
        if self._context.get('show_login', False):
            return [(r.id, r.login) for r in self]
        return super().name_get()
