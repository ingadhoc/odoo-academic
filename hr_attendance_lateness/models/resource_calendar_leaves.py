from datetime import timedelta

from odoo import api, models
from odoo.fields import Domain


class ResourceCalendarLeaves(models.Model):
    _inherit = "resource.calendar.leaves"

    @api.model_create_multi
    def create(self, vals_list):
        leaves = super().create(vals_list)
        leaves._recompute_attendance_lateness()
        return leaves

    def write(self, vals):
        self._recompute_attendance_lateness()
        res = super().write(vals)
        self._recompute_attendance_lateness()
        return res

    def unlink(self):
        self._recompute_attendance_lateness()
        return super().unlink()

    def _recompute_attendance_lateness(self):
        domains = []
        for leave in self.sudo():
            # One day of margin: dates are UTC and the check-in day is local
            domain = Domain("check_in", ">=", leave.date_from - timedelta(days=1)) & Domain(
                "check_in", "<=", leave.date_to + timedelta(days=1)
            )
            if leave.resource_id:
                domain &= Domain("employee_id.resource_id", "=", leave.resource_id.id)
            elif leave.company_id:
                domain &= Domain("employee_id.company_id", "=", leave.company_id.id)
            domains.append(domain)
        if domains:
            self.env["hr.attendance"].sudo().search(Domain.OR(domains))._recompute_lateness()
