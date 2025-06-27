##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, _



class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    def _notify_by_email_render_layout(self, message, recipients_group, msg_vals=False, render_values=None):
        lang = self.env.context.get("lang")
        model = msg_vals.get('model') if msg_vals and msg_vals.get('model') else message.model
        model_description = render_values.get('model_description') if render_values else None
        if not model_description:
            model_description = self.with_context(lang=lang)._get_model_description(model)

        view_title = _('View %s', model_description)
        button_access = recipients_group.get('button_access', {})
        if (
            button_access.get('url')
            and self.env.context.get('active_model') == 'account.move'
            and button_access.get('title') == view_title
        ):
            url = self[0].get_base_url() + '/my/invoices?filterby=invoices'
            button_access['url'] = url
            recipients_group['button_access'] = button_access

        return super()._notify_by_email_render_layout(message, recipients_group, msg_vals, render_values)
