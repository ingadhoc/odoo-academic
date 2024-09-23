##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields
from odoo.tools import get_timedelta


class SaleSubscriptionPlan(models.Model):
    _inherit = 'sale.subscription.plan'

    _sql_constraints = [
        ('check_duration_value', 'CHECK(is_unlimited OR duration_value > 0)', 'The duration can\'t be negative or 0.'),
    ]

    is_unlimited = fields.Boolean('Last Forever', default=True)
    duration_value = fields.Integer(string="End After", default=1, required=True)
    duration_unit = fields.Selection([('month', 'Months'), ('year', 'Years')], help="Contract duration", default='month', required=True)

    @property
    def duration(self):
        if not self.duration_unit or not self.duration_value:
            return False
        return get_timedelta(self.duration_value, self.duration_unit)
