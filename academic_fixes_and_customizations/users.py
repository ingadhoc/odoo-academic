# -*- encoding: utf-8 -*-
from openerp.osv import osv, fields


class res_users(osv.osv):
    _inherit = 'res.users'

    """ Con esto hacemos que las passwords no se encripten asi se pueden
    imprimir en el reporte"""
    _columns = {
        'password': fields.char(
            'Password', size=64, invisible=True, copy=False,
            help="Keep empty if you don't want the user to be able to connect on the system."),
    }

    def _set_encrypted_password(self, cr, uid, id, encrypted, context=None):
        """ Store the provided encrypted password to the database, and clears
        any plaintext password

        :param uid: id of the current user
        :param id: id of the user on which the password should be set
        """
