##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import api, fields, models


class ResPartner(models.Model):
    _name = "res.partner.link"
    _description = "res.partner.link"
    _check_company_auto = True
    _order = "sequence"
    _check_company_domain = models.check_company_domain_parent_of

    student_id = fields.Many2one("res.partner", "Student or Family", required=True, ondelete="cascade")
    company_id = fields.Many2one(related="student_id.company_id")
    # student_id = fields.Many2one('res.partner', 'Student', ondelete='cascade')
    # family_id = fields.Many2one('res.partner', 'Family', ondelete='cascade')
    relationship_id = fields.Many2one("res.partner.relationship", required=True, ondelete="restrict")
    role_ids = fields.Many2many("res.partner.role", string="Roles")
    partner_id = fields.Many2one("res.partner", required=True, ondelete="restrict", check_company=True)
    note = fields.Text(string="Notas")
    sequence = fields.Integer(default=10)

    # @api.constrains('student_id', 'family_id')
    # def _check_student_or_family(self):
    #     recs = self.filtered(lambda x: not x.student_id and not x.family_id)
    #     if recs:
    #         raise UserError('Los contactos y roles deben estar vinculados a una famila o a un estudiante')

    _link_unique = models.Constraint(
        "unique(student_id, partner_id)",
        "El contacto debe ser agregado por unica vez en cada familia o estudiante",
    )

    @api.model_create_multi
    def create(self, vals_list):
        """Skip links whose pair is already there, instead of hitting _link_unique.

        The same student link can reach one flush twice: the form sends back the
        one the onchange gave it, and _compute_student_links adds its own because
        it cannot see the pending one. Both inserts land in the same transaction
        and the whole save is rolled back.
        """
        pairs = [(vals.get("student_id"), vals.get("partner_id")) for vals in vals_list]
        wanted = {pair for pair in pairs if all(pair)}
        already = self.browse()
        if wanted:
            already = self.sudo().search(
                [
                    ("student_id", "in", [pair[0] for pair in wanted]),
                    ("partner_id", "in", [pair[1] for pair in wanted]),
                ]
            )
            already = already.filtered(lambda link: (link.student_id.id, link.partner_id.id) in wanted)
        seen = {(link.student_id.id, link.partner_id.id) for link in already}
        to_create = []
        for vals, pair in zip(vals_list, pairs):
            if all(pair):
                if pair in seen:
                    continue
                seen.add(pair)
            to_create.append(vals)
        return super().create(to_create) | self.browse(already.ids)
