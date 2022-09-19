import datetime
from odoo import fields, models, api, _
from odoo.tools.translate import _
from odoo.exceptions import UserError, RedirectWarning, ValidationError
from odoo.tools import float_compare, float_is_zero
from dateutil.relativedelta import relativedelta
import re
import uuid
import urlparse

emails_split = re.compile(r"[;,\n\r]+")
email_validator = re.compile(r"[^@]+@[^@]+\.[^@]+")

class HrAppraisal(models.Model):
    _inherit = "hr.appraisal"
    
    appraisal_by_coach = fields.Boolean(string='Coach')
    appraisal_coach_id = fields.Many2many('hr.employee', 'hr_emp_appraisal_coach_rel', 'hr_appraisal_id')
    appraisal_coach_survey_id = fields.Many2one('survey.survey', string="Coach's Appraisal")
    
    appraisal_by_short = fields.Boolean(string='90 Days Appraisal')
    appraisal_short_id = fields.Many2many('hr.employee', 'hr_emp_appraisal_short_rel', 'hr_appraisal_id')
    appraisal_short_survey_id = fields.Many2one('survey.survey', string="Short Review Survey")

    direct_report_anonymous = fields.Boolean(string='Anonymous')
    colleague_report_anonymous = fields.Boolean(string='Anonymous')

    total_score = fields.Integer(string="Score",compute="_compute_total_answer_score")
    appraisal_completed_date = fields.Char(string="Completed Date",compute="_compute_completed_date")
    date_close = fields.Datetime(string='Appraisal Deadline', required=True)


    @api.multi
    def _compute_total_answer_score(self):
        appraisal_obj = self.env['hr.appraisal'].search([])
        for rec in appraisal_obj:
            answer_obj = self.env['survey.user_input'].search([('appraisal_id' ,'=' , rec.id),('state' , '=' , 'done')])
            ans_score = 0.00
            if answer_obj:
                for score in answer_obj:
                    ans_score += score.quizz_score
            
            rec.total_score = ans_score

    @api.multi
    def _compute_completed_date(self):
        appraisal_obj = self.env['hr.appraisal'].search([])
        for rec in appraisal_obj:
            complete_obj = self.env['survey.user_input'].search([('appraisal_id' ,'=' , rec.id),('state' , '=' , 'done')],order="create_date desc",limit=1)
            if complete_obj.create_date:
                rec.appraisal_completed_date = complete_obj.create_date

    @api.model
    def create(self, vals):
        res = super(HrAppraisal, self).create(vals)
        res.company_id = res.employee_id.company_id.id

        return res
    
    def _prepare_user_input_receivers(self):
        """
        @return: returns a list of tuple (survey, list of employees).
        """
        appraisal_receiver = []
        if self.manager_appraisal and self.manager_ids and self.manager_survey_id:
            appraisal_receiver.append((self.manager_survey_id, self.manager_ids, 'manager'))
        if self.colleagues_appraisal and self.colleagues_ids and self.colleagues_survey_id:
            appraisal_receiver.append((self.colleagues_survey_id, self.colleagues_ids, 'colleagues'))
        if self.collaborators_appraisal and self.collaborators_ids and self.collaborators_survey_id:
            appraisal_receiver.append((self.collaborators_survey_id, self.collaborators_ids, 'collaborators'))
        if self.employee_appraisal and self.employee_survey_id:
            appraisal_receiver.append((self.employee_survey_id, self.employee_id, 'employee'))
        if self.appraisal_by_coach and self.appraisal_coach_id and self.appraisal_coach_survey_id:
            appraisal_receiver.append((self.appraisal_coach_survey_id, self.appraisal_coach_id, 'coach'))
        if self.appraisal_by_short and self.appraisal_short_id and self.appraisal_short_survey_id:
            appraisal_receiver.append((self.appraisal_short_survey_id, self.appraisal_short_id, 'short'))
        return appraisal_receiver

    @api.multi
    def send_appraisal(self):
        ComposeMessage = self.env['survey.mail.compose.message']
        for appraisal in self:
            appraisal_receiver = appraisal._prepare_user_input_receivers()
            for survey, receivers, category in appraisal_receiver:
                for employee in receivers:
                    email = employee.related_partner_id.email or employee.work_email
                    render_template = appraisal.mail_template_id.with_context(email=email, survey=survey, employee=employee, category=category).generate_email([appraisal.id])
                    if category == 'collaborators' and self.direct_report_anonymous == True:
                        public = 'email_public_link'
                    elif category == 'colleagues' and self.colleague_report_anonymous == True:
                        public = 'email_public_link'
                    else:
                        public = 'email_private'
                    values = {
                        'survey_id': survey.id,
                        'public': public,
                        'partner_ids': employee.related_partner_id and [(4, employee.related_partner_id.id)] or False,
                        'multi_email': email,
                        'subject': survey.title,
                        'body': render_template[appraisal.id]['body'],
                        'date_deadline': appraisal.date_close,
                        'model': appraisal._name,
                        'res_id': appraisal.id,
                    }
                    compose_message_wizard = ComposeMessage.with_context(active_id=appraisal.id, active_model=appraisal._name).create(values)
                    compose_message_wizard.send_mail()  # Sends a mail and creates a survey.user_input
            appraisal.message_post(body=_("Appraisal(s) form have been sent"), subtype="hr_appraisal.mt_appraisal_sent")
        return True

    
