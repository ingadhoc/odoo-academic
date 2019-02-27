##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo.api import Environment, SUPERUSER_ID

from odoo.addons.mail.models.mail_activity import MailActivity
from odoo import fields

try:
    from odoo.addons.report_aeroo.translate import extend_trans_generate as trans_generate
except:
    from odoo.tools.translate import trans_generate


def post_load_hook():

    def new_trans_generate(lang, modules, cr):
        translations = trans_generate(lang, modules, cr)
        # if ('academic', 'model', 'survey.page,title', 'academic.survey_page_10', 'Preguntas', 'Preguntas', ())
        # for item in translations:
        #     if item[]
        # print(" ------------------- post_init_hook")
        # env = Environment(cr, SUPERUSER_ID, {})
        # model = 'survey.page'
        # survey_fields = env['ir.model.fields'].search([
        #     ('name', 'in', ['description', 'title']),
        #     ('model', '=', model)])
        # survey_fields._write({'translate': False})
        # translations = env['ir.translation'].search([
        #     ('name', 'in', ['survey.page,description', 'survey.page,title']),
        #     ('module', '=', 'academic'),
        # ])
        # translations.unlink()
