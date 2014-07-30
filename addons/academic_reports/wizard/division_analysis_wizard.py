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
    consider_disabled_person = fields.Boolean(string='Considerar Personas con Discapacidad?')
    groups = fields.Char('Groups',)
    periods = fields.Char('Periods',)
    company = fields.Char('Comapny',)
    include_diagnosis_eval = fields.Boolean('Incluir Evaluaciones Diagnóstico?',)

    @api.multi
    def action_confirm(self):
        group_ids = [x.id for x in self.group_ids]
        period_ids = [x.id for x in self.period_ids]
        company_id = self.company_id.id
        consider_disabled_person = self.consider_disabled_person
        include_diagnosis_eval = self.include_diagnosis_eval

        periods = ', '.join([x.name for x in self.period_ids])
        groups = ', '.join([x.complete_name for x in self.group_ids])
        company = self.company_id.name

        context = self.with_context(groups=groups, 
            periods=periods, 
            company=company, 
            period_ids=period_ids, 
            group_ids=group_ids,
            company_id=company_id,
            consider_disabled_person=consider_disabled_person,
            include_diagnosis_eval=include_diagnosis_eval,
            ).env.context

        return {
            'name': _('Tablero'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'kanban',
            'res_model': 'academic.division_analysis',
            'target': 'inlineview',
            'context': context,
        }