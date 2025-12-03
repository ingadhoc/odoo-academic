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
