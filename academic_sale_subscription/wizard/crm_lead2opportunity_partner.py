##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import api, fields, models


class CrmLead2opportunityPartner(models.TransientModel):
    _inherit = "crm.lead2opportunity.partner"

    action = fields.Selection(
        selection_add=[("nothing", "Do not link to a customer")],
        ondelete={"nothing": lambda recs: recs.write({"action": "create"})},
    )

    @api.depends("lead_id")
    def _compute_action(self):
        super()._compute_action()
        # the academic flow builds its contacts from the family group, not from the conversion
        self.action = "nothing"
