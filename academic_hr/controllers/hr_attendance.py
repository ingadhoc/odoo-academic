from odoo import http
from odoo.addons.hr_attendance.controllers.main import HrAttendance
from odoo.fields import Domain


class HrAttendanceKiosk(HrAttendance):
    @http.route("/hr_attendance/employees_infos", type="jsonrpc", auth="public")
    def employees_infos(self, token, limit, offset, domain):
        domain = Domain(domain) & Domain("main_employee_id", "!=", False)
        return super().employees_infos(token, limit, offset, domain)
