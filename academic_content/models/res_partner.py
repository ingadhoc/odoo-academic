from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # como compania herada de partner usamos un nombre distinto
    # al que tiene projects en companias
    partner_academic_project_ids = fields.Many2many(
        related='company_id.academic_project_ids',
        # el store nos está dando un error, probamos sacarlo, no estoy seguro
        # de que sea necesario
        # store=True,
    )
