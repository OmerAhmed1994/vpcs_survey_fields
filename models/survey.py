# -*- coding: utf-8 -*-
import base64
import re
from odoo import api, fields, models, SUPERUSER_ID, _

ADDRESS_FIELDS = ['street', 'street2', 'city', 'zip', 'state_id', 'country_id']
NAME_FIELDS = ['first_name', 'middle_name', 'last_name']
email_validator = re.compile(r"[^@]+@[^@]+\.[^@]+")


class Survey(models.Model):
    _inherit = 'survey.survey'

    @api.model
    def prepare_result(self, question, current_filters=None):
        current_filters = current_filters if current_filters else []

        # Name
        if question.type == 'name':
            result_summary = []
            for input_line in question.user_input_line_ids:
                if not(current_filters) or input_line.user_input_id.id in current_filters:
                    result_summary.append(input_line)
            return result_summary

        # Binary
        if question.type == 'binary':
            result_summary = []
            for input_line in question.user_input_line_ids:
                if not (current_filters) or input_line.user_input_id.id in current_filters:
                    result_summary.append(input_line)
            return result_summary

        # Sign
        if question.type == 'sign':
            result_summary = []
            for input_line in question.user_input_line_ids:
                if not (current_filters) or input_line.user_input_id.id in current_filters:
                    result_summary.append(input_line)
            return result_summary

        # Address
        if question.type == 'address':
            all_addresses = []
            answers = {}
            for input_line in question.user_input_line_ids:
                _country_id = int(input_line.country_id.id or 0)
                answers.setdefault(_country_id, {
                    'text': input_line.country_id.name or _('Undefined'),
                    'count': 0,
                })
                answers[_country_id]['count'] += 1

                all_addresses.append({
                    'street': input_line.street,
                    'street2': input_line.street2,
                    'city': input_line.city,
                    'state': input_line.state_id.name,
                    'country': input_line.country_id.name,
                    'zip': input_line.zip,
                    'print_url': input_line.user_input_id.print_url,
                    'token': input_line.user_input_id.token,
                })

            return {'answers': list(answers.values()), 'addresses': all_addresses}

        # Relational Field
        if question.type == 'm2o':
            answers = {}
            for input_line in question.user_input_line_ids:
                _m2o_id = int(input_line.value_m2o or 0)
                answers.setdefault(_m2o_id, {
                    'text': input_line.value_text or _('Undefined'),
                    'count': 0,
                })
                answers[_m2o_id]['count'] += 1
            return {'answers': list(answers.values())}

        return super(Survey, self).prepare_result(question, current_filters)


class SurveyQuestion(models.Model):
    _inherit = 'survey.question'

    type = fields.Selection(selection_add=[
        ('name', 'First Name - Middle Name - Last Name'),
        ('m2o', 'Relational Field'),
        ('binary', 'Upload File'),
        ('address', 'Address'),
        ('sign', 'Digital Signature')])
    model_id = fields.Many2one("ir.model", string="Model", domain="[('transient','=',False)]")
    validation_type = fields.Selection(selection=[
        ('url', 'Validation URL'),
        ('phone', 'Validation Phone'),
        ('email', 'Validation E-Mail')],
        string="Validations")
    show_sign = fields.Boolean(string='Show in Result ?')

    # Validate Fields
    @api.multi
    def validate_m2o(self, post, answer_tag):
        errors = {}
        answer = post.get(answer_tag, '').strip()
        if self.constr_mandatory and not answer:
            errors.update({answer_tag: self.constr_error_msg})
        return errors

    @api.multi
    def validate_name(self, post, answer_tag):
        errors = {}
        if self.constr_mandatory:
            if not post.get(answer_tag + '_first_name') or not answer_tag + '_last_name':
                errors.update({answer_tag: self.constr_error_msg})
        return errors

    @api.multi
    def validate_textbox(self, post, answer_tag):
        self.ensure_one()
        errors = {}
        answer = post[answer_tag].strip()
        # Empty answer to mandatory question
        if self.constr_mandatory and not answer:
            errors.update({answer_tag: self.constr_error_msg})

        if answer and self.validation_type == 'email':
            if not email_validator.match(answer):
                errors.update(
                    {answer_tag: _('This answer must be an email address')})

        if answer and self.validation_type == 'url':
            regex = re.compile(
                r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
                r'localhost|'
                r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
                r'(?::\d+)?'
                r'(?:/?|[/?]\S+)$', re.IGNORECASE)
            if re.match(regex, answer) is None:
                errors.update({answer_tag: _("Invalid URL format. (eg. www.example.com)")})

        if answer and self.validation_type == 'phone' and not self.validation_required:
            ALLOWED_PHONE_CHAR = list(map(str, range(1, 9))) + [' ', '+']
            for a in answer:
                if a not in ALLOWED_PHONE_CHAR:
                    errors.update(
                        {answer_tag: _("Invalid Phone Format. (eg. 9876543210)")})
                    break

        # Answer validation (if properly defined)
        # Length of the answer must be in a range
        if answer and self.validation_required:
            if not (self.validation_length_min <= len(
                    answer) <= self.validation_length_max):
                errors.update({answer_tag: self.validation_error_msg})
        return errors

    @api.multi
    def validate_address(self, post, answer_tag):
        errors = {}
        address = []
        for f_name in ADDRESS_FIELDS:
            f_name = answer_tag + '_' + f_name
            if post.get(f_name):
                address.append(post.get(f_name, '').strip())

        if self.constr_mandatory and not address:
            errors.update({answer_tag: self.constr_error_msg})
        return errors

    @api.multi
    def validate_binary(self, post, answer_tag):
        errors = {}
        answer = post.get(answer_tag, '')
        if self.constr_mandatory and not answer:
            errors.update({answer_tag: self.constr_error_msg})
        return errors

    @api.multi
    def validate_sign(self, post, answer_tag):
        errors = {}
        answer = post.get(answer_tag, '')
        if self.constr_mandatory and not answer:
            errors.update({answer_tag: self.constr_error_msg})
        return errors


