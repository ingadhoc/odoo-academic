##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models


class ResUsers(models.Model):
    _inherit = 'res.users'

    def _set_encrypted_password(self, uid, pw):
        """ Si es estudiante no limpiamos las password, solo guardamos la encriptada
        TODO deberiamos mejorar y solo guardar la password si venimos desde los groups, es decir
        forzando contraseña nosotros. Pero tendriamos que en ese caso ademas hacer que el init que borramos
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
