from datetime import timedelta

from odoo import api, models
from odoo.fields import Domain


class ResourceCalendarLeaves(models.Model):
    _inherit = "resource.calendar.leaves"

    @api.model_create_multi
    def create(self, vals_list):
        leaves = super().create(vals_list)
        self.env["hr.attendance"]._recompute_lateness_matching(leaves._lateness_domain())
        return leaves

    def write(self, vals):
        # Dates may move the period: the old one and the new one both need it
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
        return Domain.OR(domains) if domains else Domain.FALSE
