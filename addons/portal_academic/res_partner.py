# -*- coding: utf-8 -*-
from openerp import fields, api, models


class partner(models.Model):

    """"""

    _inherit = 'res.partner'

    @api.model
    def _default_template_user_id(self):
        partner_type = self.env.context.get(
            'partner_type', self.env.context.get(
                'default_partner_type', False))
        group_ids = self.env['res.users']
        if partner_type == 'gral_administrator':
            group_ids = self.env.ref(
                'portal_academic.gral_administrator_template_user')
        elif partner_type == 'administrator':
            group_ids = self.env.ref(
                'portal_academic.administrator_template_user')
        elif partner_type == 'teacher':
            group_ids = self.env.ref(
                'portal_academic.teacher_template_user')
        elif partner_type == 'student':
            group_ids = self.env.ref(
                'portal_academic.student_template_user')
        return group_ids and group_ids.id or group_ids

    template_user_id = fields.Many2one(
        'res.users',
        string="Template User",
        domain=[('active', '=', False)],
        default=_default_template_user_id)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
