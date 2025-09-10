from odoo import api, fields, models


class HolidaysAllocation(models.Model):
    _inherit = "hr.leave.allocation"

    employee_id = fields.Many2one("hr.employee", domain=lambda self: self._get_employee_domain())

    @api.model
    def _get_employee_domain(self):
        if len(self.env.user.employee_ids) > 1:
            return [("id", "in", self.env.user.employee_ids.ids)]
        elif self.env.user.employee_id:
            return [("id", "=", self.env.user.employee_id.id)]
        return []

    @api.model
    def default_get(self, field_list):
        result = super().default_get(field_list)
        if len(self.env.user.employee_ids) > 1:
            result["employee_id"] = self.env.user.employee_ids[0].id
        elif self.env.user.employee_id:
            result["employee_id"] = self.env.user.employee_id.id
        return result
