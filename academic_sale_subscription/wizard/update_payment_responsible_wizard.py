from odoo import api, fields, models


class UpdatePaymentResponsibleWizard(models.TransientModel):
    _name = "update.payment.responsible.wizard"
    _description = "Update Payment Responsible"

    update_type = fields.Selection(
        [
            ("auto", "Automatic"),
            ("manual", "Manual"),
        ],
        default="auto",
        required=True,
        help="In automatic mode, the system will try to suggest the payment responsible based on the defined rules. In manual mode, you can select the responsible manually.",
    )
    invoice_ids = fields.Many2many("account.move")
    line_ids = fields.One2many(
        "update.payment.responsible.line", "wizard_id", compute="_compute_line_ids", readonly=False, store=True
    )

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        active_ids = self.env.context.get("active_ids", [])
        res["invoice_ids"] = [(6, 0, active_ids)]
        return res

    @api.depends("update_type")
    def _compute_line_ids(self):
        for rec in self:
            if rec.update_type == "manual":
                lines = []
                for inv in rec.invoice_ids:
                    suggested = self._get_suggested_responsible(inv)
                    lines.append(
                        (
                            0,
                            0,
                            {
                                "invoice_id": inv.id,
                                "new_responsible_id": suggested if suggested else False,
                            },
                        )
                    )
                rec.write({"line_ids": lines})

    def action_update_responsible(self):
        if self.update_type == "auto":
            for inv in self.invoice_ids:
                suggested = self._get_suggested_responsible(inv)
                if suggested and inv.partner_id != suggested:
                    inv.with_context(skip_readonly_check=True).write({"partner_id": suggested.id})
                    if inv.matched_payment_ids:
                        inv.matched_payment_ids.with_context(skip_readonly_check=True).write(
                            {"partner_id": suggested.id}
                        )
        else:
            for line in self.line_ids.filtered("new_responsible_id"):
                inv = line.invoice_id
                if inv.partner_id != line.new_responsible_id:
                    inv.with_context(skip_readonly_check=True).write({"partner_id": line.new_responsible_id.id})
                    if inv.matched_payment_ids:
                        inv.matched_payment_ids.with_context(skip_readonly_check=True).write(
                            {"partner_id": line.new_responsible_id.id}
                        )

    def _get_suggested_responsible(self, inv):
        # tiene estudiante definida en factura
        if inv.student_id:
            student_links = inv.student_id.student_link_ids.filtered(
                lambda x: self.env.ref("academic.paying_role") in x.role_ids
            )
            if student_links:
                return student_links.sorted("sequence")[:1].partner_id

        # el partner_id es estudiante
        if inv.partner_id.partner_type == "student":
            student_links = inv.partner_id.student_link_ids.filtered(
                lambda x: self.env.ref("academic.paying_role") in x.role_ids
            )
            if student_links:
                return student_links.sorted("sequence")[:1].partner_id

        # el partner_id es familia
        elif inv.partner_id.partner_type == "family":
            if inv.partner_id.links_by_student:
                student = inv.partner_id.child_ids.filtered(lambda x: x.partner_type == "student")[:1]
                student_links = (
                    student.student_link_ids.filtered(lambda x: self.env.ref("academic.paying_role") in x.role_ids)
                    if student
                    else False
                )
            else:
                student_links = inv.partner_id.student_link_ids.filtered(
                    lambda x: self.env.ref("academic.paying_role") in x.role_ids
                )
            if student_links:
                return student_links.sorted("sequence")[:1].partner_id

        # el padre del partner_id es familia
        elif inv.partner_id.parent_id and inv.partner_id.parent_id.partner_type == "family":
            if inv.partner_id.parent_id.links_by_student:
                student = inv.partner_id.parent_id.child_ids.filtered(lambda x: x.partner_type == "student")[:1]
                student_links = (
                    student.student_link_ids.filtered(lambda x: self.env.ref("academic.paying_role") in x.role_ids)
                    if student
                    else False
                )
            else:
                student_links = inv.partner_id.student_link_ids.filtered(
                    lambda x: self.env.ref("academic.paying_role") in x.role_ids
                )
            student_links = inv.partner_id.parent_id.student_link_ids.filtered(
                lambda x: self.env.ref("academic.paying_role") in x.role_ids
            )
            if student_links:
                return student_links.sorted("sequence")[:1].partner_id

        # el partner_id es pariente, por si hay un partner en la factura que no es el primero definido como responsable de pago
        elif inv.partner_id.partner_type == "parent":
            family = inv.partner_id.partner_link_ids.filtered(lambda x: x.student_id.partner_type == "family").mapped(
                "student_id"
            )[:1]
            if family:
                if family.links_by_student:
                    student = family.childs_ids.filtered(lambda x: x.partner_type == "student")[:1]
                    student_links = (
                        student.student_link_ids.filtered(lambda x: self.env.ref("academic.paying_role") in x.role_ids)
                        if student
                        else False
                    )
                else:
                    student_links = family.student_link_ids.filtered(
                        lambda x: self.env.ref("academic.paying_role") in x.role_ids
                    )
                if student_links:
                    return student_links.sorted("sequence")[:1].partner_id

        return False


class UpdatePaymentResponsibleLine(models.TransientModel):
    _name = "update.payment.responsible.line"
    _description = "Update Payment Responsible Line"

    wizard_id = fields.Many2one("update.payment.responsible.wizard", string="Wizard", required=True, ondelete="cascade")
    invoice_id = fields.Many2one("account.move", string="Invoice", required=True)
    current_responsible_id = fields.Many2one(
        "res.partner", string="Current Responsible", related="invoice_id.partner_id"
    )
    new_responsible_id = fields.Many2one("res.partner", string="New Responsible")
