##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import Command, _, models
from odoo.exceptions import ValidationError


class ResPartnerLink(models.Model):
    _inherit = "res.partner.link"

    def _get_affected_students(self, link):
        """Get list of students affected by this link."""
        if link.student_id.partner_type == "student":
            return [link.student_id]
        elif link.student_id.partner_type == "family":
            return link.student_id.student_ids.filtered(lambda s: s.partner_type == "student")
        return []

    def _check_payment_responsible_restrictions(self, links):
        """Check if payment responsible role can be removed/deleted."""
        if not links:
            return

        paying_role = self.env.ref("academic.paying_role")

        for link in links:
            if paying_role not in link.role_ids:
                continue

            students_to_check = self._get_affected_students(link)
            if not students_to_check:
                continue

            pending_invoices = self.env["account.move"].search(
                [
                    ("student_id", "in", [s.id for s in students_to_check]),
                    ("move_type", "in", ["out_invoice", "out_refund"]),
                    ("state", "=", "posted"),
                    ("amount_residual", ">", 0),
                ],
                limit=1,
            )

            if pending_invoices:
                student_with_debt = pending_invoices.student_id
                raise ValidationError(
                    _(
                        'Cannot remove "Payment Responsible" role from contact %s '
                        "because student %s has pending invoices."
                    )
                    % (link.partner_id.name, student_with_debt.name)
                )

            active_subscriptions = self.env["sale.order"].search(
                [
                    ("partner_invoice_id", "=", link.partner_id.id),
                    ("subscription_state", "=", "3_progress"),
                    ("partner_id", "in", [s.id for s in students_to_check]),
                ],
                limit=1,
            )

            if active_subscriptions:
                student_with_subscription = active_subscriptions.partner_id
                raise ValidationError(
                    _(
                        'Cannot remove "Payment Responsible" role from contact %s '
                        "because student %s has active subscriptions."
                    )
                    % (link.partner_id.name, student_with_subscription.name)
                )

    def _process_role_commands(self, old_roles, role_commands):
        """Process Many2many commands to determine resulting roles."""
        new_roles = old_roles

        if not isinstance(role_commands, list):
            return new_roles

        ResPartnerRole = self.env["res.partner.role"]

        for command in role_commands:
            if command[0] == Command.SET:
                new_roles = ResPartnerRole.browse(command[2])
            elif command[0] == Command.LINK:
                new_roles |= ResPartnerRole.browse(command[1])
            elif command[0] == Command.UNLINK:
                new_roles -= ResPartnerRole.browse(command[1])
            elif command[0] == Command.CLEAR:
                new_roles = ResPartnerRole
            elif command[0] == Command.DELETE:
                new_roles -= ResPartnerRole.browse(command[1])

        return new_roles

    def write(self, vals):
        if "role_ids" in vals:
            paying_role = self.env.ref("academic.paying_role")
            links_to_check = []

            for link in self:
                if paying_role not in link.role_ids:
                    continue

                new_roles = self._process_role_commands(link.role_ids, vals["role_ids"])
                if paying_role not in new_roles:
                    links_to_check.append(link)

            if links_to_check:
                self._check_payment_responsible_restrictions(links_to_check)

        return super().write(vals)

    def unlink(self):
        paying_role = self.env.ref("academic.paying_role")
        links_with_paying_role = self.filtered(lambda l: paying_role in l.role_ids)

        if links_with_paying_role:
            self._check_payment_responsible_restrictions(links_with_paying_role)

        return super().unlink()

    def action_change_payment_responsible(self):
        paying_role = self.env.ref("academic.paying_role")
        if paying_role not in self.role_ids:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Warning"),
                    "message": _("This link does not have the Payment Responsible role."),
                    "type": "warning",
                    "sticky": False,
                },
            }

        return {
            "type": "ir.actions.act_window",
            "name": _("Change Payment Responsible"),
            "res_model": "update.payment.responsible.partner.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {"active_id": self.partner_id.id},
        }
