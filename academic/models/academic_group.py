##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import api, models, fields, _
from datetime import date
from odoo.exceptions import UserError
import random
import string


class AcademicGroup(models.Model):
    _name = 'academic.group'
    _description = 'group'
    _order = "company_id, year desc, level_id asc, division_id asc"
    _rec_names_search = ['level_id.name', 'level_id.section_id.name', 'division_id.name', 'year', 'subject_id.name']

    _sql_constraints = [
        ('group_unique',
         'unique(subject_id, company_id, parent_id, shift_id, level_id, year, division_id)',
         'Group should be unique per Institution, Subject, Course-Division and Year')]

    # virtual_group = fields.Boolean()
    year = fields.Integer(
        required=True,
        default=date.today().year,
        compute='_compute_year',
        store=True,
        readonly=False,
        recursive=True,
        precompute=True,
    )
    division_id = fields.Many2one(
        'academic.division',
        string='Division',
    )
    shift_id = fields.Many2one(
        'academic.shift',
        string='Shift',
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        context={'default_is_company': True},
        default=lambda self: self.env.company,
        compute='_compute_company',
        store=True,
        readonly=False,
        recursive=True,
        precompute=True,
    )
    study_plan_level_ids = fields.Many2many(related='company_id.study_plan_id.level_ids')
    level_id = fields.Many2one(
        'academic.level',
        string='Level',
        required=True,
        compute='_compute_level',
        store=True,
        readonly=False,
        recursive=True,
        precompute=True,
    )
    subject_id = fields.Many2one(
        'academic.subject',
        string='Subject',
        required=False,
        compute='_compute_subject',
        store=True,
        readonly=False,
        recursive=True,
    )
    teacher_id = fields.Many2one(
        'res.partner',
        string='Teacher',
        required=False,
        context={'default_partner_type': 'teacher'},
        domain=[('partner_type', '=', 'teacher')],
    )
    student_ids = fields.Many2many(
        'res.partner',
        'academic_student_group_ids_student_ids_rel',
        'group_id',
        'partner_id',
        string='Student',
        context={'default_partner_type': 'student'},
        domain=[('partner_type', '=', 'student')],
    )
    complete_name = fields.Char(
        compute='_compute_complete_name',
    )
    # TODO borrar en 18 si nadie se quejo de que lo sacamos de UI
    sequence = fields.Integer(help='Used to order Groups', default=10)
    active = fields.Boolean(default=True)
    student_ids_count = fields.Integer(
        string='Student Count',
        compute='_compute_student_ids_count',
        store=True,
        readonly=False,
    )
    capacity = fields.Integer(compute='_compute_capacity', store=True, readonly=False, recursive=True,)
    vacancy = fields.Integer(compute='_compute_vacancy', store=True, readonly=False)
    parent_id = fields.Many2one('academic.group',)
    child_ids = fields.One2many('academic.group', 'parent_id')

    @api.depends('child_ids.capacity')
    def _compute_capacity(self):
        for rec in self.filtered('child_ids'):
            rec.capacity = sum(rec.child_ids.mapped('capacity'))

    @api.depends('capacity', 'student_ids_count')
    def _compute_vacancy(self):
        for rec in self:
            rec.vacancy = rec.capacity - rec.student_ids_count

    @api.depends('parent_id.level_id')
    def _compute_level(self):
        for rec in self.filtered('parent_id'):
            rec.level_id = rec.parent_id.level_id

    @api.depends('parent_id.company_id')
    def _compute_company(self):
        for rec in self.filtered('parent_id'):
            rec.company_id = rec.parent_id.company_id

    @api.depends('parent_id.subject_id')
    def _compute_subject(self):
        for rec in self.filtered('parent_id'):
            rec.subject_id = rec.parent_id.subject_id

    @api.depends('parent_id.year')
    def _compute_year(self):
        for rec in self.filtered('parent_id'):
            rec.year = rec.parent_id.year

    def _compute_display_name(self):
        for rec in self.filtered('complete_name'):
            rec.display_name = rec.complete_name

    @api.depends(
        'subject_id',
        'company_id',
        'level_id',
        'division_id',
        'year')
    def _compute_complete_name(self):
        for line in self:
            name = line.company_id.name or ''
            name += ', {}'.format(line.level_id.name or '')

            if line.division_id:
                name += ' {}'.format(line.division_id.name or '')

            section_name = line.level_id.section_id.name if line.level_id and line.level_id.section_id else ''
            if section_name:
                name += ' - {}'.format(section_name)

            name += ' - {}{}'.format(_('Year: '), line.year or '')

            line.complete_name = name.strip(', - ')

    def create_students_users(self):
        '''
        This function create users if they don't exist for students related
         to this group.
        '''
        self.student_ids.quickly_create_portal_user()
        # Creamos contrasenas para todos los students que no tengan una
        # explicita (no hashed)
        for user in \
                self.student_ids.mapped('user_ids')\
                    .filtered(lambda x: not x.password):
            user.password = ''.join(random.choice(
                string.ascii_uppercase + string.digits) for _ in range(6))

    def print_users(self):
        '''
        This function prints a report with users login and password.
        '''
        self.ensure_one()
        self.create_students_users()
        report = self.env['ir.actions.report'].search(
            [('report_name', '=', 'academic.template_report_users')],
            limit=1).report_action(self)
        return report

    @api.depends('child_ids.student_ids', 'student_ids')
    def _compute_student_ids_count(self):
        for group in self:
            group.student_ids_count = len(group.student_ids) + sum(group.child_ids.mapped('student_ids_count'))

    def _get_all_student(self):
        all_student_ids = self.student_ids.ids
        for child in self.child_ids:
            all_student_ids.extend(child._get_all_student())
        return list(set(all_student_ids))

    def open_student_list(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id('academic.action_academic_partner_students')

        all_student = self._get_all_student()
        if all_student:
            action['domain'] = [('partner_type', '=', 'student'), ('id', 'in', all_student)]

        return action

    @api.ondelete(at_uninstall=False)
    def _protect_unlink(self):
        if self.filtered(lambda x: x.student_ids or x.child_ids):
            raise UserError('No se pueden borrar groups con estudiantes o que tengan grupos hijos')
