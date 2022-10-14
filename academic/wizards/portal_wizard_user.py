from odoo import models, _
from odoo.addons.portal.wizard.portal_wizard import extract_email
from odoo.tools import ustr
import re
import unicodedata


class PortalWizardUser(models.TransientModel):
    _inherit = 'portal.wizard.user'

    def _clean_and_make_unique(self, name):
        # when an alias name appears to already be an email, we keep the local
        # part only
        def remove_accents(input_str):
            """Suboptimal-but-better-than-nothing way to replace accented
            latin letters by an ASCII equivalent. Will obviously change the
            meaning of input_str and work only for some cases"""
            input_str = ustr(input_str)
            nkfd_form = unicodedata.normalize('NFKD', input_str)
            return u''.join(
                [c for c in nkfd_form if not unicodedata.combining(c)])

        name = remove_accents(name).lower().split('@')[0]
        name = re.sub(r'[^\w+.]+', '.', name)
        return self._find_unique(name)

    def _find_unique(self, name):
        """Find a unique alias name similar to ``name``. If ``name`` is
           already taken, make a variant by adding an integer suffix until
           an unused alias is found.
        """
        sequence = None
        while True:
            new_name = "%s%s" % (
                name, sequence) if sequence is not None else name
            if not self.env['res.users'].search([('login', '=', new_name)]):
                break
            sequence = (sequence + 1) if sequence else 2
        return new_name

    def get_error_messages(self):
        res = super().get_error_messages()
        if any([lis.find(_("Some contacts don't have a valid email: ")) for lis in res]):
            if len(res) == 2:
                res = []
            else:
                res.remove(_("Some contacts don't have a valid email: "))
        return res

    def _create_user(self):
        """ we overwrite this method because its not inheritable
        """
        company_id = self.env.context.get('company_id')
        vals = {
            'partner_id': self.partner_id.id,
            'company_id': company_id,
            'company_ids': [(6, 0, [company_id])],
            'groups_id': [(6, 0, [])],
        }
        if self.partner_id.email:
            vals['login'] = extract_email(self.partner_id.email)
            vals['email'] = extract_email(self.partner_id.email)
        else:
            vals['login'] = self._clean_and_make_unique(self.partner_id.name)
        return self.env['res.users'].with_context(no_reset_password=True).create(vals)
