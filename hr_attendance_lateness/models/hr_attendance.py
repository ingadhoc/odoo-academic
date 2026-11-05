from datetime import UTC, datetime, time, timedelta

from odoo import api, fields, models
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


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

            # Attendances produced by a time rule are not check-ins, as in core's validation
            if not attendance.check_in or not attendance.employee_id or attendance.time_rule_id:
                continue

            employee = attendance.employee_id
            # Timezone and schedule live on hr.version: use the ones in effect that day
            try:
                tz = ZoneInfo(employee._get_tz(date=attendance.check_in))
            except ZoneInfoNotFoundError:
                tz = UTC

            check_in_local = attendance.check_in.replace(tzinfo=UTC).astimezone(tz)
            day_start = datetime.combine(check_in_local.date(), time.min, tzinfo=tz)

            version = employee.sudo()._get_version(check_in_local.date())
            calendar = version.resource_calendar_id or employee.company_id.resource_calendar_id
            # A flexible schedule has no start time to compare against
            if not calendar or calendar._is_flexible():
                continue

            # Works for fixed (weekly) and variable (dated, recurrent) schedules
            intervals = calendar._attendance_intervals_batch(day_start, day_start + timedelta(days=1))[False]
            if not intervals:
                continue

            expected_check_in_local = min(start for start, _stop, _attendance in intervals)
            attendance.expected_check_in = expected_check_in_local.astimezone(UTC).replace(tzinfo=None)

            delta = attendance.check_in - attendance.expected_check_in

            if delta.total_seconds() > 0:
                late_minutes = int(delta.total_seconds() / 60)
                attendance.late_minutes = late_minutes

                if late_minutes > lateness_threshold:
                    attendance.is_late = True
