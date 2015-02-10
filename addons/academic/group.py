# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning


class group(models.Model):
    """"""

    _name = 'academic.group'
    _description = 'group'
    _rec_name = 'complete_name'

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        context={'default_is_company':True},
        default=lambda self: self.env['res.company']._company_default_get('academic.group')
        )
    type = fields.Selection(
        [(u'student', u'Student'), (u'teacher', u'Teacher'), (u'administrator', u'Administrator'), (u'gral_administrator', u'Gral. Administrator')],
        string='type'
        )
    year = fields.Integer(
        string='Year',
        required=True
        )
    division_id = fields.Many2one(
        'academic.division',
        string='Division',
        copy=False
        )
    level_id = fields.Many2one(
        'academic.level',
        string='Level',
        required=True
        )
    subject_id = fields.Many2one(
        'academic.subject',
        string='Subject',
        required=True
        )
    teacher_id = fields.Many2one(
        'res.partner',
        string='Teacher',
        required=True,
        context={'default_partner_type':'teacher'},
        domain=[('partner_type','=','teacher')]
        )
    student_ids = fields.Many2many(
        'res.partner',
        'academic_student_group_ids_student_ids_rel',
        'group_id',
        'partner_id',
        string='Student',
        context={'default_partner_type':'student'},
        domain=[('partner_type','=','student')]
        )
    complete_name = fields.Char(
        compute='_complete_name',
        string='Complete Name',
        store=True,
        )

    _constraints = [
        ('group_unique',
            'unique(subject_id, company_id, level_id, year, division_id)',
            'Group should be unique per Institution, Subject, Course-Division and Year')
    ]

    @api.one
    @api.depends(
        'year',
        'subject_id',
        'subject_id.name',
        'company_id',
        'company_id.name',
        'division_id',
        'division_id.name',
        )
    def _complete_name(self):
        """ Forms complete name of location from parent location to child location.
        @return: Dictionary of values
        """
        name = "%s - %s, %s - %s - %s - Año: %i" % (
            self.subject_id.name,
            self.company_id.name,
            self.level_id.name,
            self.division_id and ' ' + self.division_id.name or '',
            self.level_id.section_id.name,
            self.year,
            )
        self.complete_name = name

    def create_students_users(self, cr, uid, ids, context=None):
        '''
        This function create users if they don't exist for students related to this group.
        '''
        for group in self.browse(cr, uid, ids, context=context):
            partners = group.student_ids
            partner_ids = [x.id for x in partners]
            print 'partner_ids', partner_ids
            # Create users, if they already exists it will update grupos and activate them
            self.pool.get('res.partner').quickly_create_user(cr, uid, partner_ids, context=context)
        return False

    def print_users(self, cr, uid, ids, context=None):
        '''
        This function prints a report with users login and password. 
        '''
        assert len(ids) == 1, 'This option should only be used for a single id at a time'
        self.create_students_users(cr, uid, ids, context=context)
        return self.pool['report'].get_action(cr, uid, ids, 'academic_x.template_report_users', context=context)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
