from odoo import api, models


class HrLeaveType(models.Model):
    _inherit = "hr.leave.type"

    @api.model
    def get_allocation_data_request(self, target_date=None, hidden_allocations=True):
        employee = self.env["hr.employee"].with_context(multiple_employees=True)._get_contextual_employee()

        if employee and len(employee) > 1:
            combined_data = []
            for emp in employee:
                emp_data = super(HrLeaveType, self.with_context(employee_id=emp.id)).get_allocation_data_request(
                    target_date, hidden_allocations
                )
                # Modify each entry to have unique keys and include employee name
                for entry in emp_data:
                    if len(entry) >= 4:
                        # entry format: (name, data_dict, requires_allocation, leave_type_id)
                        unique_key = f"{entry[3]}_{emp.id}"
                        # Add employee name to the leave type name for clarity
                        employee_leave_name = f"{entry[0]} ({emp.name})"
                        modified_entry = (employee_leave_name, entry[1], entry[2], unique_key)
                        combined_data.append(modified_entry)
                    else:
                        combined_data.append(entry)
            return combined_data

        return super().get_allocation_data_request(target_date, hidden_allocations)
