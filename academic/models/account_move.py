from odoo import _, models, fields, api
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    student_id = fields.Many2one('res.partner', string='Alumno', domain="[('parent_id', '=', partner_id), ('partner_type', '=', 'student')]")

    @api.constrains('student_id')
    def _check_student(self):
        invoices_wo_student = self.filtered(lambda x: x.type in ["out_invoice", "out_refund"] and not x.student_id)
        if invoices_wo_student:
            msg = _("Las facturas de clientes y notas de debito debe tener asociado siempre un alumno")
            if len(invoices_wo_student) > 1:
                msg += ".\n" + _("Los siguientes documentos no cumplen esa condición:") + "\n\n - %s" % '\n - '.join(invoices_wo_student.mapped('display_name'))
            raise ValidationError(msg)
