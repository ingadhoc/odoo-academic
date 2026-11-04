##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import api, fields, models

NAME_PARTS = ("firstname", "middlename", "lastname", "second_lastname")


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

    @api.depends("firstname", "lastname", "second_lastname", "middlename")
    def _compute_name(self):
        for rec in self.filtered(lambda x: x.partner_type in ("student", "family", "parent")):
            rec.name = " ".join(filter(None, [rec.firstname, rec.middlename, rec.lastname, rec.second_lastname]))

    def _parts_from_name(self, name, partner_type):
        """Split an academic name that arrives whole, on an import or over RPC.

        The form writes the parts instead, so it never goes through here: that
        is what keeps the name and its parts from recomputing each other.
        """
        if partner_type == "family":
            return {"lastname": name or False}
        if partner_type not in ("student", "parent"):
            return {}
        words = (name or "").strip().split()
        return {
            "firstname": words[0] if words else False,
            "lastname": " ".join(words[1:]) if len(words) > 1 else False,
        }

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if "name" in vals and not any(part in vals for part in NAME_PARTS):
                vals.update(self._parts_from_name(vals["name"], vals.get("partner_type")))
        return super().create(vals_list)

    def write(self, vals):
        if "name" not in vals or any(part in vals for part in NAME_PARTS):
            return super().write(vals)

        result = super().write(vals)
        for rec in self:
            parts = rec._parts_from_name(rec.name, rec.partner_type)
            if parts:
                super(ResPartner, rec).write(parts)
        return result
