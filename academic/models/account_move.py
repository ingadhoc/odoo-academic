from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    student_ids = fields.Many2many('res.partner', compute="_compute_student_ids")
    partner_shipping_id = fields.Many2one(domain="[('id', 'in', student_ids), ('partner_type', '=', 'student')]")

    @api.depends('partner_id')
    def _compute_student_ids(self):
        for rec in self:
            if rec.partner_id:
                student_ids = self.env['res.partner.link'].search(
                    [('partner_id', '=', rec.partner_id.id), ('role_ids', 'in', self.env.ref('academic.paying_role').id)]
                ).mapped('student_id.id')
                rec.student_ids = [(6, 0, student_ids)]
            else:
                rec.student_ids = [(5, 0, 0)]