class HrJob(models.Model):
    _inherit = "hr.job"
    
    short_survey_id = fields.Many2one("survey.survey",string="Short Review Survey")
    long_survey_id = fields.Many2one("survey.survey",string="Long Review Survey" )
    colleague_survey_id = fields.Many2one("survey.survey",string="Colleague Review Survey")
    career_goals_survey = fields.Many2one("survey.survey",string="Career Goals Survey")
    
    
    # @api.onchange('job_template')
    # def on_change_job_template(self):
    #     self.career_goals_survey = self.job_template.career_goals_survey.id
    #     self.short_survey_id = self.job_template.short_survey_id.id
    #     self.long_survey_id = self.job_template.long_survey_id.id
    #     self.colleague_survey_id = self.job_template.colleague_survey_id.id
            
    #     return super(HrJob, self).on_change_job_template()    
    
    
class HrEmployee(models.Model):
    _inherit = "hr.employee"
    
    appraisal_by_coach = fields.Boolean(string='Coach')
    appraisal_coach_id = fields.Many2many('hr.employee', 'emp_appraisal_coach_rel', 'hr_appraisal_id')
    appraisal_coach_survey_id = fields.Many2one('survey.survey', string="Coach's Appraisal")
    
    appraisal_by_short = fields.Boolean(string='90 Days Appraisal')
    appraisal_short_id = fields.Many2many('hr.employee', 'emp_appraisal_short_rel', 'hr_appraisal_id')
    appraisal_short_survey_id = fields.Many2one('survey.survey', string="Short Review Survey")

    auto_send_appraisals = fields.Boolean(string='Auto Send Appraisals')
    direct_report_anonymous = fields.Boolean(string='Anonymous')
    colleague_report_anonymous = fields.Boolean(string='Anonymous')
    
    appraisal_frequency = fields.Integer(string='Appraisal Repeat Every', default=6)
    appraisal_frequency_unit = fields.Selection([('year', 'Year'), ('month', 'Month')], string='Appraisal Frequency', copy=False, default='month')    
    appraisal_date = fields.Datetime(string='Next Appraisal Date', help="The date of the next appraisal is computed by the appraisal plan's dates (first appraisal + periodicity).")

    @api.onchange('appraisal_by_short','parent_id', 'job_id')
    def onchange_appraisal_by_short(self):   
        if self.appraisal_by_short and self.parent_id:
            self.appraisal_short_id = [self.parent_id.id]
        else:
            self.appraisal_short_id = False
                     
        if self.job_id:
            if self.job_id.short_survey_id:
                self.appraisal_short_survey_id=self.job_id.short_survey_id                
             

               
    @api.onchange('appraisal_by_manager', 'parent_id', 'job_id')
    def onchange_manager_appraisal(self):
        if self.appraisal_by_manager and self.parent_id:
            self.appraisal_manager_ids = [self.parent_id.id]
        else:
            self.appraisal_manager_ids = False
            
        if self.job_id:
            if self.job_id.long_survey_id:
                self.appraisal_manager_survey_id=self.job_id.long_survey_id
                
    @api.onchange('appraisal_self', 'job_id')
    def onchange_self_employee(self):
        if self.appraisal_self:
            self.appraisal_employee = self.name
        else:
            self.appraisal_employee = False
            
        if self.job_id:
            if self.job_id.long_survey_id:
                self.appraisal_self_survey_id=self.job_id.long_survey_id
                
    @api.onchange('appraisal_by_collaborators', 'job_id')
    def onchange_subordinates(self):
        if self.appraisal_by_collaborators:
            self.appraisal_collaborators_ids = self.child_ids
        else:
            self.appraisal_collaborators_ids = False
            
        if self.job_id:
            if self.job_id.long_survey_id:
                self.appraisal_collaborators_survey_id=self.job_id.long_survey_id

    @api.onchange('appraisal_by_colleagues', 'job_id')
    def onchange_colleagues(self):
        if self.appraisal_by_colleagues and self.parent_id:

            self.appraisal_colleagues_ids = self.search([('id', '!=', self._origin.id), ('parent_id', '=', self.parent_id.id)])
        else:
            self.appraisal_colleagues_ids = False
            
        if self.job_id:
            if self.job_id.colleague_survey_id:
                self.appraisal_colleagues_survey_id=self.job_id.colleague_survey_id

    @api.onchange('appraisal_by_coach', 'coach_id', 'job_id')
    def onchange_appraisal_by_coach(self):
        if self.appraisal_by_coach and self.coach_id:
            self.appraisal_coach_id = [self.coach_id.id]
        else:
            self.appraisal_coach_id = False
            
        if self.job_id:
            if self.job_id.long_survey_id:
                self.appraisal_coach_survey_id=self.job_id.long_survey_id
                self.appraisal_collaborators_survey_id=self.job_id.long_survey_id
            
    @api.model
    def run_employee_appraisal(self, automatic=False, use_new_cursor=False):  # cronjob
        current_date = datetime.date.today()
