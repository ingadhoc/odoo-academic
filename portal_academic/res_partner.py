# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import fields, api, models


class partner(models.Model):

    """"""

    _inherit = 'res.partner'

    @api.model
    def _default_template_user_id(self):
        partner_type = self.env.context.get(
            'partner_type', self.env.context.get(
                'default_partner_type', False))
        users = self.env['res.users']
        if partner_type == 'gral_administrator':
            users = self.env.ref(
                'portal_academic.gral_administrator_template_user')
        elif partner_type == 'administrator':
            users = self.env.ref(
                'portal_academic.administrator_template_user')
        elif partner_type == 'teacher':
            users = self.env.ref(
                'portal_academic.teacher_template_user')
        elif partner_type == 'parent':
            users = self.env.ref(
                'portal_academic.parent_template_user')
        elif partner_type == 'student':
            users = self.env.ref(
                'portal_academic.student_template_user')
        return users and users.id or users

    # Esto no lo venimos usando, es de la otra version de academic o de
    # integracion con parnter user
    template_user_id = fields.Many2one(
        'res.users',
        string="Template User",
        domain=[('active', '=', False)],
        default=_default_template_user_id)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
