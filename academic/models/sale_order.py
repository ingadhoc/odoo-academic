# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api


class SaleOrder(models.Model):
    _inherit = "sale.order"
    # Don't do port-forward

    website_id = fields.Many2one('website', string='Website', readonly=True,
                                 help='Website through which this order was placed.')

    @api.multi
    def get_base_url(self):
        """When using multi-website, we want the user to be redirected to the
        most appropriate website if possible."""
        res = super(SaleOrder, self).get_base_url()
        return self.website_id and self.website_id._get_http_domain() or res
