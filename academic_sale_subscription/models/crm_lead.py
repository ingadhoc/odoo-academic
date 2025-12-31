##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import fields, models


class CrmLead(models.Model):
    _inherit = "crm.lead"

    group_id = fields.Many2one("academic.group")

    def _create_customer(self, with_parent=None):
        if self.group_id:
            return super(CrmLead, self.with_context(default_partner_type="student"))._create_customer(
                with_parent=with_parent
            )
        return super()._create_customer(with_parent=with_parent)

    def _message_post_after_hook(self, message, msg_vals):
        """Override to prevent automatic partner assignment when posting messages through chatter.
        In the standard CRM behavior, when you send a message from the chatter to a recipient
        whose email matches the lead's email_from, it automatically assigns that partner to the lead.
        This override disables that automatic assignment.
        """
        return super(models.Model, self)._message_post_after_hook(message, msg_vals)
