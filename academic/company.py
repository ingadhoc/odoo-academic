# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, api, _
from openerp.exceptions import Warning


class company(models.Model):

    """"""

    _inherit = 'res.company'

    company_group_ids = fields.One2many(
        'academic.group', 'company_id', string='Groups')
    # we add store to fix a problem showing logo on companies
    logo = fields.Binary(store=True)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
