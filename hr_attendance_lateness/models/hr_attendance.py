from datetime import datetime

import pytz
from odoo import api, fields, models


class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    expected_check_in = fields.Datetime(
        string="Expected Check-in",
        compute="_compute_lateness_metrics",
        store=True,
    )
    late_minutes = fields.Integer(
        compute="_compute_lateness_metrics",
        store=True,
    )
    is_late = fields.Boolean(
        compute="_compute_lateness_metrics",
        store=True,
    )

    @api.depends("check_in", "employee_id", "employee_id.resource_calendar_id")
    def _compute_lateness_metrics(self):
        for attendance in self:
            lateness_threshold = attendance.employee_id.company_id.attendance_lateness_threshold

            attendance.expected_check_in = False
            attendance.late_minutes = 0
            attendance.is_late = False

            if not attendance.check_in or not attendance.employee_id:
                continue

            calendar = (
                attendance.employee_id.resource_calendar_id or attendance.employee_id.company_id.resource_calendar_id
            )
            if not calendar:
                continue

            tz_name = attendance.employee_id.tz or calendar.tz or "UTC"

            try:
                tz = pytz.timezone(tz_name)
            except pytz.UnknownTimeZoneError:
                tz = pytz.UTC

            check_in_utc = pytz.UTC.localize(attendance.check_in)
            check_in_local = check_in_utc.astimezone(tz)

            # Get the day of the week (0 = Monday, 6 = Sunday)
            weekday = str(check_in_local.weekday())

            # Find the calendar attendance for this day
            calendar_attendances = calendar.attendance_ids.filtered(lambda a: a.dayofweek == weekday)

            if not calendar_attendances:
                continue

            first_attendance = calendar_attendances.sorted(key=lambda a: a.hour_from)[0]

            start_hour = first_attendance.hour_from

            hours = int(start_hour)
            minutes = int((start_hour % 1) * 60)

            expected_check_in_naive = datetime(
                check_in_local.year,
                check_in_local.month,
                check_in_local.day,
                hours,
                minutes,
                0,
            )

            expected_check_in_local = tz.localize(expected_check_in_naive)

            expected_check_in_utc = expected_check_in_local.astimezone(pytz.UTC)

            attendance.expected_check_in = expected_check_in_utc.replace(tzinfo=None)

            delta = attendance.check_in - attendance.expected_check_in

            if delta.total_seconds() > 0:
                late_minutes = int(delta.total_seconds() / 60)
                attendance.late_minutes = late_minutes

                if late_minutes > lateness_threshold:
                    attendance.is_late = True
