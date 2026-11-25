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

    def test_plain_lead_keeps_standard_action(self):
        lead = self.env["crm.lead"].create(
            {
                "name": "Test Conversion Plain Lead",
                "type": "lead",
                "contact_name": "Test Conversion Plain Contact",
                "email_from": "test.conversion.plain@example.com",
            }
        )
        self.assertEqual(self._wizard(lead).action, "create")

    def test_conversion_creates_no_contact(self):
        wizard = self._wizard(self.academic_lead)
        partners_before = self.env["res.partner"].search_count([])
        wizard.action_apply()
        self.assertEqual(self.academic_lead.type, "opportunity")
        self.assertFalse(self.academic_lead.partner_id)
        self.assertEqual(self.env["res.partner"].search_count([]), partners_before)
