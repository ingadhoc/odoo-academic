##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields


class ResUsers(models.Model):
    _inherit = 'res.users'

    # """ Con esto hacemos que las passwords no se encripten asi se pueden
    # imprimir en el reporte"""
    # password = fields.Char(
    #     'Password',
    #     size=64,
    #     invisible=True,
    #     copy=False,
    #     help="Keep empty if you don't want the user to be able"
    #     " to connect on the system.",
    # )

    # def _set_encrypted_password(self, encrypted):
    #     """ Store the provided encrypted password to the database, and clears
    #     any plaintext password

    #     :param uid: id of the current user
    #     :param id: id of the user on which the password should be set
    #     """
