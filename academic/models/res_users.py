##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields
from odoo.addons.auth_crypt.models.res_users import ResUsers


def new_init(self):
    """Moneky patch para desactivar crear los hash"""
    pass


ResUsers.init = new_init


class ResUsers(models.Model):
    _inherit = 'res.users'

    """ Con esto hacemos que las passwords no se encripten asi se pueden
    imprimir en el reporte"""
    password = fields.Char(
        'Password',
        size=64,
        invisible=True,
        copy=False,
        help="Keep empty if you don't want the user to be able"
        " to connect on the system.",
    )

    def _set_encrypted_password(self, encrypted):
        """ Store the provided encrypted password to the database, and clears
        any plaintext password

        :param uid: id of the current user
        :param id: id of the user on which the password should be set
        """

    def name_get(self):
        if self._context.get('show_login', False):
            return [(r.id, r.login) for r in self]
        return super().name_get()
