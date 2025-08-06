from collections import defaultdict

from odoo import Command, _, api, fields, models
from odoo.exceptions import UserError


class UpdatePaymentResponsibleWizard(models.TransientModel):
    _name = "update.payment.responsible.wizard"
    _description = "Update Payment Responsible"

    invoice_ids = fields.Many2many("account.move")
    line_ids = fields.One2many("update.payment.responsible.line", "wizard_id")

    def _get_max_invoices_limit(self):
        try:
            max_invoices = int(
                self.env["ir.config_parameter"]
                .sudo()
                .get_param("academic_sale_subscription.max_invoices_update_payment_responsible", default="200")
            )
            if max_invoices <= 0:
                max_invoices = 200
        except (ValueError, TypeError):
            max_invoices = 200
        return max_invoices

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        active_ids = self.env.context.get("active_ids", [])
        max_invoices = self._get_max_invoices_limit()
        if len(active_ids) > max_invoices:
            raise UserError(_("You can only select a maximum of %s invoices at once.") % max_invoices)

        res["invoice_ids"] = [(6, 0, active_ids)]
        lines = []
        if active_ids:
            invoices = self.env["account.move"].browse(active_ids)
            grouped = defaultdict(list)
            for inv in invoices:
                key = (inv.partner_id.id, inv.student_id.id if inv.student_id else None)
                grouped[key].append(inv)
            for invs in grouped.values():
                suggested, payment_responsible_ids = self._get_suggested_responsible(invs[0])
                current_responsible_id = invs[0].partner_id.id
                lines.append(
                    (
                        0,
                        0,
                        {
                            "invoice_ids": [Command.set([inv.id for inv in invs])],
                            "current_responsible_id": current_responsible_id,
                            "payment_responsible_ids": [Command.set(payment_responsible_ids)],
                            "new_responsible_id": suggested,
                        },
                    )
                )
        res["line_ids"] = lines
        return res

    def action_update_responsible(self):
        for line in self.line_ids.filtered("new_responsible_id"):
            invoices = line.invoice_ids.filtered(lambda inv: not inv.matched_payment_ids)
            if invoices and line.current_responsible_id != line.new_responsible_id:
                invoices.with_context(skip_readonly_check=True).write({"partner_id": line.new_responsible_id.id})

    def _get_suggested_responsible(self, inv):
        paying_role = self.env.ref("academic.paying_role")
        responsible_ids = set()
        suggested = False

        # tiene estudiante definida en factura
        if inv.student_id:
            student_links = inv.student_id.student_link_ids.filtered(lambda x: paying_role in x.role_ids)
            if student_links:
                suggested = student_links.sorted("sequence")[:1].partner_id
                responsible_ids.update(student_links.mapped("partner_id").ids)

        # el partner_id es estudiante
        elif inv.partner_id.partner_type == "student":
            student_links = inv.partner_id.student_link_ids.filtered(lambda x: paying_role in x.role_ids)
            if student_links:
                suggested = student_links.sorted("sequence")[:1].partner_id
                responsible_ids.update(student_links.mapped("partner_id").ids)

        # el partner_id es familia
        elif inv.partner_id.partner_type == "family":
            if inv.partner_id.links_by_student:
                student = inv.partner_id.child_ids.filtered(lambda x: x.partner_type == "student")[:1]
                if student:
                    student_links = student.student_link_ids.filtered(lambda x: paying_role in x.role_ids)
                    if student_links:
                        suggested = student_links.sorted("sequence")[:1].partner_id
                        responsible_ids.update(student_links.mapped("partner_id").ids)
            else:
                student_links = inv.partner_id.student_link_ids.filtered(lambda x: paying_role in x.role_ids)
                if student_links:
                    suggested = student_links.sorted("sequence")[:1].partner_id
                    responsible_ids.update(student_links.mapped("partner_id").ids)

        # el partner_id es pariente
        elif inv.partner_id.partner_type == "parent":
            family = inv.partner_id.partner_link_ids.filtered(lambda x: x.student_id.partner_type == "family").mapped(
                "student_id"
            )[:1]
            if family:
                family = family[0]
                if family.links_by_student:
                    student = family.child_ids.filtered(lambda x: x.partner_type == "student")[:1]
                    if student:
                        student_links = student.student_link_ids.filtered(lambda x: paying_role in x.role_ids)
                        if student_links:
                            suggested = student_links.sorted("sequence")[:1].partner_id
                            responsible_ids.update(student_links.mapped("partner_id").ids)
                else:
                    student_links = family.student_link_ids.filtered(lambda x: paying_role in x.role_ids)
                    if student_links:
                        suggested = student_links.sorted("sequence")[:1].partner_id
                        responsible_ids.update(student_links.mapped("partner_id").ids)
        return suggested, list(responsible_ids)


class UpdatePaymentResponsibleLine(models.TransientModel):
    _name = "update.payment.responsible.line"
    _description = "Update Payment Responsible Line"

    wizard_id = fields.Many2one("update.payment.responsible.wizard", string="Wizard", required=True, ondelete="cascade")
    invoice_ids = fields.Many2many("account.move", string="Invoices")
    current_responsible_id = fields.Many2one("res.partner")
    payment_responsible_ids = fields.Many2many("res.partner")
    new_responsible_id = fields.Many2one(
        "res.partner",
        domain="[('id', 'in', payment_responsible_ids)]",
    )
