from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    attendance_lateness_threshold = fields.Integer(
        related="company_id.attendance_lateness_threshold",
        readonly=False,
    )