#         current_date = datetime.now()
        # Create perdiodic appraisal if appraisal date is in less than a week adn the appraisal for this perdiod has not been created yet:
        for employee in self.search([
            ('periodic_appraisal', '=', True),
#             ('periodic_appraisal_created', '=', False),
            ('appraisal_date', '<=', (datetime.datetime.now() + relativedelta(days=15)).strftime('%Y-%m-%d %H:%M:%S')),
            ('appraisal_date', '>=', (datetime.datetime.now()).strftime('%Y-%m-%d %H:%M:%S'))], limit=50):
            
            vals = {'employee_id': employee.id,
                    'date_close': employee.appraisal_date,
                    
                    'manager_appraisal': employee.appraisal_by_manager,
                    'manager_ids': [(4, manager.id) for manager in employee.appraisal_manager_ids],
                    'manager_survey_id': employee.appraisal_manager_survey_id.id,
                    
                    'colleagues_appraisal': employee.appraisal_by_colleagues,
                    'colleagues_ids': [(4, colleagues.id) for colleagues in employee.appraisal_colleagues_ids],
                    'colleagues_survey_id': employee.appraisal_colleagues_survey_id.id,
                    
                    'employee_appraisal': employee.appraisal_self,
                    'employee_survey_id': employee.appraisal_self_survey_id.id,
                    
                    'collaborators_appraisal': employee.appraisal_by_collaborators,
                    'collaborators_ids': [(4, subordinates.id) for subordinates in employee.appraisal_collaborators_ids],
                    'collaborators_survey_id': employee.appraisal_collaborators_survey_id.id,
                    
                    'appraisal_by_coach': employee.appraisal_by_coach,
                    'appraisal_coach_id': [(4, coaches.id) for coaches in employee.appraisal_coach_id],
                    'appraisal_coach_survey_id': employee.appraisal_coach_survey_id.id,
                    
                    'appraisal_by_short': employee.appraisal_by_short,
                    'appraisal_short_id': [(4, short.id) for short in employee.appraisal_short_id],
                    'appraisal_short_survey_id': employee.appraisal_short_survey_id.id,
                    'direct_report_anonymous':employee.direct_report_anonymous,
                    'colleague_report_anonymous':employee.colleague_report_anonymous
                    }
            hr_app=self.env['hr.appraisal'].create(vals)

            
            if employee.auto_send_appraisals:
                hr_app.with_context({'employee': employee.name,'model':'appraisal'}).button_send_appraisal()
                
            months = employee.appraisal_frequency if employee.appraisal_frequency_unit == 'month' else employee.appraisal_frequency * 12
            employee.appraisal_date=fields.Date.to_string(current_date + relativedelta(months=months))            
            employee.periodic_appraisal_created = False
            self._cr.commit()
        
        # Set the date of the next appraisal to come if the date is passed:
