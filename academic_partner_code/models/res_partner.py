##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import fields, models, api


class Partner(models.Model):
    _inherit = 'res.partner'

    academic_code = fields.Char(
        'Academic Code',
        copy=False,
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('partner_type') == 'family':
                vals['academic_code'] = self.env['ir.sequence'].next_by_code('partner.academic.code')
        return super().create(vals_list)

    _sql_constraints = {
        ('academic_code_uniq', 'unique(academic_code)',
            'Academic Code must be unique!')
    }
