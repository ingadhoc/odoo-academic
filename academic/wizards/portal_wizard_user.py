from odoo import models, _
from odoo.tools import email_normalize
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
        if any([(lis.find(_("Some contacts don't have a valid email: ")) + 1) for lis in res]):
            if len(res) == 2:
                res = []
            else:
                res.remove(res[0])
        return res

    def _create_user(self):
        """ we overwrite this method because its not inheritable
        """
        vals = {
            'partner_id': self.partner_id.id,
            'company_id': self.env.company.id,
            'company_ids': [(6, 0, self.env.company.ids)],
            'groups_id': [(6, 0, [])],
        }
        if self.partner_id.email:
            vals['login'] = email_normalize(self.partner_id.email)
            vals['email'] = email_normalize(self.partner_id.email)
        else:
            vals['login'] = self._clean_and_make_unique(self.partner_id.name)
        return self.env['res.users'].with_context(no_reset_password=True).create(vals)

    def _get_group_by_partner_type(self):
        group_mapping = {
            'gral_administrator': 'academic.group_portal_gral_administrator',
            'administrator': 'academic.group_portal_administrator',
            'teacher': 'academic.group_portal_teacher',
            'parent': 'academic.group_portal_parent',
            'student': 'academic.group_portal_student',
        }
        group_ref = group_mapping.get(self.partner_id.partner_type)
        if group_ref:
            return self.env.ref(group_ref)
        return None

    def action_grant_access(self):
        result = super().action_grant_access()
        partner_group = self._get_group_by_partner_type()
        portal_backend_group = self.env.ref('portal_backend.group_portal_backend')
        if partner_group and portal_backend_group:
            self.user_id.write({'groups_id': [(4, partner_group.id), (4, portal_backend_group.id)]})
        return result
