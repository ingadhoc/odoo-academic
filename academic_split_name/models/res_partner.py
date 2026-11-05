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

        Returns the four parts, the ones the name does not give as False: the
        name that arrives replaces the parts that were there, instead of mixing
        with them.

        The form writes the parts instead, so it never goes through here: that
        is what keeps the name and its parts from recomputing each other.
        """
        if partner_type not in ("student", "parent", "family"):
            return {}
        parts = dict.fromkeys(NAME_PARTS, False)
        if partner_type == "family":
            parts["lastname"] = name or False
            return parts
        words = (name or "").strip().split()
        if words:
            parts["firstname"] = words[0]
            parts["lastname"] = " ".join(words[1:]) if len(words) > 1 else False
        return parts

    def _split_name_into_parts(self):
        """Fill the parts from the name already stored on the record.

        It reads `partner_type` from the record and not from the values: on an
        import from a list, or on a contact created from a lead, the type
        arrives as a default in the context and never reaches them.
        """
        for rec in self:
            parts = rec._parts_from_name(rec.name, rec.partner_type)
            if parts:
                super(ResPartner, rec).write(parts)

    @api.model_create_multi
    def create(self, vals_list):
        to_split = [("name" in vals and not any(part in vals for part in NAME_PARTS)) for vals in vals_list]
        records = super().create(vals_list)
        for record, split in zip(records, to_split):
            if split:
                record._split_name_into_parts()
        return records

    def write(self, vals):
        if "name" not in vals or any(part in vals for part in NAME_PARTS):
            return super().write(vals)

        result = super().write(vals)
        self._split_name_into_parts()
        return result
