##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import api, fields, models


class CrmLead(models.Model):
    _inherit = "crm.lead"

    group_id = fields.Many2one('academic.group')
