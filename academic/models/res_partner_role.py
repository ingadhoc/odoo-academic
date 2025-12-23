##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import api, fields, models
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _name = "res.partner.role"
    _description = "res.partner.role"

    name = fields.Char(required=True)
    # TODO tal vez agregar un selection de los tipos fuertes y permitir abm? por ahora vamos con los
    # external ids
    # name = fields.Char(required=True)
    color = fields.Integer(
        "Color Index",
    )
    active = fields.Boolean(default=True)

    @api.constrains("active")
    def _check_paying_role_active(self):
        paying_role = self.env.ref("academic.paying_role", raise_if_not_found=False)
        for rec in self:
            if paying_role and rec == paying_role and not rec.active:
                raise UserError(
                    self.env._("The 'Responsable de pago' role cannot be deactivated as it is required by the system.")
                )
