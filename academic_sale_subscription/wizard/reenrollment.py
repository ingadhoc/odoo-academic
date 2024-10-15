##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import fields, models, _
from odoo.exceptions import ValidationError


class SaleOrderReenrollmentWizard(models.TransientModel):
    _name = 'sale.order.reenrollment.wizard'

    sale_order_template_id = fields.Many2one(
        'sale.order.template',
        required=True,
        domain=[('recurrence_id', '!=', False)]
    )

    def action_generate_reenrollment(self):
        if not (self.sale_order_template_id.start_day and self.sale_order_template_id.start_month):
            raise ValidationError(_("The selected subscription plan does not have a start day or start month."))

        products = self.sale_order_template_id.sale_order_template_line_ids
        recurring_product = products.filtered(lambda x: x.recurring_invoice)
        no_recurring_product = products - recurring_product
        if not (recurring_product and no_recurring_product):
            raise ValidationError(_("It is required to have at least one recurring product and one non-recurring product."))

        active_ids = self.env.context.get('active_ids', [])
        sale_order_ids = self.env['sale.order'].browse(active_ids)

        sale_orders_with_active_renewal = sale_order_ids.filtered('renewal_order_id')
        if sale_orders_with_active_renewal:
            sale_order_names = "\n- ".join(sale_orders_with_active_renewal.mapped('name'))
            raise ValidationError(_(
                "The following subscriptions have already a linked renewal order:\n- %s\nPlease follow up the renewal on those orders."
                "\nTo create the renewal for the other orders, you can filter by 'No re-enrollment process'."
            ) % sale_order_names)

        subscriptions = sale_order_ids.with_context(sale_order_template_id=self.sale_order_template_id.id).generate_reenrollment()

        action = self.env.ref('sale_subscription.sale_subscription_action').read()[0]
        action.update({
            'domain': [('id', 'in', subscriptions.ids)],
            'views': sorted(action['views'], key=lambda v: v[1] != 'tree'),  # show tree view first
            'context': {'default_is_subscription': 1}
        })
        return action
