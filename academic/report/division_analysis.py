##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api
import odoo.addons.decimal_precision as dp


class AcademicDivisionAnalysis(models.Model):

    _name = 'academic.division_analysis'
    _description = 'academic.division_analysis'

    name = fields.Char(
        'Division',
    )
    groups = fields.Char(
        compute='_compute_indicators',
    )
    periods = fields.Char(
        compute='_compute_indicators',
    )
    company = fields.Char(
        compute='_compute_indicators',
    )
    consider_disabled_person = fields.Char(
        compute='_compute_indicators',)
    include_diagnosis_eval = fields.Char(
        'Include Diagnosis Evaluations',
        compute='_compute_indicators',
    )

    # Agregamos estos indicadores aca para
    # poder mostrarlos donde queremos y porque no podemos mostrar el campo o2m
    # Indicador Interno Lengua
    subi_internal_lang_ind_id = fields.Many2one(
        'survey.question.indicator',
        'Indicator subi_avg_note_lang_value',)
    subi_internal_lang_sub_id = fields.Many2one(
        'academic.subject',
        'Subject subi_internal_lang_value',)
    subi_internal_lang_weight = fields.Float(
        'weight subi_internal_lang_value',
        digits=dp.get_precision(
            'Sub Indicator Weight'))
    subi_internal_lang_value = fields.Float(
        'Indicador Interno Lengua',
        compute='_compute_indicators',
        digits=dp.get_precision('Sub Indicator Value'),
        readonly=True)
    # Indicador Interno Matemática
    subi_internal_math_ind_id = fields.Many2one(
        'survey.question.indicator',
        'Indicator subi_internal_math_value',)
    subi_internal_math_sub_id = fields.Many2one(
        'academic.subject',
        'Subject subi_internal_math_value',)
    subi_internal_math_weight = fields.Float(
        'weight subi_internal_math_value',
        digits=dp.get_precision(
            'Sub Indicator Weight'),
    )
    subi_internal_math_value = fields.Float(
        'Indicador Interno Matemática',
        compute='_compute_indicators',
        digits=dp.get_precision('Sub Indicator Value'),
        readonly=True)

    # Indicador Externo Lengua
    subi_external_lang_ind_id = fields.Many2one(
        'survey.question.indicator', 'Indicator subi_avg_note_lang_value',)
    subi_external_lang_sub_id = fields.Many2one(
        'academic.subject', 'Subject subi_external_lang_value',)
    subi_external_lang_weight = fields.Float(
        'weight subi_external_lang_value',
        digits=dp.get_precision(
            'Sub Indicator Weight'))
    subi_external_lang_value = fields.Float(
        'Indicador Externo Lengua',
        compute='_compute_indicators',
        digits=dp.get_precision('Sub Indicator Value'),
        readonly=True)
    # Indicador Externo Matemática
    subi_external_math_ind_id = fields.Many2one(
        'survey.question.indicator', 'Indicator subi_external_math_value',)
    subi_external_math_sub_id = fields.Many2one(
        'academic.subject', 'Subject subi_external_math_value',)
    subi_external_math_weight = fields.Float(
        'weight subi_external_math_value', digits=dp.get_precision(
            'Sub Indicator Weight'))
    subi_external_math_value = fields.Float(
        'Indicador Externo Matemática',
        compute='_compute_indicators',
        digits=dp.get_precision('Sub Indicator Value'),
        readonly=True)

    # Porcentaje de horas dadas Lengua
    subi_avg_hour_lang_ind_id = fields.Many2one(
        'survey.question.indicator',
        'Indicator subi_avg_hour_lang_value',)
    subi_avg_hour_lang_sub_id = fields.Many2one(
        'academic.subject',
        'Subject subi_avg_hour_lang_value',)
    subi_avg_hour_lang_weight = fields.Float(
        'weight subi_avg_hour_lang_value',
        digits=dp.get_precision(
            'Sub Indicator Weight'))
    subi_avg_hour_lang_value = fields.Float(
        'Porcentaje de horas dadas Lengua',
        compute='_compute_indicators',
        digits=dp.get_precision('Sub Indicator Value'),
        readonly=True)
    # Porcentaje de horas dadas Matematica
    subi_avg_hour_math_ind_id = fields.Many2one(
        'survey.question.indicator',
        'Indicator subi_avg_hour_math_value',)
    subi_avg_hour_math_sub_id = fields.Many2one(
        'academic.subject',
        'Subject subi_avg_hour_math_value',)
    subi_avg_hour_math_weight = fields.Float(
        'weight subi_avg_hour_math_value',
        digits=dp.get_precision(
            'Sub Indicator Weight'))
    subi_avg_hour_math_value = fields.Float(
        'Porcentaje de horas dadas Matematica',
        compute='_compute_indicators',
        digits=dp.get_precision(
            'Sub Indicator Value'),
        readonly=True)

    # Porcentaje de temas desarrollados Lengua
    subi_avg_topics_lang_ind_id = fields.Many2one(
        'survey.question.indicator',
        'Indicator subi_avg_topics_lang_value',)
    subi_avg_topics_lang_sub_id = fields.Many2one(
        'academic.subject',
        'Subject subi_avg_topics_lang_value',)
    subi_avg_topics_lang_weight = fields.Float(
        'weight subi_avg_topics_lang_value',
        digits=dp.get_precision(
            'Sub Indicator Weight'))
    subi_avg_topics_lang_value = fields.Float(
        'Porcentaje de temas desarrollados Lengua',
        compute='_compute_indicators',
        digits=dp.get_precision(
            'Sub Indicator Value'),
        readonly=True)
    # Porcentaje de temas desarrollados Matematica
    subi_avg_topics_math_ind_id = fields.Many2one(
        'survey.question.indicator',
        'Indicator subi_avg_topics_math_value',)
    subi_avg_topics_math_sub_id = fields.Many2one(
        'academic.subject',
        'Subject subi_avg_topics_math_value',)
    subi_avg_topics_math_weight = fields.Float(
        'weight subi_avg_topics_math_value',
        digits=dp.get_precision(
            'Sub Indicator Weight'))
    subi_avg_topics_math_value = fields.Float(
        'Porcentaje de temas desarrollados Matematica',
        compute='_compute_indicators',
        digits=dp.get_precision(
            'Sub Indicator Value'),
        readonly=True)

    # Porcentaje de proyectos específicos Lengua
    subi_avg_spec_proj_lang_ind_id = fields.Many2one(
        'survey.question.indicator',
        'Indicator subi_avg_spec_proj_lang_value',)
    subi_avg_spec_proj_lang_sub_id = fields.Many2one(
        'academic.subject',
        'Subject subi_avg_spec_proj_lang_value',)
    subi_avg_spec_proj_lang_weight = fields.Float(
        'weight subi_avg_spec_proj_lang_value',
        digits=dp.get_precision(
            'Sub Indicator Weight'))
    subi_avg_spec_proj_lang_value = fields.Float(
        'Porcentaje de temas desarrollados Lengua',
        compute='_compute_indicators',
        digits=dp.get_precision('Sub Indicator Value'),
        readonly=True)
    # Porcentaje de proyectos específicos Matematica
    subi_avg_spec_proj_math_ind_id = fields.Many2one(
        'survey.question.indicator',
        'Indicator subi_avg_spec_proj_math_value',)
    subi_avg_spec_proj_math_sub_id = fields.Many2one(
        'academic.subject',
        'Subject subi_avg_spec_proj_math_value',)
    subi_avg_spec_proj_math_weight = fields.Float(
        'weight subi_avg_spec_proj_math_value',
        digits=dp.get_precision(
            'Sub Indicator Weight'))
    subi_avg_spec_proj_math_value = fields.Float(
        'Porcentaje de temas desarrollados Matematica',
        compute='_compute_indicators',
        digits=dp.get_precision(
            'Sub Indicator Value'),
        readonly=True)

    # Porcentaje de capacitación pertinente Lengua
    subi_avg_relevant_training_lang_ind_id = fields.Many2one(
        'survey.question.indicator',
        'Indicator subi_avg_relevant_training_lang_value',)
    subi_avg_relevant_training_lang_sub_id = fields.Many2one(
        'academic.subject', 'Subject subi_avg_relevant_training_lang_value',)
    subi_avg_relevant_training_lang_weight = fields.Float(
        'weight subi_avg_relevant_training_lang_value',
        digits=dp.get_precision('Sub Indicator Weight'))
    subi_avg_relevant_training_lang_value = fields.Float(
        'Porcentaje de temas desarrollados Lengua',
        compute='_compute_indicators',
        digits=dp.get_precision(
            'Sub Indicator Value'),
        readonly=True)
    # Porcentaje de capacitación pertinente Matematica
    subi_avg_relevant_training_math_ind_id = fields.Many2one(
        'survey.question.indicator',
        'Indicator subi_avg_relevant_training_math_value',)
    subi_avg_relevant_training_math_sub_id = fields.Many2one(
        'academic.subject',
        'Subject subi_avg_relevant_training_math_value',)
    subi_avg_relevant_training_math_weight = fields.Float(
        'weight subi_avg_relevant_training_math_value',
        digits=dp.get_precision('Sub Indicator Weight'))
    subi_avg_relevant_training_math_value = fields.Float(
        'Porcentaje de temas desarrollados Matematica',
        compute='_compute_indicators', digits=dp.get_precision(
            'Sub Indicator Value'),
        readonly=True)

    # Porcentaje de entrevistas con docentes - Lengua
    subi_avg_teacher_interview_lang_ind_id = fields.Many2one(
        'survey.question.indicator',
        'Indicator subi_avg_teacher_interview_lang_value',)
    subi_avg_teacher_interview_lang_sub_id = fields.Many2one(
        'academic.subject',
        'Subject subi_avg_teacher_interview_lang_value',)
    subi_avg_teacher_interview_lang_weight = fields.Float(
        'weight subi_avg_teacher_interview_lang_value',
        digits=dp.get_precision('Sub Indicator Weight'))
    subi_avg_teacher_interview_lang_value = fields.Float(
        'Porcentaje de temas desarrollados Matematica',
        compute='_compute_indicators',
        digits=dp.get_precision(
            'Sub Indicator Value'),
        readonly=True)
    # Porcentaje de entrevistas con docentes - Matemática
    subi_avg_teacher_interview_math_ind_id = fields.Many2one(
        'survey.question.indicator',
        'Indicator subi_avg_teacher_interview_math_value',)
    subi_avg_teacher_interview_math_sub_id = fields.Many2one(
        'academic.subject',
        'Subject subi_avg_teacher_interview_math_value',)
    subi_avg_teacher_interview_math_weight = fields.Float(
        'weight subi_avg_teacher_interview_math_value',
        digits=dp.get_precision('Sub Indicator Weight'))
    subi_avg_teacher_interview_math_value = fields.Float(
        'Porcentaje de temas desarrollados Matematica',
        compute='_compute_indicators',
        digits=dp.get_precision(
            'Sub Indicator Value'),
        readonly=True)

    # Porcentaje tiempo asignado a temas Lengua
    subi_timextopic_lang_ind_id = fields.Many2one(
        'survey.question.indicator',
        'Indicator subi_timextopic_lang_value',)
    subi_timextopic_lang_sub_id = fields.Many2one(
        'academic.subject',
        'Subject subi_timextopic_lang_value',)
    subi_timextopic_lang_weight = fields.Float(
        'weight subi_timextopic_lang_value',
        digits=dp.get_precision(
            'Sub Indicator Weight'))
    subi_timextopic_lang_value = fields.Float(
        'Porcentaje de temas desarrollados Matematica',
        compute='_compute_indicators',
        digits=dp.get_precision(
            'Sub Indicator Value'),
        readonly=True)
    # Porcentaje tiempo asignado a temas pedagógico Matematica
    subi_timextopic_math_ind_id = fields.Many2one(
        'survey.question.indicator',
        'Indicator subi_timextopic_math_value',)
    subi_timextopic_math_sub_id = fields.Many2one(
        'academic.subject',
        'Subject subi_timextopic_math_value',)
    subi_timextopic_math_weight = fields.Float(
        'weight subi_timextopic_math_value',
        digits=dp.get_precision(
            'Sub Indicator Weight'))
    subi_timextopic_math_value = fields.Float(
        'Porcentaje de temas desarrollados Matematica',
        compute='_compute_indicators',
        digits=dp.get_precision(
            'Sub Indicator Value'),
        readonly=True)

    # Porcentaje de asistencia padre o madre
    subi_avg_parent_att_ind_id = fields.Many2one(
        'survey.question.indicator',
        'Indicator subi_avg_student_interview_value',)
    subi_avg_parent_att_sub_id = fields.Many2one(
        'academic.subject', 'Subject subi_avg_parent_att_value',)
    subi_avg_parent_att_weight = fields.Float(
        'weight subi_avg_parent_att_value',
        digits=dp.get_precision(
            'Sub Indicator Weight'))
    subi_avg_parent_att_value = fields.Float(
        'Porcentaje de temas desarrollados Matematica',
        compute='_compute_indicators',
        digits=dp.get_precision(
            'Sub Indicator Value'),
        readonly=True)

    student_perfomance = fields.Float(
        'Student Performance', compute="_compute_indicators",
        digits=dp.get_precision('Sub Indicator Weight'))
    teacher_perfomance = fields.Float(
        'Teacher Performance', compute="_compute_indicators",
        digits=dp.get_precision('Sub Indicator Weight'))
    administrator_perfomance = fields.Float(
        'Administrator Performance', compute="_compute_indicators",
        digits=dp.get_precision('Sub Indicator Weight'))

    @api.multi
    def _compute_indicators(self):
        for rec in self:
            rec.subi_internal_lang_value = rec._get_values(
                rec.subi_internal_lang_ind_id, rec.subi_internal_lang_sub_id,
                rec.subi_internal_lang_weight)
            rec.subi_internal_math_value = rec._get_values(
                rec.subi_internal_math_ind_id, rec.subi_internal_math_sub_id,
                rec.subi_internal_math_weight)

            rec.subi_external_lang_value = rec._get_values(
                rec.subi_external_lang_ind_id, rec.subi_external_lang_sub_id,
                rec.subi_external_lang_weight)
            rec.subi_external_math_value = rec._get_values(
                rec.subi_external_math_ind_id, rec.subi_external_math_sub_id,
                rec.subi_external_math_weight)

            rec.subi_avg_hour_lang_value = rec._get_values(
                rec.subi_avg_hour_lang_ind_id, rec.subi_avg_hour_lang_sub_id,
                rec.subi_avg_hour_lang_weight)
            rec.subi_avg_hour_math_value = rec._get_values(
                rec.subi_avg_hour_math_ind_id, rec.subi_avg_hour_math_sub_id,
                rec.subi_avg_hour_math_weight)

            rec.subi_avg_topics_lang_value = rec._get_values(
                rec.subi_avg_topics_lang_ind_id,
                rec.subi_avg_topics_lang_sub_id,
                rec.subi_avg_topics_lang_weight)
            rec.subi_avg_topics_math_value = rec._get_values(
                rec.subi_avg_topics_math_ind_id,
                rec.subi_avg_topics_math_sub_id,
                rec.subi_avg_topics_math_weight)

            rec.subi_avg_spec_proj_lang_value = rec._get_values(
                rec.subi_avg_spec_proj_lang_ind_id, rec.
                subi_avg_spec_proj_lang_sub_id,
                rec.subi_avg_spec_proj_lang_weight)
            rec.subi_avg_spec_proj_math_value = rec._get_values(
                rec.subi_avg_spec_proj_math_ind_id, rec.
                subi_avg_spec_proj_math_sub_id,
                rec.subi_avg_spec_proj_math_weight)

            rec.subi_avg_relevant_training_lang_value = rec._get_values(
                rec.subi_avg_relevant_training_lang_ind_id, rec.
                subi_avg_relevant_training_lang_sub_id, rec.
                subi_avg_relevant_training_lang_weight)
            rec.subi_avg_relevant_training_math_value = rec._get_values(
                rec.subi_avg_relevant_training_math_ind_id, rec.
                subi_avg_relevant_training_math_sub_id, rec.
                subi_avg_relevant_training_math_weight)

            rec.subi_avg_teacher_interview_lang_value = rec._get_values(
                rec.subi_avg_teacher_interview_lang_ind_id, rec.
                subi_avg_teacher_interview_lang_sub_id, rec.
                subi_avg_teacher_interview_lang_weight)
            rec.subi_avg_teacher_interview_math_value = rec._get_values(
                rec.subi_avg_teacher_interview_math_ind_id, rec.
                subi_avg_teacher_interview_math_sub_id, rec.
                subi_avg_teacher_interview_math_weight)

            rec.subi_timextopic_lang_value = rec._get_values(
                rec.subi_timextopic_lang_ind_id,
                rec.subi_timextopic_lang_sub_id,
                rec.subi_timextopic_lang_weight)
            rec.subi_timextopic_math_value = rec._get_values(
                rec.subi_timextopic_math_ind_id,
                rec.subi_timextopic_math_sub_id,
                rec.subi_timextopic_math_weight)

            rec.subi_avg_parent_att_value = rec._get_values(
                rec.subi_avg_parent_att_ind_id, rec.subi_avg_parent_att_sub_id,
                rec.subi_avg_parent_att_weight)

        # Performance -
            rec.student_perfomance = rec.subi_internal_lang_value + \
                rec.subi_internal_math_value \
                + rec.subi_external_lang_value + rec.subi_external_math_value

            rec.teacher_perfomance = rec.subi_avg_hour_lang_value +\
                rec.subi_avg_hour_math_value \
                + rec.subi_avg_topics_lang_value +\
                rec.subi_avg_topics_math_value \
                + rec.subi_avg_spec_proj_lang_value +\
                rec.subi_avg_spec_proj_math_value \
                + rec.subi_avg_relevant_training_lang_value +\
                rec.subi_avg_relevant_training_math_value

            rec.administrator_perfomance = \
                rec.subi_avg_teacher_interview_lang_value + \
                rec.subi_avg_teacher_interview_math_value \
                + rec.subi_timextopic_lang_value +\
                rec.subi_timextopic_math_value \
                + rec.subi_avg_parent_att_value

        # Get names
        groups = self.env.context.get('groups', False)
        periods = self.env.context.get('periods', False)
        company = self.env.context.get('company', False)
        consider_disabled_person = self.env.context.get(
            'consider_disabled_person', False)
        include_diagnosis_eval = self.env.context.get(
            'include_diagnosis_eval', False)
        rec.groups = groups
        rec.periods = periods
        rec.company = company
        rec.consider_disabled_person = consider_disabled_person
        rec.include_diagnosis_eval = include_diagnosis_eval

    def _get_values(self, indicator, subject, weight):

        def get_user_input_scores(
                self, domain, get_max_indicator_rel_scores=True):
            user_input_question_scores = self.env[
                'survey.user_input_question_score'].search(domain)

            # Hago este read exclusviamente porque sin este read vuelve a
            # calcular los campos funcion
            user_input_question_scores.read(['indicator_rel_score'])
            indicator_rel_scores = [x.indicator_rel_score
                                    for x in user_input_question_scores]

            max_indicator_rel_scores = []
            if get_max_indicator_rel_scores:
                # Hago este read exclusviamente porque sin este read vuelve a
                #  calcular los campos funcion
                question_ids = [x.question_id.id
                                for x in user_input_question_scores]
                questions = self.env['survey.question'].search(
                    [('id', 'in', question_ids)])
                questions.read(['max_indicator_rel_score'])

                max_indicator_rel_scores = [
                    x.question_id.max_indicator_rel_score
                    for x in user_input_question_scores]
            return indicator_rel_scores, max_indicator_rel_scores
        period_ids = self.env.context.get('period_ids', False)
        group_ids = self.env.context.get('group_ids', False)
        company_id = self.env.context.get('company_id', False)
        include_diagnosis_eval = self.env.context.get(
            'include_diagnosis_eval', False)
        consider_disabled_person = self.env.context.get(
            'consider_disabled_person', False)

    # Descartamos las dont consider
        domain = [
            '|', ('user_input_id.observation_category_id', '=', False),
            ('user_input_id.observation_category_id.dont_consider', '!=', True)
        ]

    # If not indicator we return False
        if indicator:
            domain.append(('question_id.indicator_id', '=', indicator.id))
        else:
            return False

        if subject:
            domain.append(
                ('user_input_id.group_id.subject_id', '=', subject.id))

    # Append restrictions from context
        # Si no se especifica tener en cuenta personas con discapacidad,
        # las sacamos del analisis
        if not consider_disabled_person:
            domain.append(
                ('user_input_id.partner_id.disabled_person', '!=', True))
        # Si no se especifica tener en cuenta evaluaciones de diagnostico,
        # las sacamos del analisis
        if not include_diagnosis_eval:
            domain.append(('user_input_id.survey_id.is_diagnosis', '=', False))
        if period_ids:
            domain.append(
                ('question_id.survey_id.period_id', 'in', period_ids))
        if company_id:
            domain.append(('user_input_id.company_id', '=', company_id))

    # Calculamos los indicadores segun su tipo
        value = 0.0
        if indicator.calc_type == 'group_max':
            max_group_scores = []
            if not group_ids:
                group_domain = []
                if company_id:
                    group_domain = [('company_id', '=', company_id)]
                group_ids = [x.id
                             for x in self.env['academic.group'].search(
                                 group_domain)]

            for group_id in group_ids:
                group_domain = domain[:]
                group_domain.append(('user_input_id.group_id', '=', group_id))
                group_indicator_rel_scores, group_max_indicator_rel_scores =\
                    get_user_input_scores(
                        self, group_domain, get_max_indicator_rel_scores=False)
                if group_indicator_rel_scores:
                    max_group_indicator_rel_score = max(
                        group_indicator_rel_scores)
                    max_group_scores.append(max_group_indicator_rel_score)
                    if len(max_group_scores) != 0:
                        value = (
                            sum(
                                max_group_scores) / len(
                                    max_group_scores)) * (weight / 100.0)

        elif indicator.calc_type == 'group_average':
            if group_ids:
                domain.append(('user_input_id.group_id', 'in', group_ids))

            indicator_rel_scores, max_indicator_rel_scores = \
                get_user_input_scores(self, domain)
            sum_max_indicator_rel_scores = sum(max_indicator_rel_scores)
            if sum_max_indicator_rel_scores and\
                    sum_max_indicator_rel_scores != 0.0:
                value = (sum(indicator_rel_scores) /
                         sum(max_indicator_rel_scores)) * (weight / 100.0)
        return value
