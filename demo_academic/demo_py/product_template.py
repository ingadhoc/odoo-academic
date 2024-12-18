from odoo import models, api
import logging

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model
    def _init_demo_base(self):
        product_ids_in_module = self.env['ir.model.data'].search([
            ('module', '=', 'demo_academic'),
            ('model', '=', 'product.template')
        ]).mapped('res_id')

        products = self.env['product.template'].search([
            ('id', 'not in', product_ids_in_module),
            ('active', '=', True)
        ])

        for product in products:
            try:
                product.active = False
            except Exception as e:
                _logger.info(
                    "No se pudo archivar el producto %s (ID: %s). Error: %s",
                    product.display_name, product.id, str(e)
                )
