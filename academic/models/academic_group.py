##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import api, models, fields, _
from datetime import date


class AcademicGroup(models.Model):
    _name = 'academic.group'
    _description = 'group'

    type = fields.Selection([
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('administrator', 'Administrator'),
        ('gral_administrator', 'gral_administrator')]
    )
    year = fields.Integer(
        required=True,
        default=date.today().year,
    )
    division_id = fields.Many2one(
        'academic.division',
        string='Division',
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        context={'default_is_company': True},
        default=lambda s: s.env['res.company']._company_default_get(
            'academic.group'),
    )
    level_id = fields.Many2one(
        'academic.level',
        string='Level',
        required=True,
    )
    subject_id = fields.Many2one(
        'academic.subject',
        string='Subject',
        required=True,
    )
    teacher_id = fields.Many2one(
        'res.partner',
        string='Teacher',
        required=True,
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
    group_evaluation_ids = fields.One2many(
        'academic.group_evaluation',
        'group_id',
        string='Evaluations',
        context={'from_group': True},
    )

    complete_name = fields.Char(
        compute='_compute_complete_name',
    )

    _sql_constraints = [
        ('group_unique',
         'unique(subject_id, company_id, level_id, year, division_id)',
         'Group should be unique per Institution, Subject,'
         ' Course-Division and Year')]

    def name_get(self):
        # always return the full hierarchical name
        res = []
        for rec in self.filtered('complete_name'):
            name = rec.complete_name
            res.append((rec.id, name))
        return res

    @api.depends(
        'subject_id',
        'company_id',
        'level_id',
        'division_id',
        'year')
    def _compute_complete_name(self):
        """ Forms complete name of location from parent location to
         child location.
        @return: Dictionary of values
        """
        for line in self:
            name = line.subject_id.name
            name += ' - ' + line.company_id.name
            name += ', ' + line.level_id.name
            if line.division_id:
                name += ' ' + line.division_id.name
            name += ' - ' + line.level_id.section_id.name
            name += ' - ' + _('Year: ') + str(line.year)
            line.complete_name = name

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = [
                '|', '|', ('subject_id.name', operator, name),
                ('company_id.name', operator, name),
                ('level_id.name', operator, name),
                ('year', operator, name)
            ]
            result = self.search(args + domain, limit=limit).name_get()
        else:
            result = self.search(args, limit=limit).name_get()
        return result

    @api.multi
    def copy(self, default=None):
        if default is None:
            default = {}
        default = default.copy()
        default['division_id'] = False
        default['group_evaluation_ids'] = []
        return super(AcademicGroup, self).copy(default)

    @api.multi
    def create_students_users(self):
        '''
        This function create users if they don't exist for students related
         to this group.
        '''
        # Create users, if they already exists it will update
        #  grupos and activate them
        self.student_ids.quickly_create_portal_user(
            self.env.ref('academic.group_portal_student').id)

    @api.multi
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
