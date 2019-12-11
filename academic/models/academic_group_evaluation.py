##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import api, models, fields, _
from odoo.exceptions import UserError
import uuid


class AcademicGroupEvaluation(models.Model):

    _name = 'academic.group_evaluation'
    _description = 'group_evaluation'
    _inherit = ['mail.thread']

    date_open = fields.Datetime(
        readonly=True,
    )
    date_close = fields.Datetime(
        readonly=True,
    )
    observation = fields.Text(
        string='Observations',
        states={'closed': [('readonly', True)]},
    )
    contingencies = fields.Boolean(
        string='Contingencies?',
        states={'closed': [('readonly', True)]}
    )
    state = fields.Selection(
        [('invisible', 'Invisible'),
         ('visible', 'Visible'),
         ('open', 'Open'),
         ('closed', 'Closed')],
        readonly=True,
        required=True,
        default='invisible',
    )
    group_id = fields.Many2one(
        'academic.group',
        string='Group',
        readonly=True,
        required=True,
        states={'invisible': [('readonly', False)]},
        ondelete='cascade',
        default=lambda self: self._context.get('group_id', False),
    )
    survey_id = fields.Many2one(
        'survey.survey',
        string='Evaluation',
        readonly=True,
        required=True,
        states={'invisible': [('readonly', False)]},
        context={'default_is_evaluation': True},
        domain=[('is_evaluation', '=', True)],
        ondelete='cascade',
        default=lambda self: self._context.get('survey_id', False),
    )
    user_input_ids = fields.One2many(
        'survey.user_input',
        'group_evaluation_id',
        string='Users Inputs',
        states={'closed': [('readonly', True)]},
    )

    company_id = fields.Many2one(
        'res.company',
        related='group_id.company_id',
    )
    time_used = fields.Float(
        compute='_compute_time_used',
    )

    _sql_constraints = [
        ('group_uniq', 'unique(group_id, survey_id)',
         'There can not be two groups for the same evaluation.'), ]

    @api.multi
    def _compute_time_used(self, names):
        for record in self:
            if record.date_open:
                date_open = fields.Datetime.from_string(record.date_open)
            if record.date_close:
                date_close = fields.Datetime.from_string(record.date_close)
            if date_open and date_close:
                record.time_used = date_close - date_open

    @api.multi
    def unlink(self):
        for record in self:
            if record.state != 'invisible':
                raise UserError(
                    _('Solo pueden borrarse evaluaciones en estado invisible.\
                        ATENCION: esa borrará los registros correspondientes a\
                        la evaluación del grupo, en caso de que haya\
                        respuestas registradas'))
        return super(AcademicGroupEvaluation, self).unlink()

    def set_invisible(self):
        self.write({'state': 'invisible'})

    def set_visible(self):
        self.write({'state': 'visible'})

    def set_closed(self):
        self.ensure_one()
        user_input_obj = self.env['survey.user_input']
        user_inputs = user_input_obj.search(
            [('group_evaluation_id', 'in', self.ids)])
        for user_input_state in user_inputs.read(['state']):
            if user_input_state['state'] != 'done':
                raise UserError(_(
                    "You can not close a Group Evaluation with user inputs"
                    " not done. First you should close each user input."))
        self.write({'state': 'closed', 'date_close': fields.Datetime.now()})

    @api.multi
    def print_users(self):
        '''
        This function prints a report with users login and password.
        '''
        # TODO: print students, teachers or administrators
        #  depending on the type of evaluation group

        self.ensure_one()
        self.group_id.self.create_students_users()
        report = self.env['ir.actions.report'].search(
            [('report_name', '=', 'academic.template_group_ev_report_users')],
            limit=1).report_action(self)
        return report

    @api.multi
    def action_send_survey(self):
        survey_response_obj = self.env['survey.user_input']
        partner_obj = self.env['res.partner']

        def create_response(survey_id, answered_by, apply_to,
                            group_evaluation_id):
            response_ids = survey_response_obj.search([
                ('survey_id', '=', survey_id),
                ('partner_id', '=', answered_by),
                ('apply_to_id', '=', apply_to),
                ('group_evaluation_id', '=', group_evaluation_id),
            ])
            if not response_ids:
                token = uuid.uuid4().__str__()
                return survey_response_obj.create({
                    'survey_id': survey_id,
                    'date_create': fields.Datetime.now(),
                    'type': 'link',
                    'state': 'new',
                    'token': token,
                    'partner_id': answered_by,
                    'apply_to_id': apply_to,
                    'group_evaluation_id': group_evaluation_id})
            return False

        for group_evaluation in self:
            survey_id = group_evaluation.survey_id.id
            # group_id = group_evaluation.group_id.id
            group_evaluation_id = group_evaluation.id
            administrator_id = partner_obj.search([
                ('partner_type', '=', 'administrator'),
                ('company_id', '=', group_evaluation.group_id.company_id.id),
                ('section_id', '=', group_evaluation.group_id.
                 level_id.section_id.id),
            ], limit=1).id

            if group_evaluation.survey_id.apply_to == 'teacher':
                apply_to = group_evaluation.group_id.teacher_id.id
            elif group_evaluation.survey_id.apply_to == 'administrator':
                if not administrator_id:
                    raise UserError(
                        _('There is no administrator set up for %s') %
                        (group_evaluation.group_id.company_id.name))
                apply_to = administrator_id
            else:
                apply_to = False

            if group_evaluation.survey_id.answered_by == 'teacher':
                answered_by = group_evaluation.group_id.teacher_id.id
            elif group_evaluation.survey_id.answered_by == 'administrator':
                if not administrator_id:
                    raise UserError(_(
                        'There is no administrator set up for %s') %
                        (group_evaluation.group_id.company_id.name))
                answered_by = administrator_id
            else:
                answered_by = False

            if group_evaluation.survey_id.apply_to == 'student' or \
                    group_evaluation.survey_id.answered_by == 'student':
                # if group_evaluation.survey_id.answered_by == 'student':
                for student in group_evaluation.group_id.student_ids:
                    if group_evaluation.survey_id.apply_to == 'student':
                        apply_to = student.id
                    if group_evaluation.survey_id.answered_by == 'student':
                        answered_by = student.id
                    create_response(survey_id,
                                    answered_by,
                                    apply_to,
                                    group_evaluation_id)
            else:
                create_response(survey_id,
                                answered_by,
                                apply_to,
                                group_evaluation_id)
        self.write({'state': 'open', 'date_open': fields.Datetime.now()})
        return True
