from datetime import UTC, datetime, time

from odoo import api, models
from odoo.fields import Domain
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

LATENESS_FIELDS = {"resource_calendar_id", "tz", "date_version", "active"}


class HrVersion(models.Model):
    _inherit = "hr.version"

    @api.model_create_multi
    def create(self, vals_list):
        versions = super().create(vals_list)
        versions._recompute_attendance_lateness()
        return versions

    def write(self, vals):
        recompute = bool(LATENESS_FIELDS & set(vals))
        if recompute:
            # Before and after: date_version may move the period
            self._recompute_attendance_lateness()
        res = super().write(vals)
        if recompute:
            self._recompute_attendance_lateness()
        return res

    def unlink(self):
        self._recompute_attendance_lateness()
        return super().unlink()

    def _recompute_attendance_lateness(self):
        """Recompute the attendances of the period each version is in effect, not the whole history."""
        domains = []
        for version in self.sudo():
            versions = version.employee_id.version_ids
            domain = Domain("employee_id", "=", version.employee_id.id)
            # Before its first version, an employee uses that first version
            if any(other.date_version < version.date_version for other in versions):
                domain &= Domain("check_in", ">=", version._lateness_day_start(version.date_version))
            later = versions.filtered(lambda other: other.date_version > version.date_version)
            if later:
                following = min(later, key=lambda other: other.date_version)
                domain &= Domain("check_in", "<", following._lateness_day_start(following.date_version))
            domains.append(domain)
        if domains:
            self.env["hr.attendance"].sudo().search(Domain.OR(domains))._recompute_lateness()

    def _lateness_day_start(self, day):
        """Start of a local day of this version, as the naive UTC datetime check-ins are stored in."""
        try:
            tz = ZoneInfo(self._get_tz())
        except ZoneInfoNotFoundError:
            tz = UTC
        return datetime.combine(day, time.min, tzinfo=tz).astimezone(UTC).replace(tzinfo=None)
