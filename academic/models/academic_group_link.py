##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import api, fields, models
from odoo.exceptions import UserError


class AcademicGroupLink(models.Model):
    _name = 'academic.group.link'
    _description = 'Academic Group Link'

    group_id = fields.Many2one('academic.group', required=True, ondelete='cascade')
    lead_id = fields.Many2one('crm.lead')
    student_id = fields.Many2one('res.partner', domain=[('partner_type', '=', 'student')], compute='_compute_student_id', store=True)
    registration_so_line_id = fields.Many2one('sale.order.line')
    main_so_line_id = fields.Many2one('sale.order.line')
    status = fields.Selection(
        selection=[
            ('lost', 'Lost'),
            ('prospect', 'Prospect'),
            ('enrolling', 'Enrolling'),
            ('not_enrolled', 'Not Enrolled'),
            ('enrolled', 'Enrolled'),
            ('active', 'Active'),
            ('leave', 'Leave'),
        ],
        compute="_compute_status",
        store=True
    )
    display_name = fields.Char(compute='_compute_display_name')

    # TODO revisar si queremos restringuir algunos casos
    # @api.ondelete(at_uninstall=False)
    # def _unlink_check_sale_line(self):
    #     for rec in self:
    #         if rec.main_so_line_id:
    #             raise UserError('You cannot delete the link. You must first unlink the main line.')
    #         elif rec.registration_so_line_id:
    #             raise UserError('You cannot delete the link. You must first unlink the registration line.')

    @api.depends('registration_so_line_id.state', 'main_so_line_id.state', 'lead_id.active', 'lead_id.probability')
    def _compute_status(self):
        for rec in self:
            reg_line = rec.registration_so_line_id
            main_line = rec.main_so_line_id
            lead = rec.lead_id

            if main_line.order_id.state == 'sale':
                rec.status = 'active'
            elif main_line.order_id.state == 'cancel':
                rec.status = 'leave'
            elif reg_line.order_id.state in ['draft', 'sent']:
                rec.status = 'enrolling'
            elif reg_line.order_id.state == 'sale':
                rec.status = 'enrolled'
            elif reg_line.order_id.state == 'cancel':
                rec.status = 'not_enrolled'
            elif lead and lead.active == False and lead.probability == 0:
                rec.status = 'lost'
            elif lead:
                rec.status = 'prospect'
            else:
                rec.status = False

    def _compute_display_name(self):
        for rec in self:
            rec.display_name = rec.student_id.name or rec.lead_id.partner_id.name or rec.lead_id.contact_name or rec.lead_id.name

    @api.depends('lead_id', 'lead_id.partner_id')
    def _compute_student_id(self):
        for rec in self:
            if rec.lead_id and not rec.registration_so_line_id and not rec.main_so_line_id:
                rec.student_id = rec.lead_id.partner_id