#         for employee in self.search([('periodic_appraisal', '=', True), ('periodic_appraisal_created','=',True),('appraisal_date', '<=', current_date + relativedelta(days=15)),
#             ('appraisal_date', '>=', current_date)]): 
#             months = employee.appraisal_frequency if employee.appraisal_frequency_unit == 'month' else employee.appraisal_frequency * 12
#             employee.write({
#                 'appraisal_date': fields.Date.to_string(current_date + relativedelta(months=months)),
#                 'periodic_appraisal_created': False
#             })

class SurveyMailComposeMessage(models.TransientModel):
    _inherit = 'survey.mail.compose.message'

    token = fields.Char('Identification token',readonly=True,copy=False)

    @api.model
    def default_get(self, fields):
        rec = super(SurveyMailComposeMessage, self).default_get(fields)
        token = self.env.context
        if 'token' in token:
            rec.update({'token':token['token']})

        return rec

    @api.multi
    def send_mail(self, auto_commit=False):
        """ Process the wizard content and proceed with sending the related
            email(s), rendering any template patterns on the fly if needed """

        SurveyUserInput = self.env['survey.user_input']
        Partner = self.env['res.partner']
        Mail = self.env['mail.mail']
        anonymous_group = self.env.ref('portal.group_anonymous', raise_if_not_found=False)

        def create_response_and_send_mail(wizard, token, partner_id, email):
            """ Create one mail by recipients and replace __URL__ by link with identification token """
            #set url
            url = wizard.survey_id.public_url

            url = urlparse.urlparse(url).path[1:]  # dirty hack to avoid incorrect urls

            if token:
                url = url + '/' + token

            # post the message
            values = {
                'model': None,
                'res_id': None,
                'subject': wizard.subject,
                'body': wizard.body.replace("__URL__", url),
                'body_html': wizard.body.replace("__URL__", url),
                'parent_id': None,
                'attachment_ids': wizard.attachment_ids and [(6, 0, wizard.attachment_ids.ids)] or None,
                'email_from': wizard.email_from or None,
                'auto_delete': True,
            }
            if partner_id:
                values['recipient_ids'] = [(4, partner_id)]
            else:
                values['email_to'] = email
            Mail.create(values).send()

        def create_token(wizard, partner_id, email):
            if context.get("survey_resent_token"):
                survey_user_input = SurveyUserInput.search([('survey_id', '=', wizard.survey_id.id),
                    ('state', 'in', ['new', 'skip']), '|', ('partner_id', '=', partner_id),
                    ('email', '=', email)], limit=1)
                if survey_user_input:
                    return survey_user_input.token
            if wizard.public == 'public_link'  :
                return None
            elif wizard.public == 'email_public_link':
                if self.token:
                    return self.token
                else:
                    token = uuid.uuid4().__str__()
                # create response with token
                    survey_user_input = SurveyUserInput.create({
                        'survey_id': wizard.survey_id.id,
                        'deadline': wizard.date_deadline,
                        'date_create': fields.Datetime.now(),
                        'type': 'link',
                        'state': 'new',
                        'token': token})
                    return survey_user_input.token

            else:
                if self.token:
                    return self.token
                else:
                    token = uuid.uuid4().__str__()
                # create response with token
                    survey_user_input = SurveyUserInput.create({
                        'survey_id': wizard.survey_id.id,
                        'deadline': wizard.date_deadline,
                        'date_create': fields.Datetime.now(),
                        'type': 'link',
                        'state': 'new',
                        'token': token,
                        'partner_id': partner_id,
                        'email': email})
                    return survey_user_input.token

        for wizard in self:
            # check if __URL__ is in the text
            if wizard.body.find("__URL__") < 0:
                raise UserError(_("The content of the text don't contain '__URL__'. \
                    __URL__ is automaticaly converted into the special url of the survey."))

            context = self.env.context
            if not wizard.multi_email and not wizard.partner_ids and (context.get('default_partner_ids') or context.get('default_multi_email')):
                wizard.multi_email = context.get('default_multi_email')
                wizard.partner_ids = context.get('default_partner_ids')

            # quick check of email list
            emails_list = []
            if wizard.multi_email:
                emails = set(emails_split.split(wizard.multi_email)) - set(wizard.partner_ids.mapped('email'))
                for email in emails:
                    email = email.strip()
                    if email_validator.match(email):
                        emails_list.append(email)

            # remove public anonymous access
            partner_list = []
            for partner in wizard.partner_ids:
                if not anonymous_group or not partner.user_ids or anonymous_group not in partner.user_ids[0].groups_id:
                    partner_list.append({'id': partner.id, 'email': partner.email})

            if not len(emails_list) and not len(partner_list):                
                if self.env.context.get('model') == 'appraisal':
                    template_id = self.env.ref('vitalpet_appraisal_enhancements.appraisal_failed_to_send_mail').id
                    mail_template = self.env['mail.template'].browse(template_id)

                    if mail_template:
                        mail_template.with_context(employee=self.env.context.get('employee')).send_mail(self.id, force_send=True)

                if wizard.model == 'res.partner' and wizard.res_id:
                    return False                
                raise UserError(_("Please enter at least one valid recipient."))

            for email in emails_list:
                partner = Partner.search([('email', '=', email)], limit=1)
                token = create_token(wizard, partner.id, email)
                create_response_and_send_mail(wizard, token, partner.id, email)

            for partner in partner_list:
                token = create_token(wizard, partner['id'], partner['email'])
                create_response_and_send_mail(wizard, token, partner['id'], partner['email'])

        return {'type': 'ir.actions.act_window_close'}


