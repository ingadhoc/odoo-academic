##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import api, models, fields, _
from odoo.exceptions import UserError


class ResPartner(models.Model):

    _inherit = 'res.partner'
    _check_company_auto = True
    _check_company_domain = models.check_company_domain_parent_of

    parent_id = fields.Many2one(check_company=True)
    partner_type = fields.Selection([
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('administrator', 'Administrator'),
        ('gral_administrator', 'General Administrator'),
        ('parent', 'Relative'),
        ('other', 'Other'),
        ('family', 'Family'),
    ],
        change_default=True,
        string='Tipo de Contacto Académico',
        compute='_compute_partner_type',
        readonly=False,
        store=True,
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
    student_link_ids = fields.One2many(
        'res.partner.link', 'student_id', string='Contactos y Roles', copy=True,
        compute='_compute_student_links', readonly=False, store=True, recursive=True)

    @api.depends('parent_links_by_student', 'parent_id.student_link_ids')
    def _compute_student_links(self):
        """ Si se confirugan los contactos en la flia, los propagamos a los hijos. Lo hacemos así para que:
        a) en todo el codigo solo miremos siempre hijos, lo de la familia es un asistente
        b) si se marca llevar en estudiantes ya van a tener toda la data que tenía la familia """
        for rec in self.filtered(lambda x: x.partner_type == 'student' and x.parent_id and not x.parent_links_by_student):
            rec.student_link_ids = [(5, 0, 0)] + [(0, 0, {
                'relationship_id': x.relationship_id.id,
                'role_ids': x.role_ids,
                'partner_id': x.partner_id.id,
                'note': x.note}) for x in rec.parent_id.student_link_ids]

    partner_link_ids = fields.One2many('res.partner.link', 'partner_id', string='Roles', copy=True)
    links_by_student = fields.Boolean(string='Contactos y Roles por Estudiante')
    company_family_required = fields.Boolean(related='company_id.family_required')
    parent_links_by_student = fields.Boolean(related='parent_id.links_by_student', string="La familia define Contactos y Roles por Estudiante")
    # creamos nuevo campo porque el child_ids como ya esta en la vista nos propaga el mode kanban
    # al hacerlo con mode tree nos simplfica bastante la herencia de vista porque no tenemos que agregar en el quick
    # create tantas cosas
    student_ids = fields.One2many('res.partner', 'parent_id')
    company_id = fields.Many2one(compute='_compute_company_id', store=True, readonly=False)
    # company_type = fields.Selection(selection_add=[('family', 'Family')])
    # is_family = fields.Boolean()

    # @api.depends('is_family')
    # def _compute_company_type(self):
    #     families = self.filtered(lambda x: x.is_company and x.is_family)
    #     families.company_type = 'family'
    #     return super(ResPartner, self - families)._compute_company_type()

    # def _write_company_type(self):
    #     families = self.filtered(lambda x: x.company_type == 'family')
    #     families.is_company = True
    #     families.is_family = True
    #     return super(ResPartner, self - families)._write_company_type()

    @api.constrains('company_id', 'partner_type', 'parent_id')
    def _check_family_configured(self):
        if self.filtered(lambda x: x.partner_type == 'student' and x.company_id.family_required and x.parent_id.partner_type != 'family'):
            raise UserError('En la institucion, los estudiantes deben estar vinculados a una familia')

    @api.constrains('parent_id', 'partner_type')
    def _check_family_student_relation(self):
        if self.filtered(lambda x: x.partner_type != 'student' and x.parent_id.partner_type == 'family'):
            raise UserError('Los contactos de una familia solo pueden ser estudiantes')

    def _compute_related_user_id(self):
        for rec in self:
            rec.related_user_id = rec.user_ids and rec.user_ids[0]

    @api.depends('is_company')
    def _compute_partner_type(self):
        self.filtered(lambda x: x.is_company and x.partner_type).partner_type = False

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

    @api.depends('parent_id')
    def _compute_company_id(self):
        """
        Si soy parte de una compañía (o familia, es campo "parent_id"), queremos que todos los childs tengan misma company
        Ahora bien, si la compañía está compartida (parent_id = False) matenemos fleixibilidad con los hijos.
        Por defecto ponemos la company donde está parado el usuario pero permitimos sacarla o cambiarla.
        Un padre, madre o estudiante podrían en algunos casos de uso estar compartidos entre varias instituciones
        """
        for rec in self:
            rec.company_id = rec.parent_id.company_id or rec.env.company

    def _onchange_company_id(self):
        # anulamos el onchange nativo de odoo porque ahora lo hicimos compute
        return
