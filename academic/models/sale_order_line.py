##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    group_id = fields.Many2one('academic.group', compute='_compute_group', inverse='_inverse_group')
    academic_product_type = fields.Selection(
        selection=[
            ('main', 'Main'),
            ('registration', 'Registration'),
        ],
        related='product_id.academic_product_type',
    )


    def _compute_group(self):
        for rec in self:
            group_link = False
            if rec.product_template_id and rec.product_template_id.academic_product_type:
                product_type = rec.product_template_id.academic_product_type
                if product_type == 'registration':
                    group_link = rec.env['academic.group.link'].search([('registration_so_line_id', '=', rec.id)], limit=1)
                else:
                    group_link = rec.env['academic.group.link'].search([('main_so_line_id', '=', rec.id)], limit=1)
            rec.group_id = group_link.group_id if group_link else False

    def _inverse_group(self):
        for rec in self:
            product_type = rec.product_id.academic_product_type
            if not rec.group_id:
                rec.env['academic.group.link'].search([('registration_so_line_id' if product_type == 'registration' else 'main_so_line_id', '=', rec.id)], limit=1).unlink()

            if not rec.product_id or not rec.product_id.academic_product_type or not rec.order_id.partner_id:
                continue

            if rec.group_id:
                link = rec.env['academic.group.link'].search([('group_id', '=', rec.group_id.id), ('student_id', '=', rec.order_id.partner_id.id)], limit=1)

                if product_type == 'registration':
                    vals = {'registration_so_line_id': rec.id}
                else:
                    vals = {'main_so_line_id': rec.id}

                if link:
                    link.write(vals)
                else:
                    vals.update({
                        'student_id': rec.order_id.partner_id.id,
                        'group_id': rec.group_id.id,
                    })
                    rec.env['academic.group.link'].create(vals)