class SurveyUserInput(models.Model):
    _inherit = "survey.user_input"

    @api.model
    def create(self, vals):        
        
        ctx = self.env.context
        if ctx.get('active_id') and ctx.get('active_model') == 'hr.appraisal':
            vals['appraisal_id'] = ctx.get('active_id')
            
        if 'appraisal_id' in vals:
            vals['deadline'] = self.env['hr.appraisal'].search([('id', '=', vals['appraisal_id'])]).date_close
            
        return super(SurveyUserInput, self).create(vals) 

    @api.multi
    def action_survey_resend(self):
        """ Send again the invitation """
        self.ensure_one()
        local_context = {
            'survey_resent_token': True,
            'default_partner_ids': self.partner_id and [self.partner_id.id] or [],
            'default_multi_email': self.email or "",
            'default_public': 'email_private',
            'token':self.token,
        }
        return self.survey_id.with_context(local_context).action_send_survey()

class Survey(models.Model):
    _inherit = 'survey.survey'


    @api.multi
    def action_send_survey(self):
        """ Open a window to compose an email, pre-filled with the survey message """
        # Ensure that this survey has at least one page with at least one question.
        if not self.page_ids or not [page.question_ids for page in self.page_ids if page.question_ids]:
            raise UserError(_('You cannot send an invitation for a survey that has no questions.'))

        if self.stage_id.closed:
            raise UserError(_("You cannot send invitations for closed surveys."))

        template = self.env.ref('survey.email_template_survey', raise_if_not_found=False)

        local_context = dict(
            self.env.context,
            default_model='survey.survey',
            default_res_id=self.id,
            default_survey_id=self.id,
            default_use_template=bool(template),
            default_template_id=template and template.id or False,
            default_composition_mode='comment'
        )
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'survey.mail.compose.message',
            'target': 'new',
            'context': local_context,
        }

