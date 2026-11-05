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
        compute="_compute_is_late",
        store=True,
    )

    @api.depends(
        "check_in",
        "employee_id",
        "state",
        "time_rule_id",
    )
    def _compute_lateness_metrics(self):
        for attendance in self:
            attendance.expected_check_in = False
            attendance.late_minutes = 0

            # Time rule outputs are not check-ins (as in core's validation), and refused ones do not count
            if (
                not attendance.check_in
                or not attendance.employee_id
                or attendance.time_rule_id
                or attendance.state == "refused"
            ):
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

            # Work intervals of the day: fixed and variable slots, minus holidays and time off
            resource = employee.sudo().resource_id
            intervals = calendar._work_intervals_batch(
                day_start,
                day_start + timedelta(days=1),
                resources_per_tz={tz: resource},
                domain=[("company_id", "in", [False, employee.company_id.id]), ("count_as", "=", "absence")],
            )[resource.id]
            # Duration based slots have no start time
            starts = [start for start, _stop, slot in intervals if not slot.duration_based]
            if not starts:
                continue

            attendance.expected_check_in = min(starts).astimezone(UTC).replace(tzinfo=None)

            delta = attendance.check_in - attendance.expected_check_in

            if delta.total_seconds() > 0:
                attendance.late_minutes = int(delta.total_seconds() / 60)

    # Apart from the schedule: a new threshold only compares numbers, it does not read schedules
    @api.depends("late_minutes", "employee_id.company_id.attendance_lateness_threshold")
    def _compute_is_late(self):
        for attendance in self:
            late_minutes = attendance.late_minutes
            # Never late without minutes late, even with a negative threshold
            attendance.is_late = (
                late_minutes > 0 and late_minutes > attendance.employee_id.company_id.attendance_lateness_threshold
            )

    def _recompute_lateness(self):
        for field_name in ("expected_check_in", "late_minutes", "is_late"):
            self.env.add_to_compute(self._fields[field_name], self)
