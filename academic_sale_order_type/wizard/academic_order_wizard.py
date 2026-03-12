##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################

from odoo import api, fields, models


class OrderWizard(models.TransientModel):
    _inherit = "academic.order.wizard"

    type_id = fields.Many2one("sale.order.type", string="Order Type", check_company=True)
    company_id = fields.Many2one("res.company", default=lambda self: self.env.company)
    order_type_required = fields.Boolean(related="company_id.sale_order_type_required")
    pricelist_id = fields.Many2one("product.pricelist", compute="_compute_pricelist_id", store=True, readonly=False)
    payment_term_id = fields.Many2one(
        "account.payment.term", compute="_compute_payment_term_id", store=True, readonly=False
    )

    @api.depends("type_id")
    def _compute_pricelist_id(self):
        for wizard in self.filtered("type_id.pricelist_id"):
            wizard.pricelist_id = wizard.type_id.pricelist_id

    @api.depends("type_id")
    def _compute_payment_term_id(self):
        for wizard in self.filtered("type_id.payment_term_id"):
            wizard.payment_term_id = wizard.type_id.payment_term_id

    def _create_mass_subscription(self, vals=None):
        vals = vals or {}
        if self.type_id:
            vals["type_id"] = self.type_id.id
        return super()._create_mass_subscription(vals=vals)