class SendAppraisalLink(models.TransientModel):
    _name = 'send.appraisal.link'

    @api.multi
    def send_mail_again(self):
        for survey_id in self._context.get('active_ids'):
            survey_input_obj = self.env['survey.user_input'].search([('id','=',survey_id)])
            ComposeMessage = self.env['survey.mail.compose.message']
            email = survey_input_obj.email
#             temp_id=self.env['mail.template'].search([('id','=',27)])
            
            
            
            employee=0
            if survey_input_obj.partner_id:
                employee=self.env['hr.employee'].search([('address_home_id','=',survey_input_obj.partner_id.id)])
                partner=self.env['res.partner'].search([('id','=',survey_input_obj.partner_id.id)])
            elif survey_input_obj.email:
                partner_id=self.env['res.partner'].search([('email','=',survey_input_obj.email)])
                if partner_id:
                    for rec in partner_id:
                        if self.env['hr.employee'].search([('address_home_id','=',rec.id)]):
                            employee=self.env['hr.employee'].search([('address_home_id','=',rec.id)])                    
                        else:
                            partner=rec
            else:
                raise UserError(_("Please enter at least one valid recipient."))
            
            email = employee.related_partner_id.email or employee.work_email
            template_id = self.env.ref('vitalpet_appraisal_enhancements.send_appraisal_template_new').id
            mail_template_id = self.env['mail.template'].browse(template_id)
            
            if survey_input_obj.appraisal_id:
                render_template = mail_template_id.with_context(email=email, survey=survey_input_obj.survey_id, employee=employee,partner=partner).generate_email([survey_input_obj.appraisal_id.id])
    #             render_template = temp_id.with_context(email=email, survey=survey_input_obj.survey_id).generate_email([survey_input_obj.appraisal_id.id])
                values = {
                    'survey_id': survey_input_obj.survey_id.id,
                    'public': 'email_private',
                    'partner_ids': survey_input_obj.partner_id and [(4, survey_input_obj.partner_id.id)] or False,
                    'multi_email': email,
                    'subject': survey_input_obj.survey_id.title,
                    'body': render_template[survey_input_obj.appraisal_id.id]['body'],
                    'date_deadline': survey_input_obj.deadline,
                    'model': survey_input_obj.appraisal_id._name,
                    'res_id': survey_input_obj.appraisal_id.id,
                    'token':survey_input_obj.token,
                }
                compose_message_wizard = ComposeMessage.with_context(active_id=survey_input_obj.appraisal_id.id, active_model=survey_input_obj.appraisal_id._name).create(values)
                compose_message_wizard.send_mail()
            
            else:
                raise UserError("This is not an appraisal survey")

        return True
    
    
    
    
    
