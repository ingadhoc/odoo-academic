from odoo import api, models


class ResourceCalendar(models.Model):
    _inherit = "resource.calendar"

    def write(self, vals):
        res = super().write(vals)
        if "calendar_type" in vals:
            self._recompute_attendance_lateness()
        return res

    def _recompute_attendance_lateness(self):
        # Every version that used the schedule: the expected check-in is read per day
        versions = (
            self.env["hr.version"]
            .sudo()
            .with_context(active_test=False)
            .search([("resource_calendar_id", "in", self.ids)])
        )
        if versions:
            self.env["hr.attendance"].sudo().search(
                [("employee_id", "in", versions.employee_id.ids)]
            )._recompute_lateness()


class ResourceCalendarAttendance(models.Model):
    _inherit = "resource.calendar.attendance"

    @api.model_create_multi
    def create(self, vals_list):
        slots = super().create(vals_list)
        slots.calendar_id._recompute_attendance_lateness()
        return slots

    def write(self, vals):
        calendars = self.calendar_id
        res = super().write(vals)
        (calendars | self.calendar_id)._recompute_attendance_lateness()
        return res

    def unlink(self):
        self.calendar_id._recompute_attendance_lateness()
        return super().unlink()
