from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools import sql


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    main_employee_id = fields.Many2one(
        "hr.employee",
        string="Main Employee",
    )
    child_employee_ids = fields.One2many(
        "hr.employee",
        "main_employee_id",
        string="Child Employees",
    )
    company_id = fields.Many2one(
        compute="_compute_company_id",
        store=True,
        readonly=False,
    )

    def init(self):
        """Remove the unique constraint on user_id and company_id"""
        super().init()

        # Drop the unique constraint if it exists
        self.env.cr.execute("""
            SELECT conname
            FROM pg_constraint
            WHERE conname LIKE '%user_uniq%'
            AND conrelid = (SELECT oid FROM pg_class WHERE relname = 'hr_employee')
        """)

        constraint = self.env.cr.fetchone()
        if constraint:
            constraint_name = constraint[0]
            # pylint: disable=sql-injection - Using SQL.identifier for safe identifier composition
            self.env.cr.execute(
                sql.SQL(
                    "ALTER TABLE %(table)s DROP CONSTRAINT %(constraint)s",
                    table=sql.SQL.identifier("hr_employee"),
                    constraint=sql.SQL.identifier(constraint_name),
                )
            )

    @api.depends("main_employee_id", "main_employee_id.company_id")
    def _compute_company_id(self):
        for employee in self:
            if employee.main_employee_id:
                employee.company_id = employee.main_employee_id.company_id
            elif not employee.company_id:
                employee.company_id = self.env.company

    @api.constrains("main_employee_id")
    def _check_main_employee_recursion(self):
        if self._has_cycle("main_employee_id"):
            raise UserError(self.env._("You cannot create circular references in the employee hierarchy."))

    @api.constrains("company_id", "main_employee_id")
    def _check_child_employee_company(self):
        for employee in self:
            if employee.main_employee_id and employee.company_id != employee.main_employee_id.company_id:
                raise UserError(
                    self.env._(
                        "Child employees must have the same company as their main employee. "
                        "Employee '%(employee_name)s' company must be '%(company_name)s'.",
                        employee_name=employee.name,
                        company_name=employee.main_employee_id.company_id.name,
                    )
                )

    def write(self, vals):
        res = super().write(vals)
        # Propagate user_id to child employees
        if "user_id" in vals and self.child_employee_ids:
            self.child_employee_ids.write({"user_id": vals["user_id"]})

        # Propagate company_id to child employees
        if "company_id" in vals and self.child_employee_ids:
            self.child_employee_ids.write({"company_id": vals["company_id"]})

        return res
