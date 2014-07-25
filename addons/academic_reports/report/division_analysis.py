# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
import openerp.addons.decimal_precision as dp

class academic_division_analysis(models.Model):
    """"""
    
    _name = 'academic.division_analysis'
    _description = 'academic.division_analysis'

    name = fields.Char('Division')
    group_id = fields.Many2one('academic.group','Group',)
    company_id = fields.Many2one('res.company','Company',)
    
    # Agregamos estos indicadores aca para poder mostrarlos donde queremos y porque no podemos mostrar el campo o2m
    # Indicador Interno Lengua
    subi_internal_lang_ind_id = fields.Many2one('survey.question.indicator','Indicator subi_avg_note_lang_value',)
    subi_internal_lang_sub_id = fields.Many2one('academic.subject','Subject subi_internal_lang_value',)
    subi_internal_lang_weight = fields.Float('weight subi_internal_lang_value', digits_compute=dp.get_precision('Sub Indicator Weight'))
    subi_internal_lang_value = fields.Float('Indicador Interno Lengua', compute='_get_indicators', digits_compute=dp.get_precision('Sub Indicator Value'), readonly=True)
    # Indicador Interno Matemática
    subi_internal_math_ind_id = fields.Many2one('survey.question.indicator','Indicator subi_internal_math_value',)
    subi_internal_math_sub_id = fields.Many2one('academic.subject','Subject subi_internal_math_value',)
    subi_internal_math_weight = fields.Float('weight subi_internal_math_value', digits_compute=dp.get_precision('Sub Indicator Weight'))
    subi_internal_math_value = fields.Float('Indicador Interno Matemática', compute='_get_indicators', digits_compute=dp.get_precision('Sub Indicator Value'), readonly=True)    

    # Indicador Externo Lengua
    subi_external_lang_ind_id = fields.Many2one('survey.question.indicator','Indicator subi_avg_note_lang_value',)
    subi_external_lang_sub_id = fields.Many2one('academic.subject','Subject subi_external_lang_value',)
    subi_external_lang_weight = fields.Float('weight subi_external_lang_value', digits_compute=dp.get_precision('Sub Indicator Weight'))
    subi_external_lang_value = fields.Float('Indicador Externo Lengua', compute='_get_indicators', digits_compute=dp.get_precision('Sub Indicator Value'), readonly=True)
    # Indicador Externo Matemática
    subi_external_math_ind_id = fields.Many2one('survey.question.indicator','Indicator subi_external_math_value',)
    subi_external_math_sub_id = fields.Many2one('academic.subject','Subject subi_external_math_value',)
    subi_external_math_weight = fields.Float('weight subi_external_math_value', digits_compute=dp.get_precision('Sub Indicator Weight'))
    subi_external_math_value = fields.Float('Indicador Externo Matemática', compute='_get_indicators', digits_compute=dp.get_precision('Sub Indicator Value'), readonly=True)    

    # Porcentaje de horas dadas Lengua
    subi_avg_hour_lang_ind_id = fields.Many2one('survey.question.indicator','Indicator subi_avg_hour_lang_value',)
    subi_avg_hour_lang_sub_id = fields.Many2one('academic.subject','Subject subi_avg_hour_lang_value',)
    subi_avg_hour_lang_weight = fields.Float('weight subi_avg_hour_lang_value', digits_compute=dp.get_precision('Sub Indicator Weight'))
    subi_avg_hour_lang_value = fields.Float('Porcentaje de horas dadas Lengua', compute='_get_indicators', digits_compute=dp.get_precision('Sub Indicator Value'), readonly=True)
    # Porcentaje de horas dadas Matematica
    subi_avg_hour_math_ind_id = fields.Many2one('survey.question.indicator','Indicator subi_avg_hour_math_value',)
    subi_avg_hour_math_sub_id = fields.Many2one('academic.subject','Subject subi_avg_hour_math_value',)
    subi_avg_hour_math_weight = fields.Float('weight subi_avg_hour_math_value', digits_compute=dp.get_precision('Sub Indicator Weight'))
    subi_avg_hour_math_value = fields.Float('Porcentaje de horas dadas Matematica', compute='_get_indicators', digits_compute=dp.get_precision('Sub Indicator Value'), readonly=True)    
    
    # Porcentaje de temas desarrollados Lengua
    subi_avg_topics_lang_ind_id = fields.Many2one('survey.question.indicator','Indicator subi_avg_topics_lang_value',)
    subi_avg_topics_lang_sub_id = fields.Many2one('academic.subject','Subject subi_avg_topics_lang_value',)
    subi_avg_topics_lang_weight = fields.Float('weight subi_avg_topics_lang_value', digits_compute=dp.get_precision('Sub Indicator Weight'))
    subi_avg_topics_lang_value = fields.Float('Porcentaje de temas desarrollados Lengua', compute='_get_indicators', digits_compute=dp.get_precision('Sub Indicator Value'), readonly=True)
    # Porcentaje de temas desarrollados Matematica
    subi_avg_topics_math_ind_id = fields.Many2one('survey.question.indicator','Indicator subi_avg_topics_math_value',)
    subi_avg_topics_math_sub_id = fields.Many2one('academic.subject','Subject subi_avg_topics_math_value',)
    subi_avg_topics_math_weight = fields.Float('weight subi_avg_topics_math_value', digits_compute=dp.get_precision('Sub Indicator Weight'))
    subi_avg_topics_math_value = fields.Float('Porcentaje de temas desarrollados Matematica', compute='_get_indicators', digits_compute=dp.get_precision('Sub Indicator Value'), readonly=True)    
        
    # Porcentaje de proyectos específicos Lengua
    subi_avg_spec_proj_lang_ind_id = fields.Many2one('survey.question.indicator','Indicator subi_avg_spec_proj_lang_value',)
    subi_avg_spec_proj_lang_sub_id = fields.Many2one('academic.subject','Subject subi_avg_spec_proj_lang_value',)
    subi_avg_spec_proj_lang_weight = fields.Float('weight subi_avg_spec_proj_lang_value', digits_compute=dp.get_precision('Sub Indicator Weight'))
    subi_avg_spec_proj_lang_value = fields.Float('Porcentaje de temas desarrollados Lengua', compute='_get_indicators', digits_compute=dp.get_precision('Sub Indicator Value'), readonly=True)
    # Porcentaje de proyectos específicos Matematica
    subi_avg_spec_proj_math_ind_id = fields.Many2one('survey.question.indicator','Indicator subi_avg_spec_proj_math_value',)
    subi_avg_spec_proj_math_sub_id = fields.Many2one('academic.subject','Subject subi_avg_spec_proj_math_value',)
    subi_avg_spec_proj_math_weight = fields.Float('weight subi_avg_spec_proj_math_value', digits_compute=dp.get_precision('Sub Indicator Weight'))
    subi_avg_spec_proj_math_value = fields.Float('Porcentaje de temas desarrollados Matematica', compute='_get_indicators', digits_compute=dp.get_precision('Sub Indicator Value'), readonly=True)    
            
    # Porcentaje de capacitación pertinente Lengua
    subi_avg_relevant_training_lang_ind_id = fields.Many2one('survey.question.indicator','Indicator subi_avg_relevant_training_lang_value',)
    subi_avg_relevant_training_lang_sub_id = fields.Many2one('academic.subject','Subject subi_avg_relevant_training_lang_value',)
    subi_avg_relevant_training_lang_weight = fields.Float('weight subi_avg_relevant_training_lang_value', digits_compute=dp.get_precision('Sub Indicator Weight'))
    subi_avg_relevant_training_lang_value = fields.Float('Porcentaje de temas desarrollados Lengua', compute='_get_indicators', digits_compute=dp.get_precision('Sub Indicator Value'), readonly=True)
    # Porcentaje de capacitación pertinente Matematica
    subi_avg_relevant_training_math_ind_id = fields.Many2one('survey.question.indicator','Indicator subi_avg_relevant_training_math_value',)
    subi_avg_relevant_training_math_sub_id = fields.Many2one('academic.subject','Subject subi_avg_relevant_training_math_value',)
    subi_avg_relevant_training_math_weight = fields.Float('weight subi_avg_relevant_training_math_value', digits_compute=dp.get_precision('Sub Indicator Weight'))
    subi_avg_relevant_training_math_value = fields.Float('Porcentaje de temas desarrollados Matematica', compute='_get_indicators', digits_compute=dp.get_precision('Sub Indicator Value'), readonly=True)    
                
    # Porcentaje de entrevistas con docentes  
    subi_avg_teacher_interview_ind_id = fields.Many2one('survey.question.indicator','Indicator subi_avg_teacher_interview_value',)
    subi_avg_teacher_interview_sub_id = fields.Many2one('academic.subject','Subject subi_avg_teacher_interview_value',)
    subi_avg_teacher_interview_weight = fields.Float('weight subi_avg_teacher_interview_value', digits_compute=dp.get_precision('Sub Indicator Weight'))
    subi_avg_teacher_interview_value = fields.Float('Porcentaje de temas desarrollados Matematica', compute='_get_indicators', digits_compute=dp.get_precision('Sub Indicator Value'), readonly=True)    
    
    # Porcentaje tiempo asignado a temas pedagógico Lengua
    subi_timextopic_ped_lang_ind_id = fields.Many2one('survey.question.indicator','Indicator subi_timextopic_ped_lang_value',)
    subi_timextopic_ped_lang_sub_id = fields.Many2one('academic.subject','Subject subi_timextopic_ped_lang_value',)
    subi_timextopic_ped_lang_weight = fields.Float('weight subi_timextopic_ped_lang_value', digits_compute=dp.get_precision('Sub Indicator Weight'))
    subi_timextopic_ped_lang_value = fields.Float('Porcentaje de temas desarrollados Matematica', compute='_get_indicators', digits_compute=dp.get_precision('Sub Indicator Value'), readonly=True)        
    # Porcentaje tiempo asignado a temas pedagógico Matematica
    subi_timextopic_ped_math_ind_id = fields.Many2one('survey.question.indicator','Indicator subi_timextopic_ped_math_value',)
    subi_timextopic_ped_math_sub_id = fields.Many2one('academic.subject','Subject subi_timextopic_ped_math_value',)
    subi_timextopic_ped_math_weight = fields.Float('weight subi_timextopic_ped_math_value', digits_compute=dp.get_precision('Sub Indicator Weight'))
    subi_timextopic_ped_math_value = fields.Float('Porcentaje de temas desarrollados Matematica', compute='_get_indicators', digits_compute=dp.get_precision('Sub Indicator Value'), readonly=True)    
        
    # Porcentaje tiempo asignado a temas organizativos Lengua
    subi_timextopic_org_lang_ind_id = fields.Many2one('survey.question.indicator','Indicator subi_timextopic_org_lang_value',)
    subi_timextopic_org_lang_sub_id = fields.Many2one('academic.subject','Subject subi_timextopic_org_lang_value',)
    subi_timextopic_org_lang_weight = fields.Float('weight subi_timextopic_org_lang_value', digits_compute=dp.get_precision('Sub Indicator Weight'))
    subi_timextopic_org_lang_value = fields.Float('Porcentaje de temas desarrollados Matematica', compute='_get_indicators', digits_compute=dp.get_precision('Sub Indicator Value'), readonly=True)        
    # Porcentaje tiempo asignado a temas organizativos Matematica
    subi_timextopic_org_math_ind_id = fields.Many2one('survey.question.indicator','Indicator subi_timextopic_org_math_value',)
    subi_timextopic_org_math_sub_id = fields.Many2one('academic.subject','Subject subi_timextopic_org_math_value',)
    subi_timextopic_org_math_weight = fields.Float('weight subi_timextopic_org_math_value', digits_compute=dp.get_precision('Sub Indicator Weight'))
    subi_timextopic_org_math_value = fields.Float('Porcentaje de temas desarrollados Matematica', compute='_get_indicators', digits_compute=dp.get_precision('Sub Indicator Value'), readonly=True)    
    
    # Porcentaje de entrevistas con alumnos  
    subi_avg_student_interview_ind_id = fields.Many2one('survey.question.indicator','Indicator subi_avg_student_interview_value',)
    subi_avg_student_interview_sub_id = fields.Many2one('academic.subject','Subject subi_avg_student_interview_value',)
    subi_avg_student_interview_weight = fields.Float('weight subi_avg_student_interview_value', digits_compute=dp.get_precision('Sub Indicator Weight'))
    subi_avg_student_interview_value = fields.Float('Porcentaje de temas desarrollados Matematica', compute='_get_indicators', digits_compute=dp.get_precision('Sub Indicator Value'), readonly=True)    
        
    # Porcentaje de asistencia padre o madre
    subi_avg_marriage_att_ind_id = fields.Many2one('survey.question.indicator','Indicator subi_avg_student_interview_value',)
    subi_avg_marriage_att_sub_id = fields.Many2one('academic.subject','Subject subi_avg_marriage_att_value',)
    subi_avg_marriage_att_weight = fields.Float('weight subi_avg_marriage_att_value', digits_compute=dp.get_precision('Sub Indicator Weight'))
    subi_avg_marriage_att_value = fields.Float('Porcentaje de temas desarrollados Matematica', compute='_get_indicators', digits_compute=dp.get_precision('Sub Indicator Value'), readonly=True)    
            
    # Porcentaje de asistencia padre o madre
    subi_avg_parent_att_ind_id = fields.Many2one('survey.question.indicator','Indicator subi_avg_student_interview_value',)
    subi_avg_parent_att_sub_id = fields.Many2one('academic.subject','Subject subi_avg_parent_att_value',)
    subi_avg_parent_att_weight = fields.Float('weight subi_avg_parent_att_value', digits_compute=dp.get_precision('Sub Indicator Weight'))
    subi_avg_parent_att_value = fields.Float('Porcentaje de temas desarrollados Matematica', compute='_get_indicators', digits_compute=dp.get_precision('Sub Indicator Value'), readonly=True)    
    
    student_perfomance = fields.Float('Student Performance', compute="_get_indicators", digits_compute=dp.get_precision('Sub Indicator Weight'))
    teacher_perfomance = fields.Float('Teacher Performance', compute="_get_indicators", digits_compute=dp.get_precision('Sub Indicator Weight'))
    director_perfomance = fields.Float('Director Performance', compute="_get_indicators", digits_compute=dp.get_precision('Sub Indicator Weight'))

    @api.one
    def _get_indicators(self):
        print 'self.env.context', self.env.context
        self.subi_internal_lang_value = self._get_value(self.subi_internal_lang_ind_id, self.subi_internal_lang_sub_id, self.subi_internal_lang_weight)[0]
        self.subi_internal_math_value = self._get_value(self.subi_internal_math_ind_id, self.subi_internal_math_sub_id, self.subi_internal_math_weight)[0]
        
        self.subi_external_lang_value = self._get_value(self.subi_external_lang_ind_id, self.subi_external_lang_sub_id, self.subi_external_lang_weight)[0]
        self.subi_external_math_value = self._get_value(self.subi_external_math_ind_id, self.subi_external_math_sub_id, self.subi_external_math_weight)[0]
        
        self.subi_avg_hour_lang_value = self._get_value(self.subi_avg_hour_lang_ind_id, self.subi_avg_hour_lang_sub_id, self.subi_avg_hour_lang_weight)[0]
        self.subi_avg_hour_math_value = self._get_value(self.subi_avg_hour_math_ind_id, self.subi_avg_hour_math_sub_id, self.subi_avg_hour_math_weight)[0]

        self.subi_avg_topics_lang_value = self._get_value(self.subi_avg_topics_lang_ind_id, self.subi_avg_topics_lang_sub_id, self.subi_avg_topics_lang_weight)[0]
        self.subi_avg_topics_math_value = self._get_value(self.subi_avg_topics_math_ind_id, self.subi_avg_topics_math_sub_id, self.subi_avg_topics_math_weight)[0]

        self.subi_avg_spec_proj_lang_value = self._get_value(self.subi_avg_spec_proj_lang_ind_id, self.subi_avg_spec_proj_lang_sub_id, self.subi_avg_spec_proj_lang_weight)[0]
        self.subi_avg_spec_proj_math_value = self._get_value(self.subi_avg_spec_proj_math_ind_id, self.subi_avg_spec_proj_math_sub_id, self.subi_avg_spec_proj_math_weight)[0]

        self.subi_avg_relevant_training_lang_value = self._get_value(self.subi_avg_relevant_training_lang_ind_id, self.subi_avg_relevant_training_lang_sub_id, self.subi_avg_relevant_training_lang_weight)[0]
        self.subi_avg_relevant_training_math_value = self._get_value(self.subi_avg_relevant_training_math_ind_id, self.subi_avg_relevant_training_math_sub_id, self.subi_avg_relevant_training_math_weight)[0]
        
        self.subi_avg_teacher_interview_value = self._get_value(self.subi_avg_teacher_interview_ind_id, self.subi_avg_teacher_interview_sub_id, self.subi_avg_teacher_interview_weight)[0]
        
        self.subi_timextopic_ped_lang_value = self._get_value(self.subi_timextopic_ped_lang_ind_id, self.subi_timextopic_ped_lang_sub_id, self.subi_timextopic_ped_lang_weight)[0]
        self.subi_timextopic_ped_math_value = self._get_value(self.subi_timextopic_ped_math_ind_id, self.subi_timextopic_ped_math_sub_id, self.subi_timextopic_ped_math_weight)[0]

        self.subi_timextopic_org_lang_value = self._get_value(self.subi_timextopic_org_lang_ind_id, self.subi_timextopic_org_lang_sub_id, self.subi_timextopic_org_lang_weight)[0]
        self.subi_timextopic_org_math_value = self._get_value(self.subi_timextopic_org_math_ind_id, self.subi_timextopic_org_math_sub_id, self.subi_timextopic_org_math_weight)[0]

        self.subi_avg_student_interview_value = self._get_value(self.subi_avg_student_interview_ind_id, self.subi_avg_student_interview_sub_id, self.subi_avg_student_interview_weight)[0]
        
        self.subi_avg_marriage_att_value = self._get_value(self.subi_avg_marriage_att_ind_id, self.subi_avg_marriage_att_sub_id, self.subi_avg_marriage_att_weight)[0]
        self.subi_avg_parent_att_value = self._get_value(self.subi_avg_parent_att_ind_id, self.subi_avg_parent_att_sub_id, self.subi_avg_parent_att_weight)[0]

        # Performance - Desempenos    
        self.student_perfomance = self.subi_internal_lang_value + self.subi_internal_math_value \
            + self.subi_external_lang_value + self.subi_external_math_value

        self.teacher_perfomance = self.subi_avg_hour_lang_value + self.subi_avg_hour_math_value \
            + self.subi_avg_topics_lang_value + self.subi_avg_topics_math_value \
            + self.subi_avg_spec_proj_lang_value + self.subi_avg_spec_proj_math_value \
            + self.subi_avg_relevant_training_lang_value + self.subi_avg_relevant_training_math_value
        
        self.director_perfomance = self.subi_avg_teacher_interview_value \
            + self.subi_timextopic_ped_lang_value + self.subi_timextopic_ped_math_value \
            + self.subi_timextopic_org_lang_value + self.subi_timextopic_org_math_value \
            + self.subi_timextopic_org_lang_value + self.subi_timextopic_org_math_value \
            + self.subi_avg_student_interview_value \
            + self.subi_avg_marriage_att_value + self.subi_avg_parent_att_value

    @api.one
    # TODO ampliar esta funcion para que pueda recibir estos argumentos
    # Para esto voy a tener que agregar trimestre y anos
    # def _get_value(self, indicator, subject, weight, year, quarter=False, group_ids=False, company_id=False):
    def _get_value(self, indicator, subject, weight):
        print 'self.env.context', self.env.context
        group_id = self.env.context.get('default_group_id', False)
        company_id = self.env.context.get('default_company_id', False)
        
        domain = []
        # If not indicator we return False
        if indicator:
            domain.append(('question_id.indicator_id','=',indicator.id))
        else:
            return False

        if subject:
            domain.append(('user_input_id.group_id.subject_id','=',subject.id))            
        
        # Append restrictions from context
        if group_id:
            domain.append(('user_input_id.group_id','=',group_id))
        if company_id:
            domain.append(('user_input_id.company_id','=',company_id))

        user_input_question_score_ids = self.env['survey.user_input_question_score'].search(domain)
        
        # Hago este read exclusviamente porque sin este read vuelve a calcular los campos funcion
        print len(user_input_question_score_ids.read(['indicator_rel_score']))
        indicator_rel_scores = [x.indicator_rel_score for x in user_input_question_score_ids]

        
        # Hago este read exclusviamente porque sin este read vuelve a calcular los campos funcion
        question_ids = [x.question_id.id for x in user_input_question_score_ids]
        questions = self.env['survey.question'].search([('id','in',question_ids)])
        print len(questions.read(['max_indicator_rel_score']))
        
        max_indicator_rel_scores = [x.question_id.max_indicator_rel_score for x in user_input_question_score_ids]
        sum_max_indicator_rel_scores = sum(max_indicator_rel_scores)
        value = 0.0
        if sum_max_indicator_rel_scores and sum_max_indicator_rel_scores != 0.0:
            value = (sum(indicator_rel_scores) / sum(max_indicator_rel_scores)) * (weight / 100.0)
        return value

