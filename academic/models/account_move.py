from odoo import _, models, fields, api
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

    # Este campo solo lo uso para calcular el dominio del student_id ya que implica una búsqueda por el rol de pago.
    student_ids = fields.Many2many('res.partner', string="Students List", compute="_compute_student_ids")
    student_id = fields.Many2one('res.partner', domain="[('id', 'in', student_ids), ('partner_type', '=', 'student')]", index=True)

    @api.constrains('student_id', 'move_type')
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

    def _message_get_default_recipients(self):
        """ Por defecto las plantillas mandan a partner_id pero para nosotros el partners es el estudiante.
        Cambiamos plantillas para que usen el campo "use_default_to" y luego cae en este método de python donde
        podemos ir mejorando a medida que nos pidan y modificar la logica de recipients.
        Por ahora lo mandamos solo al partner de facturación si está definido
        En facturas puntulamente, odoo suscribe al parter id en el metodo post.
        Dejamos ese feateure y decidimos agregar otros responsables de pago en el envio de email
        """
        default_recipients = super()._message_get_default_recipients()
        for record in self:
            # calculo analogo sale.order.partner_invoice_ids (Eventulamente podemos hacer un helper en student link)
            partners_invoice = record.student_id.student_link_ids.filtered(
                lambda x: self.env.ref('academic.paying_role') in x.role_ids).mapped('partner_id') if record.student_id else False
            payment_responsible = record.partner_id | partners_invoice
            if payment_responsible:
                default_recipients[record.id] = {
                    'email_cc': False,
                    'email_to': False,
                    'partner_ids': payment_responsible.ids,
                }
        return default_recipients
