from odoo import api, models


class HrEmployeeBase(models.AbstractModel):
    _inherit = "hr.employee.base"

    @api.model
    def _get_contextual_employee(self):
        if self.env.context.get("multiple_employees") and len(self.env.user.employee_ids) > 1:
            return self.env.user.employee_ids
        return super()._get_contextual_employee()
