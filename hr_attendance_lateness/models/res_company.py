from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    attendance_lateness_threshold = fields.Integer(
        default=0,
    )
