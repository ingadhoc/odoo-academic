from odoo import fields, models


class SaleOrderCloseReason(models.Model):
    _inherit = "sale.order.close.reason"

    release_vacancy = fields.Boolean(
        help="If enabled, closing with this reason will release the associated vacancy.",
        default=False,
    )
