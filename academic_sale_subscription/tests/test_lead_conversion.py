##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import Command
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestLeadConversion(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.academic_lead = cls.env["crm.lead"].create(
            {
                "name": "Test Conversion Academic Lead",
                "type": "lead",
                "contact_name": "Test Conversion Contact",
                "email_from": "test.conversion.academic@example.com",
                "family_member_ids": [
                    Command.create({"member_type": "family", "name": "Test Conversion Family"}),
                    Command.create({"member_type": "student", "name": "Test Conversion Student"}),
                ],
            }
        )

    def test_conversion_creates_no_contact(self):
        partners_before = self.env["res.partner"].search_count([])
        self.academic_lead.action_convert_to_opportunity()
        self.assertEqual(self.academic_lead.type, "opportunity")
        self.assertFalse(self.academic_lead.partner_id)
        self.assertEqual(self.env["res.partner"].search_count([]), partners_before)

    def test_matching_partner_is_not_linked(self):
        """Standard links the partner it finds by email; the family group decides the contact instead."""
        partner = self.env["res.partner"].create(
            {"name": "Test Conversion Known Partner", "email": "test.conversion.known@example.com"}
        )
        lead = self.env["crm.lead"].create(
            {
                "name": "Test Conversion Known Lead",
                "type": "lead",
                "email_from": partner.email,
            }
        )
        self.assertEqual(lead._find_matching_partner(), partner)
        lead.action_convert_to_opportunity()
        self.assertEqual(lead.type, "opportunity")
        self.assertFalse(lead.partner_id)

    def test_conversion_keeps_the_partner_already_set(self):
        partner = self.env["res.partner"].create({"name": "Test Conversion Set Partner"})
        lead = self.env["crm.lead"].create(
            {
                "name": "Test Conversion Set Lead",
                "type": "lead",
                "partner_id": partner.id,
            }
        )
        lead.action_convert_to_opportunity()
        self.assertEqual(lead.type, "opportunity")
        self.assertEqual(lead.partner_id, partner)

    def test_mass_wizard_keeps_standard_behaviour(self):
        """The mass wizard already converts without a customer unless the user asks for one."""
        wizard = (
            self.env["crm.lead2opportunity.partner.mass"]
            .with_context(active_model="crm.lead", active_ids=self.academic_lead.ids)
            .create({})
        )
        self.assertFalse(wizard.link_to_matching_customer)
        partners_before = self.env["res.partner"].search_count([])
        wizard.action_apply()
        self.assertEqual(self.academic_lead.type, "opportunity")
        self.assertFalse(self.academic_lead.partner_id)
        self.assertEqual(self.env["res.partner"].search_count([]), partners_before)