# Esto no lo pudimos usar porque el foreach en la kanban no sabemos como funciona y a su vez no sabriamos como poner cada elemento donde queremos
# class academic_division_analysis_detail(models.Model):
#     """"""
    
#     _name = 'academic.division_analysis_detail'
#     _description = 'academic.division_analysis detail'

#     indicator_id = fields.Many2one ('survey.question.indicator', 'Indicator')
#     subject_id = fields.Many2one ('academic.subject', 'Subject')
#     value = fields.Float ('Value', compute="_get_value")
#     weight = fields.Float ('Ponderator', required=True)
#     sequence = fields.Integer ('Sequence', required=True)
#     # TODO agregar un ondelete para hacer la composicion
#     division_analysis_id  = fields.Many2one ('academic.division_analysis', 'Division Analysis', required=True, ondelete="cascade")

#     @api.one
#     def _get_value(self):
#         group_id = self.env.context.get('default_group_id', False)
#         company_id = self.env.context.get('default_company_id', False)
#         print 'self.env.context22222222222', self.env.context
#         # subject_id = self.env.context.get('default_subject_id', False)
#         domain = []
#         if group_id:
#             domain.append(('user_input_id.group_id','=',group_id))
#         if company_id:
#             domain.append(('user_input_id.company_id','=',company_id))
#         if self.subject_id:
#             domain.append(('user_input_id.group_id.subject_id','=',self.subject_id.id))            
#         # user_input_question_score_ids = self.env['survey.user_input_question_score'].search(domain)
#         # scores = [x.score for x in user_input_question_score_ids]
#         # value = sum(scores) * self.weight / len(scores)
#         value = 5
#         self.value = value
