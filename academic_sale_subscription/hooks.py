##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################


def post_init_hook(env):
    """Esto lo dejamos solo para los templates de órdenes de venta y no en facturas debido a que
    en facturas hay un wizard custom y no heredamos el método de _message_get_default_recipients,
    si se mandan facturas desde el chatter no se van a sugerir, aunque en facturas primero se confirma
    (al confirmar se agregan los responsables de pago como seguidores) y luego se enviaría la factura,
    así que siempre van a enviarse a los seguidores de la factura.
    """
    templates = env["mail.template"].search([("model_id.model", "=", "sale.order")])
    templates.use_default_to = True

    base_module = env.ref("base.module_base")
    if base_module.demo:  # If it has demo data...
        _remove_native_demo_data(env)


def _remove_native_demo_data(env):
    native_demo_modules = ["crm", "sale", "sale_subscription", "sale_subscription_ux"]

    demo_data_ids = env["ir.model.data"].search(
        [("module", "in", native_demo_modules), ("model", "in", ["crm.lead", "crm.team", "crm.stage", "sale.order"])]
    )

    if not demo_data_ids:
        return

    for data_id in demo_data_ids:
        record = env[data_id.model].browse(data_id.res_id).exists()
        if record:
            if data_id.model == "sale.order":
                if record.subscription_id:
                    record.subscription_id.set_close()
                if record.state not in ["draft", "cancel"]:
                    record._action_cancel()
                record.unlink()
            else:
                record.unlink()
