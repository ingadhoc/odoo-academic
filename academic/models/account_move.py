from odoo import _, models, fields, api
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

    # Este campo solo lo uso para calcular el dominio del student_id ya que implica una búsqueda por el rol de pago.
    student_ids = fields.Many2many('res.partner', compute="_compute_student_ids")
    student_id = fields.Many2one('res.partner', string='Alumno', domain="[('id', 'in', student_ids), ('partner_type', '=', 'student')]")

    @api.constrains('student_id')
    def _check_student(self):
        invoices_wo_student = self.filtered(lambda x: x.move_type in ["out_invoice", "out_refund"] and not x.student_id)
        if invoices_wo_student:
            msg = _("Las facturas de clientes y notas de debito debe tener asociado siempre un alumno.")
            if len(invoices_wo_student) > 1:
                msg += ".\n" + _("Los siguientes documentos no cumplen esa condición:") + "\n\n - %s" % '\n - '.join(invoices_wo_student.mapped('display_name'))
            raise ValidationError(msg)

    @api.depends('partner_id')
    def _compute_student_ids(self):
        for rec in self:
            if rec.partner_id:
                student_ids = self.env['res.partner.link'].search(
                    [('partner_id', '=', rec.partner_id.id), ('role_ids', 'in', self.env.ref('academic.paying_role').id)]
                ).mapped('student_id.id')
                rec.student_ids = [(6, 0, student_ids)]
            else:
                rec.student_ids = [(5, 0, 0)]
