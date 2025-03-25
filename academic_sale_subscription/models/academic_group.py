##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models


class AcademicGroup(models.Model):
    _inherit = "academic.group"

    def open_order_wizard(self):
        action = self.env.ref('academic_sale_subscription.action_view_academic_order_wizard').read()[0]
        action.update({
            'context': {'default_student_ids': self.academic_group_link_ids.mapped("student_id.id")}
        })
        return action
