##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class CrmLead(models.Model):
    _inherit = "crm.lead"

    group_id = fields.Many2one("academic.group")
    family_member_ids = fields.One2many("crm.lead.family.member", "lead_id")

    @api.constrains("family_member_ids")
    def _check_unique_types(self):
        for rec in self:
            if len(rec.family_member_ids.filtered(lambda m: m.member_type == "family")) > 1:
                raise ValidationError(self.env._("There can only be one Family per opportunity."))
            if len(rec.family_member_ids.filtered(lambda m: m.member_type == "student")) > 1:
                raise ValidationError(self.env._("There can only be one Student per opportunity."))

    def action_create_family(self):
        self.ensure_one()
        company_id = self.company_id.id if self.company_id else False
        Partner = self.env["res.partner"].with_context(skip_family_check=True)

        family_member = self.family_member_ids.filtered(lambda m: m.member_type == "family")[:1]
        student_member = self.family_member_ids.filtered(lambda m: m.member_type == "student")[:1]
        other_members = self.family_member_ids.filtered(lambda m: m.member_type == "parent")

        family = None
        if family_member:
            family = family_member.partner_id or Partner.create(
                {
                    "name": family_member.name,
                    "partner_type": "family",
                    "company_id": company_id,
                }
            )
            family_member.partner_id = family

        if student_member:
            student = (
                student_member.partner_id
                or self.partner_id
                or Partner.create(
                    {
                        "name": student_member.name or self.partner_name,
                        "partner_type": "student",
                        "email": student_member.email or self.email_from,
                        "vat": student_member.vat,
                        "company_id": company_id,
                        **(({"parent_id": family.id}) if family else {}),
                    }
                )
            )
            student_member.partner_id = student
            if not self.partner_id:
                self.partner_id = student
            if family and student.parent_id != family:
                student.write({"parent_id": family.id})

        if family:
            existing_partners = family.student_link_ids.mapped("partner_id")
            for member in other_members:
                partner = member.partner_id or Partner.create(
                    {
                        "name": member.name,
                        "vat": member.vat,
                        "email": member.email,
                        "partner_type": "parent",
                        "company_id": company_id,
                    }
                )
                member.partner_id = partner
                if partner not in existing_partners:
                    family.student_link_ids = [
                        (
                            0,
                            0,
                            {
                                "partner_id": partner.id,
                                "relationship_id": member.relationship_id.id,
                                "role_ids": [(6, 0, member.role_ids.ids)],
                            },
                        )
                    ]
            return {
                "type": "ir.actions.act_window",
                "res_model": "res.partner",
                "res_id": family.id,
                "view_mode": "form",
                "target": "current",
            }

    def _create_customer(self, with_parent=None):
        if self.group_id:
            return super(
                CrmLead, self.with_context(default_partner_type="student", skip_family_check=True)
            )._create_customer(with_parent=with_parent)
        return super()._create_customer(with_parent=with_parent)

    def _message_post_after_hook(self, message, msg_vals):
        """Override to prevent automatic partner assignment when posting messages through chatter.
        In the standard CRM behavior, when you send a message from the chatter to a recipient
        whose email matches the lead's email_from, it automatically assigns that partner to the lead.
        This override disables that automatic assignment.
        """
        return super(models.Model, self)._message_post_after_hook(message, msg_vals)
