# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.osv import osv
from openerp.exceptions import except_orm, Warning, RedirectWarning

class academic_division_analysis_wizard(osv.osv_memory):
    _name = "academic.division_analysis_wizard"
    _description = "Division Analysis Wizard"

    group_ids = fields.Many2many('academic.group', 'division_analysis_group_rel',string='Groups')
    period_ids = fields.Many2many('academic.period', 'division_analysis_periods_rel',string='Period')
    company_id = fields.Many2one('res.company', string='Company')

    @api.multi
    def action_confirm(self):
        group_ids = [x.id for x in self.group_ids]
        period_ids = [x.id for x in self.group_ids]
        company_id = self.company_id.id
        print 'context1', self.env.context
        context = self.with_context(company_id=company_id, period_ids=period_ids, group_ids=group_ids).env.context
        print 'context2', context
        return {
            'name': _('Division Analysis'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'kanban',
            'res_model': 'academic.division_analysis',
            # 'views': [(compose_form.id, 'form')],
            # 'view_id': compose_form.id,
            'target': 'current',
            'context': context,
        }