class SurveyUserInput(models.Model):
    _inherit = 'survey.user_input'

    attachment_ids = fields.Many2many('ir.attachment', string="Attachments")
    attachment_count = fields.Integer("Attachment Count", compute="_compute_attachment_count")

    @api.multi
    def _compute_attachment_count(self):
        for rec in self:
            rec.attachment_count = len(rec.attachment_ids.ids)

    def get_sign(self):
        return self.user_input_line_ids.filtered(lambda line: line.answer_type == 'sign')

class UserInput(models.Model):
    _inherit = 'survey.user_input_line'

    answer_type = fields.Selection(selection_add=[
        ('name', 'First Name - Middle Name - Last Name'),
        ('m2o', 'Relational Field'),
        ('binary', 'Upload File'),
        ('lang', 'Language Selector'),
        ('address', 'Address'),
        ('sign', 'Digital Signature')])
    value_m2o = fields.Integer('ID Selected in Relational Field')
    attachment_id = fields.Many2one('ir.attachment', string='Attachment')

    first_name = fields.Char("First Name")
    middle_name = fields.Char("Middle Name")
    last_name = fields.Char("Last Name")

    img_sign = fields.Binary("Digital Signature")

    street = fields.Char()
    street2 = fields.Char()
    zip = fields.Char(change_default=True)
    city = fields.Char()
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict')
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')
    
    value_address = fields.Char(compute='_compute_value_address')
    
    def _compute_value_address(self):
        for rec in self:
            rec.value_address =  "{}-{}-{}-{}-{}-{}".format(rec.street, rec.street2 , rec.zip , rec.city ,rec.state_id and rec.state_id.name or '',rec.state_id and rec.country_id.name or '',)

    value_name = fields.Char(compute='_compute_value_name')
    
    def _compute_value_name(self):
        for rec in self:
            rec.value_name =  "{} {} {}".format(rec.first_name, rec.middle_name , rec.last_name)

    # Save Fields
    @api.model
    def save_line_m2o(self, user_input_id, question, post, answer_tag):
        vals = {
            'user_input_id': user_input_id,
            'question_id': question.id,
            'page_id': question.page_id.id,
            'survey_id': question.survey_id.id,
            'skipped': False
        }
        if post.get(answer_tag, '').strip() != '':
            record_id = int(post[answer_tag])
            record = self.env[question.model_id.sudo(SUPERUSER_ID).model].sudo(SUPERUSER_ID).browse(record_id)
            vals.update({
                'answer_type': 'm2o',
                'value_m2o': record_id,
                'value_text': record.display_name,
            })
        else:
            vals.update({'answer_type': None, 'skipped': True})
        record = self.search([
            ('user_input_id', '=', user_input_id),
            ('survey_id', '=', question.survey_id.id),
            ('question_id', '=', question.id)], limit=1)
        if record:
            record.sudo(SUPERUSER_ID).write(vals)
        else:
            self.sudo(SUPERUSER_ID).create(vals)
        return True

    @api.model
    def save_line_binary(self, user_input_id, question, post, answer_tag):
        vals = {
            'user_input_id': user_input_id,
            'question_id': question.id,
            'page_id': question.page_id.id,
            'survey_id': question.survey_id.id,
            'skipped': False
        }
        attachment_value = {}
        record = self.search([
            ('user_input_id', '=', user_input_id),
            ('survey_id', '=', question.survey_id.id),
            ('question_id', '=', question.id)], limit=1)

        attachment = self.env['ir.attachment'].sudo(SUPERUSER_ID)
        if post.get(answer_tag, '') != '':
            file = post[answer_tag]
            attachment_value = {
                'name': file.filename,
                'datas': base64.encodestring(file.read()),
                'datas_fname': file.filename,
                'res_model': self._name,
                'res_id': record.id,
                'description': question.question,
            }
            vals.update({'answer_type': 'binary'})
            if attachment_value and not record.attachment_id:
                # Create New Attachment if not Found
                attachment = attachment.sudo(SUPERUSER_ID).create(attachment_value)
                vals.update({'attachment_id': attachment.id})
        else:
            vals.update({'answer_type': None, 'skipped': True})

        if record:
            # Write Record
            if attachment_value and record.attachment_id:
                record.attachment_id.sudo(SUPERUSER_ID).write(attachment_value)
            record.sudo(SUPERUSER_ID).write(vals)
        else:
            # Create New Record
            # Link Created Attachment
            record = self.sudo(SUPERUSER_ID).create(vals)
            if attachment:
                attachment.sudo(SUPERUSER_ID).write({'res_id': record.id})
                main_answer = self.env['survey.user_input'].sudo(SUPERUSER_ID).browse(user_input_id)
                main_answer.attachment_ids = [(4, attachment.id)]
        return True

    @api.model
    def save_line_name(self, user_input_id, question, post, answer_tag):
        vals = {
            'user_input_id': user_input_id,
            'question_id': question.id,
            'survey_id': question.survey_id.id,
            'skipped': False,
        }
        names = {}
        for f_name in NAME_FIELDS:
            names.update({f_name: post.get(answer_tag + '_' + f_name)})
        if names:
            vals.update({'answer_type': 'name'})
            vals.update(names)
        else:
            vals.update({'answer_type': None, 'skipped': True})

        old_uil = self.search([
            ('user_input_id', '=', user_input_id),
            ('survey_id', '=', question.survey_id.id),
            ('question_id', '=', question.id)
        ])
        if old_uil:
            old_uil.sudo(SUPERUSER_ID).write(vals)
        else:
            old_uil.sudo(SUPERUSER_ID).create(vals)
        return True

    @api.model
    def save_line_address(self, user_input_id, question, post, answer_tag):
        vals = {
            'user_input_id': user_input_id,
            'question_id': question.id,
            'survey_id': question.survey_id.id,
            'skipped': False,
        }

        address = {}
        for f_name in ADDRESS_FIELDS:
            address.update({f_name: post.get(answer_tag + '_' + f_name)})
        if address:
            address.update({'answer_type': 'address'})
            vals.update(address)
        else:
            vals.update({'answer_type': None, 'skipped': True})

        old_uil = self.search([
            ('user_input_id', '=', user_input_id),
            ('survey_id', '=', question.survey_id.id),
            ('question_id', '=', question.id)
        ])
        if old_uil:
            old_uil.sudo(SUPERUSER_ID).write(vals)
        else:
            old_uil.sudo(SUPERUSER_ID).create(vals)
        return True

    @api.model
    def save_line_sign(self, user_input_id, question, post, answer_tag):
        vals = {
            'user_input_id': user_input_id,
            'question_id': question.id,
            'page_id': question.page_id.id,
            'survey_id': question.survey_id.id,
            'skipped': False
        }

        if answer_tag in post and post[answer_tag].strip():
            img_data = post[answer_tag]
            vals.update({'answer_type': 'sign', 'img_sign': img_data})
        else:
            vals.update({'answer_type': None, 'skipped': True})

        old_uil = self.search([
            ('user_input_id', '=', user_input_id),
            ('survey_id', '=', question.survey_id.id),
            ('question_id', '=', question.id)
        ])
        if old_uil:
            old_uil.sudo(SUPERUSER_ID).sudo(SUPERUSER_ID).write(vals)
        else:
            old_uil.sudo(SUPERUSER_ID).sudo(SUPERUSER_ID).create(vals)
        return True

    