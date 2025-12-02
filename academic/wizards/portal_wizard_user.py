from odoo import models


class PortalWizardUser(models.TransientModel):
    _inherit = "portal.wizard.user"

    def _get_group_by_partner_type(self):
        group_mapping = {
            "gral_administrator": "academic.group_portal_gral_administrator",
            "administrator": "academic.group_portal_administrator",
            "teacher": "academic.group_portal_teacher",
            "parent": "academic.group_portal_parent",
            "student": "academic.group_portal_student",
        }
        group_ref = group_mapping.get(self.partner_id.partner_type)
        if group_ref:
            return self.env.ref(group_ref)
        return None

    def action_grant_access(self):
        result = super().action_grant_access()
        partner_group = self._get_group_by_partner_type()
        portal_backend_group = self.env.ref("portal_backend.group_portal_backend", raise_if_not_found=False)
        groups_to_add = []
        if partner_group:
            groups_to_add.append((4, partner_group.id))
        if portal_backend_group:
            groups_to_add.append((4, portal_backend_group.id))
        if groups_to_add:
            self.user_id.write({"group_ids": groups_to_add})
        return result
