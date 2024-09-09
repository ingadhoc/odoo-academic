##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api, _
from datetime import datetime


class SaleOrder(models.Model):
    _inherit = "sale.order"

    renewal_order_id = fields.Many2one('sale.order', on_delete="set null", readonly=True)
    renewal_state = fields.Selection(selection=[
            ('er', 'In re-enrollment process'),
            ('r', 'Re-enrolled'),
            ('nr', 'Not re-enrolled'),
            ('sr', 'No re-enrollment process')],
        compute="_compute_renewal_state",
        store=True
    )
    same_subscription_id = fields.Many2one('sale.order', compute='_compute_same_subscription_id', store=False)

    @api.depends('renewal_order_id', 'renewal_order_id.state')
    def _compute_renewal_state(self):
        for rec in self:
            if not rec.renewal_order_id:
                rec.renewal_state = 'sr'
            elif rec.renewal_order_id.state in ['sale', 'done']:
                rec.renewal_state = 'r'
            elif rec.renewal_order_id.state == 'cancel':
                rec.renewal_state = 'nr'
            else:
                rec.renewal_state = 'er'

    def action_open_reenrollment_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Re-enrollment Wizard',
            'res_model': 'sale.order.reenrollment.wizard',
            'view_mode': 'form',
            'view_id': self.env.ref('academic_sale_subscription.sale_order_reenrollment_wizard_form').id,
            'target': 'new',
            'context': {'active_ids': self.env.context.get('active_ids', [])},
        }

    def generate_reenrollment(self):
        sale_order_template_id = self.env.context.get('sale_order_template_id')
        subscriptions = self.env['sale.order']
        for subscription in self:
            new_subscription = self.create({
                'partner_id': subscription.partner_id.id,
                'sale_order_template_id': sale_order_template_id,
            })

            new_subscription._onchange_sale_order_template_id()
            new_subscription.order_line.filtered(lambda x: x.product_id and x.product_id.recurring_invoice).write({'product_uom_qty': 0})

            subscription.renewal_order_id = new_subscription
            subscriptions += new_subscription

            message_body = _("This re-enrollment sale order was generated from subscription <a href='#' data-oe-model='sale.order' data-oe-id='%d'>%s</a>.") % (
                subscription.id, subscription.name
            )
            new_subscription.message_post(
                body=message_body,
            )
        return subscriptions

    def action_confirm(self):
        super().action_confirm()
        for rec in self.filtered(lambda x: x.is_subscription and x.sale_order_template_id and x.sale_order_template_id.start_day):
            rec.order_line.filtered(lambda x: x.product_id and x.product_id.recurring_invoice).write({'product_uom_qty': 1})

            start_day = rec.sale_order_template_id.start_day
            start_month = int(rec.sale_order_template_id.start_month)

            today = fields.Date.today()
            current_year = today.year

            next_start_date = datetime(current_year, start_month, start_day).date()
            if next_start_date < today:
                next_start_date = datetime(current_year + 1, start_month, rec.sale_order_template_id.start_day)

            rec.next_invoice_date = next_start_date
            rec.start_date = next_start_date

    def action_open_renewal_order(self):
        self.ensure_one()
        if self.renewal_order_id:
            return {
                'type': 'ir.actions.act_window',
                'name': _('Renewal Order'),
                'view_mode': 'form',
                'res_model': 'sale.order',
                'res_id': self.renewal_order_id.id,
                'target': 'current',
            }

    @api.depends('order_line.product_id', 'partner_id', 'start_date', 'state')
    def _compute_same_subscription_id(self):
        for subscription in self:
            recurring_lines = subscription.order_line.filtered(lambda line: line.product_id.recurring_invoice)

            if recurring_lines:
                subscription_id = subscription._origin.id
                Subscription = self.with_context(active_test=False).sudo()

                domain = [
                    ('partner_id', '=', subscription.partner_id.id),
                    ('order_line.product_id', 'in', recurring_lines.product_id.ids),
                    ('state', '=', 'sale'),
                    ('stage_id.category', '!=', 'closed')
                ]

                if subscription_id:
                    domain += [('id', '!=', subscription_id)]

                if not subscription.start_date:
                    domain += [
                        ('start_date', '<=', fields.Date.today()),
                        '|',
                        ('end_date', '=', False),
                        ('end_date', '>=', fields.Date.today())
                    ]
                else:
                    domain += [
                        ('start_date', '<=', subscription.start_date),
                        '|',
                        ('end_date', '=', False),
                        ('end_date', '>=', subscription.start_date)
                    ]

                subscription.same_subscription_id = Subscription.search(domain, limit=1)
            else:
                subscription.same_subscription_id = False
