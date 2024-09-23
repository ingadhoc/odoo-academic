##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import datetime


class SaleOrderTemplate(models.Model):
    _inherit = "sale.order.template"

    start_day = fields.Integer()
    start_month = fields.Selection(
        selection=[
            ('1', 'January'),
            ('2', 'February'),
            ('3', 'March'),
            ('4', 'April'),
            ('5', 'May'),
            ('6', 'June'),
            ('7', 'July'),
            ('8', 'August'),
            ('9', 'September'),
            ('10', 'October'),
            ('11', 'November'),
            ('12', 'December')
        ]
    )

    @api.constrains('start_day', 'start_month')
    def _check_valid_date(self):
        for rec in self:
            if not rec.start_month and not rec.start_day:
                continue

            if bool(rec.start_month) != bool(rec.start_day):
                raise ValidationError(_("If a month is specified, a day must also be specified, and vice versa."))

            try:
                month = int(rec.start_month)
                # Validate that the combination of month and day is correct, considering non-leap years
                datetime(year=2023, month=month, day=rec.start_day)
            except ValueError:
                raise ValidationError(_("The combination of month and day is not valid. Please enter a correct date."))
