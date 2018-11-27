##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import api, models, fields


class AcademicPeriod(models.Model):

    _name = 'academic.period'
    _description = 'period'
    _order = 'year desc'

    name = fields.Char(
        required=True,
    )
    year = fields.Integer(
        required=True,
    )

    @api.multi
    def name_get(self):
        res = []
        for rec in self:
            name = rec.name
            name += ' - ' + str(rec.year)
            res.append((rec.id, name))
        return res

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('name', operator, name), ('year', operator, name)]
            result = self.search(args + domain, limit=limit).name_get()
        else:
            result = self.search(args, limit=limit).name_get()
        return result
