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
    student_id = fields.Many2one('res.partner', required=True, domain=[('partner_type', '=', 'student')])
    registration_so_line_id = fields.Many2one('sale.order.line')
    main_so_line_id = fields.Many2one('sale.order.line')
    status = fields.Selection(
        selection=[
            ('active', 'Active'),
            ('inactive', 'Inactive'),
            ('enrolled', 'Enrolled'),
            ('not_enrolled', 'Not Enrolled'),
            ('enrolling', 'Enrolling'),
            ('prospect', 'Prospect'),
        ],
        compute="_compute_status",
        store=True
    )

    @api.ondelete(at_uninstall=False)
    def _unlink_check_sale_line(self):
        for rec in self:
            if rec.main_so_line_id:
                raise UserError('You cannot delete the link. You must first unlink the main line.')
            elif rec.registration_so_line_id:
                raise UserError('You cannot delete the link. You must first unlink the registration line.')

    @api.depends('registration_so_line_id.state', 'main_so_line_id.state', 'lead_id')
    def _compute_status(self):
        for rec in self:
            reg_line = rec.registration_so_line_id
            main_line = rec.main_so_line_id
            lead = rec.lead_id

            if main_line:
                state = main_line.order_id.state
                if state == 'sale':
                    rec.status = 'active'
                    continue
                elif state == 'cancel':
                    rec.status = 'inactive'
                    continue

            if reg_line:
                state = reg_line.order_id.state
                if state in ['draft', 'sent']:
                    rec.status = 'enrolling'
                elif state == 'sale':
                    rec.status = 'enrolled'
                elif state == 'cancel':
                    rec.status = 'not_enrolled'
                continue

            if lead:
                rec.status = 'prospect'
            else:
                rec.status = False

