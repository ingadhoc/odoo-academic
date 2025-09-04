from odoo import api, fields, models
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    # Este campo solo lo uso para calcular el dominio del student_id ya que implica una búsqueda por el rol de pago.
    student_ids = fields.Many2many("res.partner", string="Students List", compute="_compute_student_ids")
    student_id = fields.Many2one(
        "res.partner",
        domain="[('id', 'in', student_ids), ('partner_type', '=', 'student')]",
        index=True,
        context={"default_partner_type": "student"},
    )
    family_id = fields.Many2one("res.partner", related="student_id.parent_id", store=True, string="Family")
    require_student_on_invoices = fields.Boolean(related="company_id.require_student_on_invoices")
    is_academic_sale = fields.Boolean(compute="_compute_is_academic_sale")

    @api.constrains("student_id", "move_type")
    def _check_student(self):
        # Está saltando warning en runbot por esta constrains ya que hay facturas sin estudiante, por lo tanto
        # desactivamos el chequeo cuando se hace la instalación
        if self.env.context.get("install_mode"):
            return True
        if self.filtered(lambda x: x.require_student_on_invoices and x.is_academic_sale):
            invoices_wo_student = self.filtered(
                lambda x: x.move_type in ["out_invoice", "out_refund"] and not x.student_id
            )
            if invoices_wo_student:
                msg = self.env._("Las facturas de clientes y notas de debito debe tener asociado siempre un alumno.")
                if len(invoices_wo_student) > 1:
                    msg += (
                        ".\n"
                        + self.env._("Los siguientes documentos no cumplen esa condición:")
                        + "\n\n - %s" % "\n - ".join(invoices_wo_student.mapped("display_name"))
                    )
                raise ValidationError(msg)

    @api.depends("partner_id")
    def _compute_student_ids(self):
        for rec in self:
            if rec.partner_id:
                student_ids = (
                    self.env["res.partner.link"]
                    .search(
                        [
                            ("partner_id", "=", rec.partner_id.id),
                            ("role_ids", "in", self.env.ref("academic.paying_role").id),
                        ]
                    )
                    .mapped("student_id.id")
                )
                rec.student_ids = [(6, 0, student_ids)]
            else:
                rec.student_ids = [(5, 0, 0)]

    def _post(self, soft=True):
        for rec in self:
            partners_invoice = rec.student_id.payment_responsible_ids if rec.student_id else self.env["res.partner"]
            rec.message_subscribe(
                [
                    payment_responsible.id
                    for payment_responsible in rec.partner_id | partners_invoice
                    if payment_responsible not in rec.sudo().message_partner_ids
                ]
            )
        return super()._post(soft=soft)

    def _compute_is_academic_sale(self):
        for rec in self:
            rec.is_academic_sale = (
                self.env["sale.order"].search([("invoice_ids", "in", [rec.id])], limit=1).is_academic_sale
            )

    def _get_suggested_responsible(self):
        self.ensure_one()
        paying_role = self.env.ref("academic.paying_role")
        responsible_ids = set()
        suggested = False

        # tiene estudiante definida en factura
        if self.student_id:
            student_links = self.student_id.student_link_ids.filtered(lambda x: paying_role in x.role_ids)
            if student_links:
                suggested = student_links.sorted("sequence")[:1].partner_id
                responsible_ids.update(student_links.mapped("partner_id").ids)

        # el partner_id es estudiante
        elif self.partner_id.partner_type == "student":
            student_links = self.partner_id.student_link_ids.filtered(lambda x: paying_role in x.role_ids)
            if student_links:
                suggested = student_links.sorted("sequence")[:1].partner_id
                responsible_ids.update(student_links.mapped("partner_id").ids)

        # el partner_id es familia
        elif self.partner_id.partner_type == "family":
            if self.partner_id.links_by_student:
                student = self.partner_id.child_ids.filtered(lambda x: x.partner_type == "student")[:1]
                if student:
                    student_links = student.student_link_ids.filtered(lambda x: paying_role in x.role_ids)
                    if student_links:
                        suggested = student_links.sorted("sequence")[:1].partner_id
                        responsible_ids.update(student_links.mapped("partner_id").ids)
            else:
                student_links = self.partner_id.student_link_ids.filtered(lambda x: paying_role in x.role_ids)
                if student_links:
                    suggested = student_links.sorted("sequence")[:1].partner_id
                    responsible_ids.update(student_links.mapped("partner_id").ids)

        # el partner_id es pariente
        elif self.partner_id.partner_type == "parent":
            family = self.partner_id.partner_link_ids.filtered(lambda x: x.student_id.partner_type == "family").mapped(
                "student_id"
            )[:1]
            if family:
                family = family[0]
                if family.links_by_student:
                    student = family.child_ids.filtered(lambda x: x.partner_type == "student")[:1]
                    if student:
                        student_links = student.student_link_ids.filtered(lambda x: paying_role in x.role_ids)
                        if student_links:
                            suggested = student_links.sorted("sequence")[:1].partner_id
                            responsible_ids.update(student_links.mapped("partner_id").ids)
                else:
                    student_links = family.student_link_ids.filtered(lambda x: paying_role in x.role_ids)
                    if student_links:
                        suggested = student_links.sorted("sequence")[:1].partner_id
                        responsible_ids.update(student_links.mapped("partner_id").ids)
        return suggested, list(responsible_ids)
