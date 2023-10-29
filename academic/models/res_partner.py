##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import api, models, fields, _
from odoo.exceptions import UserError


class ResPartner(models.Model):

    _inherit = 'res.partner'

    partner_type = fields.Selection([
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('administrator', 'Administrator'),
        ('gral_administrator', 'General Administrator'),
        ('parent', 'Relative'),
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
        string='Teacher Groups',
    )
    student_group_ids = fields.Many2many(
        'academic.group',
        'academic_student_group_ids_student_ids_rel',
        'partner_id',
        'group_id',
        string='Student Groups',
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
    exit_date = fields.Date(
    )
    medical_insurance = fields.Char(
        copy=False,
    )
    dni = fields.Integer(
        'DNI',
    )
    related_user_id = fields.Many2one(
        'res.users',
        compute='_compute_related_user_id',
    )
    partner_link_ids = fields.One2many('res.partner.link', 'student_id', string='Vínculos')

    def _compute_related_user_id(self):
        for rec in self:
            rec.related_user_id = rec.user_ids and rec.user_ids[0]

    @api.onchange('is_company')
    def _check_partner_type(self):
        for record in self.filtered(lambda x: x.is_company and x.partner_type):
            record.partner_type = False

    def write(self, vals):
        if 'is_company' in vals and vals.get('is_company'):
            vals['partner_type'] = False
        return super(ResPartner, self).write(vals)

    def quickly_create_portal_user(self):
        """ Metodo que crea o activa usuario inactivo en el grupo portal que
        se defina
        """
        # TODO: el metodo onchange_portal_id no existe.
        # Esto dejo de usarse pero queda el codigo por posible implementacion a futuro
        raise UserError(_("Esta función se encuentra en desarrollo!"))
        wizard = self.env['portal.wizard'].with_context(
            default_active_ids=self.ids, active_ids=self.ids,
            active_id=self.ids and self.ids[0] or False,
            active_model='res.partner').create({})
        wizard.user_ids.write({'in_portal': True})
        wizard.action_apply()
