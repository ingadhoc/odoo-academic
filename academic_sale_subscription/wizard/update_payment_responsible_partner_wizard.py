##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class UpdatePaymentResponsiblePartnerWizard(models.TransientModel):
    _name = "update.payment.responsible.partner.wizard"
    _description = "Update Payment Responsible from Partner"

    current_partner_id = fields.Many2one(
        "res.partner", string="Current Payment Responsible", required=True, readonly=True
    )
    new_partner_id = fields.Many2one("res.partner", string="New Payment Responsible", required=True)
    available_partner_ids = fields.Many2many(
        "res.partner", "payment_responsible_available_rel", "wizard_id", "partner_id", string="Available Partners"
    )

    invoice_count = fields.Integer(string="Pending Invoices", readonly=True)
    invoice_ids = fields.Many2many(
        "account.move",
        "payment_responsible_invoice_rel",
        "wizard_id",
        "invoice_id",
        string="Invoices to Update",
        readonly=True,
    )

    sale_count = fields.Integer(string="Active Sales/Subscriptions", readonly=True)
    sale_ids = fields.Many2many(
        "sale.order",
        "payment_responsible_sale_rel",
        "wizard_id",
        "order_id",
        string="Sales/Subscriptions to Update",
        readonly=True,
    )

    warning_message = fields.Text(readonly=True)
    student_ids = fields.Many2many("res.partner", "payment_responsible_student_rel", "wizard_id", "student_id")

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        active_id = self.env.context.get("active_id")

        if not active_id:
            raise UserError(_("No partner selected."))

        partner = self.env["res.partner"].browse(active_id)

        paying_role = self.env.ref("academic.paying_role")
        partner_links_with_paying_role = partner.partner_link_ids.filtered(lambda l: paying_role in l.role_ids)
        if not partner_links_with_paying_role:
            raise UserError(_("Partner %s does not have the Payment Responsible role.") % partner.name)

        affected_students = self.env["res.partner"]
        for link in partner_links_with_paying_role:
            if link.student_id.partner_type == "student":
                affected_students |= link.student_id
            elif link.student_id.partner_type == "family":
                affected_students |= link.student_id.student_ids.filtered(lambda s: s.partner_type == "student")

        res["current_partner_id"] = active_id
        res["student_ids"] = [(6, 0, affected_students.ids)]

        available_partners = (
            self.env["res.partner.link"].search([("student_id", "in", affected_students.ids)]).mapped("partner_id")
        )
        res["available_partner_ids"] = [(6, 0, available_partners.ids)]

        pending_invoices = self.env["account.move"].search(
            [
                ("partner_id", "=", active_id),
                ("move_type", "in", ["out_invoice", "out_refund"]),
                ("state", "=", "posted"),
                ("amount_residual", ">", 0),
            ]
        )

        invoices_without_payments = pending_invoices.filtered(lambda inv: not inv.matched_payment_ids)

        active_sales = self.env["sale.order"].search(
            [
                ("partner_invoice_id", "=", active_id),
                "|",
                ("state", "in", ["draft", "sent"]),
                ("subscription_state", "=", "3_progress"),
            ]
        )

        res.update(
            {
                "invoice_count": len(invoices_without_payments),
                "invoice_ids": [(6, 0, invoices_without_payments.ids)],
                "sale_count": len(active_sales),
                "sale_ids": [(6, 0, active_sales.ids)],
            }
        )

        warning_parts = []
        if invoices_without_payments:
            warning_parts.append(
                _("%d pending invoices (without registered payments)") % len(invoices_without_payments)
            )
        if active_sales:
            warning_parts.append(_("%d active sales/subscriptions") % len(active_sales))

        if warning_parts:
            res["warning_message"] = _("This action will update the payment responsible for: %s") % ", ".join(
                warning_parts
            )
        else:
            res["warning_message"] = _("No records found to update.")

        return res

    def action_update_payment_responsible(self):
        if not self.new_partner_id:
            raise UserError(_("Please select a new payment responsible."))

        if self.current_partner_id == self.new_partner_id:
            raise UserError(_("New payment responsible must be different from current one."))

        updated_invoices = 0
        updated_sales = 0

        if self.invoice_ids:
            self.invoice_ids.with_context(skip_readonly_check=True).write({"partner_id": self.new_partner_id.id})
            updated_invoices = len(self.invoice_ids)

        if self.sale_ids:
            self.sale_ids.write({"partner_invoice_id": self.new_partner_id.id})
            orders_to_subscribe = self.sale_ids.filtered(
                lambda o: self.new_partner_id.id not in o.sudo().message_partner_ids.ids
            )
            if orders_to_subscribe:
                orders_to_subscribe.message_subscribe([self.new_partner_id.id])
            updated_sales = len(self.sale_ids)

        paying_role = self.env.ref("academic.paying_role")

        processed_partners = set()

        for student in self.student_ids:
            target_partner = student
            if student.parent_id and not student.parent_links_by_student:
                target_partner = student.parent_id

            if target_partner.id in processed_partners:
                continue
            processed_partners.add(target_partner.id)

            all_links = target_partner.student_link_ids
            min_sequence = min(all_links.mapped("sequence") or [10])

            new_partner_link = all_links.filtered(lambda l: l.partner_id == self.new_partner_id)
            if new_partner_link:
                vals_to_write = {}

                if paying_role not in new_partner_link.role_ids:
                    vals_to_write["role_ids"] = [(4, paying_role.id)]

                if new_partner_link.sequence >= min_sequence:
                    vals_to_write["sequence"] = min_sequence - 1

                if vals_to_write:
                    new_partner_link.write(vals_to_write)

            old_partner_link = all_links.filtered(lambda l: l.partner_id == self.current_partner_id)
            if old_partner_link and paying_role in old_partner_link.role_ids:
                if old_partner_link.sequence < min_sequence:
                    old_partner_link.write({"sequence": min_sequence + 10})

            # Force recompute if we updated a parent, so changes propagate to students immediately
            if target_partner != student:
                students_to_update = self.env["res.partner"].search(
                    [("parent_id", "=", target_partner.id), ("partner_type", "=", "student")]
                )
                students_to_update._compute_student_links()

        message_parts = []
        if updated_invoices:
            message_parts.append(_("%d invoices updated") % updated_invoices)
        if updated_sales:
            message_parts.append(_("%d sales/subscriptions updated") % updated_sales)

        message_parts.append(_("Payment responsible roles updated"))

        if message_parts:
            message = _("Payment responsible successfully updated for: %s") % ", ".join(message_parts)
        else:
            message = _("No records were updated.")

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Success"),
                "message": message,
                "type": "success",
                "sticky": False,
                "next": {
                    "type": "ir.actions.client",
                    "tag": "soft_reload",
                },
            },
        }
