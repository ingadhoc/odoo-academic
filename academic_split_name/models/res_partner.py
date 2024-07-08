##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import fields, models, api


class ResPartner(models.Model):
    _inherit = "res.partner"

    name = fields.Char(
        compute="_compute_name",
        store=True,
        readonly=False,
    )
    firstname = fields.Char("Primer Nombre")
    middlename = fields.Char("Segundo Nombre")
    lastname = fields.Char("Primer Apellido")
    second_lastname = fields.Char("Segundo Apellido")

    @api.depends('firstname', 'lastname', 'second_lastname', 'middlename')
    def _compute_name(self):
        for rec in self.filtered(lambda x: x.partner_type in ('student', 'family', 'parent')):
            name_parts = filter(None, [rec.firstname, rec.middlename, rec.lastname, rec.second_lastname])
            rec.name = " ".join(name_parts)
