##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models


class AcademicGroup(models.Model):
    _inherit = "academic.group"

    def open_order_wizard(self):
        action = self.env.ref("academic_sale_subscription.action_view_academic_order_wizard").read()[0]
        action.update({"context": {"default_student_ids": self.student_ids.ids}})
        return action

    def _compute_fee_student_count(self):
        super()._compute_fee_student_count()
        for group in self:
            group.fee_student_count = len(
                group.fee_so_line_ids.filtered(
                    lambda x: x.order_id.subscription_state in ["3_progress", "4_paused"]
                ).mapped("order_id.partner_id")
            )

    def open_fee_sales(self):
        super().open_fee_sales()
        action = self.env["ir.actions.actions"]._for_xml_id("sale.action_quotations_with_onboarding")
        action.update(
            {
                "domain": [
                    (
                        "id",
                        "in",
                        self.fee_so_line_ids.filtered(
                            lambda x: x.order_id.subscription_state in ["3_progress", "4_paused"]
                        )
                        .mapped("order_id")
                        .ids,
                    )
                ],
                "context": {},
            }
        )
        return action
