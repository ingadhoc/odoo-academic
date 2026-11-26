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

    def _wizard(self, lead):
        return (
            self.env["crm.lead2opportunity.partner"]
            .with_context(active_model="crm.lead", active_id=lead.id, active_ids=lead.ids)
            .create({})
        )

    def test_academic_lead_defaults_to_no_customer(self):
        self.assertEqual(self._wizard(self.academic_lead).action, "nothing")

    def test_plain_lead_defaults_to_no_customer(self):
        """A lead with no academic data yet gets the same default: the family is loaded later."""
        lead = self.env["crm.lead"].create(
            {
                "name": "Test Conversion Plain Lead",
                "type": "lead",
                "contact_name": "Test Conversion Plain Contact",
                "email_from": "test.conversion.plain@example.com",
            }
        )
        self.assertEqual(self._wizard(lead).action, "nothing")

    def test_matching_partner_defaults_to_no_customer(self):
        """The default wins over 'exist': a matching partner would land on the opportunity too."""
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
        self.assertEqual(self._wizard(lead).action, "nothing")

    def test_mass_wizard_keeps_standard_action(self):
        """The mass wizard computes its own action and must keep Odoo's default."""
        wizard = (
            self.env["crm.lead2opportunity.partner.mass"]
            .with_context(
                active_model="crm.lead",
                active_ids=self.academic_lead.ids,
            )
            .create({})
        )
        self.assertEqual(wizard.action, "each_exist_or_create")

    def test_conversion_creates_no_contact(self):
        wizard = self._wizard(self.academic_lead)
        partners_before = self.env["res.partner"].search_count([])
        wizard.action_apply()
        self.assertEqual(self.academic_lead.type, "opportunity")
        self.assertFalse(self.academic_lead.partner_id)
        self.assertEqual(self.env["res.partner"].search_count([]), partners_before)
