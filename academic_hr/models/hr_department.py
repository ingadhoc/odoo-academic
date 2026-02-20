from odoo import models


class HrDepartment(models.Model):
    _inherit = "hr.department"

    def _compute_total_employee(self):
        emp_data = (
            self.env["hr.employee"]
            .sudo()
            ._read_group(
                [
                    ("department_id", "in", self.ids),
                    ("company_id", "in", self.env.companies.ids),
                    ("main_employee_id", "!=", False),
                ],
                ["department_id"],
                ["__count"],
            )
        )
        result = {department.id: count for department, count in emp_data}
        for department in self:
            department.total_employee = result.get(department.id, 0)
