##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import fields, models


class CrmLead(models.Model):
    _inherit = "crm.lead"

    group_id = fields.Many2one('academic.group')

    def _create_customer(self):
        res = super()._create_customer()
        if self.env.context.get('from_lead'):
            res.partner_type = 'student'
        return res
