##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class CrmLead(models.Model):
    _inherit = "crm.lead"

    group_id = fields.Many2one("academic.group")
    family_member_ids = fields.One2many("crm.lead.family.member", "lead_id")
    suggested_family_id = fields.Many2one(
        "res.partner",
        compute="_compute_suggested_family_data",
    )
    suggested_family_count = fields.Integer(
        compute="_compute_suggested_family_data",
    )
    suggested_family_ids = fields.Many2many(
        "res.partner",
        string="Suggested Families",
        compute="_compute_suggested_family_data",
    )
    suggested_family_note = fields.Char(
        compute="_compute_suggested_family_data",
    )
    suggested_family_message = fields.Html(
        compute="_compute_suggested_family_data",
    )

    @api.constrains("family_member_ids")
    def _check_unique_types(self):
        for rec in self:
            if len(rec.family_member_ids.filtered(lambda m: m.member_type == "family")) > 1:
                raise ValidationError(self.env._("There can only be one Family per opportunity."))
            if len(rec.family_member_ids.filtered(lambda m: m.member_type == "student")) > 1:
                raise ValidationError(self.env._("There can only be one Student per opportunity."))

    def _get_suggested_families(self):
        self.ensure_one()
        parent_vats = {
            member.vat.strip()
            for member in self.family_member_ids.filtered(lambda m: m.member_type == "parent" and m.vat)
            if member.vat and member.vat.strip()
        }
        if not parent_vats:
            return self.env["res.partner"]
        links = self.env["res.partner.link"].search(
            [
                ("partner_id.vat", "in", list(parent_vats)),
                ("student_id.partner_type", "=", "family"),
            ]
        )
        return links.mapped("student_id")

    @api.depends("family_member_ids.member_type", "family_member_ids.vat", "family_member_ids.partner_id")
    def _compute_suggested_family_data(self):
        for rec in self:
            families = rec._get_suggested_families()
            selected_family = rec.family_member_ids.filtered(lambda m: m.member_type == "family").mapped("partner_id")
            families -= selected_family
            rec.suggested_family_ids = families
            rec.suggested_family_count = len(families)
            rec.suggested_family_id = families[:1] if len(families) == 1 else False
            if not families:
                rec.suggested_family_note = False
                rec.suggested_family_message = False
            elif len(families) == 1:
                family = families[:1]
                family_url = "/web#id=%(id)s&model=res.partner&view_type=form" % {"id": family.id}
                rec.suggested_family_note = rec.env._(
                    "A family was found for the entered parent DNI: %(family)s. You can link it in the Family line.",
                    family=family.display_name,
                )
                rec.suggested_family_message = rec.env._(
                    "A family was found for the entered parent DNI: <a href='%(url)s'>%(family)s</a>.",
                    url=family_url,
                    family=family.display_name,
                )
            else:
                rec.suggested_family_note = rec.env._(
                    "Multiple families were found for the entered parent DNI values. "
                    "Please select the correct Family contact in the Family line."
                )
                rec.suggested_family_message = rec.env._(
                    "Multiple families were found for the entered parent DNI values. "
                    "Use 'Open families' to review them, then link the correct one in the Family line."
                )

    def action_open_suggested_family(self):
        self.ensure_one()
        families = self.suggested_family_ids
        if not families:
            raise UserError(self.env._("No related family was found for the entered parent DNI."))
        if len(families) == 1:
            return {
                "type": "ir.actions.act_window",
                "res_model": "res.partner",
                "res_id": families.id,
                "view_mode": "form",
                "target": "current",
            }
        return {
            "type": "ir.actions.act_window",
            "name": self.env._("Suggested Families"),
            "res_model": "res.partner",
            "view_mode": "list,form",
            "domain": [("id", "in", families.ids), ("partner_type", "=", "family")],
            "target": "current",
        }

    def _normalize_dni(self, vat):
        return "".join(char for char in (vat or "") if char.isalnum()).lower()

    def _link_relative_members_from_family(self, family):
        self.ensure_one()
        relatives = self.family_member_ids.filtered(lambda m: m.member_type == "parent" and not m.partner_id and m.vat)
        if not relatives:
            return 0
        family = family.with_context(active_test=False)
        candidate_partners = family.student_link_ids.mapped("partner_id")
        if not candidate_partners:
            students = family.student_ids.filtered(lambda s: s.partner_type == "student")
            candidate_partners = students.mapped("student_link_ids.partner_id")
        partners_by_dni = {}
        for partner in candidate_partners:
            partner_dni = self._normalize_dni(partner.vat)
            if partner_dni and partner_dni not in partners_by_dni:
                partners_by_dni[partner_dni] = partner
        linked_count = 0
        for relative in relatives:
            partner = partners_by_dni.get(self._normalize_dni(relative.vat))
            if not partner:
                continue
            relative.write(
                {
                    "partner_id": partner.id,
                    "name": partner.name,
                    "email": partner.email,
                }
            )
            linked_count += 1
        return linked_count

    def action_link_suggested_family(self):
        self.ensure_one()
        if self.suggested_family_count != 1:
            return self.action_open_suggested_family()
        family = self.suggested_family_id
        family_member = self.family_member_ids.filtered(lambda m: m.member_type == "family")[:1]
        if not family_member:
            self.write(
                {
                    "family_member_ids": [
                        (
                            0,
                            0,
                            {
                                "member_type": "family",
                                "name": family.name,
                                "partner_id": family.id,
                            },
                        )
                    ]
                }
            )
            family_member = self.family_member_ids.filtered(lambda m: m.member_type == "family")[:1]
        else:
            family_member.write({"partner_id": family.id, "name": family.name})
        self._link_relative_members_from_family(family)
        return {"type": "ir.actions.client", "tag": "soft_reload"}

    def _validate_family_group_before_create(self):
        self.ensure_one()
        family_member = self.family_member_ids.filtered(lambda m: m.member_type == "family")[:1]
        student_member = self.family_member_ids.filtered(lambda m: m.member_type == "student")[:1]
        parent_members = self.family_member_ids.filtered(lambda m: m.member_type == "parent")

        missing_data = []
        if not family_member:
            missing_data.append(self.env._("Add one Family line."))
        if not student_member:
            missing_data.append(self.env._("Add one Student line."))
        if not parent_members:
            missing_data.append(self.env._("Add at least one Relative line (father/mother/tutor)."))

        parents_without_relationship = parent_members.filtered(lambda m: not m.relationship_id)
        if parents_without_relationship:
            missing_data.append(self.env._("Complete the relationship on all Relative lines."))

        if missing_data:
            raise UserError(
                self.env._(
                    "You cannot create the Academic Structure yet. Please complete Family Group data:\n- %(details)s",
                    details="\n- ".join(missing_data),
                )
            )

    def _assign_suggested_family(self):
        self.ensure_one()
        family_member = self.family_member_ids.filtered(lambda m: m.member_type == "family")[:1]
        if not family_member or family_member.partner_id or not self.suggested_family_id:
            return
        family_member.partner_id = self.suggested_family_id
        family_member.name = self.suggested_family_id.name

    def action_create_family(self):
        self.ensure_one()
        self._validate_family_group_before_create()
        self._assign_suggested_family()
        company_id = self.company_id.id if self.company_id else False

        family_member = self.family_member_ids.filtered(lambda m: m.member_type == "family")[:1]
        student_member = self.family_member_ids.filtered(lambda m: m.member_type == "student")[:1]
        other_members = self.family_member_ids.filtered(lambda m: m.member_type == "parent")

        parent_vals_list = [
            {
                "name": member.name,
                "vat": member.vat,
                "email": member.email,
                "relationship_id": member.relationship_id.id,
                "role_ids": member.role_ids.ids,
                "partner_id": member.partner_id or None,
            }
            for member in other_members
        ]

        result = self.env["res.partner"]._create_academic_structure(
            family_vals={"name": family_member.name},
            student_vals={
                "name": student_member.name or self.partner_name,
                "vat": student_member.vat,
                "email": student_member.email or self.email_from,
            },
            parent_vals_list=parent_vals_list,
            company_id=company_id,
            family=family_member.partner_id or None,
            student=(student_member.partner_id or self.partner_id) or None,
        )

        family = result["family"]
        student = result["student"]
        family_member.partner_id = family
        student_member.partner_id = student
        if not self.partner_id:
            self.partner_id = student
        for member, partner in zip(other_members, result["parents"]):
            member.partner_id = partner

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
