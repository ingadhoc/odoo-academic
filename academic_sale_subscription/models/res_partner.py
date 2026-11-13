##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
import logging
from collections import defaultdict

from odoo import api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


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

    @api.model
    def _cron_send_grouped_invoice_notice(self):
        for company in self.env["res.company"].search([("academic_grouped_invoice_notice", "=", True)]):
            self.with_company(company)._send_grouped_invoice_notice()

    @api.model
    def _get_grouped_invoice_notice_domain(self):
        return [
            ("company_id", "=", self.env.company.id),
            ("move_type", "=", "out_invoice"),
            ("state", "=", "posted"),
            ("is_move_sent", "=", False),
            ("student_id", "!=", False),
        ]

    def _get_grouped_invoice_notice_moves(self):
        """Invoices of this notice. The mail template only displays what this method returns."""
        self.ensure_one()
        return self.env["account.move"].browse(self.env.context.get("grouped_invoice_notice_move_ids", []))

    def _get_grouped_invoice_notice_total_due(self):
        """What the students of this responsible still owe, including what is not in this notice. Invoices are
        billed to a single responsible, but every responsible of a student sees the whole debt."""
        self.ensure_one()
        moves = self.env["account.move"].search(
            [
                ("company_id", "=", self.env.company.id),
                ("student_id.payment_responsible_ids", "in", self.ids),
                ("move_type", "in", ["out_invoice", "out_refund"]),
                ("state", "=", "posted"),
                ("payment_state", "in", ["not_paid", "partial"]),
            ]
        )
        return sum(moves.mapped("amount_residual_signed"))

    @api.model
    def _send_grouped_invoice_notice(self):
        moves = self.env["account.move"].search(self._get_grouped_invoice_notice_domain())
        if not moves:
            return
        template = self.env.company.academic_grouped_invoice_notice_template_id
        if not template:
            _logger.warning(
                "No grouped invoice notice template set on company %s, skipping it.", self.env.company.display_name
            )
            return

        moves_by_responsible = defaultdict(lambda: self.env["account.move"])
        for move in moves:
            for responsible in move.student_id.payment_responsible_ids:
                moves_by_responsible[responsible] |= move

        for responsible in [responsible for responsible in moves_by_responsible if not responsible.email]:
            body = self.env._(
                "The grouped invoice notice was not sent: %s has no email address.", responsible.display_name
            )
            for move in moves_by_responsible.pop(responsible):
                move.message_post(body=body, subtype_xmlid="mail.mt_note")
        if not moves_by_responsible:
            return

        # The legal PDF comes from Odoo's own sending mechanism; the manual method generates and links it
        # without mailing one invoice at a time. One call for every invoice going out, because Odoo renders
        # the pdfs in batches and a call per responsible would render a batch for each of them.
        to_notice = self.env["account.move"].union(*moves_by_responsible.values())
        self.env["account.move.send"]._generate_and_send_invoices(
            to_notice, allow_raising=False, allow_fallback_pdf=True, sending_methods={"manual"}
        )
        for responsible, responsible_moves in moves_by_responsible.items():
            responsible._send_grouped_invoice_notice_mail(template, responsible_moves)

    def _send_grouped_invoice_notice_mail(self, template, moves):
        self.ensure_one()
        # A copy of each pdf, so that deleting the notice mail never reaches the invoice attachment
        attachments = self.env["ir.attachment"].create(
            [
                {"name": attachment.name, "raw": attachment.raw, "mimetype": attachment.mimetype}
                for attachment in self.env["account.move.send"]._get_invoice_extra_attachments(moves)
            ]
        )
        template.with_context(grouped_invoice_notice_move_ids=moves.ids).send_mail(
            self.id, email_values={"attachment_ids": attachments.ids}
        )
        # Odoo only marks the move when it creates the pdf, so a move that already had one would be noticed again
        moves.is_move_sent = True
        body = self.env._("Grouped invoice notice sent to %s.", self.display_name)
        for move in moves:
            move.message_post(body=body, subtype_xmlid="mail.mt_note")

    def action_archive(self):
        if not self.env.context.get("skip_debt_check"):
            families = self.filtered(lambda p: p.partner_type == "family" and p.active)
            families_with_debt = families.filtered(lambda f: f.student_ids._get_students_with_debt())
            if families_with_debt:
                return {
                    "type": "ir.actions.act_window",
                    "res_model": "archive.family.debt.wizard",
                    "views": [(False, "form")],
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
