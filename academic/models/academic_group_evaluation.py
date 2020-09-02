##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, _
from odoo.exceptions import UserError


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

    company_id = fields.Many2one(
        'res.company',
        related='group_id.company_id',
    )
    time_used = fields.Float(
        compute='_compute_time_used',
    )

    _sql_constraints = [
        ('group_uniq', 'unique(group_id)',
         'There can not be two groups for the same evaluation.'), ]

    def _compute_time_used(self, names):
        for record in self:
            if record.date_open:
                date_open = fields.Datetime.from_string(record.date_open)
            if record.date_close:
                date_close = fields.Datetime.from_string(record.date_close)
            if date_open and date_close:
                record.time_used = date_close - date_open

    def unlink(self):
        for record in self:
            if record.state != 'invisible':
                raise UserError(
                    _('Solo pueden borrarse evaluaciones en estado invisible.\
                        ATENCION: esa borrará los registros correspondientes a\
                        la evaluación del grupo, en caso de que haya\
                        respuestas registradas'))
        return super(AcademicGroupEvaluation, self).unlink()
