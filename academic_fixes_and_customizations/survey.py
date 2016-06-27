# -*- encoding: utf-8 -*-
from openerp.osv import osv


class survey_survey(osv.Model):

    _inherit = 'survey.survey'

    def copy(self, cr, uid, id, default=None, context=None):
        new_survey_id = super(survey_survey, self).copy(
            cr, uid, id, default, context)
        question_obj = self.pool['survey.question']
        question_ids = question_obj.search(
            cr, uid, [('page_id.survey_id', '=', new_survey_id)])
        question_obj._get_max_score(cr, uid, question_ids, context)
        return new_survey_id
