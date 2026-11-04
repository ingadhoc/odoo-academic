from odoo import api, models


class ResUsers(models.Model):
    _inherit = "res.users"

    @api.depends("employee_ids")
    @api.depends_context("company", "uid")
    def _compute_company_employee(self):
        """Pick one employee out of the several this module allows per company.

        The Many2one raises if the core hands it more than one record, so the
        computation cannot be delegated to super(): the main employee wins.
        """
        employee_per_user = dict(
            self.env["hr.employee"]
            .sudo()
            ._read_group(
                domain=[("user_id", "in", self.ids), ("company_id", "=", self.env.company.id)],
                groupby=["user_id"],
                aggregates=["id:recordset"],
            )
        )

        for user in self:
            employee = employee_per_user.get(user, self.env["hr.employee"])
            if user != self.env.user and not self.env.su:
                # since the search is done in sudo to avoid cache issues, apply access rules
                employee = employee.filtered(lambda e: e.has_access("read"))
            user.employee_id = employee.filtered(lambda e: not e.main_employee_id)[:1] or employee[:1]
