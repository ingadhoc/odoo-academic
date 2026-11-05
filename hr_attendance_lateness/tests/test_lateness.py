from datetime import UTC, datetime, time, timedelta

from dateutil.relativedelta import MO, relativedelta
from odoo import Command, fields
from odoo.tests import TransactionCase
from zoneinfo import ZoneInfo


class TestAttendanceLateness(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.tz_name = "America/Argentina/Buenos_Aires"
        cls.tz = ZoneInfo(cls.tz_name)
        # Anchor on a Monday at least a week ago: weekdays are known and the
        # version created the next day is already in effect today
        cls.monday = fields.Date.today() + relativedelta(weekday=MO(-2))
        cls.env.company.attendance_lateness_threshold = 5
        # Morning and afternoon slots: the expected check-in is the first one
        cls.fixed_calendar = cls.env["resource.calendar"].create(
            {
                "name": "Lateness fixed",
                "calendar_type": "fixed",
                "attendance_ids": [Command.clear()]
                + [
                    Command.create({"dayofweek": str(day), "hour_from": hour_from, "hour_to": hour_to})
                    for day in range(5)
                    for hour_from, hour_to in ((9, 13), (14, 18))
                ],
            }
        )

    def _employee(self, calendar):
        # The first version starts before the scenario, so later versions become current
        return self.env["hr.employee"].create(
            {
                "name": "Lateness employee",
                "resource_calendar_id": calendar.id,
                "tz": self.tz_name,
                "date_version": self.monday - relativedelta(months=1),
            }
        )

    def _check_in(self, employee, day, hour, minute=0):
        local = datetime.combine(day, time(hour, minute), tzinfo=self.tz)
        check_in = local.astimezone(UTC).replace(tzinfo=None)
        return self.env["hr.attendance"].create(
            {"employee_id": employee.id, "check_in": check_in, "check_out": check_in + timedelta(hours=1)}
        )

    def _utc(self, day, hour, minute=0):
        return datetime.combine(day, time(hour, minute), tzinfo=self.tz).astimezone(UTC).replace(tzinfo=None)

    def _assert_invariants(self, attendance):
        threshold = attendance.employee_id.company_id.attendance_lateness_threshold
        self.assertGreaterEqual(attendance.late_minutes, 0)
        self.assertEqual(attendance.is_late, attendance.late_minutes > threshold)
        if not attendance.expected_check_in:
            self.assertEqual(attendance.late_minutes, 0)

    def test_lateness_against_fixed_schedule(self):
        cases = [
            ("early", 8, 55, 0, False),
            ("within the threshold", 9, 4, 4, False),
            ("over the threshold", 9, 20, 20, True),
            ("afternoon slot does not reset the expected time", 14, 10, 310, True),
        ]
        for label, hour, minute, late_minutes, is_late in cases:
            with self.subTest(label):
                attendance = self._check_in(self._employee(self.fixed_calendar), self.monday, hour, minute)
                self.assertRecordValues(
                    attendance,
                    [
                        {
                            "expected_check_in": self._utc(self.monday, 9),
                            "late_minutes": late_minutes,
                            "is_late": is_late,
                        }
                    ],
                )
                self._assert_invariants(attendance)

    def test_no_expected_check_in_on_a_day_off(self):
        saturday = self.monday + timedelta(days=5)
        attendance = self._check_in(self._employee(self.fixed_calendar), saturday, 11)
        self.assertRecordValues(attendance, [{"expected_check_in": False, "late_minutes": 0, "is_late": False}])
        self._assert_invariants(attendance)

    def test_no_expected_check_in_with_flexible_schedule(self):
        calendar = self.env["resource.calendar"].create(
            {"name": "Lateness flexible", "calendar_type": "undefined", "attendance_ids": [Command.clear()]}
        )
        attendance = self._check_in(self._employee(calendar), self.monday, 11)
        self.assertRecordValues(attendance, [{"expected_check_in": False, "late_minutes": 0, "is_late": False}])
        self._assert_invariants(attendance)

    def test_lateness_against_variable_schedule(self):
        # A variable schedule has dated slots instead of a weekly pattern
        calendar = self.env["resource.calendar"].create(
            {
                "name": "Lateness variable",
                "calendar_type": "variable",
                "attendance_ids": [
                    Command.clear(),
                    Command.create({"date": self.monday, "hour_from": 10, "hour_to": 16}),
                ],
            }
        )
        employee = self._employee(calendar)
        with self.subTest("dated slot"):
            attendance = self._check_in(employee, self.monday, 10, 30)
            self.assertRecordValues(
                attendance,
                [{"expected_check_in": self._utc(self.monday, 10), "late_minutes": 30, "is_late": True}],
            )
            self._assert_invariants(attendance)
        with self.subTest("same weekday, another week"):
            next_monday = self.monday + timedelta(weeks=1)
            attendance = self._check_in(employee, next_monday, 10, 30)
            self.assertRecordValues(attendance, [{"expected_check_in": False, "late_minutes": 0, "is_late": False}])
            self._assert_invariants(attendance)

    def test_new_version_keeps_past_lateness(self):
        # Timezone and schedule are per version: a new version must not rewrite the past
        early_calendar = self.fixed_calendar.copy({"name": "Lateness early"})
        early_calendar.attendance_ids.filtered(lambda a: a.hour_from == 9).hour_from = 7
        employee = self._employee(self.fixed_calendar)
        attendance = self._check_in(employee, self.monday, 9, 30)
        employee.create_version(
            {
                "date_version": self.monday + timedelta(days=1),
                "resource_calendar_id": early_calendar.id,
                "tz": "Europe/Madrid",
            }
        )
        self.assertEqual(employee.resource_calendar_id, early_calendar)
        attendance._compute_lateness_metrics()
        self.assertRecordValues(
            attendance,
            [{"expected_check_in": self._utc(self.monday, 9), "late_minutes": 30, "is_late": True}],
        )
        self._assert_invariants(attendance)

    def test_time_rule_attendance_is_not_a_check_in(self):
        # Time rules split attendances: their outputs do not start at the employee's arrival
        employee = self._employee(self.fixed_calendar)
        attendances = self.env["hr.attendance"].with_context(skip_time_rules=True)
        source = attendances.create(
            {"employee_id": employee.id, "check_in": self._utc(self.monday, 9), "check_out": self._utc(self.monday, 18)}
        )
        rule = self.env.ref("hr_work_entry.hr_time_rule_employee_schedule")
        output = attendances.create(
            rule._get_output_attendance_vals(employee, self._utc(self.monday, 18), self._utc(self.monday, 21), source)
        )
        self.assertRecordValues(output, [{"expected_check_in": False, "late_minutes": 0, "is_late": False}])
        self.assertRecordValues(
            source, [{"expected_check_in": self._utc(self.monday, 9), "late_minutes": 0, "is_late": False}]
        )
        self._assert_invariants(output)
