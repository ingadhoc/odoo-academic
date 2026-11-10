from datetime import UTC, datetime, time, timedelta
from unittest.mock import patch

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
        # Checks independent from the computation: no lateness without minutes late or without an expected time
        self.assertGreaterEqual(attendance.late_minutes, 0)
        if attendance.is_late:
            self.assertGreater(attendance.late_minutes, 0)
        if attendance.late_minutes:
            self.assertTrue(attendance.expected_check_in)

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

    def test_new_version_recomputes_only_its_period(self):
        # Timezone and schedule are per version: a new version rewrites its own period, not the past
        early_calendar = self.fixed_calendar.copy({"name": "Lateness early"})
        early_calendar.attendance_ids.filtered(lambda a: a.hour_from == 9).hour_from = 7
        employee = self._employee(self.fixed_calendar)
        wednesday = self.monday + timedelta(days=2)
        before = self._check_in(employee, self.monday, 9, 30)
        after = self._check_in(employee, wednesday, 9, 30)
        self.assertRecordValues(after, [{"expected_check_in": self._utc(wednesday, 9), "late_minutes": 30}])
        # Mark the stored value outside the new period: it must not be recomputed
        self.env.flush_all()
        self.env.cr.execute("UPDATE hr_attendance SET late_minutes = 999 WHERE id = %s", [before.id])
        before.invalidate_recordset()
        employee.create_version(
            {
                "date_version": self.monday + timedelta(days=1),
                "resource_calendar_id": early_calendar.id,
                "tz": "Europe/Madrid",
            }
        )
        self.assertEqual(employee.resource_calendar_id, early_calendar)
        self.assertRecordValues(before, [{"expected_check_in": self._utc(self.monday, 9), "late_minutes": 999}])
        madrid_start = (
            datetime.combine(wednesday, time(7), tzinfo=ZoneInfo("Europe/Madrid")).astimezone(UTC).replace(tzinfo=None)
        )
        self.assertRecordValues(
            after,
            [
                {
                    "expected_check_in": madrid_start,
                    "late_minutes": int((after.check_in - madrid_start).total_seconds() / 60),
                    "is_late": True,
                }
            ],
        )
        self._assert_invariants(after)

    def test_deleted_version_recomputes_its_period(self):
        early_calendar = self.fixed_calendar.copy({"name": "Lateness early on delete"})
        early_calendar.attendance_ids.filtered(lambda a: a.hour_from == 9).hour_from = 7
        employee = self._employee(self.fixed_calendar)
        wednesday = self.monday + timedelta(days=2)
        version = employee.create_version(
            {"date_version": self.monday + timedelta(days=1), "resource_calendar_id": early_calendar.id}
        )
        attendance = self._check_in(employee, wednesday, 9, 30)
        self.assertRecordValues(attendance, [{"expected_check_in": self._utc(wednesday, 7), "late_minutes": 150}])
        version.unlink()
        self.assertRecordValues(
            attendance,
            [{"expected_check_in": self._utc(wednesday, 9), "late_minutes": 30, "is_late": True}],
        )
        self._assert_invariants(attendance)

    def test_schedule_read_once_for_many_attendances(self):
        employees = self._employee(self.fixed_calendar) | self._employee(self.fixed_calendar)
        days = [self.monday + timedelta(days=offset) for offset in (0, 1, 2, 7, 8)]
        calendar_class = type(self.env["resource.calendar"])
        original = calendar_class._work_intervals_batch
        calls = []

        def counted(calendar, *args, **kwargs):
            calls.append(calendar)
            return original(calendar, *args, **kwargs)

        with patch.object(calendar_class, "_work_intervals_batch", counted):
            attendances = self.env["hr.attendance"].create(
                [
                    {
                        "employee_id": employee.id,
                        "check_in": self._utc(day, 9, 30),
                        "check_out": self._utc(day, 17),
                    }
                    for employee in employees
                    for day in days
                ]
            )
            self.env.flush_all()
        self.assertEqual(len(calls), 1)
        self.assertRecordValues(
            attendances,
            [
                {"expected_check_in": self._utc(day, 9), "late_minutes": 30, "is_late": True}
                for _employee in employees
                for day in days
            ],
        )

    def test_flexible_before_the_range_does_not_leak(self):
        # The range starts on another employee's day, when this one still had a flexible schedule
        flexible = self.env["resource.calendar"].create(
            {"name": "Lateness flexible before", "calendar_type": "undefined", "attendance_ids": [Command.clear()]}
        )
        employee = self.env["hr.employee"].create(
            {
                "name": "Lateness employee, flexible before",
                "resource_calendar_id": flexible.id,
                "tz": self.tz_name,
                "date_version": self.monday - relativedelta(months=1),
                "contract_date_start": self.monday - relativedelta(months=1),
            }
        )
        employee.create_version(
            {"date_version": self.monday + timedelta(days=1), "resource_calendar_id": self.fixed_calendar.id}
        )
        wednesday = self.monday + timedelta(days=2)
        attendances = self.env["hr.attendance"].create(
            [
                {
                    "employee_id": self._employee(self.fixed_calendar).id,
                    "check_in": self._utc(self.monday, 9, 30),
                    "check_out": self._utc(self.monday, 17),
                },
                {
                    "employee_id": employee.id,
                    "check_in": self._utc(wednesday, 9, 30),
                    "check_out": self._utc(wednesday, 17),
                },
            ]
        )
        self.assertRecordValues(
            attendances,
            [
                {"expected_check_in": self._utc(self.monday, 9), "late_minutes": 30, "is_late": True},
                {"expected_check_in": self._utc(wednesday, 9), "late_minutes": 30, "is_late": True},
            ],
        )
        self._assert_invariants(attendances[1])

    def test_negative_threshold_needs_minutes_late(self):
        self.env.company.attendance_lateness_threshold = -5
        saturday = self.monday + timedelta(days=5)
        attendance = self._check_in(self._employee(self.fixed_calendar), saturday, 11)
        self.assertRecordValues(attendance, [{"late_minutes": 0, "is_late": False}])
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

    def test_time_off_is_not_expected_work(self):
        employee = self._employee(self.fixed_calendar)
        monday_attendance = self._check_in(employee, self.monday, 11)
        with self.subTest("holiday loaded after the check-in"):
            self.assertTrue(monday_attendance.is_late)
            holiday = self.env["resource.calendar.leaves"].create(
                {
                    "name": "Holiday",
                    "calendar_id": self.fixed_calendar.id,
                    "date_from": self._utc(self.monday, 0),
                    "date_to": self._utc(self.monday, 23, 59),
                }
            )
            self.assertRecordValues(
                monday_attendance, [{"expected_check_in": False, "late_minutes": 0, "is_late": False}]
            )
            self._assert_invariants(monday_attendance)
        with self.subTest("holiday removed: the lateness comes back"):
            holiday.unlink()
            self.assertRecordValues(
                monday_attendance,
                [{"expected_check_in": self._utc(self.monday, 9), "late_minutes": 120, "is_late": True}],
            )
            self._assert_invariants(monday_attendance)
        tuesday = self.monday + timedelta(days=1)
        with self.subTest("partial time off: expected when it ends"):
            time_off = self.env["resource.calendar.leaves"].create(
                {
                    "name": "Doctor",
                    "resource_id": employee.resource_id.id,
                    "date_from": self._utc(tuesday, 9),
                    "date_to": self._utc(tuesday, 11),
                }
            )
            attendance = self._check_in(employee, tuesday, 11, 10)
            self.assertRecordValues(
                attendance,
                [{"expected_check_in": self._utc(tuesday, 11), "late_minutes": 10, "is_late": True}],
            )
            self._assert_invariants(attendance)
        with self.subTest("time off moved to another day"):
            wednesday = self.monday + timedelta(days=2)
            time_off.write({"date_from": self._utc(wednesday, 9), "date_to": self._utc(wednesday, 11)})
            self.assertRecordValues(
                attendance,
                [{"expected_check_in": self._utc(tuesday, 9), "late_minutes": 130, "is_late": True}],
            )
            self._assert_invariants(attendance)

    def test_time_off_on_a_parent_company_schedule(self):
        # The time off takes the schedule's company, the parent one, while the employee is in the child
        child = self.env["res.company"].create({"name": "Lateness child", "parent_id": self.env.company.id})
        employee = (
            self.env["hr.employee"]
            .with_company(child)
            .create(
                {
                    "name": "Lateness employee, child company",
                    "company_id": child.id,
                    "resource_calendar_id": self.fixed_calendar.id,
                    "tz": self.tz_name,
                    "date_version": self.monday - relativedelta(months=1),
                }
            )
        )
        tuesday = self.monday + timedelta(days=1)
        time_off = self.env["resource.calendar.leaves"].create(
            {
                "name": "Doctor",
                "resource_id": employee.resource_id.id,
                "calendar_id": self.fixed_calendar.id,
                "date_from": self._utc(tuesday, 9),
                "date_to": self._utc(tuesday, 11),
            }
        )
        self.assertEqual(time_off.company_id, self.env.company)
        attendance = self._check_in(employee, tuesday, 11, 10)
        self.assertRecordValues(
            attendance,
            [{"expected_check_in": self._utc(tuesday, 11), "late_minutes": 10, "is_late": True}],
        )
        self._assert_invariants(attendance)

    def test_no_expected_check_in_with_duration_based_schedule(self):
        calendar = self.env["resource.calendar"].create(
            {
                "name": "Lateness duration",
                "calendar_type": "fixed",
                "attendance_ids": [Command.clear()]
                + [
                    Command.create({"dayofweek": str(day), "hour_from": 0, "hour_to": 0, "duration_hours": 6})
                    for day in range(5)
                ],
            }
        )
        attendance = self._check_in(self._employee(calendar), self.monday, 11)
        self.assertRecordValues(attendance, [{"expected_check_in": False, "late_minutes": 0, "is_late": False}])
        self._assert_invariants(attendance)

    def test_refused_attendance_is_not_late(self):
        attendance = self._check_in(self._employee(self.fixed_calendar), self.monday, 9, 30)
        self.assertTrue(attendance.is_late)
        attendance.action_refuse()
        self.assertRecordValues(attendance, [{"state": "refused", "late_minutes": 0, "is_late": False}])
        self._assert_invariants(attendance)

    def test_recompute_on_threshold_not_on_schedule_change(self):
        attendance = self._check_in(self._employee(self.fixed_calendar), self.monday, 9, 30)
        self.assertTrue(attendance.is_late)
        with self.subTest("threshold"):
            self.env.company.attendance_lateness_threshold = 60
            self.assertRecordValues(attendance, [{"late_minutes": 30, "is_late": False}])
            self._assert_invariants(attendance)
        with self.subTest("an edited schedule slot applies from now on, as core work entries"):
            monday_slots = self.fixed_calendar.attendance_ids.filtered(
                lambda slot: slot.dayofweek == "0" and slot.hour_from == 9
            )
            monday_slots.hour_from = 8
            self.assertRecordValues(
                attendance,
                [{"expected_check_in": self._utc(self.monday, 9), "late_minutes": 30, "is_late": False}],
            )
            self._assert_invariants(attendance)
            new_attendance = self._check_in(self._employee(self.fixed_calendar), self.monday, 9, 30)
            self.assertRecordValues(
                new_attendance, [{"expected_check_in": self._utc(self.monday, 8), "late_minutes": 90}]
            )
