##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import fields, models
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = "res.partner"

    current_subscription_ids = fields.One2many(
        "sale.order.line",
        compute="_compute_current_subscription",
    )

    def _compute_current_subscription(self):
        for rec in self:
            rec.current_subscription_ids = (
                self.env["sale.order.line"]
                .search([("order_partner_id", "=", rec.id), ("order_id.subscription_state", "=", "3_progress")])
                .filtered(
                    lambda line: not line.order_id.end_date
                    or (line.order_id.next_invoice_date and line.order_id.next_invoice_date < line.order_id.end_date)
                )
            )

    def _has_pending_debt(self):
        self.ensure_one()
        if self.partner_type != "student":
            return False

        payment_responsible = self.payment_responsible_ids
        if not payment_responsible:
            return False

        unpaid_invoices = self.env["account.move"].search(
            [
                ("partner_id", "in", payment_responsible.ids),
                ("move_type", "in", ["out_invoice", "out_refund"]),
                ("state", "=", "posted"),
                ("payment_state", "in", ["not_paid", "partial"]),
            ],
            limit=1,
        )
        return bool(unpaid_invoices)

    def _get_students_with_debt(self):
        students = self.filtered(lambda r: r.partner_type == "student")
        if not students:
            return self.env["res.partner"]

        all_responsible_ids = students.mapped("payment_responsible_ids").ids
        if not all_responsible_ids:
            return self.env["res.partner"]

        unpaid_invoices = self.env["account.move"].search(
            [
                ("partner_id", "in", all_responsible_ids),
                ("move_type", "in", ["out_invoice", "out_refund"]),
                ("state", "=", "posted"),
                ("payment_state", "in", ["not_paid", "partial"]),
            ],
        )
        responsible_with_debt = unpaid_invoices.mapped("partner_id")
        return students.filtered(lambda s: s.payment_responsible_ids & responsible_with_debt)

    def action_archive(self):
        if not self.env.context.get("skip_debt_check"):
            families = self.filtered(lambda p: p.partner_type == "family" and p.active)
            families_with_debt = families.filtered(lambda f: f.student_ids._get_students_with_debt())
            if families_with_debt:
                return {
                    "type": "ir.actions.act_window",
                    "res_model": "archive.family.debt.wizard",
                    "view_mode": "form",
                    "target": "new",
                    "context": {"default_family_ids": [(6, 0, self.ids)]},
                }
        return super().action_archive()

    def open_academic_order_wizard(self):
        action = self.env["ir.actions.actions"]._for_xml_id(
            "academic_sale_subscription.action_view_academic_order_wizard"
        )
        if academic_group := self.env.context.get("academic_group_id"):
            action.update(
                {
                    "context": {"academic_group_id": academic_group},
                }
            )
        return action

    def action_generate_debt_free_certificate(self):
        students = self.filtered(lambda r: r.partner_type == "student")

        if not students:
            return False

        students_with_debt = students._get_students_with_debt()

        if students_with_debt:
            raise UserError(
                self.env._(
                    "The payment responsible of the following students have pending debt and certificates cannot be generated:"
                )
                + "\n - "
                + "\n - ".join(students_with_debt.mapped("name"))
            )

        students_no_debt = students - students_with_debt

        if len(students_no_debt) == 1:
            return self.env.ref("academic_sale_subscription.report_debt_free_certificate").report_action(
                students_no_debt
            )

        # For multiple students, use academic_do_multi_print
        report = self.env.ref("academic_sale_subscription.report_debt_free_certificate")
        report_actions = [report.report_action(student, config=False) for student in students_no_debt]

        return {
            "type": "ir.actions.client",
            "tag": "academic_do_multi_print",
            "params": {
                "reports": report_actions,
            },
        }

    def action_send_debt_free_certificate_email(self):
        students = self.filtered(lambda r: r.partner_type == "student")
        students_with_debt = students._get_students_with_debt()
        students_no_debt = students - students_with_debt

        if students_with_debt:
            raise UserError(
                self.env._(
                    "The payment responsible of the following students have pending debt and certificates cannot be sent:"
                )
                + "\n - "
                + "\n - ".join(students_with_debt.mapped("name"))
            )

        if students_no_debt:
            template = self.env.ref("academic_sale_subscription.email_template_debt_free_certificate")
            for student in students_no_debt:
                if student.payment_responsible_ids:
                    template.send_mail(student.id, force_send=True)

            if len(students_no_debt) == 1:
                message = self.env._("Certificate sent successfully to payment responsible.")
            else:
                message = self.env._("%s certificates sent successfully.") % len(students_no_debt)

            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": self.env._("Certificates Sent"),
                    "message": message,
                    "type": "success",
                    "sticky": False,
                },
            }
