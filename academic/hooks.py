##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################

def post_init_hook(env):
    ''' Esto lo dejamos solo para los templates de órdenes de venta y no en facturas debido a que
    en facturas hay un wizard custom y no heredamos el método de _message_get_default_recipients,
    si se mandan facturas desde el chatter no se van a sugerir, aunque en facturas primero se confirma
    (al confirmar se agregan los responsables de pago como seguidores) y luego se enviaría la factura,
    así que siempre van a enviarse a los seguidores de la factura.
    '''
    templates = env['mail.template'].search([('model_id.model', '=', 'sale.order')])
    templates.use_default_to = True
