##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    name = fields.Char(
        compute="_compute_name",
        store=True,
        readonly=False,
    )
    firstname = fields.Char("Primer Nombre", compute="_compute_firstname", store=True, readonly=False)
    middlename = fields.Char("Segundo Nombre")
    lastname = fields.Char("Primer Apellido", compute="_compute_lastname", store=True, readonly=False)
    second_lastname = fields.Char("Segundo Apellido")

    @api.model
    def _split_firstname_lastname(self, full_name):
        parts = (full_name or "").strip().split()

        if not parts:
            return False, False

        if len(parts) == 1:
            return parts[0], False

        if len(parts) == 2:
            return parts[0], parts[1]

        if len(parts) == 3:
            return " ".join(parts[:2]), parts[2]

        if len(parts) == 4:
            return " ".join(parts[:2]), " ".join(parts[2:])

        return " ".join(parts[:2]), " ".join(parts[2:])

    @api.depends("firstname", "lastname", "second_lastname", "middlename")
    def _compute_name(self):
        for rec in self.filtered(lambda x: x.partner_type in ("student", "family", "parent")):
            rec = rec.with_context(skip_name_split_compute=True)
            name_parts = filter(None, [rec.firstname, rec.middlename, rec.lastname, rec.second_lastname])
            rec.name = " ".join(name_parts)

    @api.depends("name")
    def _compute_firstname(self):
        if self.env.context.get("skip_name_split_compute"):
            return
        for rec in self.filtered(lambda x: x.partner_type in ("student", "parent")):
            rec.firstname, _lastname = self._split_firstname_lastname(rec.name)

    @api.depends("name")
    def _compute_lastname(self):
        if self.env.context.get("skip_name_split_compute"):
            return
        for rec in self.filtered(lambda x: x.partner_type == "family"):
            rec.lastname = rec.name or False
        for rec in self.filtered(lambda x: x.partner_type in ("student", "parent")):
            _firstname, rec.lastname = self._split_firstname_lastname(rec.name)
