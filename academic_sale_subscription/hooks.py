##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo.tools import convert_file


def post_init_hook(env):
    _set_sale_templates_default_to(env)
    _load_subscription_plans(env)
    _set_grouped_invoice_notice_template(env)


def _set_sale_templates_default_to(env):
    """Esto lo dejamos solo para los templates de órdenes de venta y no en facturas debido a que
    en facturas hay un wizard custom y no heredamos el método de _message_get_default_recipients,
    si se mandan facturas desde el chatter no se van a sugerir, aunque en facturas primero se confirma
    (al confirmar se agregan los responsables de pago como seguidores) y luego se enviaría la factura,
    así que siempre van a enviarse a los seguidores de la factura.
    """
    templates = env["mail.template"].search([("model_id.model", "=", "sale.order")])
    templates.use_default_to = True


def _load_subscription_plans(env):
    """Load the default plans here and not from `data`: an updated database already has its own
    plans and would end up with duplicates.
    """
    convert_file(
        env,
        "academic_sale_subscription",
        "data/subscription_plan_data.xml",
        None,
        mode="init",
        noupdate=True,
    )


def _set_grouped_invoice_notice_template(env):
    companies = env["res.company"].search([("academic_grouped_invoice_notice_template_id", "=", False)])
    companies.academic_grouped_invoice_notice_template_id = env.ref(
        "academic_sale_subscription.email_template_grouped_invoice_notice"
    )
