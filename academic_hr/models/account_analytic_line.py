from odoo import api, models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    @api.model
    def default_get(self, field_list):
        result = super().default_get(field_list)
        if len(self.env.user.employee_ids) > 1:
            result["employee_id"] = self.env.user.employee_ids[0].id
        return result
