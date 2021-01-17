# -*- coding: utf-8 -*-
import json

from odoo import http
from odoo.http import request
from odoo.addons.survey.controllers.main import Survey
from odoo import SUPERUSER_ID

ADDRESS_FIELDS = ['street', 'street2', 'city', 'zip', 'state_id', 'country_id']
NAME_FIELDS = ['first_name', 'middle_name', 'last_name']


class VpsSurvey(Survey):


    def _print_survey(self, survey, token=None):
        res = super()._print_survey(survey, token)
        res.qcontext.update({'SUPERUSER_ID': SUPERUSER_ID})
        return res

    @http.route(['/survey/cprefill/<model("survey.survey"):survey>/<string:token>',
                 '/survey/cprefill/<model("survey.survey"):survey>/<string:token>/<model("survey.page"):page>'],
                type='http', auth='public', website=True)
    def custom_prefill(self, survey, token, page=None, **post):
        UserInputLine = request.env['survey.user_input_line']
        ret = {}

        # Fetch previous answers
        if page:
            domain = [('user_input_id.token', '=', token), ('page_id', '=', page.id)]
        else:
            domain = [('user_input_id.token', '=', token)]

        # Return non empty answers in a JSON compatible format
        previous_answers = UserInputLine.sudo().search(domain)
        for answer in previous_answers:
            if not answer.skipped:
                answer_data = answer.read()[0]
                answer_tag = '%s_%s_%s' % (answer.survey_id.id, answer.page_id.id, answer.question_id.id)
                if answer.answer_type == 'name':
                    for f_name in NAME_FIELDS:
                        ret.update({answer_tag + '_' + f_name: answer_data.get(f_name)})
                elif answer.answer_type == 'm2o':
                    answer_value = int(answer.value_m2o)
                    ret.update({answer_tag: answer_value})
                elif answer.answer_type == 'address':
                    for f_name in ADDRESS_FIELDS:
                        f_val = answer_data.get(f_name)
                        if '_id' in f_name and f_val:
                            f_val = answer_data.get(f_name, [False])[0]
                        ret.update({answer_tag + '_' + f_name: f_val})
                elif answer.answer_type == 'text' and answer.question_id.type == 'textbox':
                    answer_value = answer.value_text
                    ret.update({answer_tag: answer_value})
                elif answer.answer_type == 'binary':
                    answer_value = answer.attachment_id.name
                    ret.update({answer_tag: answer_value})
                elif answer.answer_type == 'sign':
                    answer_value = answer.img_sign
                    ret.update({answer_tag: answer_value.decode('utf-8')})
        return json.dumps(ret)

    # def get_graph_data(self, question, current_filters=None):
    #     current_filters = current_filters if current_filters else []
    #     Survey = request.env['survey.survey']

    #     if question.type == 'm2o':
    #         result = Survey.prepare_result(question, current_filters)['answers']
    #         return json.dumps(result)
    #     if question.type == 'address':
    #         result = Survey.prepare_result(question, current_filters)['answers']
    #         return json.dumps(result)
    #     return super(VpsSurvey, self).get_graph_data(question, current_filters=None)
