from odoo import api, fields, models
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    # Este campo solo lo uso para calcular el dominio del student_id ya que implica una búsqueda por el rol de pago.
    student_ids = fields.Many2many("res.partner", string="Students List", compute="_compute_student_ids")
    student_id = fields.Many2one(
        "res.partner", domain="[('id', 'in', student_ids), ('partner_type', '=', 'student')]", index=True
    )

    @api.constrains("student_id", "move_type")
    def _check_student(self):
        # Está saltando warning en runbot por esta constrains ya que hay facturas sin estudiante, por lo tanto
        # desactivamos el chequeo cuando se hace la instalación
        if self.env.context.get("install_mode"):
            return True
        invoices_wo_student = self.filtered(lambda x: x.move_type in ["out_invoice", "out_refund"] and not x.student_id)
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
