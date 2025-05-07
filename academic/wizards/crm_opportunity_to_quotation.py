from odoo import api, fields, models, _
from odoo.exceptions import UserError


class Opportunity2Quotation(models.TransientModel):
    _inherit = 'crm.quotation.partner'

    def action_apply(self):
        if self.action == 'create':
            return super(Opportunity2Quotation, self.with_context(from_lead=True)).action_apply()
        return super().action_apply()
