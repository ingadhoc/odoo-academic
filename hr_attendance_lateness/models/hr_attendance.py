from collections import defaultdict
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
        # Work intervals are read once per schedule, timezone and company, for the whole range of days
        groups = defaultdict(list)
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
            version = employee.sudo()._get_version(check_in_local.date())
            calendar = version.resource_calendar_id or employee.company_id.resource_calendar_id
            # A flexible schedule has no start time to compare against
            if not calendar or calendar._is_flexible():
                continue

            day_start = datetime.combine(check_in_local.date(), time.min, tzinfo=tz)
            groups[calendar, tz, employee.company_id].append((attendance, employee.sudo().resource_id, day_start))

        for (calendar, tz, company), items in groups.items():
            domain = [("company_id", "in", [False, company.id]), ("count_as", "=", "absence")]
            resources = self.env["resource.resource"].sudo().browse({resource.id for _att, resource, _day in items})
            days = [day_start for _att, _resource, day_start in items]
            starts = self._lateness_first_starts(
                calendar, tz, resources, min(days), max(days) + timedelta(days=1), domain
            )
            for attendance, resource, day_start in items:
                day_starts = starts.get(resource.id)
                if day_starts is None:
                    # Flexible on the first day of the range: core fills it with synthetic slots, so ask for its day only
                    day_starts = self._lateness_first_starts(
                        calendar, tz, resource, day_start, day_start + timedelta(days=1), domain
                    ).get(resource.id, {})
                expected = day_starts.get(day_start.date())
                if not expected:
                    continue

                attendance.expected_check_in = expected.astimezone(UTC).replace(tzinfo=None)

                delta = attendance.check_in - attendance.expected_check_in

                if delta.total_seconds() > 0:
                    attendance.late_minutes = int(delta.total_seconds() / 60)

    @api.model
    def _lateness_first_starts(self, calendar, tz, resources, start, stop, domain):
        """Start of the first working slot of each local day, as ``{resource_id: {date: datetime}}``.

        Work intervals are the fixed and variable slots minus holidays and time off. A resource that
        got core's synthetic slots of a flexible schedule is left out.
        """
        intervals_per_resource = calendar._work_intervals_batch(
            start, stop, resources_per_tz={tz: resources}, domain=domain
        )
        result = {}
        for resource in resources:
            intervals = list(intervals_per_resource[resource.id])
            if any(not slot.id for _start, _stop, slot in intervals):
                continue
            first_starts = result[resource.id] = {}
            for interval_start, interval_stop, slot in intervals:
                # Duration based slots have no start time
                if slot.duration_based:
                    continue
                day = interval_start.date()
                while day <= (interval_stop - timedelta(microseconds=1)).date():
                    day_start = max(interval_start, datetime.combine(day, time.min, tzinfo=tz))
                    if day not in first_starts or day_start < first_starts[day]:
                        first_starts[day] = day_start
                    day += timedelta(days=1)
        return result

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

    @api.model
    def _recompute_lateness_matching(self, domain):
        """Mark the attendances matching ``domain``, for a trigger outside this model."""
        if not domain.is_false():
            self.sudo().search(domain)._recompute_lateness()
