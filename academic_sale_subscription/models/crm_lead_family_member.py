from odoo import fields, models
from odoo.exceptions import UserError


class CrmLeadFamilyMember(models.Model):
    _name = "crm.lead.family.member"
    _description = "CRM Lead Family Member"

    lead_id = fields.Many2one("crm.lead", ondelete="cascade", required=True)
    partner_id = fields.Many2one("res.partner")
    member_type = fields.Selection(
        [
            ("family", "Family"),
            ("student", "Student"),
            ("parent", "Relative"),
        ],
        required=True,
        default="parent",
    )
    name = fields.Char(required=True)
    relationship_id = fields.Many2one("res.partner.relationship")
    vat = fields.Char(string="DNI")
    email = fields.Char()
    role_ids = fields.Many2many("res.partner.role")

    def unlink(self):
        if self.filtered("partner_id"):
            raise UserError(self.env._("You cannot delete a line that is already linked to a contact."))
        return super().unlink()

    def action_open_partner(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "res.partner",
            "res_id": self.partner_id.id,
            "view_mode": "form",
            "target": "current",
        }
