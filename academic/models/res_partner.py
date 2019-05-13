##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import api, models, fields


class ResPartner(models.Model):

    _inherit = 'res.partner'

    @api.model
    def _default_template_user_id(self):
        partner_type = self.env.context.get(
            'partner_type',
            self.env.context.get('default_partner_type', False))
        user = False
        if partner_type == 'gral_administrator':
            user = self.env.ref(
                'academic.gral_administrator_template_user').id
        elif partner_type == 'administrator':
            user = self.env.ref(
                'academic.administrator_template_user').id
        elif partner_type == 'teacher':
            user = self.env.ref(
                'academic.teacher_template_user').id
        elif partner_type == 'parent':
            user = self.env.ref(
                'academic.parent_template_user')
        elif partner_type == 'student':
            user = self.env.ref(
                'academic.student_template_user').id
        return user

    partner_type = fields.Selection([
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('administrator', 'Administrator'),
        ('gral_administrator', 'General Administrator'),
        ('parent', 'Parent'),
        ('other', 'Other'),
    ],
        change_default=True,
    )
    section_id = fields.Many2one(
        'academic.section',
        string='Section',
    )
    promotion_id = fields.Many2one(
        'academic.promotion',
        string='Promotion',
    )
    teacher_group_ids = fields.One2many(
        'academic.group',
        'teacher_id',
        string='Groups',
    )
    student_group_ids = fields.Many2many(
        'academic.group',
        'academic_student_group_ids_student_ids_rel',
        'partner_id',
        'group_id',
        string='Groups',
    )
    template_user_id = fields.Many2one(
        'res.users',
        'Template User',
        domain=[('active', '=', False)],
        default=_default_template_user_id,
    )
    disabled_person = fields.Boolean(
        'Disabled Person?',
        help='¿Alumno/a con Dificultades de aprendizaje?'
    )
    sex = fields.Selection(
        [('M', 'Male'), ('F', 'Female')],
        string='Sex',
    )
    file_number = fields.Char(
        copy=False,
    )
    birthdate = fields.Date(
        copy=False,
    )
    admission_date = fields.Date(
    )
    exit_date = fields.Char(
    )
    medical_insurance = fields.Char(
        copy=False,
    )
    relationship_id = fields.Many2one(
        'res.partner.relationship',
    )
    withdraw = fields.Boolean(
    )

    @api.constrains('is_company')
    @api.onchange('is_company')
    def _check_partner_type(self):
        recs = self.filtered(lambda x: x.is_company and x.partner_type)
        recs.update({'partner_type': False})

    @api.multi
    def quickly_create_portal_user(self, portal_group):
        """ Metodo que crea o activa usuario inactivo en el grupo portal que
        se defina
        """
        wizard = self.env['portal.wizard'].with_context(
            default_active_ids=self.ids, active_ids=self.ids).create({
                'portal_id': portal_group,
            })
        wizard.onchange_portal_id()
        wizard.user_ids.write({'in_portal': True})
        wizard.action_apply()
        # res_users = self.pool.get('res.users')
        # # Make this an option
        # context = dict(context or {}, no_reset_password=True)

        # for partner in self.browse(cr, SUPERUSER_ID, ids, context):
        #     group_ids = []
        #     if not partner.template_user_id:
        #         raise osv.except_osv(_('Non template user selected!'),
        #                              _('Please define a template user
        #  for this partner: "%s" (id:%d).') % (partner.name, partner.id))
        #     group_ids = [x.id for x in partner.template_user_id.groups_id]
        #     user_ids = self.retrieve_user(cr, SUPERUSER_ID, partner, context)
        #     # create a user if necessary, and make sure it is in the portal
        #     # group
        #     if not user_ids:
        #         user_ids = [
        #             self._create_user(cr, SUPERUSER_ID, partner, context)]
        #     res_users.write(
        #         cr, SUPERUSER_ID, user_ids, {
        # 'active': True, 'groups_id': [(6, 0, group_ids)]})
        #     # prepare for the signup process
        #     # TODO make an option of this
        #     # partner.signup_prepare()
        #     # TODO option to send or not email
        #     # self._send_email(cr, uid, partner, context)
        #     elif user_ids:
        #         # deactivate user
        #         res_users.write(cr,
        # SUPERUSER_ID, user_ids, {'active': False})
