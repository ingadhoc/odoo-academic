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
        self.env["hr.attendance"]._recompute_lateness_matching(versions._lateness_domain())
        return versions

    def write(self, vals):
        if not LATENESS_FIELDS & set(vals):
            return super().write(vals)
        # date_version may move the period: the old one and the new one both need it
        before = self._lateness_domain()
        res = super().write(vals)
        self.env["hr.attendance"]._recompute_lateness_matching(Domain.OR([before, self._lateness_domain()]))
        return res

    def unlink(self):
        # The domain is read before the rows go and marked after they are gone:
        # unlink() flushes the pending computations before deleting
        domain = self._lateness_domain()
        res = super().unlink()
        self.env["hr.attendance"]._recompute_lateness_matching(domain)
        return res

    def _lateness_domain(self):
        """The attendances of the period each version is in effect, not the whole history."""
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
        return Domain.OR(domains) if domains else Domain.FALSE

    def _lateness_day_start(self, day):
        """Start of a local day of this version, as the naive UTC datetime check-ins are stored in."""
        try:
            tz = ZoneInfo(self._get_tz())
        except ZoneInfoNotFoundError:
            tz = UTC
        return datetime.combine(day, time.min, tzinfo=tz).astimezone(UTC).replace(tzinfo=None)
