# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import http
from odoo.http import request
import xlsxwriter
from lxml import etree
import base64
import time
import datetime
import csv
import logging
from odoo.tools.yaml_tag import Record
import re
from urlparse import urljoin
from odoo.addons.website.models.website import slug
logger = logging.getLogger(__name__)

from odoo import models, fields, api , _
from odoo.exceptions import ValidationError,UserError
from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta
import uuid


class ProductionType(models.Model):
    _inherit = "hr.job.seniority.title"

    documents_template_ids = fields.Many2many('signature.request.template',string="Detailed Job Description")

class Applicant(models.Model):
    _inherit = "hr.applicant"

    emergency_contact_name = fields.Char("Name")
    emergency_contact_phone = fields.Char("Phone")
    emergency_contact_relationship = fields.Char("Relationship")
    # hire_date = fields.Date("Hire Date")
    offer_send_date = fields.Date("Offer Send Date")
    offer_expiration_date = fields.Date("Offer Expiration Date")
    
    @api.multi
    def write(self, vals):

        # if vals.get('job_id'):
        #     job_obj = self.env['hr.job'].search([('id' , '=' , vals.get('job_id'))])
        #     if job_obj.job_type:
        #         vals['contract_type_id'] = job_obj.job_type.id

        if vals.get('email_from'):
            match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', vals.get('email_from'))
            if match == None:
                raise ValidationError('Please enter a valid email or check the spaces before and after the email id')

            # else:
            #     return super(Applicant, self).write(vals)

        stage_obj = self.env['hr.recruitment.stage'].search([('name', '=', 'Onboarding')])        
        if vals.get('stage_id') == stage_obj.id:
            onboarding_id=self.env['hr.employee.onboarding'].search([('applicant_id', '=', self.id)]) 
            if not onboarding_id:
                onboard_id = self.env['hr.employee.onboarding'].create({
                    'name' : self.name or False,
                    'first_name' : self.partner_name or False,
                    'middle_name' : self.middle_name or False,
                    'last_name' : self.last_name or False,
                    'mail' : self.email_from or False,
                    'phone' : self.partner_phone or False,
                    'responsible' : self.user_id.id or False,
                    'applied_job' : self.job_id.id or False,
                    'company' : self.company_id.id or False,
                    'job_seniority_title' : self.seniority_title_id.id or False,
                    'applicant_id' : self.id,
                    'state_id' : 'offer',
                    'expected_salary' : self.salary_expected,
                    'proposed_salary' : self.salary_proposed,
                    'pay_rate' : self.salary_proposed,
                    'available' : self.availability,
                    'priority' : self.priority,
                    'emergency_contact_name' : self.emergency_contact_name,
                    'emergency_contact_phone' : self.emergency_contact_phone,
                    'emergency_contact_relationship' : self.emergency_contact_relationship,
                    'contract_type' : self.contract_type_id.id,
                    # 'notes' : self.description or '',
                    })
                for line in self.academic_experience_ids:
                    for values in line:
                        self.env['academic.experience'].create({
                            'academic_experience':values.academics,
                            'institute':values.institute,
                            'diploma':values.diploma,
                            'field_of_study':values.field_of_study,
                            'start_date':values.start_date,
                            'end_date':values.end_date,
                            'academic_experience_id':onboard_id.id,
                            }) 
                for line in self.professional_experience_ids:
                    for values in line:
                        self.env['professional.experience'].create({
                            'position':values.position,
                            'employer':values.employer,
                            'start_date':values.start_date,
                            'end_date':values.end_date,
                            'professional_experience_id':onboard_id.id,
                            }) 
                for line in self.certification_ids:
                    for values in line:
                        self.env['certification.details'].create({
                            'certifications':values.certifications,
                            'certificate_code':values.certification_number,
                            'issued_by':values.issued_by,
                            'professional_license':values.professional_license,
                            'state_issued_id':values.state_issued_id.id,
                            'start_date':values.start_date,
                            'end_date':values.end_date,
                            'certification_id':onboard_id.id,
                            }) 


        offer_stage_obj = self.env['hr.recruitment.stage'].search([('name', '=', 'Offer Letter')])        
        if vals.get('stage_id') == offer_stage_obj.id:    
            self.offer_send_date = datetime.now().date()
            self.offer_expiration_date = datetime.now().date() + timedelta(days=7)
            # template_id = self.job_id.job_template.email_template_id
            # if template_id:
                
            #     template_id.send_mail(self.id, force_send=True)

            # else:
            #     raise ValidationError(_('Please configure offer letter email template for the applied job template'))
            
        res = super(Applicant, self).write(vals)
        return res

    @api.model
    def create(self, vals):

        # if vals.get('job_id'):
        #     job_obj = self.env['hr.job'].search([('id' , '=' , vals.get('job_id'))])
        #     if job_obj.job_type:
        #         vals['contract_type_id'] = job_obj.job_type.id
                # self.contract_type_id = job_obj.job_type.id

        if vals.get('email_from'):
            match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', vals.get('email_from'))
            if match == None:
                raise ValidationError('Please enter a valid email or check the spaces before and after the email id')

            # else:
            #     return super(Applicant, self).create(vals)
            
        ctx = self.env.context
        if ctx.get('direct_hire') == 'Onboarding':
            vals['stage_id'] = self.env['hr.recruitment.stage'].search([('name', '=', 'Onboarding')]).id
            res = super(Applicant, self).create(vals)
            onboarding_id=self.env['hr.employee.onboarding'].search([('applicant_id', '=', res.id)]) 
            if not onboarding_id:
                onboard_id = self.env['hr.employee.onboarding'].create({
                    'name' : res.name or False,
                    'first_name' : res.partner_name or False,
                    'middle_name' : res.middle_name or False,
                    'last_name' : res.last_name or False,
                    'mail' : res.email_from or False,
                    'phone' : res.partner_phone or False,
                    'responsible' : res.user_id.id or False,
                    'applied_job' : res.job_id.id or False,
                    'company' : res.company_id.id or False,
                    'job_seniority_title' : res.seniority_title_id.id or False,
                    'applicant_id' : res.id,
                    'state_id' : 'offer',
                    'expected_salary' : res.salary_expected,
                    'proposed_salary' : res.salary_proposed,
                    'pay_rate' : res.salary_proposed,
                    'available' : res.availability,
                    'priority' : res.priority,
                    'emergency_contact_name' : res.emergency_contact_name,
                    'emergency_contact_phone' : res.emergency_contact_phone,
                    'emergency_contact_relationship' : res.emergency_contact_relationship,
                    'contract_type' : res.contract_type_id.id,
                    # 'notes' : res.description or '',
                    })
                for line in res.academic_experience_ids:
                    for values in line:
                        self.env['academic.experience'].create({
                            'academic_experience':values.academics,
                            'institute':values.institute,
                            'diploma':values.diploma,
                            'field_of_study':values.field_of_study,
                            'start_date':values.start_date,
                            'end_date':values.end_date,
                            'academic_experience_id':onboard_id.id,
                            }) 
                for line in res.professional_experience_ids:
                    for values in line:
                        self.env['professional.experience'].create({
                            'position':values.position,
                            'employer':values.employer,
                            'start_date':values.start_date,
                            'end_date':values.end_date,
                            'professional_experience_id':onboard_id.id,
                            }) 
                for line in res.certification_ids:
                    for values in line:
                        self.env['certification.details'].create({
                            'certifications':values.certifications,
                            'certificate_code':values.certification_number,
                            'issued_by':values.issued_by,
                            'professional_license':values.professional_license,
                            'state_issued_id':values.state_issued_id.id,
                            'start_date':values.start_date,
                            'end_date':values.end_date,
                            'certification_id':onboard_id.id,
                            }) 
        else:
            res = super(Applicant, self).create(vals)
        return res

    def unlink(self):
        for rec in self:
            applicant_obj = self.env['hr.employee.onboarding'].search([('applicant_id' , '=' , rec.id)])
            if applicant_obj:
                raise ValidationError(_('You can not delete the onboarded applicant record'))
            else:
                return super(Applicant, self).unlink()

    @api.onchange('job_id')
    def onchange_contract_type(self):
        self.contract_type_id = self.job_id.job_type

    @api.onchange('email_from')
    def validate_mail(self):
        if self.email_from:
            match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', self.email_from)
            if match == None:
                raise ValidationError('Please enter a valid email or check the spaces before and after the email id')
    
    @api.multi
    def onboarding_to_hired(self):
        stage_obj = self.env['hr.recruitment.stage'].search([('name', '=', 'Onboarding')])
        stage_change_obj = self.env['hr.recruitment.stage'].search([('name', '=', 'Hired')])

        applicant_obj = self.env['hr.applicant'].search([('stage_id' , '=' , stage_obj.id)])

        for rec in applicant_obj:
            onboarding_obj = self.env['hr.employee.onboarding'].search([('applicant_id' , '=' , rec.id)])

            if onboarding_obj:
                rec.stage_id = stage_change_obj.id

class SurveyUserInput(models.Model):
    _inherit = "survey.user_input"

    onboarding_id = fields.Many2one('hr.employee.onboarding', string='Onboarding')

    @api.model
    def create(self, vals):
        ctx = self.env.context
        if ctx.get('active_id') and ctx.get('active_model') == 'hr.employee.onboarding':
            vals['onboarding_id'] = ctx.get('active_id')
        return super(SurveyUserInput, self).create(vals)

    @api.multi
    def write(self,vals):
        if vals.get('state'):
            if vals['state']=='done':
                if self.onboarding_id:
                    self.onboarding_id.benefits_states = 'to_approve'

        return super(SurveyUserInput, self).write(vals)
    

class SignatureRequestItem(models.Model):
    _inherit = "signature.request.item"


    @api.multi
    def send_signature_accesses(self, subject=None, message=None):
        base_context = self.env.context
        if not self.env.context.get('template_ids') and self.env.context.get('status') != 'launch':
            template_id = self.env.ref('website_sign.website_sign_mail_template').id
        elif self.env.context.get('status') == 'launch':
            template_id = self.env.ref('vitalpet_onboarding.onboarding_launch_pack').id
        else:
            template_id = self.env.ref('vitalpet_onboarding.multiple_documents_sign').id
        mail_template = self.env['mail.template'].browse(template_id)

        email_from_usr = self[0].create_uid.partner_id.name
        email_from_mail = self[0].create_uid.partner_id.email
        email_from = "%(email_from_usr)s <%(email_from_mail)s>" % {'email_from_usr': email_from_usr, 'email_from_mail': email_from_mail}
        link_list = []
        if len(self) != 1:
        # for sign_link in self:
            if self.env.context.get('template_ids'):
                link = "sign/document/%(request_id)s/%(access_token)s" % {'request_id': self[0].signature_request_id.id, 'access_token': self[0].access_token}
                link_list.append(link)

            else:
                link_list = "sign/document/%(request_id)s/%(access_token)s" % {'request_id': self[0].signature_request_id.id, 'access_token': self[0].access_token}
                
        else:
            if self.env.context.get('template_ids'):
                link = "sign/document/%(request_id)s/%(access_token)s" % {'request_id': self.signature_request_id.id, 'access_token': self.access_token}
                link_list.append(link)

            else:
                link_list = "sign/document/%(request_id)s/%(access_token)s" % {'request_id': self.signature_request_id.id, 'access_token': self.access_token}
        if self.env.context.get('check_id') == 'welcome':
            request.session['doc_url_list']+= ''.join(link_list)
            request.session['doc_url_list']+= '---'  
            link_list_pop = request.session['doc_url_list'].split('---')
            final_link_list =  link_list_pop[:len(link_list_pop)-1]
        if self.env.context.get('check_id') == 'welcome':
            for signer in self:
                if not signer.partner_id:
                    continue
                template = mail_template.sudo().with_context(base_context,
                    lang = signer.partner_id.lang,
                    template_type = "request",
                    email_from_usr = email_from_usr,
                    email_from_mail = email_from_mail,
                    email_from = email_from,
                    email_to = signer.partner_id.email,
                    link = final_link_list,
                    survey_link_list = self.env.context.get('benefits_link_list'),
                    employee_name = self.env.context.get('employee_name'),
                    company_name = self.env.context.get('company_name'),
                    subject = subject or ("Signature request - " + signer.signature_request_id.reference),
                    msgbody = (message or "").replace("\n", "<br/>")
                )
            if self.env.context.get('mail_send') == 1:
                template.send_mail(signer.signature_request_id.id, force_send=True)

        elif self.env.context.get('status') == 'launch':
            for signer in self:
                if not signer.partner_id:
                    continue
                template = mail_template.sudo().with_context(base_context,
                    partner_name = signer.partner_id.name, 
                    lang = signer.partner_id.lang,
                    template_type = "request",
                    email_from_usr = email_from_usr,
                    email_from_mail = email_from_mail,
                    email_from = email_from,
                    email_to = signer.partner_id.email,
                    link = "sign/document/%(request_id)s/%(access_token)s" % {'request_id': signer.signature_request_id.id, 'access_token': signer.access_token},
                    subject = subject or ("Signature request - " + signer.signature_request_id.reference),
                    msgbody = (message or "").replace("\n", "<br/>")
                )
                template.send_mail(signer.signature_request_id.id, force_send=True)

        else:
            for signer in self:
                if not signer.partner_id:
                    continue
                template = mail_template.sudo().with_context(base_context,
                    lang = signer.partner_id.lang,
                    template_type = "request",
                    email_from_usr = email_from_usr,
                    email_from_mail = email_from_mail,
                    email_from = email_from,
                    email_to = signer.partner_id.email,
                    link = "sign/document/%(request_id)s/%(access_token)s" % {'request_id': signer.signature_request_id.id, 'access_token': signer.access_token},
                    subject = subject or ("Signature request - " + signer.signature_request_id.reference),
                    msgbody = (message or "").replace("\n", "<br/>")
                )
                template.send_mail(signer.signature_request_id.id, force_send=True)

class HrOnboarding(models.Model):
    _name = "hr.employee.onboarding"
    _inherit = ['mail.thread']
    

    @api.multi
    def welcome_mail_send_all(self,form_id,welcome_email_info_vals,survey_welcome_email_info_vals):
        if welcome_email_info_vals:
            for rec in welcome_email_info_vals:
                if int(rec['welcome_applicant_tree_id'])>0:
                    welcome_email_info_obj = self.env['welcome.mail'].search([('id' , '=' , rec['welcome_applicant_tree_id'])])
                    if (rec['form_welcome_applicant_documents']):
                        welcome_email_info_obj.document = rec['form_welcome_applicant_documents']
                    if (rec['welcome_applicant_link']):
                        welcome_email_info_obj.doc_link = rec['welcome_applicant_link']
                    if (rec['welcome_applicant_status']):
                        welcome_email_info_obj.status_id = rec['welcome_applicant_status']
                    if (rec['welcome_applicant_date_sent']):
                        welcome_email_info_obj.date_sent = rec['welcome_applicant_date_sent']

                    if welcome_email_info_obj.status_id != 'canceled':
                        if (rec['welcome_applicant_expiration']):
                            welcome_email_info_obj.expiration = rec['welcome_applicant_expiration']  
                    elif welcome_email_info_obj.status_id =='canceled' and str(welcome_email_info_obj.expiration) != rec['welcome_applicant_expiration']:
                        if (rec['welcome_applicant_expiration']):
                            welcome_email_info_obj.expiration = rec['welcome_applicant_expiration']  
                    else:
                        welcome_email_info_obj.expiration = ''
                         
                else:
                    if (rec['form_welcome_applicant_documents'] or rec['welcome_applicant_link'] or rec['welcome_applicant_status']):
                        welcome_email_info_obj = self.env['welcome.mail'].create({
                            'document' : rec['form_welcome_applicant_documents'],
                            'doc_link' : rec['welcome_applicant_link'],
                            'status_id' : rec['welcome_applicant_status'],
                            'date_sent' : rec['welcome_applicant_date_sent'] or False,
                            'expiration' : rec['welcome_applicant_expiration'] or False,
                            'welcome_mail_id':form_id
                            })
                # if rec.get('welcome_applicant_expiration'):
                #     form_obj = self.env['welcome.mail'].search([('id' , '=' , int(rec.get('welcome_applicant_tree_id')))])
                #     if form_obj:
                #         form_obj.expiration = rec.get('welcome_applicant_expiration')
                # else:
                #     form_obj = self.env['welcome.mail'].search([('id' , '=' , int(rec.get('welcome_applicant_tree_id')))])
                #     if form_obj:
                #         form_obj.expiration = ''
        if survey_welcome_email_info_vals:
            for rec in survey_welcome_email_info_vals:
                if int(rec['welcome_survey_tree_id']) > 0:
                    survey_welcome_email_info_obj = self.env['welcome.survey'].search([('id' , '=' , rec['welcome_survey_tree_id'])])
                    if (rec['form_welcome_survey']):
                        survey_welcome_email_info_obj.survey = rec['form_welcome_survey']
                    if (rec['welcome_survey_link']):
                        survey_welcome_email_info_obj.survey_link = rec['welcome_survey_link']
                    if (rec['welcome_survey_status']):
                        survey_welcome_email_info_obj.status_id = rec['welcome_survey_status']
                    if (rec['welcome_survey_date_sent']):
                        survey_welcome_email_info_obj.date_sent = rec['welcome_survey_date_sent']
                    if (rec['welcome_survey_expiration']):
                        survey_welcome_email_info_obj.expiration = rec['welcome_survey_expiration']  

                else:
                    if (rec['form_welcome_survey'] or rec['welcome_survey_link'] or rec['welcome_survey_status']):
                        survey_welcome_email_info_obj = self.env['welcome.survey'].create({
                            'survey' : rec['form_welcome_survey'],
                            'survey_link' : rec['welcome_survey_link'],
                            'status_id' : rec['welcome_survey_status'],
                            'date_sent' : rec['welcome_survey_date_sent'] or False,
                            'expiration' : rec['welcome_survey_expiration'] or False,
                            'welcome_benefit_survey_id':form_id
                            })

                # if rec.get('welcome_survey_expiration'):
                #     form_obj = self.env['welcome.survey'].search([('id' , '=' , int(rec.get('welcome_survey_tree_id')))])
                #     if form_obj:
                #         form_obj.expiration = rec.get('welcome_survey_expiration')
                # else:
                #     form_obj = self.env['welcome.survey'].search([('id' , '=' , int(rec.get('welcome_survey_tree_id')))])
                #     if form_obj:
                #         form_obj.expiration = ''
        if form_id:
            # doc_dict=''
            employee_obj = self.env['hr.employee.onboarding'].browse(int(form_id))
            if employee_obj.mail:
                survey_list = []
                survey_link = []
                for vals in employee_obj.welcome_benefit_survey_ids:
                    token = uuid.uuid4().__str__()
                    if not employee_obj.survey_id_ref:
                        survey_id_obj = self.env['survey.user_input'].create({
                        'survey_id': vals.survey.id,
                        'date_create': fields.Datetime.now(),
                        'type': 'link',
                        'state': 'new',
                        'token': token,
                        'partner_id': employee_obj.partner_id.id,
                        'email': employee_obj.mail,
                        'onboarding_id' : form_id})

                        survey_list.append(survey_id_obj.id)

                        self.env.cr.execute("select survey_id,token from survey_user_input where onboarding_id="+form_id)
                        results = self.env.cr.dictfetchall()

                        for record in results:
                            survey = self.env['survey.survey'].search([('id' , '=' , record['survey_id'])])

                            base_url = '/' if self.env.context.get('relative_url') else self.env['ir.config_parameter'].get_param('web.base.url')
                            public_url = urljoin(base_url, "survey/start/%s" % (slug(survey)))
                            benifits_survey_info = public_url+"/"+record['token'] 

                            survey_link.append(benifits_survey_info)

                        employee_obj.welcome_benefit_survey_ids.request_id = survey_id_obj.id
                        employee_obj.welcome_benefit_survey_ids.date_sent = fields.datetime.now()
                        employee_obj.welcome_benefit_survey_ids.survey_link = benifits_survey_info 
                        employee_obj.benefits_states = 'to_approve'


                    else:
                        self.env.cr.execute("select survey_id,token from survey_user_input where onboarding_id="+form_id)
                        results = self.env.cr.dictfetchall()

                        for record in results:
                            survey = self.env['survey.survey'].search([('id' , '=' , record['survey_id'])])

                            base_url = '/' if self.env.context.get('relative_url') else self.env['ir.config_parameter'].get_param('web.base.url')
                            public_url = urljoin(base_url, "survey/start/%s" % (slug(survey)))
                            benifits_survey_info = public_url+"/"+record['token'] 

                            survey_link.append(benifits_survey_info)

                        
                employee_obj.survey_id_ref = survey_list

                if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", employee_obj.mail) != None:
                    welcome_mail_length = len(employee_obj.welcome_mail_ids)
                    i = 0
                    request.session['doc_url_list'] = ''
                    for d_line in employee_obj.welcome_mail_ids:    
                        i+=1     
                        if i == welcome_mail_length:
                            template_ids =[]
                            roles = []
                            template_id = self.env['signature.request.template'].search([('id', '=', d_line.document.id)])
                            
                            if template_id:
                                signature_template = self.env["signature.request.template"].search([("id", "=", template_id.id)])
                                reference = signature_template.attachment_id.name
                                request_item = self.env["signature.item"].search([('template_id', '=', template_id.id)])
                               
                                for req_item in request_item:
                                    if req_item.responsible_id.id not in roles:
                                        roles.append(req_item.responsible_id.id)
                                
                                template_ids.append((template_id.id, reference))
                            applicant_obj = self.env['hr.applicant'].search([('id' , '=' , employee_obj.applicant_id)])
                            if applicant_obj.partner_id:
                                if template_ids:
                                    signers = []
                                    signer = {}
                                    for role in roles:
                                        signer={
                                        'partner_id' : applicant_obj.partner_id.id,
                                        'role': role
                                        }
                                        signers.append(signer)
                                    req_id = self.env["signature.request"].with_context({'template_ids': template_ids, 'reference': template_ids,'benefits_link_list' : survey_link,'length':i, 'mail_send': 1,'employee_name' : employee_obj.new_employee_id.name,'company_name' : employee_obj.new_employee_id.company_id.name,'check_id' : 'welcome'}).initialize_new(template_ids[0][0], signers, followers=[], reference=reference, subject="", message="", send=True)
                            else:
                                pay_term = self.env['account.payment.term'].search([('name', '=', 'Immediate Payment')]).id
                                pay_mode = self.env['account.payment.mode'].search([('name', '=', 'Manual Payment')]).id
                                rel_user = self.env['res.partner'].create({
                                    'firstname' : employee_obj.first_name or False,
                                    'middlename' : employee_obj.middle_name or False,
                                    'lastname' : employee_obj.last_name or False,
                                    'email' : employee_obj.mail or False,
                                    'company_id' : employee_obj.company.id or False,
                                    'property_supplier_payment_term_id' : pay_term or False,
                                    'supplier_payment_mode_id' : pay_mode or False,
                                    'state_id' : employee_obj.state.id or False,
                                    'city' : employee_obj.city or False,
                                    'street' : employee_obj.street or False,
                                    'street2' : employee_obj.street2 or False,
                                    'country_id' : employee_obj.country.id or False,
                                    'zip' : employee_obj.zip or False,
                                    })
                                applicant_obj.partner_id = rel_user
                                employee_obj.partner_id = rel_user
                                if template_ids:
                                    signers = []
                                    signer = {}
                                    for role in roles:
                                        signer={
                                        'partner_id' : rel_user.id,
                                        'role': role
                                        }
                                        signers.append(signer)
                                    req_id = self.env["signature.request"].with_context({'template_ids': template_ids, 'reference': template_ids,'benefits_link_list' : survey_link,'length':i, 'mail_send': 1,'employee_name' : employee_obj.new_employee_id.name,'company_name' : employee_obj.new_employee_id.company_id.name,'check_id' : 'welcome'}).initialize_new(template_ids[0][0], signers, followers=[], reference=reference, subject="", message="", send=True)
                        else:
                            template_ids =[]
                            roles = []
                            template_id = self.env['signature.request.template'].search([('id', '=', d_line.document.id)])
                            
                            if template_id:
                                signature_template = self.env["signature.request.template"].search([("id", "=", template_id.id)])
                                reference = signature_template.attachment_id.name
                                request_item = self.env["signature.item"].search([('template_id', '=', template_id.id)])
                               
                                for req_item in request_item:
                                    if req_item.responsible_id.id not in roles:
                                        roles.append(req_item.responsible_id.id)
                                
                                template_ids.append((template_id.id, reference))
                            applicant_obj = self.env['hr.applicant'].search([('id' , '=' , employee_obj.applicant_id)])
                            if applicant_obj.partner_id:
                                if template_ids:
                                    signers = []
                                    signer = {}
                                    for role in roles:
                                        signer={
                                        'partner_id' : applicant_obj.partner_id.id,
                                        'role': role
                                        }
                                        signers.append(signer)
                                    req_id = self.env["signature.request"].with_context({'template_ids': template_ids, 'reference': template_ids,'benefits_link_list' : survey_link, 'mail_send': 0,'check_id' : 'welcome'}).initialize_new(template_ids[0][0], signers, followers=[], reference=reference, subject="", message="", send=True)

                            else:
                                pay_term = self.env['account.payment.term'].search([('name', '=', 'Immediate Payment')]).id
                                pay_mode = self.env['account.payment.mode'].search([('name', '=', 'Manual Payment')]).id
                                rel_user = self.env['res.partner'].create({
                                    'firstname' : employee_obj.first_name or False,
                                    'middlename' : employee_obj.middle_name or False,
                                    'lastname' : employee_obj.last_name or False,
                                    'email' : employee_obj.mail or False,
                                    'company_id' : employee_obj.company.id or False,
                                    'property_supplier_payment_term_id' : pay_term or False,
                                    'supplier_payment_mode_id' : pay_mode or False,
                                    'state_id' : employee_obj.state.id or False,
                                    'city' : employee_obj.city or False,
                                    'street' : employee_obj.street or False,
                                    'street2' : employee_obj.street2 or False,
                                    'country_id' : employee_obj.country.id or False,
                                    'zip' : employee_obj.zip or False,
                                    })
                                applicant_obj.partner_id = rel_user
                                employee_obj.partner_id = rel_user
                                if template_ids:
                                    signers = []
                                    signer = {}
                                    for role in roles:
                                        signer={
                                        'partner_id' : rel_user.id,
                                        'role': role
                                        }
                                        signers.append(signer)
                                    req_id = self.env["signature.request"].with_context({'template_ids': template_ids, 'reference': template_ids,'benefits_link_list' : survey_link, 'mail_send': 0,'check_id' : 'welcome'}).initialize_new(template_ids[0][0], signers, followers=[], reference=reference, subject="", message="", send=True)
                            
                        d_line.request_id = req_id['id']
                        d_line.date_sent = fields.datetime.now()
                        d_line.doc_link = self.env['ir.config_parameter'].search([('key','=','web.base.url')]).value+'/sign/document/'+str(req_id['id'])+'/'+str(d_line.request_id.access_token)
                

                else:
                    raise ValidationError("Please enter a valid email or check the spaces before and after the email id")            


    name = fields.Char("Name",track_visibility='onchange')
    first_name = fields.Char("First Name",track_visibility='onchange')
    middle_name = fields.Char("Middle Name",track_visibility='onchange')
    last_name = fields.Char("Last Name",track_visibility='onchange')
    first_name_alias = fields.Char("First Name",track_visibility='onchange')
    middle_name_alias = fields.Char("Middle Name",track_visibility='onchange')
    last_name_alias = fields.Char("Last Name",track_visibility='onchange')
    phone = fields.Char("Phone",track_visibility='onchange')
    mail = fields.Char("Email",track_visibility='onchange')
    applied_job = fields.Many2one('hr.job', string="Applied Job",track_visibility='onchange')
    applicant_id = fields.Char("Applicant ID", readonly=True,track_visibility='onchange')
    start_date = fields.Date("Start Date", default=fields.datetime.now(),track_visibility='onchange')
    company = fields.Many2one('res.company', string="Company",track_visibility='onchange')
    responsible = fields.Many2one('res.users', string="Responsible",track_visibility='onchange')
    emp_status = fields.Many2one('hr.contract.type', string="Employee Status",track_visibility='onchange')
    expected_salary = fields.Char("Expected Salary",track_visibility='onchange')
    proposed_salary = fields.Char("Proposed Salary",track_visibility='onchange')
    available = fields.Date("Availability",track_visibility='onchange')
    nationality = fields.Many2one('res.country',string="Nationality",track_visibility='onchange')
    gender = fields.Selection([('male', 'Male'), 
                               ('female', 'Female')], string="Gender",track_visibility='onchange')
    id_number = fields.Char("Identification Number",track_visibility='onchange')
    priority = fields.Selection([('0', 'Normal'), 
                               ('1', 'Good'), 
                               ('2', 'Very Good'), 
                               ('3', 'Excellent')], "Appreciation", default='0')
    marital_status = fields.Selection([('single', 'Single'), 
                                       ('married', 'Married'),
                                       ('widower', 'Widower'),
                                       ('divorced', 'Divorced')], string="Marital Status",track_visibility='onchange')
    filing_staus = fields.Selection([('single', 'Single'), 
                                    ('married', 'Married'),
                                    ('widower', 'Married, but withhold at higher Single rate'),], string="Filing Status")
    street = fields.Char("Home Address",track_visibility='onchange')
    street2 = fields.Char(track_visibility='onchange')
    city = fields.Char(track_visibility='onchange')
    state = fields.Many2one("res.country.state", domain="[('country_id','=',country)]",string='State',track_visibility='onchange', ondelete='restrict')
    country = fields.Many2one('res.country', string='Country',track_visibility='onchange', ondelete='restrict')
    zip = fields.Char(track_visibility='onchange')
    no_of_children = fields.Char("Number of Allowances",track_visibility='onchange')
    passport_number = fields.Char("Passport Number",track_visibility='onchange')
    dl_number = fields.Char("Driving License Number",track_visibility='onchange')
    dob = fields.Date("Date of Birth",track_visibility='onchange')
    birth_country = fields.Many2one('res.country', string="Birth Country",track_visibility='onchange')
    place_of_birth = fields.Char("Place of Birth",track_visibility='onchange')
    age = fields.Integer("Age",track_visibility='onchange')
    emp_start_date = fields.Date("Start Date",track_visibility='onchange')
    scheduled_hours = fields.Integer("Scheduled Hours",track_visibility='onchange')
    benifits_seniority_date = fields.Date("Benefits Seniority Date",track_visibility='onchange')
    pay_rate = fields.Float("Pay Rate",track_visibility='onchange')
    job_seniority_title = fields.Many2one('hr.job.seniority.title', string="Job Seniority Title",track_visibility='onchange')
    state_id = fields.Selection([('offer', 'Offer Accepted'),
                                 ('background', 'Background Check'),
                                 ('to_approve', 'To Approve'),
                                 ('hire', 'Hire'),
                                 ('benefits', 'Benefits'),
                                 ('contract', 'Contract'),
                                 ('complete', 'Complete'),
                                 ('reject', 'Rejected')], string="Status",default='offer',track_visibility='onchange')
    benefits_states = fields.Selection([('not_eligible','Not Eligible'),
                                    ('pending','Pending'),
                                    ('to_approve','To Approve'),
                                    ('send','Send to Provider'),
                                    ('enrolled','Enrolled')],string="Benefit Status")
    substate_id = fields.Selection([('started', 'GetStarted0'),
                                 ('personal', 'PersonalInformation1'),
                                 ('experience', 'ExperienceandCertifications2'),
                                 ('employement', 'EmployementInformation3'),
                                 ('offer_summary', 'Summary4'),
                                 ('consent', 'BackgroundCheckConsent5'),
                                 ('background', 'BackgroundCheck6'),
                                 ('back_summary', 'Summary7'),
                                 ('adverse', 'AdverseAction8'),
                                 ('inine', 'i99'),
                                 ('everify', 'E-Verify10'),
                                 ('app_summary', 'ApplicantSummary/Hire11'),
                                 ('ben_eligiblity', 'BenefitsEligibility12'),
                                 ('welcome', 'WelcomeEmail13'),
                                 ('appraisal', 'AppraisalPlan14'),
                                 ('hire_summary', 'Summary15'),
                                 ('ben_survey', 'BenefitsSurveyResults16'),
                                 ('emp_summary', 'EmployeeSummary17'),
                                 ('contract', 'CreateContract18'),
                                 ('con_summary', 'ContractSummary19'),
                                 ('completed', 'Complete20')], string="Onboarding Status",default='started')
    e_verify = fields.Selection([('initiate', 'Initiate'),
                                 ('completed', 'Completed')], string="E-Verify",track_visibility='onchange')
    benefits_enrollment_delay = fields.Integer("Benefits Enrollment Delay",track_visibility='onchange')
    eligible_for_benefits = fields.Boolean(track_visibility='onchange')
    contract_type = fields.Many2one('hr.contract.type',string = "Contract Type")
    pay_type = fields.Selection([('yearly', 'Annual Wage'),
                                 ('monthly', 'Monthly Wage'),
                                 ('hourly', 'Hourly Wage')], string="Pay Type",track_visibility='onchange')
    ethnic_id = fields.Char("Ethnic ID",track_visibility='onchange')
    smoker = fields.Char("Smoker",track_visibility='onchange')
    progress_percentage = fields.Integer(compute="_compute_progress_percentage")
    emergency_contact_name = fields.Char("Name")
    emergency_contact_phone = fields.Char("Phone")
    emergency_contact_relationship = fields.Char("Relationship")
    image = fields.Binary("Photo", attachment=True,
        help="This field holds the image used as photo for the employee, limited to 1024x1024px.")
    
    appraisal_date = fields.Date(string='Next Appraisal Date')
    appraisal_by_manager = fields.Boolean(string='Managers')
    appraisal_manager_ids = fields.Many2many('hr.employee', 'emp_appraisal_manager_rel', 'hr_appraisal_id')
    appraisal_manager_survey_id = fields.Many2one('survey.survey', string="Manager's Appraisal")
    appraisal_by_colleagues = fields.Boolean(string='Colleagues')
    appraisal_colleagues_ids = fields.Many2many('hr.employee', 'emp_appraisal_colleagues_rel', 'hr_appraisal_id')
    appraisal_colleagues_survey_id = fields.Many2one('survey.survey', string="Employee's Appraisal")
    appraisal_self = fields.Boolean(string='Employee')
    appraisal_employee = fields.Char(string='Employee Name')
    appraisal_self_survey_id = fields.Many2one('survey.survey', string='Self Appraisal')
    appraisal_by_collaborators = fields.Boolean(string='Collaborators')
    appraisal_collaborators_ids = fields.Many2many('hr.employee', 'emp_appraisal_subordinates_rel', 'hr_appraisal_id')
    appraisal_collaborators_survey_id = fields.Many2one('survey.survey', string="collaborate's Appraisal")
    periodic_appraisal = fields.Boolean(string='Periodic Appraisal', default=False)
    periodic_appraisal_created = fields.Boolean(string='Periodic Appraisal has been created', default=False)  # Flag for the cron
    appraisal_frequency = fields.Integer(string='Appraisal Repeat Every', default=6)
    appraisal_frequency_unit = fields.Selection([('year', 'Year'), ('month', 'Month')], string='Appraisal Frequency', copy=False, default='month')
    appraisal_count = fields.Integer(compute='_compute_appraisal_count', string='Appraisals')
    partner_id = fields.Many2one('res.partner')
    appraisal_by_coach = fields.Boolean(string='Coach')
    appraisal_coach_id = fields.Many2many('hr.employee', 'emp_appraisal_coach_rel', 'hr_appraisal_id')
    appraisal_coach_survey_id = fields.Many2one('survey.survey', string="Coach's Appraisal")
    appraisal_by_short = fields.Boolean(string='90 Days Appraisal')
    appraisal_short_id = fields.Many2many('hr.employee', 'emp_appraisal_short_rel', 'hr_appraisal_id')
    appraisal_short_survey_id = fields.Many2one('survey.survey', string="Short Review Survey")
    auto_send_appraisals = fields.Boolean(string='Auto Send Appraisals')
    direct_report_anonymous = fields.Boolean(string='Anonymous')
    colleague_report_anonymous = fields.Boolean(string='Anonymous')
    notes = fields.Text("Bio")
    
    academic_experience_ids = fields.One2many('academic.experience', 'academic_experience_id', string="Academic Experience")
    professional_experience_ids = fields.One2many('professional.experience', 'professional_experience_id', string="Professional Experience")
    certification_ids = fields.One2many('certification.details', 'certification_id', string="Certifications")
    applicant_background_ids = fields.One2many('applicant.background', 'applicant_background_id', string="Applicant")
    employer_background_ids = fields.One2many('employer.background', 'employer_background_id', string="Employer")
    background_check_ids = fields.One2many('background.check', 'background_check_id', string="Background Check")
    background_check_download_ids = fields.One2many('background.check.download', 'background_check_download_id', string="Background Check Download")
    background_check_package_ids = fields.One2many('background.check.package', 'background_check_package_id', string="Background Check Package")
    consent_form_ids = fields.One2many('consent.form', 'consent_form_id', string="Consent Form")
    action_form_ids = fields.One2many('adverse.action', 'action_form_id', string="Adverse Action")
    welcome_mail_ids = fields.One2many('welcome.mail', 'welcome_mail_id', string="Welcome Mail")
    welcome_benefit_survey_ids = fields.One2many('welcome.survey', 'welcome_benefit_survey_id', string="Benefits")
    # everify_case_result_ids = fields.One2many('everify.case.result','everify_case_result_id',string='Everify Case Result',track_visibility='onchange')
    new_employee_id = fields.Many2one('hr.employee',string="Employee ID")
    new_contract_id = fields.Many2one('hr.contract',string="Contract ID")
    employee_id = fields.Integer("Employee ID")
    survey_id_ref = fields.Many2many('survey.user_input','survey_id_ref',string="Surveys")

    benefits_survey_link = fields.Char("Benefits Survey URL")
    reject_date = fields.Date("Reject Date")
    pid_document_id = fields.Many2one('signature.request',string = "PID Document")


    def _compute_progress_percentage(self):
        if self.substate_id == 'get_started':
            self.progress_percentage = 0
        if self.substate_id == 'personal':
            self.progress_percentage = 5
        if self.substate_id == 'experience':
            self.progress_percentage = 10
        if self.substate_id == 'employement':
            self.progress_percentage = 15
        if self.substate_id == 'offer_summary':
            self.progress_percentage = 20
        if self.substate_id == 'consent':
            self.progress_percentage = 25
        if self.substate_id == 'background':
            self.progress_percentage = 30
        if self.substate_id == 'back_summary':
            self.progress_percentage = 35
        if self.substate_id == 'adverse':
            self.progress_percentage = 40
        if self.substate_id == 'inine':
            self.progress_percentage = 45
        if self.substate_id == 'everify':
            self.progress_percentage = 50
        if self.substate_id == 'app_summary':
            self.progress_percentage = 55
        if self.substate_id == 'ben_eligiblity':
            self.progress_percentage = 60
        if self.substate_id == 'welcome':
            self.progress_percentage = 65
        if self.substate_id == 'appraisal':
            self.progress_percentage = 70
        if self.substate_id == 'hire_summary':
            self.progress_percentage = 75
        if self.substate_id == 'ben_survey':
            self.progress_percentage = 80
        if self.substate_id == 'emp_summary':
            self.progress_percentage = 85
        if self.substate_id == 'contract':
            self.progress_percentage = 90
        if self.substate_id == 'con_summary':
            self.progress_percentage = 95
        if self.substate_id == 'completed':
            self.progress_percentage = 100
                    

    @api.multi
    def change_status(self,form_id,substate_name,state_name):

        form_obj = self.env['hr.employee.onboarding'].search([('id','=',form_id)])

        if substate_name == 'back_summary':
            bg_list = []
            for rec in form_obj.background_check_ids:
                if rec.status_id:
                    bg_list.append({
                        'id' : rec.id or '',
                        })

            if len(bg_list) != 0:
                bg_status = 'Initiated'
                if state_name:
                    form_obj.state_id = state_name
                if substate_name:
                    form_obj.substate_id = substate_name

                return bg_status
            else:
                bg_status = 'Not Initiated'

                return bg_status

        elif state_name == 'complete' and substate_name == 'completed':
            
            applicant_obj = self.env['hr.applicant'].browse(int(form_obj.applicant_id))
            
            stage_obj = self.env['hr.recruitment.stage'].search([('name', '=', 'Hired')])
            
            if applicant_obj:
                applicant_obj.write({'stage_id':stage_obj.id})

            if state_name:
                form_obj.state_id = state_name
            if substate_name:
                form_obj.substate_id = substate_name

            return True

        else:
            if state_name:
                form_obj.state_id = state_name
            if substate_name:
                form_obj.substate_id = substate_name

            return True


    @api.onchange('dob')
    def onchange_age(self):
        today = datetime.now().date()
        birthday = datetime.strptime(self.dob, '%Y-%m-%d').date()
        self.age = today.year - birthday.year


    @api.multi
    def send_benefit_survey(self,form_id):
        if form_id:
            survey_obj = self.env['hr.employee.onboarding'].search([('id','=',form_id)])
            if(survey_obj.contract_type == survey_obj.company.eligible_for_benefits):
                ComposeMessage = self.env['survey.mail.compose.message']
                render_template = self.env.ref('survey.email_template_survey').with_context(email=survey_obj.mail, survey=survey_obj.company.benefits_survey, employee=survey_obj.new_employee_id).generate_email([survey_obj.id])

                values = {
                    'survey_id': survey_obj.company.benefits_survey.id,
                    'public': 'email_private',
                    'multi_email': survey_obj.mail,
                    'subject': survey_obj.company.benefits_survey.title,
                    'body': render_template,
                    'model': survey_obj._name,
                    'res_id': survey_obj.id,
                }
                compose_message_wizard = ComposeMessage.with_context(active_id=survey_obj.id, active_model=survey_obj._name).create(values)
                compose_message_wizard.send_mail()
                survey_obj.state_id = 'benefits'
                survey_obj.benefits_states = 'pending'
                 
            else:
                survey_obj.benefits_states = 'not_eligible'
                survey_obj.state_id = 'benefits'
                

    @api.multi
    def send_survey(self,form_id,survey_id,tree_id):
        if form_id and tree_id:
            survey_obj = self.env['hr.employee.onboarding'].search([('id' , '=' , form_id)])
            if int(tree_id) != 0 :
                survey_tree_id_obj = self.env['welcome.survey'].search([('id' , '=' , tree_id)])
            else:
                survey_tree_id_obj = self.env['welcome.survey'].create({
                        'survey': survey_id['form_welcome_survey'],
                        'welcome_benefit_survey_id': form_id
                    })              
            ComposeMessage = self.env['survey.mail.compose.message']
            render_template = self.env.ref('survey.email_template_survey').with_context(email=survey_obj.mail, survey=survey_tree_id_obj.survey, employee=survey_obj.new_employee_id).generate_email([survey_obj.id])

            values = {
                'survey_id': survey_tree_id_obj.survey.id,
                'public': 'email_private',
                'multi_email': survey_obj.mail,
                'subject': survey_tree_id_obj.survey.title,
                'body': render_template,
                'model': survey_obj._name,
                'res_id': survey_obj.id,
            }
            compose_message_wizard = ComposeMessage.with_context(active_id=survey_obj.id, active_model=survey_obj._name).create(values)
            compose_message_wizard.send_mail() 


            token = uuid.uuid4().__str__()
            
            survey_id_obj = self.env['survey.user_input'].create({
                        'survey_id': survey_tree_id_obj.survey.id,
                        # 'deadline': wizard.date_deadline,
                        'date_create': fields.Datetime.now(),
                        'type': 'link',
                        'state': 'new',
                        'token': token,
                        'partner_id': survey_obj.partner_id.id,
                        'email': survey_obj.mail,
                        'onboarding_id' : form_id})

            self.env.cr.execute("select survey_id,token from survey_user_input where onboarding_id="+form_id)
            results = self.env.cr.dictfetchall()

            for record in results:
                survey = self.env['survey.survey'].search([('id' , '=' , record['survey_id'])])
                """ Open the website page with the survey form """
                base_url = '/' if self.env.context.get('relative_url') else self.env['ir.config_parameter'].get_param('web.base.url')
                public_url = urljoin(base_url, "survey/start/%s" % (slug(survey)))
                benifits_survey_info = public_url+"/"+record['token'] 

            survey_tree_id_obj.survey_link = benifits_survey_info
            survey_tree_id_obj.request_id = survey_id_obj.id
            survey_tree_id_obj.date_sent = fields.datetime.now()

            survey_obj.benefits_survey = 'to_approve'


    @api.multi
    def send_launch_pack(self,form_id,check_id,get_started):
        send_obj = self.env['hr.employee.onboarding'].search([('id','=',form_id)])
        req_id=0
        if send_obj.substate_id == 'started':
            if check_id == 'launch':
                self.insert_records_get_started(form_id,get_started,from_pid=1)
            if form_id:
                employee_obj = self.env['hr.employee.onboarding'].search([('id','=',form_id)])
                if employee_obj.mail:
                    if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", employee_obj.mail) != None:
                        x = datetime.strptime(employee_obj.start_date, '%Y-%m-%d').year
                        personal_doc_obj = self.env['employee.settings'].search([('calendar_year' , '=' , str(x)),('emp_contract_type' , 'in' , [employee_obj.contract_type.id])], limit=1)
                        template_ids =[]
                        template_id = self.env['signature.request.template'].search([('id', '=', personal_doc_obj.personal_info_template.id)])
                       
                        if template_id:
                            req_id = ''
                            reference = template_id.attachment_id.name
                            request_item = self.env["signature.item"].search([('template_id', '=', template_id.id)])
                            
                            roles = []
                            for req_item in request_item:
                                if req_item.responsible_id.id not in roles:
                                    roles.append(req_item.responsible_id.id)
                            template_ids.append((template_id.id, reference))
                            applicant_obj = self.env['hr.applicant'].search([('id' , '=' , employee_obj.applicant_id)])
                            if applicant_obj.partner_id:
                                if template_ids:
                                    signers = []
                                    signer = {}
                                    for role in roles:
                                        signer={
                                        'partner_id' : applicant_obj.partner_id.id,
                                        'role': role
                                        }
                                        signers.append(signer)

                                    req_id = self.env["signature.request"].with_context({'template_id': template_ids, 'reference': template_ids,'status':'launch'}).initialize_new(template_ids[0][0], signers, followers=[], reference=reference, subject="", message="", send=True)
                                    employee_obj.pid_document_id = req_id['id']
                                
                            else:
                                pay_term = self.env['account.payment.term'].search([('name', '=', 'Immediate Payment')]).id
                                pay_mode = self.env['account.payment.mode'].search([('name', '=', 'Manual Payment')]).id
                                rel_user = self.env['res.partner'].create({
                                    'firstname' : employee_obj.first_name or False,
                                    'middlename' : employee_obj.middle_name or False,
                                    'lastname' : employee_obj.last_name or False,
                                    'email' : employee_obj.mail or False,
                                    'company_id' : employee_obj.company.id or False,
                                    'property_supplier_payment_term_id' : pay_term or False,
                                    'supplier_payment_mode_id' : pay_mode or False,
                                    'state_id' : employee_obj.state.id or False,
                                    'city' : employee_obj.city or False,
                                    'street' : employee_obj.street or False,
                                    'street2' : employee_obj.street2 or False,
                                    'country_id' : employee_obj.country.id or False,
                                    'zip' : employee_obj.zip or False,
                                    })
                                applicant_obj.partner_id = rel_user
                                employee_obj.partner_id = rel_user
                                if template_ids:
                                    signers = []
                                    signer = {}
                                    for role in roles:
                                        signer={
                                        'partner_id' : rel_user.id,
                                        'role': role
                                        }
                                        signers.append(signer)

                                    req_id = self.env["signature.request"].with_context({'template_ids': template_ids, 'reference': template_ids,'status':'launch'}).initialize_new(template_ids[0][0], signers, followers=[], reference=reference, subject="", message="", send=True)
                                    employee_obj.pid_document_id = req_id['id']


                        else:
                            raise ValidationError("Please select Personal Information document in configurations")
                    else:
                        raise ValidationError("Please enter a valid email or check the spaces before and after the email id")
            return req_id

        else:
            return req_id
            # raise UserError("Personal Information document is already sent")
        
    @api.multi
    def send_onboarding_documents_link(self,form_id,doc_id,tree_id,check_id):
        re_rec_id=''
        doc_dict=''
        if check_id == 'applicant':
            re_rec_id=self.insert_records_inine_applicant_info(form_id,doc_id)
        if check_id == 'employer':
            re_rec_id=self.insert_records_inine_employer_info(form_id,doc_id)

        if check_id == 'consent':
            if int(doc_id['consent_form_tree_id'])>0:
                background_consent_info_obj = self.env['consent.form'].search([('id' , '=' , doc_id['consent_form_tree_id'])])
                
                if background_consent_info_obj.status_id != 'signed':
                    if (doc_id['form_consent_documents']):
                        background_consent_info_obj.consent_form = doc_id['form_consent_documents']
                    if (doc_id['background_check_consent_form_link']):
                        background_consent_info_obj.form_link = doc_id['background_check_consent_form_link']
                    if (doc_id['background_check_consent_form_status']):
                        background_consent_info_obj.status_id = doc_id['background_check_consent_form_status']
                    if (doc_id['background_check_consent_form_date_sent']):
                        background_consent_info_obj.date_sent = doc_id['background_check_consent_form_date_sent']

                    if background_consent_info_obj.status_id != 'canceled':
                        if (doc_id['background_check_consent_form_expiration']):
                            background_consent_info_obj.expiration = doc_id['background_check_consent_form_expiration']   
                    elif background_consent_info_obj.status_id == 'canceled' and str(background_consent_info_obj.expiration) != doc_id['background_check_consent_form_expiration']:
                        if (doc_id['background_check_consent_form_expiration']):
                            background_consent_info_obj.expiration = doc_id['background_check_consent_form_expiration']   
                    else:
                        background_consent_info_obj.expiration = ''                      

                    re_rec_id = background_consent_info_obj.id

                else:
                    raise UserError('This document is already Signed.Please add new document and send again')
                     
            else:
                if (doc_id['form_consent_documents'] or doc_id['background_check_consent_form_link'] or doc_id['background_check_consent_form_status']):
                    background_consent_info_obj = self.env['consent.form'].create({
                        'consent_form' : doc_id['form_consent_documents'],
                        'form_link' : doc_id['background_check_consent_form_link'],
                        'status_id' : doc_id['background_check_consent_form_status'],
                        'date_sent' : doc_id['background_check_consent_form_date_sent'] or False,
                        'expiration' : doc_id['background_check_consent_form_expiration'] or False,
                        'consent_form_id':form_id
                        })   
                    re_rec_id = background_consent_info_obj.id
        if check_id == 'adverse':
            if int(doc_id['adverse_action_tree_id'])>0:
                adverse_action_info_obj = self.env['adverse.action'].search([('id' , '=' , doc_id['adverse_action_tree_id'])])
                if (doc_id['form_adverse_documents']):
                    adverse_action_info_obj.action_form = doc_id['form_adverse_documents']
                if (doc_id['adverse_action_link']):
                    adverse_action_info_obj.form_link = doc_id['adverse_action_link']
                if (doc_id['adverse_action_status']):
                    adverse_action_info_obj.status_id = doc_id['adverse_action_status']
                if (doc_id['adverse_action_date_sent']):
                    adverse_action_info_obj.date_sent = doc_id['adverse_action_date_sent']
                if (doc_id['adverse_action_expiration']):
                    adverse_action_info_obj.expiration = doc_id['adverse_action_expiration']        

                re_rec_id = adverse_action_info_obj.id
                     
            else:
                if (doc_id['form_adverse_documents']):
                    adverse_action_info_obj = self.env['adverse.action'].create({
                        'action_form' : doc_id['form_adverse_documents'],
                        'form_link' : doc_id['adverse_action_link'],
                        'status_id' : doc_id['adverse_action_status'],
                        'date_sent' : doc_id['adverse_action_date_sent'] or False,
                        'expiration' : doc_id['adverse_action_expiration'] or False,
                        'action_form_id':form_id
                        })
                    re_rec_id = adverse_action_info_obj.id
        if check_id == 'welcome':
            re_rec_id=self.insert_records_welcome_email_info(form_id,doc_id)
       
        tree_id=re_rec_id

        if 'form_applicant_documents' in doc_id:
            temp_id = doc_id['form_applicant_documents']
        elif 'form_employer_documents' in doc_id:
            temp_id = doc_id['form_employer_documents']
        elif 'form_consent_documents' in doc_id:
            temp_id = doc_id['form_consent_documents']
        elif 'form_adverse_documents' in doc_id:
            temp_id = doc_id['form_adverse_documents']
        elif 'form_welcome_applicant_documents' in doc_id:
            temp_id = doc_id['form_welcome_applicant_documents']

        if temp_id:
            employee_obj = self.env['hr.employee.onboarding'].search([('id','=',form_id)])
            if check_id == 'employer':
                email = employee_obj.responsible.login
            else:
                email = employee_obj.mail
            if email:
                if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email) != None:
                    template_id = self.env['signature.request.template'].search([('id', '=', temp_id)])
                    if template_id:
                        signature_template = self.env["signature.request.template"].search([("id", "=", template_id.id)])
                        reference = signature_template.attachment_id.name
                        request_item = self.env["signature.item"].search([('template_id', '=', template_id.id)])
                        roles = []
                        for req_item in request_item:
                            if req_item.responsible_id.id not in roles:
                                roles.append(req_item.responsible_id.id)
                        applicant_obj = self.env['hr.applicant'].search([('id' , '=' , employee_obj.applicant_id)])
                        if applicant_obj.partner_id:
                            signers = []
                            signer = {}
                            for role in roles:
                                signer={
                                'partner_id' : applicant_obj.partner_id.id if check_id != 'employer' else applicant_obj.user_id.partner_id.id,
                                'role': role
                                }
                                signers.append(signer)

                            if check_id == 'applicant':
                                doc_vals = self.env['applicant.background'].search([('id','=',re_rec_id)])
                                if doc_vals.doc_link:
                                    base_context = self.env.context
                                    template_id = self.env.ref('website_sign.website_sign_mail_template').id
                                    mail_template = self.env['mail.template'].browse(template_id)
                                    email_from_usr = self.env['res.users'].browse(self.env.uid).partner_id.name
                                    email_from_mail = self.env['res.users'].browse(self.env.uid).partner_id.email
                                    email_from = "%(email_from_usr)s <%(email_from_mail)s>" % {'email_from_usr': email_from_usr, 'email_from_mail': email_from_mail}                
                                    template = mail_template.sudo().with_context(base_context,
                                        lang = applicant_obj.partner_id.lang,
                                        template_type = "request",
                                        email_from_usr = email_from_usr,
                                        email_from_mail = email_from_mail,
                                        email_from = email_from,
                                        email_to = applicant_obj.partner_id.email,
                                        link = doc_vals.doc_link,
                                        subject = "Signature request - " + doc_vals.request_id.reference,
                                        msgbody = ("").replace("\n", "<br/>")
                                    )
                                    template.send_mail(doc_vals.request_id.id, force_send=True)
                                else:
                                    req_id = self.env["signature.request"].initialize_new(template_id.id, signers, followers=[], reference=reference, subject="", message="", send=True)

                            if check_id == 'employer':
                                doc_vals = self.env['employer.background'].search([('id','=',re_rec_id)])
                                if doc_vals.doc_link:
                                    base_context = self.env.context
                                    template_id = self.env.ref('website_sign.website_sign_mail_template').id
                                    mail_template = self.env['mail.template'].browse(template_id)
                                    email_from_usr = self.env['res.users'].browse(self.env.uid).partner_id.name
                                    email_from_mail = self.env['res.users'].browse(self.env.uid).partner_id.email
                                    email_from = "%(email_from_usr)s <%(email_from_mail)s>" % {'email_from_usr': email_from_usr, 'email_from_mail': email_from_mail}                
                                    template = mail_template.sudo().with_context(base_context,
                                        lang = applicant_obj.partner_id.lang,
                                        template_type = "request",
                                        email_from_usr = email_from_usr,
                                        email_from_mail = email_from_mail,
                                        email_from = email_from,
                                        email_to = applicant_obj.partner_id.email,
                                        link = doc_vals.doc_link,
                                        subject = "Signature request - " + doc_vals.request_id.reference,
                                        msgbody = ("").replace("\n", "<br/>")
                                    )
                                    template.send_mail(doc_vals.request_id.id, force_send=True)
                                else:
                                    req_id = self.env["signature.request"].initialize_new(template_id.id, signers, followers=[], reference=reference, subject="", message="", send=True)

                            if check_id == 'adverse':
                                doc_vals = self.env['adverse.action'].search([('id','=',re_rec_id)])
                                if doc_vals.form_link:
                                    base_context = self.env.context
                                    template_id = self.env.ref('website_sign.website_sign_mail_template').id
                                    mail_template = self.env['mail.template'].browse(template_id)
                                    email_from_usr = self.env['res.users'].browse(self.env.uid).partner_id.name
                                    email_from_mail = self.env['res.users'].browse(self.env.uid).partner_id.email
                                    email_from = "%(email_from_usr)s <%(email_from_mail)s>" % {'email_from_usr': email_from_usr, 'email_from_mail': email_from_mail}                
                                    template = mail_template.sudo().with_context(base_context,
                                        lang = applicant_obj.partner_id.lang,
                                        template_type = "request",
                                        email_from_usr = email_from_usr,
                                        email_from_mail = email_from_mail,
                                        email_from = email_from,
                                        email_to = applicant_obj.partner_id.email,
                                        link = doc_vals.form_link,
                                        subject = "Signature request - " + doc_vals.request_id.reference,
                                        msgbody = ("").replace("\n", "<br/>")
                                    )
                                    template.send_mail(doc_vals.request_id.id, force_send=True)
                                else:
                                    req_id = self.env["signature.request"].initialize_new(template_id.id, signers, followers=[], reference=reference, subject="", message="", send=True)

                            if check_id == 'welcome':
                                doc_vals = self.env['welcome.mail'].search([('id','=',re_rec_id)])
                                if doc_vals.doc_link:
                                    base_context = self.env.context
                                    template_id = self.env.ref('website_sign.website_sign_mail_template').id
                                    mail_template = self.env['mail.template'].browse(template_id)
                                    email_from_usr = self.env['res.users'].browse(self.env.uid).partner_id.name
                                    email_from_mail = self.env['res.users'].browse(self.env.uid).partner_id.email
                                    email_from = "%(email_from_usr)s <%(email_from_mail)s>" % {'email_from_usr': email_from_usr, 'email_from_mail': email_from_mail}                
                                    template = mail_template.sudo().with_context(base_context,
                                        lang = applicant_obj.partner_id.lang,
                                        template_type = "request",
                                        email_from_usr = email_from_usr,
                                        email_from_mail = email_from_mail,
                                        email_from = email_from,
                                        email_to = applicant_obj.partner_id.email,
                                        link = doc_vals.doc_link,
                                        subject = "Signature request - " + doc_vals.request_id.reference,
                                        msgbody = ("").replace("\n", "<br/>")
                                    )
                                    template.send_mail(doc_vals.request_id.id, force_send=True)
                                else:
                                    req_id = self.env["signature.request"].initialize_new(template_id.id, signers, followers=[], reference=reference, subject="", message="", send=True)

                            if check_id == 'consent':
                                doc_vals = self.env['consent.form'].search([('id','=',re_rec_id)])
                                if doc_vals.form_link:
                                    base_context = self.env.context
                                    template_id = self.env.ref('website_sign.website_sign_mail_template').id
                                    mail_template = self.env['mail.template'].browse(template_id)
                                    email_from_usr = self.env['res.users'].browse(self.env.uid).partner_id.name
                                    email_from_mail = self.env['res.users'].browse(self.env.uid).partner_id.email
                                    email_from = "%(email_from_usr)s <%(email_from_mail)s>" % {'email_from_usr': email_from_usr, 'email_from_mail': email_from_mail}                
                                    template = mail_template.sudo().with_context(base_context,
                                        lang = applicant_obj.partner_id.lang,
                                        template_type = "request",
                                        email_from_usr = email_from_usr,
                                        email_from_mail = email_from_mail,
                                        email_from = email_from,
                                        email_to = applicant_obj.partner_id.email,
                                        link = doc_vals.form_link,
                                        subject = "Signature request - " + doc_vals.request_id.reference,
                                        msgbody = ("").replace("\n", "<br/>")
                                    )
                                    template.send_mail(doc_vals.request_id.id, force_send=True)
                                else:
                                    req_id = self.env["signature.request"].initialize_new(template_id.id, signers, followers=[], reference=reference, subject="", message="", send=True)
                            
                        else:
                            pay_term = self.env['account.payment.term'].search([('name', '=', 'Immediate Payment')]).id
                            pay_mode = self.env['account.payment.mode'].search([('name', '=', 'Manual Payment')]).id
                            rel_user = self.env['res.partner'].create({
                                'firstname' : employee_obj.first_name or False,
                                'middlename' : employee_obj.middle_name or False,
                                'lastname' : employee_obj.last_name or False,
                                'email' : email or False,
                                'company_id' : employee_obj.company.id or False,
                                'property_supplier_payment_term_id' : pay_term or False,
                                'supplier_payment_mode_id' : pay_mode or False,
                                'state_id' : employee_obj.state.id or False,
                                'city' : employee_obj.city or False,
                                'street' : employee_obj.street or False,
                                'street2' : employee_obj.street2 or False,
                                'country_id' : employee_obj.country.id or False,
                                'zip' : employee_obj.zip or False,
                                })
                            applicant_obj.partner_id = rel_user
                            employee_obj.partner_id = rel_user
                            signers = []
                            signer = {}
                            for role in roles:
                                signer={
                                'partner_id' : rel_user.id,
                                'role': role
                                }
                                signers.append(signer)

                            
                            req_id = self.env["signature.request"].initialize_new(template_id.id, signers, followers=[], reference=reference, subject="", message="", send=True)
                            

                        if check_id == 'applicant':
                            app_obj = self.env['applicant.background'].search([('id','=',tree_id)])
                            if app_obj:
                                doc_vals = self.env['applicant.background'].search([('id','=',re_rec_id)])
                                if not doc_vals.doc_link:
                                    app_obj.request_id = req_id['id'] 
                                    app_obj.date_sent = fields.datetime.now()
                                    app_obj.doc_link = self.env['ir.config_parameter'].search([('key','=','web.base.url')]).value+'/sign/document/'+str(req_id['id'])+'/'+str(app_obj.request_id.access_token)
                                    
                                doc_dict = {
                                'id' : doc_vals.id or '',
                                'status' : doc_vals.status_id or '',
                                'link' : doc_vals.doc_link or '',
                                'sent' : doc_vals.date_sent or '',
                                'end' : doc_vals.expiration or ''
                                }
                        elif check_id == 'employer':
                            emp_obj = self.env['employer.background'].search([('id','=',tree_id)])
                            if emp_obj:
                                doc_vals = self.env['employer.background'].search([('id','=',re_rec_id)])
                                if not doc_vals.doc_link:
                                    emp_obj.request_id = req_id['id']
                                    emp_obj.date_sent = fields.datetime.now()
                                    emp_obj.doc_link = self.env['ir.config_parameter'].search([('key','=','web.base.url')]).value+'/sign/document/'+str(req_id['id'])+'/'+str(emp_obj.request_id.access_token)
                                
                                doc_dict = {
                                'id' : doc_vals.id or '',
                                'status' : doc_vals.status_id or '',
                                'link' : doc_vals.doc_link or '',
                                'sent' : doc_vals.date_sent or '',
                                'end' : doc_vals.expiration or ''
                                }
                        elif check_id == 'consent':
                            consent_obj = self.env['consent.form'].search([('id','=',tree_id)])
                            if consent_obj:
                                doc_vals = self.env['consent.form'].search([('id','=',re_rec_id)])
                                if not doc_vals.form_link:
                                    consent_obj.request_id = req_id['id']
                                    consent_obj.date_sent = fields.datetime.now()
                                    consent_obj.form_link = self.env['ir.config_parameter'].search([('key','=','web.base.url')]).value+'/sign/document/'+str(req_id['id'])+'/'+str(consent_obj.request_id.access_token)
                                
                                doc_dict = {
                                'id' : doc_vals.id or '',
                                'status' : doc_vals.status_id or '',
                                'link' : doc_vals.form_link or '',
                                'sent' : doc_vals.date_sent or '',
                                'end' : doc_vals.expiration or ''
                                }
                        elif check_id == 'adverse':
                            adverse_obj = self.env['adverse.action'].search([('id','=',tree_id)])
                            if adverse_obj:
                                doc_vals = self.env['adverse.action'].search([('id','=',re_rec_id)])
                                if not doc_vals.form_link:
                                    adverse_obj.request_id = req_id['id']
                                    adverse_obj.date_sent = fields.datetime.now()
                                    adverse_obj.form_link = self.env['ir.config_parameter'].search([('key','=','web.base.url')]).value+'/sign/document/'+str(req_id['id'])+'/'+str(adverse_obj.request_id.access_token)
                                
                                doc_dict = {
                                'id' : doc_vals.id or '',
                                'status' : doc_vals.status_id or '',
                                'link' : doc_vals.form_link or '',
                                'sent' : doc_vals.date_sent or '',
                                'end' : doc_vals.expiration or ''
                                }
                        elif check_id == 'welcome':
                            welcome_obj = self.env['welcome.mail'].search([('id','=',tree_id)])
                            if welcome_obj:
                                doc_vals = self.env['welcome.mail'].search([('id','=',re_rec_id)])
                                if not doc_vals.doc_link:
                                    welcome_obj.request_id = req_id['id']
                                    welcome_obj.date_sent = fields.datetime.now()
                                    welcome_obj.doc_link = self.env['ir.config_parameter'].search([('key','=','web.base.url')]).value+'/sign/document/'+str(req_id['id'])+'/'+str(welcome_obj.request_id.access_token)
                                
                                doc_dict = {
                                'id' : doc_vals.id or '',
                                'status' : doc_vals.status_id or '',
                                'link' : doc_vals.doc_link or '',
                                'sent' : doc_vals.date_sent or '',
                                'end' : doc_vals.expiration or ''
                                }
                

                else:
                    raise ValidationError("Please enter a valid email or check the spaces before and after the email id")

        return doc_dict

    @api.multi
    def background_check_send_all(self,form_id,inine_applicant_info_vals,inine_employer_info_vals):
        if inine_applicant_info_vals:
            for rec in inine_applicant_info_vals:
                if int(rec['applicant_tree_id'])>0:
                    inine_app_info_obj = self.env['applicant.background'].search([('id' , '=' , rec['applicant_tree_id'])])
                    if (rec['form_applicant_documents']):
                        inine_app_info_obj.document = rec['form_applicant_documents']
                    if (rec['applicant_link']):
                        inine_app_info_obj.doc_link = rec['applicant_link']
                    # if (rec['applicant_status']):
                    #     inine_app_info_obj.status_id = rec['applicant_status']
                    if (rec['applicant_date_sent']):
                        inine_app_info_obj.date_sent = rec['applicant_date_sent']

                    if inine_app_info_obj.status_id != 'canceled':
                        if (rec['applicant_expiration']):
                            inine_app_info_obj.expiration = rec['applicant_expiration']  

                    elif inine_app_info_obj.status_id == 'canceled' and str(rec['applicant_expiration']) != str(inine_app_info_obj.expiration):
                        if (rec['applicant_expiration']):
                            inine_app_info_obj.expiration = rec['applicant_expiration']  

                    else:
                        inine_app_info_obj.expiration = ''
                         
                else:
                    if (rec['form_applicant_documents'] or rec['applicant_link'] or rec['applicant_status']):
                        inine_app_info_obj = self.env['applicant.background'].create({
                            'document' : rec['form_applicant_documents'],
                            'doc_link' : rec['applicant_link'],
                            'status_id' : rec['applicant_status'],
                            'date_sent' : rec['applicant_date_sent'] or False,
                            'expiration' : rec['applicant_expiration'] or False,
                            'applicant_background_id':form_id
                            })
                # if rec.get('applicant_expiration'):
                #     form_obj = self.env['applicant.background'].search([('id' , '=' , int(rec.get('applicant_tree_id')))])
                #     if form_obj:
                #         form_obj.expiration = rec.get('applicant_expiration')
                # else:
                #     form_obj = self.env['applicant.background'].search([('id' , '=' , int(rec.get('applicant_tree_id')))])
                #     if form_obj:
                #         form_obj.expiration = ''

        if inine_employer_info_vals:
            for rec in inine_employer_info_vals:
                if int(rec['employer_tree_id'])>0:
                    inine_emp_info_obj = self.env['employer.background'].search([('id' , '=' , rec['employer_tree_id'])])
                    if (rec['form_employer_documents']):
                        inine_emp_info_obj.document = rec['form_employer_documents']
                    if (rec['employer_link']):
                        inine_emp_info_obj.doc_link = rec['employer_link']
                    # if (rec['employer_status']):
                    #     inine_emp_info_obj.status_id = rec['employer_status']
                    if (rec['employer_date_sent']):
                        inine_emp_info_obj.date_sent = rec['employer_date_sent']

                    if inine_emp_info_obj.status_id != 'canceled':
                        if (rec['employer_expiration']):
                            inine_emp_info_obj.expiration = rec['employer_expiration']  

                    elif inine_emp_info_obj.status_id == 'canceled' and str(rec['applicant_expiration']) != str(inine_emp_info_obj.expiration):      
                        if (rec['employer_expiration']):
                            inine_emp_info_obj.expiration = rec['employer_expiration'] 

                    else:
                        inine_emp_info_obj.expiration = ''
                        
                else:
                    if (rec['form_employer_documents'] or rec['employer_link'] or rec['employer_status']):
                        inine_emp_info_obj = self.env['employer.background'].create({
                            'document' : rec['form_employer_documents'],
                            'doc_link' : rec['employer_link'],
                            'status_id' : rec['employer_status'],
                            'date_sent' : rec['employer_date_sent'] or False,
                            'expiration' : rec['employer_expiration'] or False,
                            'employer_background_id':form_id
                            }) 

                if rec.get('employer_expiration'):
                    form_obj = self.env['employer.background'].search([('id' , '=' , int(rec.get('employer_tree_id')))])
                    if form_obj:
                        form_obj.expiration = rec.get('employer_expiration')
                else:
                    form_obj = self.env['employer.background'].search([('id' , '=' , int(rec.get('employer_tree_id')))])
                    if form_obj:
                        form_obj.expiration = ''
        if form_id:
            doc_dict=''
            employee_obj = self.env['hr.employee.onboarding'].browse(int(form_id))
            if employee_obj.mail:
                if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", employee_obj.mail) != None:
                    for line in employee_obj.applicant_background_ids:
                        template_id = self.env['signature.request.template'].search([('id', '=', line.document.id)])
                        if template_id:
                            signature_template = self.env["signature.request.template"].search([("id", "=", template_id.id)])
                            reference = signature_template.attachment_id.name
                            request_item = self.env["signature.item"].search([('template_id', '=', template_id.id)])
                            roles = []
                            for req_item in request_item:
                                if req_item.responsible_id.id not in roles:
                                    roles.append(req_item.responsible_id.id)
                            applicant_obj = self.env['hr.applicant'].search([('id' , '=' , employee_obj.applicant_id)])
                            if applicant_obj.partner_id:
                                signers = []
                                signer = {}
                                for role in roles:
                                    signer={
                                    'partner_id' : applicant_obj.partner_id.id,
                                    'role': role
                                    }
                                    signers.append(signer)

                                req_id = self.env["signature.request"].initialize_new(template_id.id,signers, followers=[], reference=reference, subject="", message="", send=True)
                                line.request_id = req_id['id']
                                line.date_sent = fields.datetime.now()
                                line.doc_link = self.env['ir.config_parameter'].search([('key','=','web.base.url')]).value+'/sign/document/'+str(req_id['id'])+'/'+str(line.request_id.access_token)
                            else:
                                pay_term = self.env['account.payment.term'].search([('name', '=', 'Immediate Payment')]).id
                                pay_mode = self.env['account.payment.mode'].search([('name', '=', 'Manual Payment')]).id
                                rel_user = self.env['res.partner'].create({
                                    'firstname' : employee_obj.first_name or False,
                                    'middlename' : employee_obj.middle_name or False,
                                    'lastname' : employee_obj.last_name or False,
                                    'email' : employee_obj.mail or False,                                    
                                    'company_id' : employee_obj.company.id or False,
                                    'property_supplier_payment_term_id' : pay_term or False,
                                    'supplier_payment_mode_id' : pay_mode or False,
                                    'state_id' : employee_obj.state.id or False,
                                    'city' : employee_obj.city or False,
                                    'street' : employee_obj.street or False,
                                    'street2' : employee_obj.street2 or False,
                                    'country_id' : employee_obj.country.id or False,
                                    'zip' : employee_obj.zip or False,
                                    })
                                applicant_obj.partner_id = rel_user
                                employee_obj.partner_id = rel_user
                                signers = []
                                signer = {}
                                for role in roles:
                                    signer={
                                    'partner_id' : rel_user.id,
                                    'role': role
                                    }
                                    signers.append(signer)
                                req_id = self.env["signature.request"].initialize_new(template_id.id,signers, followers=[], reference=reference, subject="", message="", send=True)
                                line.request_id = req_id['id']
                                line.date_sent = fields.datetime.now()
                                line.doc_link = self.env['ir.config_parameter'].search([('key','=','web.base.url')]).value+'/sign/document/'+str(req_id['id'])+'/'+str(line.request_id.access_token)
                    for line in employee_obj.employer_background_ids:
                        template_id = self.env['signature.request.template'].search([('id', '=', line.document.id)])
                        if template_id:
                            signature_template = self.env["signature.request.template"].search([("id", "=", template_id.id)])
                            reference = signature_template.attachment_id.name
                            request_item = self.env["signature.item"].search([('template_id', '=', template_id.id)])
                            roles = []
                            for req_item in request_item:
                                if req_item.responsible_id.id not in roles:
                                    roles.append(req_item.responsible_id.id)
                            applicant_obj = self.env['hr.applicant'].search([('id' , '=' , employee_obj.applicant_id)])
                            if applicant_obj.partner_id:
                                signers = []
                                signer = {}
                                for role in roles:
                                    signer={
                                    'partner_id' : applicant_obj.user_id.partner_id.id,
                                    'role': role
                                    }
                                    signers.append(signer)

                                req_id = self.env["signature.request"].initialize_new(template_id.id,signers, followers=[], reference=reference, subject="", message="", send=True)
                                line.request_id = req_id['id']
                                line.date_sent = fields.datetime.now()
                                line.doc_link = self.env['ir.config_parameter'].search([('key','=','web.base.url')]).value+'/sign/document/'+str(req_id['id'])+'/'+str(line.request_id.access_token)
                            else:
                                pay_term = self.env['account.payment.term'].search([('name', '=', 'Immediate Payment')]).id
                                pay_mode = self.env['account.payment.mode'].search([('name', '=', 'Manual Payment')]).id
                                rel_user = self.env['res.partner'].create({
                                    'firstname' : employee_obj.first_name or False,
                                    'middlename' : employee_obj.middle_name or False,
                                    'lastname' : employee_obj.last_name or False,
                                    'email' : employee_obj.mail or False,                                    
                                    'company_id' : employee_obj.company.id or False,
                                    'property_supplier_payment_term_id' : pay_term or False,
                                    'supplier_payment_mode_id' : pay_mode or False,
                                    'state_id' : employee_obj.state.id or False,
                                    'city' : employee_obj.city or False,
                                    'street' : employee_obj.street or False,
                                    'street2' : employee_obj.street2 or False,
                                    'country_id' : employee_obj.country.id or False,
                                    'zip' : employee_obj.zip or False,
                                    })
                                applicant_obj.partner_id = rel_user
                                employee_obj.partner_id = rel_user
                                signers = []
                                signer = {}
                                for role in roles:
                                    signer={
                                    'partner_id' : rel_user.id,
                                    'role': role
                                    }
                                    signers.append(signer)
                                req_id = self.env["signature.request"].initialize_new(template_id.id,signers, followers=[], reference=reference, subject="", message="", send=True)
                                line.request_id = req_id['id']
                                line.date_sent = fields.datetime.now()
                                line.doc_link = self.env['ir.config_parameter'].search([('key','=','web.base.url')]).value+'/sign/document/'+str(req_id['id'])+'/'+str(line.request_id.access_token)

                else:
                    raise ValidationError("Please enter a valid email or check the spaces before and after the email id")

            else:
                raise ValidationError("Please enter a valid email or check the spaces before and after the email id")

    @api.multi
    def consent_send_all(self,form_id,background_consent_info_vals):
        if background_consent_info_vals:
            for rec in background_consent_info_vals:
                if int(rec['consent_form_tree_id'])>0:
                    background_consent_info_obj = self.env['consent.form'].search([('id' , '=' , rec['consent_form_tree_id'])])
                        
                    if background_consent_info_obj.status_id != 'signed':
                        if (rec['form_consent_documents']):
                            background_consent_info_obj.consent_form = rec['form_consent_documents']
                        if (rec['background_check_consent_form_link']):
                            background_consent_info_obj.form_link = rec['background_check_consent_form_link']
                        if (rec['background_check_consent_form_status']):
                            background_consent_info_obj.status_id = rec['background_check_consent_form_status']
                        if (rec['background_check_consent_form_date_sent']):
                            background_consent_info_obj.date_sent = rec['background_check_consent_form_date_sent']
                        if (rec['background_check_consent_form_expiration']):
                            background_consent_info_obj.expiration = rec['background_check_consent_form_expiration']   

                    else:
                        raise UserError('This document is already Signed.Please add new document and send again')    
                         
                else:
                    if (rec['form_consent_documents'] or rec['background_check_consent_form_link'] or rec['background_check_consent_form_status']):
                        background_consent_info_obj = self.env['consent.form'].create({
                            'consent_form' : rec['form_consent_documents'],
                            'form_link' : rec['background_check_consent_form_link'],
                            'status_id' : rec['background_check_consent_form_status'],
                            'date_sent' : rec['background_check_consent_form_date_sent'] or False,
                            'expiration' : rec['background_check_consent_form_expiration'] or False,
                            'consent_form_id':form_id
                            })
                # if rec.get('background_check_consent_form_expiration'):
                #     form_obj = self.env['consent.form'].search([('id' , '=' , int(rec.get('consent_form_tree_id')))])
                #     if form_obj:
                #         form_obj.expiration = rec.get('background_check_consent_form_expiration')
                # else:
                #     form_obj = self.env['consent.form'].search([('id' , '=' , int(rec.get('consent_form_tree_id')))])
                #     if form_obj:
                #         form_obj.expiration = ''
        if form_id:
            doc_dict=''
            employee_obj = self.env['hr.employee.onboarding'].browse(int(form_id))
            if employee_obj.mail:
                if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", employee_obj.mail) != None:
                    for line in employee_obj.consent_form_ids:
                        template_id = self.env['signature.request.template'].search([('id', '=', line.consent_form.id)])
                        if template_id:
                            signature_template = self.env["signature.request.template"].search([("id", "=", template_id.id)])
                            reference = signature_template.attachment_id.name
                            request_item = self.env["signature.item"].search([('template_id', '=', template_id.id)])
                            roles = []
                            for req_item in request_item:
                                if req_item.responsible_id.id not in roles:
                                    roles.append(req_item.responsible_id.id)
                            
                            applicant_obj = self.env['hr.applicant'].search([('id' , '=' , employee_obj.applicant_id)])
                            if applicant_obj.partner_id:
                                signers = []
                                signer = {}
                                for role in roles:
                                    signer={
                                    'partner_id' : applicant_obj.partner_id.id,
                                    'role': role
                                    }
                                    signers.append(signer)

                                req_id = self.env["signature.request"].initialize_new(template_id.id,signers, followers=[], reference=reference, subject="", message="", send=True)
                                line.request_id = req_id['id']
                                line.date_sent = fields.datetime.now()
                                line.form_link = self.env['ir.config_parameter'].search([('key','=','web.base.url')]).value+'/sign/document/'+str(req_id['id'])+'/'+str(line.request_id.access_token)
                            else:
                                pay_term = self.env['account.payment.term'].search([('name', '=', 'Immediate Payment')]).id
                                pay_mode = self.env['account.payment.mode'].search([('name', '=', 'Manual Payment')]).id
                                rel_user = self.env['res.partner'].create({
                                    'firstname' : employee_obj.first_name or False,
                                    'middlename' : employee_obj.middle_name or False,
                                    'lastname' : employee_obj.last_name or False,
                                    'email' : employee_obj.mail or False,
                                    'company_id' : employee_obj.company.id or False,
                                    'property_supplier_payment_term_id' : pay_term or False,
                                    'supplier_payment_mode_id' : pay_mode or False,
                                    'state_id' : employee_obj.state.id or False,
                                    'city' : employee_obj.city or False,
                                    'street' : employee_obj.street or False,
                                    'street2' : employee_obj.street2 or False,
                                    'country_id' : employee_obj.country.id or False,
                                    'zip' : employee_obj.zip or False,
                                    })
                                applicant_obj.partner_id = rel_user
                                employee_obj.partner_id = rel_user
                                signers = []
                                signer = {}
                                for role in roles:
                                    signer={
                                    'partner_id' : rel_user.id,
                                    'role': role
                                    }
                                    signers.append(signer)
                                req_id = self.env["signature.request"].initialize_new(template_id.id,signers, followers=[], reference=reference, subject="", message="", send=True)
                                line.request_id = req_id['id']
                                line.date_sent = fields.datetime.now()
                                line.form_link = self.env['ir.config_parameter'].search([('key','=','web.base.url')]).value+'/sign/document/'+str(req_id['id'])+'/'+str(line.request_id.access_token)

                else:
                    raise ValidationError("Please enter a valid email or check the spaces before and after the email id")

            return True
                    

    @api.multi
    def background_check_initiate(self,form_id):

        background_obj = self.env['hr.employee.onboarding'].search([('id','=',form_id)])
#         lines=''
#         i=0
        for line in background_obj.background_check_ids:
            if line.status_id == False:
                line.status_id = 'open'
#             i+=1
#             lines+=str(line.status_id)+str(i)
#         raise ValidationError(_(lines))
        return True


    @api.multi
    def add_package(self,form_id,tree_id,package_id):
        
        form_obj = self.env['hr.employee.onboarding'].search([('id' , '=' , form_id)])
        if int(tree_id)!=0:
            remove_obj = self.env['background.check.package'].search([('id' , '=' , tree_id)])  

            if remove_obj:
                for rec in remove_obj.item.services:
                    check_id=self.env['background.check'].search([('item','=',rec.id),('background_check_id','=',int(form_id))], limit=1)
                    if check_id:
                        check_id.unlink()
            download=self.env['background.check.download'].search([('item','=',remove_obj.item.id),('background_check_download_id','=',int(form_id))], limit=1)
           
            if download:
                download.unlink()
            
            remove_obj.item=int(package_id)
            
            package_obj = self.env['background.config'].search([('id' , '=' , package_id)])
            package_list = []
            package_list.append((0,0,{'item' : package_obj}))
            if package_obj.basic_package:
                services_list = []
                for rec in package_obj.services:
                    services_list.append((0,0,{'item' : rec}))    
                form_obj.background_check_ids = services_list
                form_obj.background_check_download_ids = package_list
            
        else:
            package_obj = self.env['background.config'].search([('id' , '=' , package_id)])
            package_list = []
            package_list.append((0,0,{'item' : package_obj}))
            if package_obj.basic_package:
                services_list = []
                for rec in package_obj.services:
                    services_list.append((0,0,{'item' : rec}))    
                form_obj.background_check_ids = services_list
                form_obj.background_check_package_ids = package_list
                form_obj.background_check_download_ids = package_list

        return True


    @api.multi
    def add_service(self,form_id,tree_id,service_id):
        
        form_obj = self.env['hr.employee.onboarding'].search([('id' , '=' , form_id)])
        if int(tree_id)!=0:
            remove_obj = self.env['background.check'].search([('id' , '=' , tree_id)]) 
            if remove_obj:
                remove_download_obj = self.env['background.check.download'].search([('item','=',remove_obj.item.id),('background_check_download_id','=',int(form_id))],limit=1)
                
                if remove_download_obj:
                    remove_download_obj.unlink()
                remove_obj.item = int(service_id)
                remove_obj.status_id = ''
            service_list = []
            service_list.append((0,0,{'item' : service_id}))

            form_obj.background_check_download_ids = service_list

        else:
            service_obj = self.env['background.config'].search([('id' , '=' , service_id)])
            service_list = []
            service_list.append((0,0,{'item' : service_obj}))
            if service_list:
                form_obj.background_check_ids = service_list
                form_obj.background_check_download_ids = service_list

        return True

    
    @api.onchange('first_name', 'last_name')
    def onchange_name(self):
        self.name = str(self.first_name + self.last_name)

    @api.multi
    def write(self, vals):

        if vals.get('contract_type'):
            if int(vals.get('contract_type')) == self.company.eligible_for_benefits.id:
                vals['benefits_states'] = 'pending'
            else:
                vals['benefits_states'] = 'not_eligible'
        
        if vals.get('dob'):
            today = datetime.now().date()
            birthday = datetime.strptime(vals.get('dob'), '%Y-%m-%d').date()
            if today.month>birthday.month:
                vals['age'] = today.year - birthday.year
            elif today.day>birthday.day and today.month==birthday.month:
                vals['age'] = today.year - birthday.year
            else:
                vals['age'] = today.year - birthday.year-1

        
        if vals.get('job_seniority_title'):
            if self.welcome_mail_ids:
                [x.unlink() for x in self.welcome_mail_ids]
            if self.applicant_background_ids:
                [x.unlink() for x in self.applicant_background_ids]
            if self.employer_background_ids:
                [x.unlink() for x in self.employer_background_ids]
            if self.background_check_ids:
                [x.unlink() for x in self.background_check_ids]
            if self.consent_form_ids:
                [x.unlink() for x in self.consent_form_ids]
            if self.welcome_benefit_survey_ids:
                [x.unlink() for x in self.welcome_benefit_survey_ids]
            if self.background_check_download_ids:
                [x.unlink() for x in self.background_check_download_ids]
            if self.background_check_package_ids:
                [x.unlink() for x in self.background_check_package_ids]

            if self.company.default_service:    
                services_list = []
                package_list = []
                for item in self.company.default_service:
                    if item.basic_package:
                        package_list.append((0,0,{'item' : item}))
                        for rec in item.services:
                            services_list.append((0,0,{'item' : rec}))
                    else:
                        services_list.append((0,0,{'item' : item}))
                
                self.background_check_ids = services_list
                self.background_check_package_ids = package_list


            if self.company.default_service:   
                download_list = []
                for item in self.company.default_service:
                    download_list.append((0,0,{'item' : item}))

                self.background_check_download_ids = download_list


            if self.company.benefits_survey:
                benefit_survey_list = []
                if self.contract_type == self.company.eligible_for_benefits:
                    benefit_survey_list.append((0,0,{'survey' : self.company.benefits_survey}))

                    self.welcome_benefit_survey_ids = benefit_survey_list

            x = datetime.strptime(self.start_date, '%Y-%m-%d').year
            emp_doc_obj = self.env['employee.settings'].search([('calendar_year' , '=' , str(x)),('emp_contract_type' , 'in' , [self.contract_type.id]),('country' , '=' , self.country.id)])
            non_emp_doc_obj = self.env['employee.settings'].search([('calendar_year' , '=' , str(x)),('non_emp_contract_type' , 'in' , [self.contract_type.id]),('country' , '=' , self.country.id)])

            if emp_doc_obj.applicant_i9_template_id:
                document_obj =[]
                document_obj.append((0,0,{'document': emp_doc_obj.applicant_i9_template_id}))

                self.applicant_background_ids = document_obj

            if emp_doc_obj.employer_i9_template_id:
                document_obj =[]
                document_obj.append((0,0,{'document': emp_doc_obj.employer_i9_template_id}))

                self.employer_background_ids = document_obj

            if emp_doc_obj.direct_deposit_template:
                document_obj = []
                document_obj.append((0,0,{'document' : emp_doc_obj.direct_deposit_template}))

                self.welcome_mail_ids = document_obj

            if self.company.handbook_template:
                document_obj = []
                document_obj.append((0,0,{'document' : self.company.handbook_template}))

                self.welcome_mail_ids = document_obj


            if emp_doc_obj :
                documents_list = []
                document_obj = []
                
                
                if emp_doc_obj.emp_consent_form:
                    for rec in emp_doc_obj.emp_consent_form:
                        doc_vals = self.env['signature.request.template'].search([('id','=',rec.id)])
                        documents_list.append(({'document': doc_vals}))
                    for record in documents_list:
                        for item in record['document']:
                            document_obj.append((0,0,{'consent_form': item}))
    
                documents_list = []
                consent_obj = self.env['employee.config'].search([('state_name' , '=' , self.state.id),('emp_details_id','=',emp_doc_obj.id)])
                if consent_obj:
                    for rec in consent_obj.employee_consent_document:
                        doc_vals = self.env['signature.request.template'].search([('id','=',rec.id)])
                        documents_list.append(({'document': doc_vals}))

                        for record in documents_list:
                            for item in record['document']:
                                document_obj.append((0,0,{'consent_form': item}))
                self.consent_form_ids = document_obj


            if emp_doc_obj:
                emp_config_obj = self.env['employee.config'].search([('state_name' , '=' ,self.state.id),('emp_details_id','=',emp_doc_obj.id)])
                document_obj = []
                documents_list = []
                job_seniority_title_obj = self.env['hr.job.seniority.title'].browse(vals.get('job_seniority_title'))

                if job_seniority_title_obj.documents_template_ids:

                    documents_list = []
                    for value in job_seniority_title_obj.documents_template_ids:
                        doc_obj = self.env['signature.request.template'].search([('id','=',value.id)])
                        
                    for item in doc_obj:
                        documents_list.append(({'document':item}))

                    for record in documents_list:
                        for item in record['document']:
                            document_obj.append((0,0,{'document': item}))

                if emp_doc_obj.emp_tax_doc:
                    documents_list = []
                    for rec in emp_doc_obj.emp_tax_doc:
                        doc_vals = self.env['signature.request.template'].search([('id','=',rec.id)])
                        documents_list.append(({'document': doc_vals}))

                    for record in documents_list:
                        for item in record['document']:
                            document_obj.append((0,0,{'document': item}))

                if emp_config_obj:
                    documents_list = []
                    for line in emp_config_obj[0].emp_tax_document:
                        doc_vals = self.env['signature.request.template'].search([('id','=',line.id)])
                        documents_list.append(({'document': doc_vals}))

                    for record in documents_list:
                        for item in record['document']:
                            document_obj.append((0,0,{'document': item}))

                self.welcome_mail_ids = document_obj

            if non_emp_doc_obj:
                non_emp_config_obj = self.env['employee.config'].search([('state_name' , '=' ,self.state.id),('emp_details_id','=',emp_doc_obj.id)])
                document_obj = []
                documents_list = []
                job_seniority_title_obj = self.env['hr.job.seniority.title'].browse(vals.get('job_seniority_title'))
                if job_seniority_title_obj.documents_template_ids:
                    for value in job_seniority_title_obj.documents_template_ids:
                        doc_obj = self.env['signature.request.template'].search([('id','=',value.id)])
                        
                    for item in doc_obj:
                        documents_list.append(({'document':item}))

                    for record in documents_list:
                        for item in record['document']:
                            document_obj.append((0,0,{'document': item}))

                if emp_doc_obj.non_emp_tax_doc:
                    for rec in emp_doc_obj.non_emp_tax_doc:
                        doc_vals = self.env['signature.request.template'].search([('id','=',rec.id)])
                        documents_list.append(({'document': doc_vals}))

                    for record in documents_list:
                        for item in record['document']:
                            document_obj.append((0,0,{'document': item}))

                if non_emp_config_obj:
                    for line in non_emp_config_obj[0].non_emp_tax_document:
                        doc_vals = self.env['signature.request.template'].search([('id','=',line.id)])
                        documents_list.append(({'document': doc_vals}))

                    for record in documents_list:
                        for item in record['document']:
                            document_obj.append((0,0,{'document': item}))

                self.welcome_mail_ids = document_obj


        if vals.get('state_id') == 'benefits':
            self.benefits_enrollment_delay = self.company.benefits_enrollment_delay or 0
        
        
        res = super(HrOnboarding, self).write(vals)
   
        applicant=self.env['hr.applicant'].search([('id','=',self.applicant_id)])
        if applicant.partner_id:
            if vals.get('city'):
                    applicant.partner_id.city = vals.get('city')
            if vals.get('state'):
                    applicant.partner_id.state_id = vals.get('state')
            if vals.get('street'):
                    applicant.partner_id.street = vals.get('street')
            if vals.get('street2'):
                    applicant.partner_id.street2 = vals.get('street2')
            if vals.get('country'):
                    applicant.partner_id.country_id = vals.get('country')
            if vals.get('zip'):
                    applicant.partner_id.zip = vals.get('zip')
            if vals.get('no_of_children'):
                    if self.new_employee_id:
                        self.new_employee_id.children = vals.get('no_of_children')
                    
                    
        return res


    def get_started_info(self, form_id):
        vals = self.env['hr.employee.onboarding'].search([('id','=',form_id)])
        con_type = self.env['hr.contract.type'].search([])
        contract_types_dict={}
        for lines in con_type:
            contract_types_dict.update({lines.id:lines.name})
        get_started_dict = {
                'name' : vals.name or '',
                'mail' : vals.mail or '',
                'phone' : vals.phone or '',
                'responsible' : vals.responsible.name or '',
                'applied_job' : vals.applied_job.name or '',
                'company' : vals.company.name or '',
                'applicant_id' : vals.applicant_id,
                'expected_salary': vals.expected_salary or 0.00,
                'proposed_salary' : vals.proposed_salary or 0.00,
                'available' : vals.available or '',
                'contract_type' : vals.contract_type.id or '',
                'pay_type' : vals.pay_type or '',
                'contract_type_disp' : contract_types_dict,
                'priority' : vals.priority,
                'score' : self.env['hr.applicant'].search([('id','=',vals.applicant_id)]).score or 0.00,
                } 
        return get_started_dict
    
    def insert_records_get_started(self,form_id,get_started,from_pid=None):
        print 'fsdjf;lsfjmslf;s'
        get_started_obj = self.env['hr.employee.onboarding'].search([('id' , '=' , form_id)])
        if get_started['con_typ']:
            get_started_obj.contract_type=get_started['con_typ']
            get_started_obj.emp_status = get_started['con_typ']
        if get_started['pay_typ']:
            get_started_obj.pay_type=get_started['pay_typ']

        if not get_started_obj.pid_document_id:

            return get_started_obj.substate_id

        else:
            if get_started_obj.substate_id == 'started' and from_pid==1:
                get_started_obj.substate_id = 'personal'
            # else:
            #     raise ValidationError('Status is not updated please contact support team')

            if get_started_obj.substate_id == 'started' and get_started_obj.state_id == 'offer':
                get_started_obj.substate_id = 'personal'
            # else:
            #     raise ValidationError('Status is not updated please contact support team')


         
    
    def personalinfo(self,form_id):
        vals = self.env['hr.employee.onboarding'].search([('id','=',form_id)])
        country = self.env['res.country'].search([])
        country_dict={}
        for lines in country:
            country_dict.update({lines.id:lines.name})
        state = self.env['res.country.state'].search([])
        state_dict={}
        for lines in state:
            state_dict.update({lines.id:lines.name})
        personal_info_dict = {
                'id_no' : vals.id_number or '',
                'passport_no' : vals.passport_number or '',
                'dl_no' : vals.dl_number or '',
                'street' : vals.street or '',
                'street2' : vals.street2 or '',
                'city' : vals.city or '',
                'state' : vals.state.id or '',
                'country_id' : vals.country.id or '',
                'zip' : vals.zip or '',
                'first_name_alias' : vals.first_name_alias or '',
                'middle_name_alias' : vals.middle_name_alias or '',
                'last_name_alias' : vals.last_name_alias or '',
                'emergency_contact_name' : vals.emergency_contact_name or '',
                'emergency_contact_phone' : vals.emergency_contact_phone or '',
                'emergency_contact_relationship' : vals.emergency_contact_relationship or '',
                'gender' : vals.gender or '',
                'place_of_birth' : vals.place_of_birth or '',
                'nationality' : vals.nationality.id or '',
                'birth_country' : vals.birth_country.id or '',
                'marital_status': vals.marital_status or '',
                'filing_status': vals.filing_staus or '',
                'children' : vals.no_of_children or '',
                'ethnic_id' : vals.ethnic_id or '',
                'smoker' : vals.smoker or '',
                'dob' : vals.dob or '',
                'age' : vals.age or '',
                # 'notes' : vals.notes or '',
                'country' : country_dict,
                'state_dict' : state_dict,
            }
        
        return personal_info_dict

    def change_state_name(self,country_id):
        country_obj = self.env['res.country.state'].search([('country_id.id' , '=' , country_id)])
        state_dict = {}
        for lines in country_obj:
            state_dict.update({lines.id:lines.name})

        return state_dict

    def change_country_name(self,state_id):
        state_obj = self.env['res.country.state'].search([('id' , '=' , state_id)])
        print state_obj.country_id

        return state_obj.country_id.id

        return state_dict
       
    def insert_records_personal_info(self,form_id,personal_info):
        personal_info_obj = self.env['hr.employee.onboarding'].search([('id' , '=' , form_id)])
        if (personal_info['id_no']):
            personal_info_obj.id_number = personal_info['id_no']
        if (personal_info['passport_no']):
            personal_info_obj.passport_number = personal_info['passport_no']
        if (personal_info['dl_no']):
            personal_info_obj.dl_number = personal_info['dl_no']
        if (personal_info['street']):
            personal_info_obj.street = personal_info['street']
        if (personal_info['street2']):
            personal_info_obj.street2 = personal_info['street2']
        if (personal_info['city']):
            personal_info_obj.city = personal_info['city']
        if (personal_info['state']):
            personal_info_obj.state = personal_info['state']
        if (personal_info['country']):
            personal_info_obj.country = personal_info['country']
        if (personal_info['zip']):
            personal_info_obj.zip = personal_info['zip']
        if (personal_info['fst_name_alias']):
            personal_info_obj.first_name_alias = personal_info['fst_name_alias']
        if (personal_info['mid_name_alias']):
            personal_info_obj.middle_name_alias = personal_info['mid_name_alias']
        if (personal_info['lst_name_alias']):
            personal_info_obj.last_name_alias = personal_info['lst_name_alias']
        if (personal_info['emergency_contact_name']):
            personal_info_obj.emergency_contact_name = personal_info['emergency_contact_name']
        if (personal_info['emergency_contact_phone']):
            personal_info_obj.emergency_contact_phone = personal_info['emergency_contact_phone']
        if (personal_info['emergency_contact_relationship']):
            personal_info_obj.emergency_contact_relationship = personal_info['emergency_contact_relationship']
        if (personal_info['gender']):
            personal_info_obj.gender = personal_info['gender']
        if (personal_info['place_of_birth']):
            personal_info_obj.place_of_birth = personal_info['place_of_birth']
        if (personal_info['marital_sts']):
            personal_info_obj.marital_status = personal_info['marital_sts']
        if (personal_info['filing_sts']):
            personal_info_obj.filing_staus = personal_info['filing_sts']
        if (personal_info['noc']):
            personal_info_obj.no_of_children = personal_info['noc']
        if (personal_info['ethnic']):
            personal_info_obj.ethnic_id = personal_info['ethnic']
        if (personal_info['nationality']):
            personal_info_obj.nationality = personal_info['nationality']
        if (personal_info['birth_country']):
            personal_info_obj.birth_country = personal_info['birth_country']
        if (personal_info['smoker']):
            personal_info_obj.smoker = personal_info['smoker']
        if (personal_info['age']):
            personal_info_obj.age = personal_info['age']
        if (personal_info['dob']):
            personal_info_obj.dob = personal_info['dob']
        # if (personal_info['notes']):
        #     personal_info_obj.notes = personal_info['notes']
        # if personal_info['image']:
        #     print type(toBinary(personal_info['image']))
        #     personal_info_obj.image = base64.b64decode(personal_info['image'])
        # lst = str(personal_info['image']).split(',')
        # self.env['ir.attachment'].create({
        #                                     'res_id':int(form_id),
        #                                     'res_model':'hr.employee.onboarding',
        #                                     'index_content':'image',
        #                                     'type':'binary',
        #                                     'db_datas':lst[1],
        #                                     'res_field':'image',
        #                                     'name':'image',
        #                                 })

        if personal_info_obj.substate_id == 'personal'and personal_info_obj.state_id == 'offer':
            personal_info_obj.substate_id = 'experience'
        # else:
        #     raise ValidationError('Status is not updated please contact support team')

        return personal_info_obj.substate_id
         
        
    def experienceinfo(self,form_id):
        vals = self.env['hr.employee.onboarding'].search([('id','=',form_id)])

        state = self.env['res.country.state'].search([('country_id' , '=' , vals.applied_job.company_id.country_id.id)])
        
        state_dict={}
        for lines in state:
            state_dict.update({lines.id:lines.name})
        
        exp_academic_list=[]
        for line in vals.academic_experience_ids:
            exp_academic_list.append({
                'academic_tree_id' : line.id or '',
                'academic_experience' : line.academic_experience or '',
                'institute' : line.institute or '',
                'diploma' : line.diploma or '',
                'field_of_study' : line.field_of_study or '',
                'start_date' : line.start_date or '',
                'end_date' : line.end_date or '',
            })
            
        exp_professional_list=[]
        for line in vals.professional_experience_ids:
            exp_professional_list.append({
                'professional_tree_id' : line.id or '',
                'position' : line.position or '',
                'employer' : line.employer or '',
                'start_date' : line.start_date or '',
                'end_date' : line.end_date or '',
            })
            
        exp_certificate_list=[]
        for line in vals.certification_ids:
            exp_certificate_list.append({
                'certification_tree_id' : line.id or '',
                'certifications' : line.certifications or '',
                'certificate_code' : line.certificate_code or '',
                'issued_by' : line.issued_by or '',
                'professional_license' : line.professional_license or '',
                'state_issued_id' : line.state_issued_id.id or '',
                'start_date' : line.start_date or '',
                'end_date' : line.end_date or '',
            })
        
        experience_info_dict = {
                'exp_academic_list' : exp_academic_list or '',
                'exp_professional_list' : exp_professional_list or '',
                'exp_certificate_list' : exp_certificate_list or '',
                'state_dict' : state_dict or '',
            }
    
        return experience_info_dict
    
    def insert_records_experience_academic_info(self,form_id,offer_accepted_academic_info):

        if int(offer_accepted_academic_info['academic_tree_id'])>0:
            academic_info_obj = self.env['academic.experience'].search([('id' , '=' , offer_accepted_academic_info['academic_tree_id'])])
            if (offer_accepted_academic_info['academic_exp']):
                academic_info_obj.academic_experience = offer_accepted_academic_info['academic_exp']
            if (offer_accepted_academic_info['academic_institution']):
                academic_info_obj.institute = offer_accepted_academic_info['academic_institution']
            if (offer_accepted_academic_info['academic_diploma']):
                academic_info_obj.diploma = offer_accepted_academic_info['academic_diploma']
            if (offer_accepted_academic_info['academic_fos']):
                academic_info_obj.field_of_study = offer_accepted_academic_info['academic_fos']
            if (offer_accepted_academic_info['academic_start']):
                academic_info_obj.start_date = offer_accepted_academic_info['academic_start']
            if (offer_accepted_academic_info['academic_end']):
                academic_info_obj.end_date = offer_accepted_academic_info['academic_end']        
                 
        else:
            if (offer_accepted_academic_info['academic_exp'] or offer_accepted_academic_info['academic_institution'] or offer_accepted_academic_info['academic_diploma']):
                academic_info_obj = self.env['academic.experience'].create({
                    'academic_experience' : offer_accepted_academic_info['academic_exp'],
                    'institute' : offer_accepted_academic_info['academic_institution'],
                    'diploma' : offer_accepted_academic_info['academic_diploma'],
                    'field_of_study' : offer_accepted_academic_info['academic_fos'] or '',
                    'start_date' : offer_accepted_academic_info['academic_start'] or False,
                    'end_date' : offer_accepted_academic_info['academic_end'] or False,
                    'academic_experience_id':form_id
                    })   
        
    
    def insert_records_experience_professional_info(self,form_id,offer_accepted_professional_info):
        
        if int(offer_accepted_professional_info['professional_tree_id'])>0:
            professional_info_obj = self.env['professional.experience'].search([('id' , '=' , offer_accepted_professional_info['professional_tree_id'])])
            if (offer_accepted_professional_info['position']):
                professional_info_obj.academic_experience = offer_accepted_professional_info['position']
            if (offer_accepted_professional_info['employer']):
                professional_info_obj.institute = offer_accepted_professional_info['employer']
            if (offer_accepted_professional_info['professional_start']):
                professional_info_obj.start_date = offer_accepted_professional_info['professional_start']
            if (offer_accepted_professional_info['professional_end']):
                professional_info_obj.end_date = offer_accepted_professional_info['professional_end']        
                 
        else:
            if (offer_accepted_professional_info['position'] or offer_accepted_professional_info['employer']):
                professional_info_obj = self.env['professional.experience'].create({
                    'position' : offer_accepted_professional_info['position'],
                    'employer' : offer_accepted_professional_info['employer'],
                    'start_date' : offer_accepted_professional_info['professional_start'] or False,
                    'end_date' : offer_accepted_professional_info['professional_end'] or False,
                    'professional_experience_id':form_id
                    })    
                
    
    def insert_records_experience_certification_info(self,form_id,offer_accepted_certificate_info):
        
        if int(offer_accepted_certificate_info['certificate_tree_id'])>0:
            certification_info_obj = self.env['certification.details'].search([('id' , '=' , offer_accepted_certificate_info['certificate_tree_id'])])
            if (offer_accepted_certificate_info['certificate']):
                certification_info_obj.academic_experience = offer_accepted_certificate_info['certificate']
            if (offer_accepted_certificate_info['certificate_no']):
                certification_info_obj.institute = offer_accepted_certificate_info['certificate_no']
            if (offer_accepted_certificate_info['issued_by']):
                certification_info_obj.diploma = offer_accepted_certificate_info['issued_by']
            if (offer_accepted_certificate_info['professional_license']) != '':
                certification_info_obj.professional_license = offer_accepted_certificate_info['professional_license']
            if (offer_accepted_certificate_info['state_issued_id']):
                certification_info_obj.state_issued_id = offer_accepted_certificate_info['state_issued_id']
            if (offer_accepted_certificate_info['certificate_start']):
                certification_info_obj.start_date = offer_accepted_certificate_info['certificate_start']
            if (offer_accepted_certificate_info['certificate_end']):
                certification_info_obj.end_date = offer_accepted_certificate_info['certificate_end']        
                 
        else:
            if (offer_accepted_certificate_info['certificate'] or offer_accepted_certificate_info['certificate_no'] or offer_accepted_certificate_info['issued_by']):
                certification_info_obj = self.env['certification.details'].create({
                    'certifications' : offer_accepted_certificate_info['certificate'],
                    'certificate_code' : offer_accepted_certificate_info['certificate_no'],
                    'issued_by' : offer_accepted_certificate_info['issued_by'],
                    'professional_license' : offer_accepted_certificate_info['professional_license'],
                    'state_issued_id' : offer_accepted_certificate_info['state_issued_id'],
                    'start_date' : offer_accepted_certificate_info['certificate_start'] or False,
                    'end_date' : offer_accepted_certificate_info['certificate_end'] or False,
                    'certification_id':form_id
                    })    
        certification_info_obj = self.env['hr.employee.onboarding'].search([('id' , '=' , form_id)])
        
        # if certification_info_obj.substate_id == 'experience' and certification_info_obj.state_id == 'offer':
        #     certification_info_obj.substate_id = 'employement'
        # else:
        #     raise ValidationError('Status is not updated please contact support team')

    
    def employementinfo(self,form_id):
        vals = self.env['hr.employee.onboarding'].search([('id','=',form_id)])
        job_seniority = self.env['hr.job.seniority.title'].search([('id','in',vals.applied_job.job_template.job_seniority_id.ids)])
        job_seniority_title_dict = {}
        for values in job_seniority:
            job_seniority_title_dict.update({values.id:values.name})
        con_type = self.env['hr.contract.type'].search([])
        contract_types_dict={}
        for lines in con_type:
            contract_types_dict.update({lines.id:lines.name})
        employement_info_dict = {
                'contract_type' : vals.contract_type.id or '',
                'emp_start_date' : vals.emp_start_date or '',
                'benifits_seniority_date' : vals.benifits_seniority_date or '',
                'job_seniority_title' : vals.job_seniority_title.id or '',
                'job_seniority_title_disp' : job_seniority_title_dict,
                'contract_type_disp' : contract_types_dict,
            }
    
        return employement_info_dict
       
    def insert_records_employement_info(self,form_id,employement_info):
        employment_info_obj = self.env['hr.employee.onboarding'].search([('id' , '=' , form_id)])
        if employement_info['job_seniority_title']:
            employment_info_obj.job_seniority_title = int(employement_info['job_seniority_title'])
        if employement_info['start_date']:
            employment_info_obj.emp_start_date = employement_info['start_date']
        # if employement_info['benefits_seniority_date']:
        #     employment_info_obj.benifits_seniority_date = employement_info['benefits_seniority_date']
        
        if employment_info_obj.substate_id == 'employement' and employment_info_obj.state_id == 'offer':
            employment_info_obj.substate_id = 'offer_summary'
        # else:
        #     raise ValidationError('Status is not updated please contact support team')

        if employment_info_obj.job_seniority_title and employment_info_obj.emp_start_date:

            return True

    
    def offer_summary(self, form_id):
        vals = self.env['hr.employee.onboarding'].search([('id','=',form_id)])
        emp_sts = self.env['hr.contract.type'].search([])
        emp_sts_dict={}
        for lines in emp_sts:
            emp_sts_dict.update({lines.id:lines.name})
        

        state = self.env['res.country'].search([])
        state_dict={}
        for lines in state:
            state_dict.update({lines.id:lines.name})

        exp_academic_list=[]
        for line in vals.academic_experience_ids:
            exp_academic_list.append({
                'academic_tree_id' : line.id or '',
                'academic_experience' : line.academic_experience or '',
                'institute' : line.institute or '',
                'diploma' : line.diploma or '',
                'field_of_study' : line.field_of_study or '',
                'start_date' : line.start_date or '',
                'end_date' : line.end_date or '',
            })
            
        exp_professional_list=[]
        for line in vals.professional_experience_ids:
            exp_professional_list.append({
                'professional_tree_id' : line.id or '',
                'position' : line.position or '',
                'employer' : line.employer or '',
                'start_date' : line.start_date or '',
                'end_date' : line.end_date or '',
            })
            
        exp_certificate_list=[]
        for line in vals.certification_ids:
            exp_certificate_list.append({
                'certification_tree_id' : line.id or '',
                'certifications' : line.certifications or '',
                'certificate_code' : line.certificate_code or '',
                'issued_by' : line.issued_by or '',
                'professional_license' : line.professional_license or '',
                'state_issued_id' : line.state_issued_id.name or '',
                'start_date' : line.start_date or '',
                'end_date' : line.end_date or '',
            })
            
        offer_summary_dict = {
                'name' : vals.name or '',
                'mail' : vals.mail or '',
                'phone' : vals.phone or '',
                'responsible' : vals.responsible.name or '',
                'applied_job' : vals.applied_job.name or '',
                'company' : vals.company.name or '',
                'applicant_id' : vals.applicant_id,
                'emp_status': vals.emp_status.id or '',
                'id_no' : vals.id_number or '',
                'passport_no' : vals.passport_number or '',
                'street' : vals.street or '',
                'street2' : vals.street2 or '',
                'city' : vals.city or '',
                'state' : vals.state.name or '',
                'country_id' : vals.country.name or '',
                'zip' : vals.zip or '',
                'gender' : vals.gender,
                'marital_status': vals.marital_status or '',
                'filing_status': vals.filing_staus or '',
                'children' : vals.no_of_children or '',
                'dob' : vals.dob or '',
                'age' : vals.age or '',
                'emp_start_date' : vals.emp_start_date or '',
                'job_seniority_title' : vals.job_seniority_title.name or '',
                'benifits_seniority_date' : vals.benifits_seniority_date or '',
                'place_of_birth' : vals.place_of_birth or '',
                'nationality' : vals.nationality.name or '',
                'birth_country' : vals.birth_country.name or '',
                'scheduled_hours' : vals.scheduled_hours or '',
                'pay_rate' : vals.pay_rate or '',
                'emp_sts_disp' : emp_sts_dict,
                'exp_academic_list' : exp_academic_list or '',
                'exp_professional_list' : exp_professional_list or '',
                'exp_certificate_list' : exp_certificate_list or '',
                'state_dict' : state_dict or '',
                } 

        return offer_summary_dict
    
    def summary_state(self,form_id,summary_info):
        summary_obj = self.env['hr.employee.onboarding'].search([('id' , '=' , form_id)])
        if (summary_info['summary_employment_status']):
            summary_obj.emp_status = summary_info['summary_employment_status']
        if (summary_info['summary_scheduled_hours']):
            summary_obj.scheduled_hours = summary_info['summary_scheduled_hours']
        if (summary_info['summary_pay_rate']):
            summary_obj.pay_rate = summary_info['summary_pay_rate']
        
        if summary_obj.substate_id == 'offer_summary' and summary_obj.state_id == 'offer':
            summary_obj.substate_id = 'consent'
            summary_obj.state_id = 'background'
        # else:
        #     raise ValidationError('Status is not updated please contact support team')
       
    
    def inineinfo(self,form_id):
        vals = self.env['hr.employee.onboarding'].search([('id','=',form_id)])
        doc = self.env['signature.request.template'].search([])
        document_dict = {}
        for values in doc:
            document_dict.update({values.id:values.attachment_id.name})
        
        applicant_list=[]
        for line in vals.applicant_background_ids:
            applicant_list.append({
                'applicant_tree_id' : line.id or '',
                'document' : line.document.id or '',
                'doc_link' : line.doc_link or '',
                'status_id' : line.status_id or '',
                'date_sent' : line.date_sent or '',
                'expiration' : line.expiration or '',
            })
            
        employer_list=[]
        for line in vals.employer_background_ids:
            employer_list.append({
                'employer_tree_id' : line.id or '',
                'document' : line.document.id or '',
                'doc_link' : line.doc_link or '',
                'status_id' : line.status_id or '',
                'date_sent' : line.date_sent or '',
                'expiration' : line.expiration or '',
            }) 
            
        # everify_case_result_list=[]
        # for line in vals.everify_case_result_ids:
        #     everify_case_result_list.append({
        #         'everify_case_result_tree_id' : line.id or '',
        #         'case_number' : line.case_number or '',
        #         'status' : line.status or '',
        #         'message_code' : line.message_code or '',
        #         'eligiblity_statement' : line.eligiblity_statement or '',
        #         'statement_details' : line.statement_details or '',
        #         'date_sent' : line.date_sent or '',
        #         'date_received' : line.date_received or '',
        #         'case_status' : line.case_status or '',
        #         'everify_download_url' : line.everify_download_url or '',
        #     })  

        # everify_case_result_url=[]
        # for line in vals.everify_case_result_ids:
        #     if line.message_code == 27 or line.message_code == 29 or line.message_code == 38:
        #         everify_case_result_url.append({
        #             'everify_download_url' : line.everify_download_url or '',
        #             })            

        inine_info_dict = {
                'doc_disp' : document_dict,
                'applicant_list' : applicant_list or '',
                'employer_list' : employer_list or '',
                # 'everify_case_result_list' : everify_case_result_list or '',
                # 'everify_case_result_url' : everify_case_result_url or '',
            }
    
        return inine_info_dict

    # def everify_check_redirect(self,form_id):
    #     onboarding_obj = self.env['hr.employee.onboarding'].search([('id','=',int(form_id))])
        
    #     onboard_list =[]
    #     for line in onboarding_obj.applicant_background_ids:
    #         if line.status_id != 'signed':
    #             onboard_list.append(line.id)

    #     for row in onboarding_obj.employer_background_ids:
    #         if row.status_id != 'signed':
    #             onboard_list.append(row.id)
        
    #     if onboard_list:
    #         return 'status'
    #     else:
    #         onboarding_obj.everify_check_initiate()

    # def everify_check_initiate(self):

    #     print '--Test--'

    #     return


    # def close_everify_case(self,form_id,reason_val):
    #     everify_case_obj = self.env['everify.case.result'].search([('everify_case_result_id','=',int(form_id))])  

    #     for line in everify_case_obj:
    #         print line.case_status,'---'
    #         if line.case_status == False:
    #             line.case_status = reason_val

    #     return 1

    
    def insert_records_inine_applicant_info(self,form_id,inine_applicant_info_vals):
        if int(inine_applicant_info_vals['applicant_tree_id'])>0:
            inine_app_info_obj = self.env['applicant.background'].search([('id' , '=' , inine_applicant_info_vals['applicant_tree_id'])])
            if (inine_applicant_info_vals['form_applicant_documents']):
                inine_app_info_obj.document = inine_applicant_info_vals['form_applicant_documents']
            if (inine_applicant_info_vals['applicant_link']):
                inine_app_info_obj.doc_link = inine_applicant_info_vals['applicant_link']
            # if (inine_applicant_info_vals['applicant_status']):
            #     inine_app_info_obj.status_id = inine_applicant_info_vals['applicant_status']
            if (inine_applicant_info_vals['applicant_date_sent']):
                inine_app_info_obj.date_sent = inine_applicant_info_vals['applicant_date_sent']

            if inine_app_info_obj.status_id != 'canceled':
                if (inine_applicant_info_vals['applicant_expiration']):
                    inine_app_info_obj.expiration = inine_applicant_info_vals['applicant_expiration']  

            elif inine_app_info_obj.status_id == 'canceled' and str(inine_applicant_info_vals['applicant_expiration']) != str(inine_app_info_obj.expiration):
                if (inine_applicant_info_vals['applicant_expiration']):
                    inine_app_info_obj.expiration = inine_applicant_info_vals['applicant_expiration']  

            else:
                inine_app_info_obj.expiration = ''

            return inine_app_info_obj.id     
                 
        else:
            if (inine_applicant_info_vals['form_applicant_documents'] or inine_applicant_info_vals['applicant_link'] or inine_applicant_info_vals['applicant_status']):
                inine_app_info_obj = self.env['applicant.background'].create({
                    'document' : inine_applicant_info_vals['form_applicant_documents'],
                    'doc_link' : inine_applicant_info_vals['applicant_link'],
                    'status_id' : inine_applicant_info_vals['applicant_status'],
                    'date_sent' : inine_applicant_info_vals['applicant_date_sent'] or False,
                    'expiration' : inine_applicant_info_vals['applicant_expiration'] or False,
                    'applicant_background_id':form_id
                    })  
                return inine_app_info_obj.id
    
    def insert_records_inine_employer_info(self,form_id,inine_employer_info_vals):
        if int(inine_employer_info_vals['employer_tree_id'])>0:
            inine_emp_info_obj = self.env['employer.background'].search([('id' , '=' , inine_employer_info_vals['employer_tree_id'])])
            if (inine_employer_info_vals['form_employer_documents']):
                inine_emp_info_obj.document = inine_employer_info_vals['form_employer_documents']
            if (inine_employer_info_vals['employer_link']):
                inine_emp_info_obj.doc_link = inine_employer_info_vals['employer_link']
            # if (inine_employer_info_vals['employer_status']):
            #     inine_emp_info_obj.status_id = inine_employer_info_vals['employer_status']
            if (inine_employer_info_vals['employer_date_sent']):
                inine_emp_info_obj.date_sent = inine_employer_info_vals['employer_date_sent']

            if inine_emp_info_obj.status_id != 'canceled':
                if (inine_employer_info_vals['employer_expiration']):
                    inine_emp_info_obj.expiration = inine_employer_info_vals['employer_expiration']  

            elif inine_emp_info_obj.status_id == 'canceled' and str(inine_employer_info_vals['applicant_expiration']) != str(inine_emp_info_obj.expiration):      
                if (inine_employer_info_vals['employer_expiration']):
                    inine_emp_info_obj.expiration = inine_employer_info_vals['employer_expiration'] 

            else:
                inine_emp_info_obj.expiration = ''

            return inine_emp_info_obj.id
                 
        else:
            if (inine_employer_info_vals['form_employer_documents'] or inine_employer_info_vals['employer_link'] or inine_employer_info_vals['employer_status']):
                inine_emp_info_obj = self.env['employer.background'].create({
                    'document' : inine_employer_info_vals['form_employer_documents'],
                    'doc_link' : inine_employer_info_vals['employer_link'],
                    'status_id' : inine_employer_info_vals['employer_status'],
                    'date_sent' : inine_employer_info_vals['employer_date_sent'] or False,
                    'expiration' : inine_employer_info_vals['employer_expiration'] or False,
                    'employer_background_id':form_id
                    })    
                return inine_emp_info_obj.id
            
        inine_emp_info_obj = self.env['hr.employee.onboarding'].search([('id' , '=' , form_id)])
        # if inine_emp_info_obj.substate_id == 'inine' and inine_emp_info_obj.state_id == 'to_approve':
        #     inine_emp_info_obj.substate_id = 'everify'
        # else:
        #     raise ValidationError('Status is not updated please contact support team')

    
    def consentinfo(self,form_id):
        vals = self.env['hr.employee.onboarding'].search([('id','=',form_id)])
        
        doc = self.env['signature.request.template'].search([])
        document_dict = {}
        for values in doc:
            document_dict.update({values.id:values.attachment_id.name})
        
        consent_list=[]
        for line in vals.consent_form_ids:
            consent_list.append({
                'consent_tree_id' : line.id or '',
                'document' : line.consent_form.id or '',
                'doc_link' : line.form_link or '',
                'status_id' : line.status_id or '',
                'date_sent' : line.date_sent or '',
                'expiration' : line.expiration or '',
            })
            
        consent_info_dict = {
                'consent_list' : consent_list or '',
                'doc_disp' : document_dict,
            }
    
        return consent_info_dict    
  
    def insert_records_background_consent_info(self,form_id,background_consent_info_vals):
        if int(background_consent_info_vals['consent_form_tree_id'])>0:
            background_consent_info_obj = self.env['consent.form'].search([('id' , '=' , background_consent_info_vals['consent_form_tree_id'])])
            
            if background_consent_info_obj.status_id != 'signed':
                if (background_consent_info_vals['form_consent_documents']):
                    background_consent_info_obj.consent_form = background_consent_info_vals['form_consent_documents']
                if (background_consent_info_vals['background_check_consent_form_link']):
                    background_consent_info_obj.form_link = background_consent_info_vals['background_check_consent_form_link']
                if (background_consent_info_vals['background_check_consent_form_status']):
                    background_consent_info_obj.status_id = background_consent_info_vals['background_check_consent_form_status']
                if (background_consent_info_vals['background_check_consent_form_date_sent']):
                    background_consent_info_obj.date_sent = background_consent_info_vals['background_check_consent_form_date_sent']
                if (background_consent_info_vals['background_check_consent_form_expiration']):
                    background_consent_info_obj.expiration = background_consent_info_vals['background_check_consent_form_expiration']        
            else:
                raise UserError('This document is already Signed.Please add new document and send again')
                 
        else:
            if (background_consent_info_vals['form_consent_documents'] or background_consent_info_vals['background_check_consent_form_link'] or background_consent_info_vals['background_check_consent_form_status']):
                background_consent_info_obj = self.env['consent.form'].create({
                    'consent_form' : background_consent_info_vals['form_consent_documents'],
                    'form_link' : background_consent_info_vals['background_check_consent_form_link'],
                    'status_id' : background_consent_info_vals['background_check_consent_form_status'],
                    'date_sent' : background_consent_info_vals['background_check_consent_form_date_sent'] or False,
                    'expiration' : background_consent_info_vals['background_check_consent_form_expiration'] or False,
                    'consent_form_id':form_id
                    })   
        background_consent_info_obj = self.env['hr.employee.onboarding'].search([('id' , '=' , form_id)])
        # if background_consent_info_obj.substate_id == 'consent' and background_consent_info_obj.state_id == 'background':
        #     background_consent_info_obj.substate_id = 'background'
        # else:
        #     raise ValidationError('Status is not updated please contact support team')

    
    def backgroundinfo(self,form_id):
        vals = self.env['hr.employee.onboarding'].search([('id','=',form_id)])
        
        doc = self.env['signature.request.template'].search([])
        document_dict = {}
        for values in doc:
            document_dict.update({values.id:values.attachment_id.name})

        background_check = self.env['background.check.settings'].search([('name','=',vals.company.provider.id)])
        background_dict = {}
        background_package_dict = {}
        for vals_background in background_check.background_config_ids:
            if vals_background.basic_package:
                background_package_dict.update({vals_background.id : vals_background.name})
                for item in vals_background.services:
                    background_dict.update({str(item.id) : item.name})
            else:
                background_dict.update({str(vals_background.id) : vals_background.name})

        applicant_list=[]
        for line in vals.applicant_background_ids:
            applicant_list.append({
                'applicant_tree_id' : line.id or '',
                'document' : line.document.id or '',
                'doc_link' : line.doc_link or '',
                'status_id' : line.status_id or '',
                'date_sent' : line.date_sent or '',
                'expiration' : line.expiration or '',
            })
            
        employer_list=[]
        for line in vals.employer_background_ids:
            employer_list.append({
                'employer_tree_id' : line.id or '',
                'document' : line.document.id or '',
                'doc_link' : line.doc_link or '',
                'status_id' : line.status_id or '',
                'date_sent' : line.date_sent or '',
                'expiration' : line.expiration or '',
            })
        
        background_list=[]
        for line in vals.background_check_ids:
            background_list.append({
                'background_tree_id' : line.id or '',
                'document' : line.item.id or '',
                'status_id' : line.status_id or '',
            })
        
        background_package_list=[]
        for line in vals.background_check_package_ids:
            background_package_list.append({
                'background_package_tree_id' : line.id or '',
                'document' : line.item.id or '',
            })
            
        background_info_dict = {
                'applicant_list' : applicant_list or '',
                'employer_list' : employer_list or '',
                'background_list' : background_list or '',
                'background_package_list' : background_package_list or '',
                'background_dict' : background_dict or '',
                'background_package_dict' : background_package_dict or '',
                'doc_disp' : document_dict ,
            }
    
        return background_info_dict    
    
    def insert_records_backgroundcheck_applicant_info(self,form_id,backgroundcheck_applicant_info_vals):
        backgroundcheck_app_info_obj = self.env['hr.employee.onboarding'].search([('id' , '=' , form_id)])
        # if backgroundcheck_app_info_obj.substate_id == 'background' and backgroundcheck_app_info_obj.state_id == 'background':
        #     backgroundcheck_app_info_obj.substate_id = 'back_summary'
        # else:
        #     raise ValidationError('Status is not updated please contact support team')

        if int(backgroundcheck_applicant_info_vals['applicant_tree_id'])>0:
            backgroundcheck_app_info_obj = self.env['applicant.background'].search([('id' , '=' , backgroundcheck_applicant_info_vals['applicant_tree_id'])])
            if (backgroundcheck_applicant_info_vals['form_applicant_documents']):
                backgroundcheck_app_info_obj.document = backgroundcheck_applicant_info_vals['form_applicant_documents']
            if (backgroundcheck_applicant_info_vals['applicant_link']):
                backgroundcheck_app_info_obj.doc_link = backgroundcheck_applicant_info_vals['applicant_link']
            if (backgroundcheck_applicant_info_vals['applicant_status']):
                backgroundcheck_app_info_obj.status_id = backgroundcheck_applicant_info_vals['applicant_status']
            if (backgroundcheck_applicant_info_vals['applicant_date_sent']):
                backgroundcheck_app_info_obj.date_sent = backgroundcheck_applicant_info_vals['applicant_date_sent']
            if (backgroundcheck_applicant_info_vals['applicant_expiration']):
                backgroundcheck_app_info_obj.expiration = backgroundcheck_applicant_info_vals['applicant_expiration']        
                 
        else:
            if (backgroundcheck_applicant_info_vals['form_applicant_documents'] or backgroundcheck_applicant_info_vals['applicant_link'] or backgroundcheck_applicant_info_vals['applicant_status']):
                backgroundcheck_app_info_obj = self.env['applicant.background'].create({
                    'document' : backgroundcheck_applicant_info_vals['form_applicant_documents'],
                    'doc_link' : backgroundcheck_applicant_info_vals['applicant_link'],
                    'status_id' : backgroundcheck_applicant_info_vals['applicant_status'],
                    'date_sent' : backgroundcheck_applicant_info_vals['applicant_date_sent'] or False,
                    'expiration' : backgroundcheck_applicant_info_vals['applicant_expiration'] or False,
                    'applicant_background_id':form_id
                    })    
    
    def insert_records_backgroundcheck_employer_info(self,form_id,backgroundcheck_employer_info_vals):
        backgroundcheck_emp_info_obj = self.env['hr.employee.onboarding'].search([('id' , '=' , form_id)])
        # if backgroundcheck_emp_info_obj.substate_id == 'background' and backgroundcheck_emp_info_obj.state_id == 'background':
        #     backgroundcheck_emp_info_obj.substate_id = 'back_summary'
        # else:
        #     raise ValidationError('Status is not updated please contact support team')
        
        if int(backgroundcheck_employer_info_vals['employer_tree_id'])>0:
            backgroundcheck_emp_info_obj = self.env['employer.background'].search([('id' , '=' , backgroundcheck_employer_info_vals['employer_tree_id'])])
            if (backgroundcheck_employer_info_vals['form_employer_documents']):
                backgroundcheck_emp_info_obj.document = backgroundcheck_employer_info_vals['form_employer_documents']
            if (backgroundcheck_employer_info_vals['employer_link']):
                backgroundcheck_emp_info_obj.doc_link = backgroundcheck_employer_info_vals['employer_link']
            if (backgroundcheck_employer_info_vals['employer_status']):
                backgroundcheck_emp_info_obj.status_id = backgroundcheck_employer_info_vals['employer_status']
            if (backgroundcheck_employer_info_vals['employer_date_sent']):
                backgroundcheck_emp_info_obj.date_sent = backgroundcheck_employer_info_vals['employer_date_sent']
            if (backgroundcheck_employer_info_vals['employer_expiration']):
                backgroundcheck_emp_info_obj.expiration = backgroundcheck_employer_info_vals['employer_expiration']        

                 
        else:
            if (backgroundcheck_employer_info_vals['form_employer_documents'] or backgroundcheck_employer_info_vals['employer_link'] or backgroundcheck_employer_info_vals['employer_status']):
                backgroundcheck_emp_info_obj = self.env['employer.background'].create({
                    'document' : backgroundcheck_employer_info_vals['form_employer_documents'],
                    'doc_link' : backgroundcheck_employer_info_vals['employer_link'],
                    'status_id' : backgroundcheck_employer_info_vals['employer_status'],
                    'date_sent' : backgroundcheck_employer_info_vals['employer_date_sent'] or False,
                    'expiration' : backgroundcheck_employer_info_vals['employer_expiration'] or False,
                    'employer_background_id':form_id
                    })  

    def insert_records_background_check_info(self,form_id,background_check_info_vals):
        backgroundcheck_emp_info_obj = self.env['hr.employee.onboarding'].search([('id' , '=' , form_id)])   
        # if backgroundcheck_emp_info_obj.substate_id == 'background' and backgroundcheck_emp_info_obj.state_id == 'background':
        #     backgroundcheck_emp_info_obj.substate_id = 'back_summary'
        # else:
        #     raise ValidationError('Status is not updated please contact support team')

        if int(background_check_info_vals['background_check_tree_id'])>0:
            backgroundcheck_emp_info_obj = self.env['background.check'].search([('id' , '=' , background_check_info_vals['background_check_tree_id'])])
            if (background_check_info_vals['form_background_check_documents']):
                backgroundcheck_emp_info_obj.item = background_check_info_vals['form_background_check_documents']
            if (background_check_info_vals['background_check_status']):
                backgroundcheck_emp_info_obj.status_id = background_check_info_vals['background_check_status']     
            
            return backgroundcheck_emp_info_obj.id

        else:
            if (background_check_info_vals['form_background_check_documents']):
                backgroundcheck_emp_info_obj = self.env['background.check'].create({
                    'item' : background_check_info_vals['form_background_check_documents'],
                    'status_id' : background_check_info_vals['background_check_status'],
                    'background_check_id':form_id
                    }) 


                background_check_download_obj = self.env['background.check.download'].create({
                    'item' : background_check_info_vals['form_background_check_documents'],
                    'background_check_download_id':form_id
                    })
                return backgroundcheck_emp_info_obj.id

    def insert_records_background_check_package_info(self,form_id,background_check_package_info_vals):
        backgroundcheck_emp_info_obj = self.env['hr.employee.onboarding'].search([('id' , '=' , form_id)]) 
        # if backgroundcheck_emp_info_obj.substate_id == 'background' and backgroundcheck_emp_info_obj.state_id == 'background':
        #     backgroundcheck_emp_info_obj.substate_id = 'back_summary'
        # else:
        #     raise ValidationError('Status is not updated please contact support team')

        if int(background_check_package_info_vals['background_check_package_tree_id']) > 0:
            backgroundcheck_emp_info_obj = self.env['background.check.package'].search([('id' , '=' , background_check_package_info_vals['background_check_package_tree_id'])])
            if (background_check_package_info_vals['form_background_check_package_items']):
                backgroundcheck_emp_info_obj.item = background_check_package_info_vals['form_background_check_package_items']    
            
            return backgroundcheck_emp_info_obj.id

        else:
            if background_check_package_info_vals['form_background_check_package_items']:
                backgroundcheck_emp_info_obj = self.env['background.check.package'].create({
                    'item' : background_check_package_info_vals['form_background_check_package_items'],
                    'background_check_package_id':form_id
                    })   

                background_check_download_obj = self.env['background.check.download'].create({
                    'item' : background_check_package_info_vals['form_background_check_package_items'],
                    'background_check_download_id':form_id
                    })

                return backgroundcheck_emp_info_obj.id


    
    def backgroundsummaryinfo(self,form_id):
        vals = self.env['hr.employee.onboarding'].search([('id','=',form_id)])
        
        doc = self.env['signature.request.template'].search([])
        document_dict = {}
        for values in doc:
            document_dict.update({values.id:values.attachment_id.name})
            
        applicant_list=[]
        for line in vals.applicant_background_ids:
            applicant_list.append({
                'applicant_tree_id' : line.id or '',
                'document' : line.document.id or '',
                'doc_link' : line.doc_link or '',
                'status_id' : line.status_id or '',
                'date_sent' : line.date_sent or '',
                'expiration' : line.expiration or '',
            })
            
        employer_list=[]
        for line in vals.employer_background_ids:
            employer_list.append({
                'employer_tree_id' : line.id or '',
                'document' : line.document.id or '',
                'doc_link' : line.doc_link or '',
                'status_id' : line.status_id or '',
                'date_sent' : line.date_sent or '',
                'expiration' : line.expiration or '',
            })
        
        background_list=[]
        for line in vals.background_check_ids:
            background_list.append({
                'background_tree_id' : line.id or '',
                'document' : line.item.id or '',
                'status_id' : line.status_id or '',
            })
        
        
        background_download_list=[]
        for line in vals.background_check_download_ids:
            background_download_list.append({
                'background_tree_id' : line.id or '',
                'document' : line.item.id or '',
                'link' : line.attachment or '',
            })
        background_check_download = self.env['background.config'].search([])
        background_download_dict = {}
        for vals_background_download in background_check_download:
            background_download_dict.update({str(vals_background_download.id) : vals_background_download.name})

        background_check = self.env['background.check.settings'].search([('name','=',vals.company.provider.id)])
        background_dict = {}
        background_package_dict ={}
        for vals_background in background_check.background_config_ids:
            if vals_background.basic_package:
                background_package_dict.update({str(vals_background.id) : vals_background.name})
                for item in vals_background.services:
                    background_dict.update({str(item.id) : item.name})
            else:
                background_dict.update({str(vals_background.id) : vals_background.name})
        
        background_package_list=[]
        for line in vals.background_check_package_ids:
            background_package_list.append({
                'background_package_tree_id' : line.id or '',
                'document' : line.item.id or '',
            })

        background_summary_info_dict = {
                'applicant_list' : applicant_list or '',
                'employer_list' : employer_list or '',
                'background_list' : background_list or '',
                'background_download_list' : background_download_list or '',
                'background_package_list' : background_package_list or '',
                'doc_disp' : document_dict,
                'background_dict' : background_dict or '',
                'background_download_dict' : background_download_dict or '',
                'background_package_dict' : background_package_dict or ''
            }

        return background_summary_info_dict
    
    def insert_records_background_summary_applicant_info(self,form_id,background_summary_applicant_info_vals):
        
        if int(background_summary_applicant_info_vals['applicant_tree_id'])>0:
            backgroundcheck_app_info_obj = self.env['applicant.background'].search([('id' , '=' , background_summary_applicant_info_vals['applicant_tree_id'])])
            if (background_summary_applicant_info_vals['form_applicant_documents']):
                backgroundcheck_app_info_obj.document = background_summary_applicant_info_vals['form_applicant_documents']
            if (background_summary_applicant_info_vals['applicant_link']):
                backgroundcheck_app_info_obj.doc_link = background_summary_applicant_info_vals['applicant_link']
            if (background_summary_applicant_info_vals['applicant_status']):
                backgroundcheck_app_info_obj.status_id = background_summary_applicant_info_vals['applicant_status']
            if (background_summary_applicant_info_vals['applicant_date_sent']):
                backgroundcheck_app_info_obj.date_sent = background_summary_applicant_info_vals['applicant_date_sent']
            if (background_summary_applicant_info_vals['applicant_expiration']):
                backgroundcheck_app_info_obj.expiration = background_summary_applicant_info_vals['applicant_expiration']        
                 
        else:
            if (background_summary_applicant_info_vals['form_applicant_documents'] or background_summary_applicant_info_vals['applicant_link'] or background_summary_applicant_info_vals['applicant_status']):
                backgroundcheck_app_info_obj = self.env['applicant.background'].create({
                    'document' : background_summary_applicant_info_vals['form_applicant_documents'],
                    'doc_link' : background_summary_applicant_info_vals['applicant_link'],
                    'status_id' : background_summary_applicant_info_vals['applicant_status'],
                    'date_sent' : background_summary_applicant_info_vals['applicant_date_sent'] or False,
                    'expiration' : background_summary_applicant_info_vals['applicant_expiration'] or False,
                    'applicant_background_id':form_id
                    })      
        backgroundcheck_emp_info_obj = self.env['hr.employee.onboarding'].search([('id' , '=' , form_id)])  
        # if backgroundcheck_emp_info_obj.substate_id == 'back_summary' and backgroundcheck_emp_info_obj.state_id == 'background':
        #     backgroundcheck_emp_info_obj.substate_id = 'adverse'
        # else:
        #     raise ValidationError('Status is not updated please contact support team')
    
    def insert_records_background_summary_employer_info(self,form_id,background_summary_employer_info_vals):
        
        if int(background_summary_employer_info_vals['employer_tree_id'])>0:
            backgroundcheck_emp_info_obj = self.env['employer.background'].search([('id' , '=' , background_summary_employer_info_vals['employer_tree_id'])])
            if (background_summary_employer_info_vals['form_employer_documents']):
                backgroundcheck_emp_info_obj.document = background_summary_employer_info_vals['form_employer_documents']
            if (background_summary_employer_info_vals['employer_link']):
                backgroundcheck_emp_info_obj.doc_link = background_summary_employer_info_vals['employer_link']
            if (background_summary_employer_info_vals['employer_status']):
                backgroundcheck_emp_info_obj.status_id = background_summary_employer_info_vals['employer_status']
            if (background_summary_employer_info_vals['employer_date_sent']):
                backgroundcheck_emp_info_obj.date_sent = background_summary_employer_info_vals['employer_date_sent']
            if (background_summary_employer_info_vals['employer_expiration']):
                backgroundcheck_emp_info_obj.expiration = background_summary_employer_info_vals['employer_expiration']        
                 
        else:
            if (background_summary_employer_info_vals['form_employer_documents'] or background_summary_employer_info_vals['employer_link'] or background_summary_employer_info_vals['employer_status']):
                backgroundcheck_emp_info_obj = self.env['employer.background'].create({
                    'document' : background_summary_employer_info_vals['form_employer_documents'],
                    'doc_link' : background_summary_employer_info_vals['employer_link'],
                    'status_id' : background_summary_employer_info_vals['employer_status'],
                    'date_sent' : background_summary_employer_info_vals['employer_date_sent'] or False,
                    'expiration' : background_summary_employer_info_vals['employer_expiration'] or False,
                    'employer_background_id':form_id
                    })    
        backgroundcheck_emp_info_obj = self.env['hr.employee.onboarding'].search([('id' , '=' , form_id)])  
        # if backgroundcheck_emp_info_obj.substate_id == 'back_summary':
        #     backgroundcheck_emp_info_obj.substate_id = 'adverse'  
        # else:
        #     raise ValidationError('Status is not updated please contact support team')

    def insert_records_background_summary_info(self,form_id):
        
        # if int(background_summary_info_vals['background_check_tree_id'])>0:
        #     backgroundcheck_emp_info_obj = self.env['background.check'].search([('id' , '=' , background_summary_info_vals['background_check_tree_id'])])
        #     if (background_summary_info_vals['form_background_check_documents']):
        #         backgroundcheck_emp_info_obj.item = background_summary_info_vals['form_background_check_documents']
        #     if (background_summary_info_vals['background_check_status']):
        #         backgroundcheck_emp_info_obj.status_id = background_summary_info_vals['background_check_status']     
                 
        # else:
        #     if (background_summary_info_vals['form_background_check_documents'] or background_summary_info_vals['background_check_status']):
        #         backgroundcheck_emp_info_obj = self.env['background.check'].create({
        #             'item' : background_summary_info_vals['form_background_check_documents'],
        #             'status_id' : background_summary_info_vals['background_check_status'],
        #             'background_check_id':form_id
        #             })   

        backgroundcheck_emp_info_obj = self.env['hr.employee.onboarding'].search([('id' , '=' , form_id)])  

        download_len = len(backgroundcheck_emp_info_obj.background_check_download_ids)
        download_obj = 0
        for rec in backgroundcheck_emp_info_obj.background_check_download_ids:
            if rec.attachment:
                download_obj += 1

        if download_len != download_obj:      
            return backgroundcheck_emp_info_obj.substate_id
        # else:    
        #     if backgroundcheck_emp_info_obj.substate_id == 'back_summary' and backgroundcheck_emp_info_obj.state_id == 'background':
        #         backgroundcheck_emp_info_obj.substate_id = 'adverse'
        #         return backgroundcheck_emp_info_obj.substate_id
        #     else:
        #         raise ValidationError('Status is not updated please contact support team')
         

    def adverseinfo(self,form_id):
        vals = self.env['hr.employee.onboarding'].search([('id','=',form_id)])
        

        doc = self.env['signature.request.template'].search([])
        document_dict = {}
        for values in doc:
            document_dict.update({values.id:values.attachment_id.name})
        
        adverse_list=[]
        for line in vals.action_form_ids:
            adverse_list.append({
                'adverse_tree_id' : line.id or '',
                'document' : line.action_form.id or '',
                'doc_link' : line.form_link or '',
                'status_id' : line.status_id or '',
                'date_sent' : line.date_sent or '',
                'expiration' : line.expiration or '',
            })
      

        adverse_info_dict = {
            'adverse_list' : adverse_list or '',
            'doc_disp' : document_dict,
             }
        return adverse_info_dict    
    
    def insert_records_adverse_action_info(self,form_id,adverse_action_info_vals):
        if int(adverse_action_info_vals['adverse_action_tree_id'])>0:
            adverse_action_info_obj = self.env['adverse.action'].search([('id' , '=' , adverse_action_info_vals['adverse_action_tree_id'])])
            if (adverse_action_info_vals['form_adverse_documents']):
                adverse_action_info_obj.action_form = adverse_action_info_vals['form_adverse_documents']
            if (adverse_action_info_vals['adverse_action_link']):
                adverse_action_info_obj.form_link = adverse_action_info_vals['adverse_action_link']
            if (adverse_action_info_vals['adverse_action_status']):
                adverse_action_info_obj.status_id = adverse_action_info_vals['adverse_action_status']
            if (adverse_action_info_vals['adverse_action_date_sent']):
                adverse_action_info_obj.date_sent = adverse_action_info_vals['adverse_action_date_sent']
            if (adverse_action_info_vals['adverse_action_expiration']):
                adverse_action_info_obj.expiration = adverse_action_info_vals['adverse_action_expiration']        
                 
        else:
            if (adverse_action_info_vals['form_adverse_documents']):
                adverse_action_info_obj = self.env['adverse.action'].create({
                    'action_form' : adverse_action_info_vals['form_adverse_documents'],
                    'form_link' : adverse_action_info_vals['adverse_action_link'],
                    'status_id' : adverse_action_info_vals['adverse_action_status'],
                    'date_sent' : adverse_action_info_vals['adverse_action_date_sent'] or False,
                    'expiration' : adverse_action_info_vals['adverse_action_expiration'] or False,
                    'action_form_id':form_id
                    })   
        adverse_action_info_obj = self.env['hr.employee.onboarding'].search([('id' , '=' , form_id)]) 
        # if adverse_action_info_obj.substate_id == 'adverse' and adverse_action_info_obj.state_id == 'background':
        #     adverse_action_info_obj.substate_id = 'inine'
        #     adverse_action_info_obj.state_id = 'to_approve'
        # else:
        #     raise ValidationError('Status is not updated please contact support team')

  
    def hireeverifyinfo(self,form_id):
        vals = self.env['hr.employee.onboarding'].search([('id','=',form_id)])
        
        doc = self.env['signature.request.template'].search([])
        document_dict = {}
        for values in doc:
            document_dict.update({values.id:values.attachment_id.name})
            
        applicant_list=[]
        for line in vals.applicant_background_ids:
            applicant_list.append({
                'applicant_tree_id' : line.id or '',
                'document' : line.document.id or '',
                'doc_link' : line.doc_link or '',
                'status_id' : line.status_id or '',
                'date_sent' : line.date_sent or '',
                'expiration' : line.expiration or '',
            })
            
        employer_list=[]
        for line in vals.employer_background_ids:
            employer_list.append({
                'employer_tree_id' : line.id or '',
                'document' : line.document.id or '',
                'doc_link' : line.doc_link or '',
                'status_id' : line.status_id or '',
                'date_sent' : line.date_sent or '',
                'expiration' : line.expiration or '',
            })
        
        background_list=[]
        for line in vals.background_check_ids:
            background_list.append({
                'background_tree_id' : line.id or '',
                'document' : line.item.id or '',
                'status_id' : line.status_id or '',
            })

        background_check = self.env['background.check.settings'].search([('name','=',vals.company.provider.id)])
        background_dict = {}
        background_package_dict ={}
        for vals_background in background_check.background_config_ids:
            if vals_background.basic_package:
                background_package_dict.update({str(vals_background.id) : vals_background.name})
                for item in vals_background.services:
                    background_dict.update({str(item.id) : item.name})
            else:
                background_dict.update({str(vals_background.id) : vals_background.name})
        
        background_package_list=[]
        for line in vals.background_check_package_ids:
            background_package_list.append({
                'background_package_tree_id' : line.id or '',
                'document' : line.item.id or '',
            })
            
        hire_everify_info_dict = {
                'applicant_list' : applicant_list or '',
                'employer_list' : employer_list or '',
                'background_list' : background_list or '',
                'background_package_list' : background_package_list or '',
                'doc_disp' : document_dict,
                'e_verify' : vals.e_verify or '',
                'background_dict' : background_dict,
                'background_package_dict' : background_package_dict
            }
    
        return hire_everify_info_dict
    
    def insert_records_everify_applicant_info(self,form_id,everify_applicant_info_vals):
        
        if int(everify_applicant_info_vals['applicant_tree_id'])>0:
            everify_app_info_obj = self.env['applicant.background'].search([('id' , '=' , everify_applicant_info_vals['applicant_tree_id'])])
            if (everify_applicant_info_vals['form_applicant_documents']):
                everify_app_info_obj.document = everify_applicant_info_vals['form_applicant_documents']
            if (everify_applicant_info_vals['applicant_link']):
                everify_app_info_obj.doc_link = everify_applicant_info_vals['applicant_link']
            if (everify_applicant_info_vals['applicant_status']):
                everify_app_info_obj.status_id = everify_applicant_info_vals['applicant_status']
            if (everify_applicant_info_vals['applicant_date_sent']):
                everify_app_info_obj.date_sent = everify_applicant_info_vals['applicant_date_sent']
            if (everify_applicant_info_vals['applicant_expiration']):
                everify_app_info_obj.expiration = everify_applicant_info_vals['applicant_expiration']        
                 
        else:
            if (everify_applicant_info_vals['form_applicant_documents'] or everify_applicant_info_vals['applicant_link'] or everify_applicant_info_vals['applicant_status']):
                everify_app_info_obj = self.env['applicant.background'].create({
                    'document' : everify_applicant_info_vals['form_applicant_documents'],
                    'doc_link' : everify_applicant_info_vals['applicant_link'],
                    'status_id' : everify_applicant_info_vals['applicant_status'],
                    'date_sent' : everify_applicant_info_vals['applicant_date_sent'] or False,
                    'expiration' : everify_applicant_info_vals['applicant_expiration'] or False,
                    'applicant_background_id':form_id
                    })    
    
    def insert_records_everify_employer_info(self,form_id,everify_employer_info_vals):
        
        if int(everify_employer_info_vals['employer_tree_id'])>0:
            everify_emp_info_obj = self.env['employer.background'].search([('id' , '=' , everify_employer_info_vals['employer_tree_id'])])
            if (everify_employer_info_vals['form_employer_documents']):
                everify_emp_info_obj.document = everify_employer_info_vals['form_employer_documents']
            if (everify_employer_info_vals['employer_link']):
                everify_emp_info_obj.doc_link = everify_employer_info_vals['employer_link']
            if (everify_employer_info_vals['employer_status']):
                everify_emp_info_obj.status_id = everify_employer_info_vals['employer_status']
            if (everify_employer_info_vals['employer_date_sent']):
                everify_emp_info_obj.date_sent = everify_employer_info_vals['employer_date_sent']
            if (everify_employer_info_vals['employer_expiration']):
                everify_emp_info_obj.expiration = everify_employer_info_vals['employer_expiration']        
                 
        else:
            if (everify_employer_info_vals['form_employer_documents'] or everify_employer_info_vals['employer_link'] or everify_employer_info_vals['employer_status']):
                everify_emp_info_obj = self.env['employer.background'].create({
                    'document' : everify_employer_info_vals['form_employer_documents'],
                    'doc_link' : everify_employer_info_vals['employer_link'],
                    'status_id' : everify_employer_info_vals['employer_status'],
                    'date_sent' : everify_employer_info_vals['employer_date_sent'] or False,
                    'expiration' : everify_employer_info_vals['employer_expiration'] or False,
                    'employer_background_id':form_id
                    })    

    def insert_records_everify_background_info(self,form_id,everify_background_info_vals):
        
        if int(everify_background_info_vals['background_check_tree_id'])>0:
            backgroundcheck_emp_info_obj = self.env['background.check'].search([('id' , '=' , everify_background_info_vals['background_check_tree_id'])])
            if (everify_background_info_vals['form_background_check_documents']):
                backgroundcheck_emp_info_obj.item = everify_background_info_vals['form_background_check_documents']
            if (everify_background_info_vals['background_check_status']):
                backgroundcheck_emp_info_obj.status_id = everify_background_info_vals['background_check_status']     
                 
        else:
            if (everify_background_info_vals['form_background_check_documents'] or everify_background_info_vals['background_check_status']):
                backgroundcheck_emp_info_obj = self.env['background.check'].create({
                    'document' : everify_background_info_vals['form_background_check_documents'],
                    'status_id' : everify_background_info_vals['background_check_status'],
                    'background_check_id':form_id
                    })   
        backgroundcheck_emp_info_obj = self.env['hr.employee.onboarding'].search([('id' , '=' , form_id)])   
        if backgroundcheck_emp_info_obj.e_verify == 'completed' and backgroundcheck_emp_info_obj.substate_id == 'inine' and backgroundcheck_emp_info_obj.state_id == 'to_approve':
            backgroundcheck_emp_info_obj.substate_id = 'app_summary'
        # else:
        #     raise ValidationError('Status is not updated please contact support team')
         
    
    def hire_summary(self, form_id):
        vals = self.env['hr.employee.onboarding'].search([('id','=',form_id)])
        
        doc = self.env['signature.request.template'].search([])
        document_dict = {}
        for values in doc:
            document_dict.update({values.id:values.attachment_id.name})


        state = self.env['res.country'].search([])
        state_dict={}
        for lines in state:
            state_dict.update({lines.id:lines.name})
            
        applicant_list=[]
        for line in vals.applicant_background_ids:
            applicant_list.append({
                'applicant_tree_id' : line.id or '',
                'document' : line.document.id or '',
                'doc_link' : line.doc_link or '',
                'status_id' : line.status_id or '',
                'date_sent' : line.date_sent or '',
                'expiration' : line.expiration or '',
            })
            
        employer_list=[]
        for line in vals.employer_background_ids:
            employer_list.append({
                'employer_tree_id' : line.id or '',
                'document' : line.document.id or '',
                'doc_link' : line.doc_link or '',
                'status_id' : line.status_id or '',
                'date_sent' : line.date_sent or '',
                'expiration' : line.expiration or '',
            })
        
        background_list=[]
        for line in vals.background_check_ids:
            background_list.append({
                'background_tree_id' : line.id or '',
                'document' : line.item.id or '',
                'status_id' : line.status_id or '',
            })    
            
        exp_academic_list=[]
        for line in vals.academic_experience_ids:
            exp_academic_list.append({
                'academic_tree_id' : line.id or '',
                'academic_experience' : line.academic_experience or '',
                'institute' : line.institute or '',
                'diploma' : line.diploma or '',
                'field_of_study' : line.field_of_study or '',
                'start_date' : line.start_date or '',
                'end_date' : line.end_date or '',
            })
            
        exp_professional_list=[]
        for line in vals.professional_experience_ids:
            exp_professional_list.append({
                'professional_tree_id' : line.id or '',
                'position' : line.position or '',
                'employer' : line.employer or '',
                'start_date' : line.start_date or '',
                'end_date' : line.end_date or '',
            })
            
        exp_certificate_list=[]
        for line in vals.certification_ids:
            exp_certificate_list.append({
                'certification_tree_id' : line.id or '',
                'certifications' : line.certifications or '',
                'certificate_code' : line.certificate_code or '',
                'issued_by' : line.issued_by or '',
                'professional_license' : line.professional_license or '',
                'state_issued_id' : line.state_issued_id.name or '',
                'start_date' : line.start_date or '',
                'end_date' : line.end_date or '',
            })
        
        background_download_list=[]
        for line in vals.background_check_download_ids:
            background_download_list.append({
                'background_tree_id' : line.id or '',
                'document' : line.item.id or '',
                'link' : line.attachment or '',
            })

        background_check_download = self.env['background.config'].search([])
        background_download_dict = {}
        for vals_background_download in background_check_download:
            background_download_dict.update({str(vals_background_download.id) : vals_background_download.name})

        background_check = self.env['background.check.settings'].search([('name','=',vals.company.provider.id)])
        background_dict = {}
        background_package_dict ={}
        for vals_background in background_check.background_config_ids:
            if vals_background.basic_package:
                background_package_dict.update({str(vals_background.id) : vals_background.name})
                for item in vals_background.services:
                    background_dict.update({str(item.id) : item.name})
            else:
                background_dict.update({str(vals_background.id) : vals_background.name})
        
        background_package_list=[]
        for line in vals.background_check_package_ids:
            background_package_list.append({
                'background_package_tree_id' : line.id or '',
                'document' : line.item.id or '',
            })
            
        hire_summary_dict = {
                'name' : vals.name or '',
                'mail' : vals.mail or '',
                'phone' : vals.phone or '',
                'responsible' : vals.responsible.name or '',
                'applied_job' : vals.applied_job.name or '',
                'company' : vals.company.name or '',
                'applicant_id' : vals.applicant_id,
                'emp_status': vals.emp_status.id or '',
                'id_no' : vals.id_number or '',
                'passport_no' : vals.passport_number or '',
                'street' : vals.street or '',
                'street2' : vals.street2 or '',
                'city' : vals.city or '',
                'state' : vals.state.name or '',
                'country_id' : vals.country.name or '',
                'zip' : vals.zip or '',
                'gender' : vals.gender,
                'marital_status': vals.marital_status or '',
                'filing_status': vals.filing_staus or '',
                'children' : vals.no_of_children or '',
                'dob' : vals.dob or '',
                'age' : vals.age or '',
                'emp_start_date' : vals.emp_start_date or '',
                'job_seniority_title' : vals.job_seniority_title.name or '',
                'benifits_seniority_date' : vals.benifits_seniority_date or '',
                'place_of_birth' : vals.place_of_birth or '',
                'nationality' : vals.nationality.name or '',
                'birth_country' : vals.birth_country.name or '',
                'scheduled_hours' : vals.scheduled_hours or '',
                'pay_rate' : vals.pay_rate or '',
                'notes' : vals.notes or '',
                'exp_academic_list' : exp_academic_list or '',
                'exp_professional_list' : exp_professional_list or '',
                'exp_certificate_list' : exp_certificate_list or '',
                'applicant_list' : applicant_list or '',
                'employer_list' : employer_list or '',
                'background_list' : background_list or '',
                'doc_disp' : document_dict,
                'e_verify' : vals.e_verify or '',
                'background_dict' : background_dict or'',
                'background_download_list' : background_download_list or '',
                'background_download_dict' : background_download_dict or '' ,
                'background_package_list' : background_package_list or '',
                'state_dict' : state_dict or '',
                'background_package_dict' : background_package_dict or '',
                } 

        return hire_summary_dict

    def hire_applicant(self,form_id,bio,image):
        

        pay_term = self.env['account.payment.term'].search([('name', '=', 'Immediate Payment')]).id
        pay_mode = self.env['account.payment.mode'].search([('name', '=', 'Manual Payment')]).id
        hire_obj = self.env['hr.employee.onboarding'].browse(int(form_id))

        if bio:
            hire_obj.notes = bio

        if image:
            lst = str(image).split(',')
            self.env['ir.attachment'].create({
                                                'res_id':int(form_id),
                                                'res_model':'hr.employee.onboarding',
                                                'index_content':'image',
                                                'type':'binary',
                                                'db_datas':lst[1],
                                                'res_field':'image',
                                                'name':'image',
                                            })

        applican_obj = self.env['hr.applicant'].search([('id' , '=' , hire_obj.applicant_id)])
        manager_id = self.env['hr.employee'].search([('user_id' , '=' , hire_obj.company.manager_user_id.id)])
        if not hire_obj.partner_id:
            rel_user = self.env['res.partner'].create({
                'firstname' : hire_obj.first_name or False,
                'middlename' : hire_obj.middle_name or False,
                'lastname' : hire_obj.last_name or False,
                'email' : hire_obj.mail or False,
                'company_id' : hire_obj.company.id or False,
                'property_supplier_payment_term_id' : pay_term or False,
                'supplier_payment_mode_id' : pay_mode or False,
                'state_id' : hire_obj.state.id or False,
                'city' : hire_obj.city or False,
                'street' : hire_obj.street or False,
                'street2' : hire_obj.street2 or False,
                'country' : hire_obj.country.id or False,
                'country_id' : hire_obj.country.id or False,
                'zip' : hire_obj.zip or False,
                })

            hire_obj.partner_id = rel_user
            applicant_obj = self.env['hr.applicant'].search([('id' , '=' , hire_obj.applicant_id)])
            applicant_obj.partner_id = rel_user

        else:
            rel_user = hire_obj.partner_id


        if not hire_obj.new_employee_id:
            employee = self.env['hr.employee'].create({
                'name' : hire_obj.name or False,
                'firstname' : hire_obj.first_name or False,
                'middlename' : hire_obj.middle_name or False,
                'lastname' : hire_obj.last_name or False,
                'lastname' : hire_obj.last_name or False,
                'first_name_alias' : hire_obj.first_name_alias or False,
                'middle_name_alias' : hire_obj.middle_name_alias or False,
                'last_name_alias' : hire_obj.last_name_alias or False,
                'address_id' : hire_obj.company.partner_id.id or False,
                'work_phone' : hire_obj.phone or False,
                'work_email' : hire_obj.mail or False,
                'employment_status' : hire_obj.contract_type.id or False,
                'country_id' : hire_obj.nationality.id or False,
                'gender' : hire_obj.gender or False,
                'birthday' : hire_obj.dob or False,
                'company_id' : hire_obj.company.id or False,
                'identification_id' : hire_obj.id_number or False,
                'passport_id' : hire_obj.passport_number or False,
                'benefit_seniority_date' : hire_obj.benifits_seniority_date or False,
                'start_date' : hire_obj.emp_start_date or False,
                'job_id' : hire_obj.applied_job.id or False,
                'job_seniority_title' : hire_obj.job_seniority_title.id or False,
                'sequence' : hire_obj.job_seniority_title.sequence or False,
                'marital' : hire_obj.marital_status or False,
                'filing_staus' : hire_obj.filing_staus or False,
                'children' : hire_obj.no_of_children or False,
                'ethnic_id' : hire_obj.ethnic_id or False,
                'smoker' : hire_obj.smoker or False,
                'place_of_birth' : hire_obj.place_of_birth or False,
                'birth_country' : hire_obj.birth_country.id or False,
                'parent_id' :  manager_id.id or False,
                'address_home_id' : hire_obj.partner_id.id or False,
                'emergency_contact_name' : hire_obj.emergency_contact_name or False,
                'emergency_contact_phone' : hire_obj.emergency_contact_phone or False,
                'emergency_contact_relationship' : hire_obj.emergency_contact_relationship or False,
                'notes' : hire_obj.notes or False,
                'image' : hire_obj.image or False,
                'benefit_status' : 'not_eligible',
                'overtime_pay' : 'non_exempt',
                'hire_date' : datetime.now().date(),
                })
            for line in hire_obj.academic_experience_ids:
                for values in line:
                    self.env['hr.experience.academics'].create({
                        'academics':values.academic_experience,
                        'institute':values.institute,
                        'diploma':values.diploma,
                        'field_of_study':values.field_of_study,
                        'start_date':values.start_date,
                        'end_date':values.end_date,
                        'academic_experience_id':employee.id,
                        'employee':employee.id,
                        }) 
            for line in hire_obj.professional_experience_ids:
                for values in line:
                    self.env['hr.experience.professional'].create({
                        'position':values.position,
                        'employer':values.employer,
                        'start_date':values.start_date,
                        'end_date':values.end_date,
                        'professional_experience_id':employee.id,
                        'employee':employee.id,
                        }) 
            for line in hire_obj.certification_ids:
                for values in line:
                    self.env['hr.experience.certification'].create({
                        'certifications':values.certifications,
                        'certificate_code':values.certificate_code,
                        'issued_by':values.issued_by,
                        'professional_license' : line.professional_license or '',
                        'state_issued_id' : line.state_issued_id.id or '',
                        'start_date':values.start_date,
                        'end_date':values.end_date,
                        'certification_id':employee.id,
                        'employee':employee.id,
                        }) 
            hire_obj.new_employee_id = employee.id
            hire_obj.employee_id = employee.id
            
            hire_obj.new_employee_id.employee_id = str(employee.id)
            hire_obj.new_employee_id.time_clock = employee.id
            hire_obj.new_employee_id.hr_status = 'Active'
            if hire_obj.pid_document_id:
                hire_obj.pid_document_id.state = 'canceled'
                hire_obj.pid_document_id.request_item_ids.state = 'completed'

            applican_obj.job_id.write({'no_of_hired_employee': applican_obj.job_id.no_of_hired_employee + 1})

        hire_obj.benifits_seniority_date = datetime.now().date()
        # if hire_obj.substate_id == 'everify' and hire_obj.state_id == 'to_approve':
        #     hire_obj.substate_id = 'ben_eligiblity'
        #     hire_obj.state_id = 'hire'
        # else:
        #     raise ValidationError('Status is not updated please contact support team')

    def welcome_summary(self,form_id):
        vals = self.env['hr.employee.onboarding'].search([('id','=',form_id)])


        doc = self.env['signature.request.template'].search([])
        document_dict = {}
        for values in doc:
            document_dict.update({values.id:values.attachment_id.name})
        
        survey = self.env['survey.survey'].search([])
        survey_dict = {}
        for values in survey:
            survey_dict.update({values.id:values.title})

        welcome_list=[]
        for line in vals.welcome_mail_ids:
            welcome_list.append({
                'welcome_tree_id' : line.id or '',
                'document' : line.document.id or '',
                'doc_link' : line.doc_link or '',
                'status_id' : line.status_id or '',
                'date_sent' : line.date_sent or '',
                'expiration' : line.expiration or '',
            })
        
        survey_list=[]
        for line in vals.welcome_benefit_survey_ids:
            survey_list.append({
                'survey_tree_id' : line.id or '',
                'survey' : line.survey.id or '',
                'survey_link' : line.survey_link or '',
                'status_id' : line.status_id or '',
                'date_sent' : line.date_sent or '',
                'expiration' : line.expiration or '',
            })

        employer_list=[]
        for line in vals.employer_background_ids:
            employer_list.append({
                'employer_tree_id' : line.id or '',
                'document' : line.document.id or '',
                'doc_link' : line.doc_link or '',
                'status_id' : line.status_id or '',
                'date_sent' : line.date_sent or '',
                'expiration' : line.expiration or '',
            })


        welcome_summary_dict = {
            'everify' : vals.e_verify or '',
            'employer_list' : employer_list or '',
            'welcome_list' : welcome_list or '',
            'survey_list' : survey_list or '',
            'document_dict' : document_dict or '',
            'survey_dict' : survey_dict or ''
        }

        return welcome_summary_dict

        
    def benefits_eligibility_info(self,form_id):
        vals = self.env['hr.employee.onboarding'].search([('id','=',form_id)])
        ben_eligible = ''
        if(vals.company.eligible_for_benefits == vals.contract_type):
            ben_eligible = 'eligible'
        benefits_eligibility_dict = {
                'enrollment_delay' : vals.company.benefits_enrollment_delay or '',
                'elegible_for_benefits' : ben_eligible,
            }
        return benefits_eligibility_dict    

    def insert_vals_benefits_eligibility(self,form_id,ban_obj):
        ben_eligiblity_obj = self.env['hr.employee.onboarding'].search([('id','=',form_id)])
        if(ban_obj == 'checked'):
            ben_eligiblity_obj.eligible_for_benefits = True
        # if ben_eligiblity_obj.substate_id =='ben_eligiblity' and ben_eligiblity_obj.state_id == 'hire':
        #     ben_eligiblity_obj.substate_id = 'welcome'
        # else:
        #     raise ValidationError('Status is not updated please contact support team')

    
    def welcomemailinfo(self,form_id):
        vals = self.env['hr.employee.onboarding'].search([('id','=',form_id)])
        
        doc = self.env['signature.request.template'].search([])
        document_dict = {}
        for values in doc:
            document_dict.update({values.id:values.attachment_id.name})
        
        survey = self.env['survey.survey'].search([])
        survey_dict = {}
        for values in survey:
            survey_dict.update({values.id:values.title})
        
        welcome_list=[]
        for line in vals.welcome_mail_ids:
            welcome_list.append({
                'welcome_tree_id' : line.id or '',
                'document' : line.document.id or '',
                'doc_link' : line.doc_link or '',
                'status_id' : line.status_id or '',
                'date_sent' : line.date_sent or '',
                'expiration' : line.expiration or '',
            })
        
        survey_list=[]
        for line in vals.welcome_benefit_survey_ids:
            survey_list.append({
                'survey_tree_id' : line.id or '',
                'survey' : line.survey.id or '',
                'survey_link' : line.survey_link or '',
                'status_id' : line.status_id or '',
                'date_sent' : line.date_sent or '',
                'expiration' : line.expiration or '',
            })
            
        welcome_info_dict = {
                'welcome_list' : welcome_list or '',
                'survey_list' : survey_list or '',
                'doc_disp' : document_dict,
                'survey_dict' : survey_dict,
            }
    
        return welcome_info_dict

    def insert_records_welcome_email_info(self,form_id,welcome_email_info_vals):
        
        welcome_email_info_obj = self.env['hr.employee.onboarding'].search([('id' , '=' , form_id)])
        # print welcome_email_info_obj.substate_id,'---',welcome_email_info_obj.state_id
        # if welcome_email_info_obj.substate_id == 'welcome':
        #     welcome_email_info_obj.substate_id = 'appraisal'
        # else:
        #     raise ValidationError('Status is not updated please contact support team')


        if int(welcome_email_info_vals['welcome_applicant_tree_id'])>0:
            welcome_email_info_obj = self.env['welcome.mail'].search([('id' , '=' , welcome_email_info_vals['welcome_applicant_tree_id'])])
            if (welcome_email_info_vals['form_welcome_applicant_documents']):
                welcome_email_info_obj.document = welcome_email_info_vals['form_welcome_applicant_documents']
            if (welcome_email_info_vals['welcome_applicant_link']):
                welcome_email_info_obj.doc_link = welcome_email_info_vals['welcome_applicant_link']
            if (welcome_email_info_vals['welcome_applicant_status']):
                welcome_email_info_obj.status_id = welcome_email_info_vals['welcome_applicant_status']
            if (welcome_email_info_vals['welcome_applicant_date_sent']):
                welcome_email_info_obj.date_sent = welcome_email_info_vals['welcome_applicant_date_sent']

            if welcome_email_info_obj.status_id != 'canceled':
                if (welcome_email_info_vals['welcome_applicant_expiration']):
                    welcome_email_info_obj.expiration = welcome_email_info_vals['welcome_applicant_expiration']  
            elif welcome_email_info_obj.status_id =='canceled' and str(welcome_email_info_obj.expiration) != welcome_email_info_vals['welcome_applicant_expiration']:
                if (welcome_email_info_vals['welcome_applicant_expiration']):
                    welcome_email_info_obj.expiration = welcome_email_info_vals['welcome_applicant_expiration']  
            else:
                welcome_email_info_obj.expiration = ''

            return welcome_email_info_obj.id
                 
        else:
            if (welcome_email_info_vals['form_welcome_applicant_documents'] or welcome_email_info_vals['welcome_applicant_link'] or welcome_email_info_vals['welcome_applicant_status']):
                welcome_email_info_obj = self.env['welcome.mail'].create({
                    'document' : welcome_email_info_vals['form_welcome_applicant_documents'],
                    'doc_link' : welcome_email_info_vals['welcome_applicant_link'],
                    'status_id' : welcome_email_info_vals['welcome_applicant_status'],
                    'date_sent' : welcome_email_info_vals['welcome_applicant_date_sent'] or False,
                    'expiration' : welcome_email_info_vals['welcome_applicant_expiration'] or False,
                    'welcome_mail_id':form_id
                    })

                return welcome_email_info_obj.id

    def insert_records_survey_welcome_email_info(self,form_id,survey_welcome_email_info_vals):
        welcome_email_info_obj = self.env['hr.employee.onboarding'].search([('id' , '=' , form_id)]) 
        # if welcome_email_info_obj.substate_id == 'welcome' and welcome_email_info_obj.state_id == 'hire':
        #     welcome_email_info_obj.substate_id = 'appraisal'
        # else:
        #     raise ValidationError('Status is not updated please contact support team')

        if survey_welcome_email_info_vals['welcome_survey_tree_id'] > 0:
            survey_welcome_email_info_obj = self.env['welcome.survey'].search([('id' , '=' , survey_welcome_email_info_vals['welcome_survey_tree_id'])])
            if (survey_welcome_email_info_vals['form_welcome_survey']):
                survey_welcome_email_info_obj.survey = survey_welcome_email_info_vals['form_welcome_survey']
            if (survey_welcome_email_info_vals['welcome_survey_link']):
                survey_welcome_email_info_obj.survey_link = survey_welcome_email_info_vals['welcome_survey_link']
            if (survey_welcome_email_info_vals['welcome_survey_status']):
                survey_welcome_email_info_obj.status_id = survey_welcome_email_info_vals['welcome_survey_status']
            if (survey_welcome_email_info_vals['welcome_survey_date_sent']):
                survey_welcome_email_info_obj.date_sent = survey_welcome_email_info_vals['welcome_survey_date_sent']
            if (survey_welcome_email_info_vals['welcome_survey_expiration']):
                survey_welcome_email_info_obj.expiration = survey_welcome_email_info_vals['welcome_survey_expiration']  

            return survey_welcome_email_info_obj.id
                 
        else:
            if (survey_welcome_email_info_vals['form_welcome_survey'] or survey_welcome_email_info_vals['welcome_survey_link'] or survey_welcome_email_info_vals['welcome_survey_status']):
                survey_welcome_email_info_obj = self.env['welcome.survey'].create({
                    'survey' : survey_welcome_email_info_vals['form_welcome_survey'],
                    'survey_link' : survey_welcome_email_info_vals['welcome_survey_link'],
                    'status_id' : survey_welcome_email_info_vals['welcome_survey_status'],
                    'date_sent' : survey_welcome_email_info_vals['welcome_survey_date_sent'] or False,
                    'expiration' : survey_welcome_email_info_vals['welcome_survey_expiration'] or False,
                    'welcome_mail_id':form_id
                    })

                return survey_welcome_email_info_obj.id
        
        


    def appraisal_info(self, form_id):
        vals = self.env['hr.employee.onboarding'].search([('id','=',form_id)])
        appraisal_info_dict = {
                'appraisal_by_short' : vals.appraisal_by_short or '',
                'appraisal_by_manager' : vals.appraisal_by_manager or '',
                'appraisal_self' : vals.appraisal_self or '',
                'appraisal_by_collaborators' : vals.appraisal_by_collaborators or '',
                'direct_report_anonymous' : vals.direct_report_anonymous or '',
                'appraisal_by_colleagues' : vals.appraisal_by_colleagues or '',
                'colleague_report_anonymous' : vals.colleague_report_anonymous or '',
                'appraisal_by_coach' : vals.appraisal_by_coach or '',
                'periodic_appraisal' : vals.periodic_appraisal or '',
                'appraisal_frequency' : vals.appraisal_frequency or '',
                'appraisal_frequency_unit' : vals.appraisal_frequency_unit or '',
                'appraisal_date' : vals.appraisal_date or '',
                'auto_send_appraisals' : vals.auto_send_appraisals or '',
                } 
        return appraisal_info_dict

    def insert_records_appraisal_info(self,form_id,appraisal_plan_info):

        appraisal_obj = self.env['hr.employee.onboarding'].search([('id' , '=' , form_id)])
        emp_id = self.env['hr.employee'].search([('id' , '=' , appraisal_obj.new_employee_id.id)])

        if (appraisal_plan_info['days_appraisal']):
            emp_id.appraisal_by_short = appraisal_plan_info['days_appraisal']
            appraisal_obj.appraisal_by_short = appraisal_plan_info['days_appraisal']
        if (appraisal_plan_info['manager']):
            emp_id.appraisal_by_manager = appraisal_plan_info['manager']  
            appraisal_obj.appraisal_by_manager = appraisal_plan_info['manager']  
        if (appraisal_plan_info['employee']):
            emp_id.appraisal_self = appraisal_plan_info['employee']  
            appraisal_obj.appraisal_self = appraisal_plan_info['employee']  
        if (appraisal_plan_info['direct_report']):
            emp_id.appraisal_by_collaborators = appraisal_plan_info['direct_report']  
            appraisal_obj.appraisal_by_collaborators = appraisal_plan_info['direct_report']  
        if (appraisal_plan_info['direct_report_anonymous']):
            emp_id.direct_report_anonymous = appraisal_plan_info['direct_report_anonymous']  
            appraisal_obj.direct_report_anonymous = appraisal_plan_info['direct_report_anonymous']  
        if (appraisal_plan_info['colleagues']):
            emp_id.appraisal_by_colleagues = appraisal_plan_info['colleagues']  
            appraisal_obj.appraisal_by_colleagues = appraisal_plan_info['colleagues'] 
        if (appraisal_plan_info['colleagues_anonymous']):
            emp_id.colleague_report_anonymous = appraisal_plan_info['colleagues_anonymous']  
            appraisal_obj.colleague_report_anonymous = appraisal_plan_info['colleagues_anonymous'] 
        if (appraisal_plan_info['coach']):
            emp_id.appraisal_by_coach = appraisal_plan_info['coach']  
            appraisal_obj.appraisal_by_coach = appraisal_plan_info['coach'] 
        if (appraisal_plan_info['periodic_appraisal']):
            emp_id.periodic_appraisal = appraisal_plan_info['periodic_appraisal']  
            appraisal_obj.periodic_appraisal = appraisal_plan_info['periodic_appraisal']  
        if (appraisal_plan_info['repeat_period']):
            emp_id.appraisal_frequency = appraisal_plan_info['repeat_period']  
            appraisal_obj.appraisal_frequency = appraisal_plan_info['repeat_period']  
        if (appraisal_plan_info['period']):
            emp_id.appraisal_frequency_unit = appraisal_plan_info['period']  
            appraisal_obj.appraisal_frequency_unit = appraisal_plan_info['period']  
        if (appraisal_plan_info['next_appraisal_date']):
            emp_id.appraisal_date = appraisal_plan_info['next_appraisal_date']  
            appraisal_obj.appraisal_date = appraisal_plan_info['next_appraisal_date']  
        if (appraisal_plan_info['auto_send_appraisal']):
            emp_id.auto_send_appraisals = appraisal_plan_info['auto_send_appraisal']  
            appraisal_obj.auto_send_appraisals = appraisal_plan_info['auto_send_appraisal']  

        # if appraisal_obj.substate_id =='appraisal' and appraisal_obj.state_id == 'hire':
        #     appraisal_obj.substate_id = 'hire_summary'
        # else:
        #     raise ValidationError('Status is not updated please contact support team')


    def benefits_state(self,form_id):
        benefits_state_obj = self.env['hr.employee.onboarding'].search([('id' , '=' , form_id)])
        # if benefits_state_obj.substate_id == 'hire_summary' and benefits_state_obj.state_id == 'hire':
        #     benefits_state_obj.substate_id = 'ben_survey'
        # else:
        #     raise ValidationError('Status is not updated please contact support team')

    def employee_summary_state(self,form_id):
        emp_summary_state_obj = self.env['hr.employee.onboarding'].search([('id' , '=' , form_id)])  
        # print emp_summary_state_obj.substate_id,'!!##!!',emp_summary_state_obj.state_id
        # if emp_summary_state_obj.substate_id == 'ben_survey':
        #     emp_summary_state_obj.substate_id = 'emp_summary'
        #     emp_summary_state_obj.state_id = 'contract' 
        # else:
        #     raise ValidationError('Status is not updated please contact support team')
        
    def employee_contract_state(self,form_id):
        emp_summary_state_obj = self.env['hr.employee.onboarding'].search([('id' , '=' , form_id)])  
        # if emp_summary_state_obj.substate_id == 'emp_summary' and emp_summary_state_obj.state_id == 'contract':
        #     emp_summary_state_obj.substate_id = 'contract' 
        # else:
        #     raise ValidationError('Status is not updated please contact support team')       

    def benifits_survey_link(self,form_id):
        benifits_survey_obj = self.env['hr.employee.onboarding'].search([('id' , '=' , form_id)])
        if benifits_survey_obj.state_id=='benefits':
            benifits_survey_obj.state_id = 'contract'  
        if benifits_survey_obj.state_id=='hire':
            benifits_survey_obj.state_id = 'benefits' 
        if(benifits_survey_obj.contract_type == benifits_survey_obj.company.eligible_for_benefits):
            # results = self.env['survey.user_input'].sudo().search([('onboarding_id' , '=' , form_id)])
            self.env.cr.execute("select survey_id,token from survey_user_input where onboarding_id="+form_id)
            results = self.env.cr.dictfetchall()

            for record in results:
                survey = self.env['survey.survey'].search([('id' , '=' , record['survey_id'])])
                """ Open the website page with the survey form """
                base_url = '/' if self.env.context.get('relative_url') else self.env['ir.config_parameter'].get_param('web.base.url')
                public_url = urljoin(base_url, "survey/start/%s" % (slug(survey)))
                benifits_survey_info = public_url+"/"+record['token']

                benifits_survey_obj.benefits_survey_link = benifits_survey_info


                return benifits_survey_info
        

    def benifits_survey_results_info(self,form_id):
        benifits_survey_obj = self.env['hr.employee.onboarding'].search([('id' , '=' , form_id)])

        
        if benifits_survey_obj.contract_type == benifits_survey_obj.company.eligible_for_benefits:
            benifits_survey_results_info = benifits_survey_obj.benefits_survey_link
        else:
            benifits_survey_results_info = 0

        return benifits_survey_results_info 


    def approve_summary(self,form_id):
        approve_summary_obj = self.env['hr.employee.onboarding'].search([('id' , '=' , form_id)])

        total_count =  (len(approve_summary_obj.welcome_mail_ids)+len(approve_summary_obj.employer_background_ids)+len(approve_summary_obj.welcome_benefit_survey_ids))*100

        welcome_value = 0
        employer_value = 0
        survey_value = 0
        for line in approve_summary_obj.welcome_mail_ids:
            if line.status_id == 'signed':
                welcome_value += 100
            if line.status_id == 'sent':
                welcome_value += 50 
            if line.status_id == 'draft':
                welcome_value += 0 

        for line in approve_summary_obj.welcome_benefit_survey_ids:
            if line.status_id == 'done':
                survey_value += 100
            if line.status_id == 'skip':
                survey_value += 50 
            if line.status_id == 'new':
                survey_value += 0 

        for line in approve_summary_obj.employer_background_ids:
            if line.status_id == 'signed':
                employer_value += 100 
            if line.status_id == 'sent':
                employer_value += 50
            if line.status_id == 'draft':
                employer_value += 0


        total_value = welcome_value + employer_value + survey_value

        if total_value != 0:
            progress = (total_value*100)/total_count
        else:
            progress = 0

        return progress

    def benefits_state_send(self,form_id):
        benefits_state_obj = self.env['hr.employee.onboarding'].search([('id' , '=' , form_id)])
        benefits_state_obj.benefits_states = 'send'


    def benefits_state_enrolled(self,form_id):
        benefits_state_obj = self.env['hr.employee.onboarding'].search([('id' , '=' , form_id)])
        benefits_state_obj.benefits_states = 'enrolled'


    def employee_info(self, form_id):
        employee_summary_obj = self.env['hr.employee.onboarding'].search([('id' , '=' , form_id)])
        emp_id = self.env['hr.employee'].sudo().search([('id' , '=' , employee_summary_obj.new_employee_id.id)])
        
        employee_info_dict = {
                'name' : emp_id.name or '',
                'address_id' : emp_id.address_id.street or '',
                'street2' : emp_id.address_id.street2 or '',
                'city' : emp_id.address_id.city or '',
                'state' : emp_id.address_id.state_id.name or '',
                'country' : emp_id.address_id.country_id.name or '',
                'mobile_phone' : emp_id.mobile_phone or '',
                'work_email' : emp_id.work_email or '',
                'work_phone' : emp_id.work_phone or '',
                'job_id' : emp_id.job_id.name or '',
                'job_seniority_title' : emp_id.job_seniority_title.name or '',
                'employment_status' : emp_id.employment_status.name or '',
                'parent_id' : emp_id.parent_id.name or '',
                'coach_id' : emp_id.coach_id.name or '',
                'manager_checkbox' : emp_id.manager or '',
                'country_id' : emp_id.country_id.name or '',
                'identification_id' : emp_id.identification_id or '',
                'passport_id' : emp_id.passport_id or '',
                'address_home_id' : emp_id.address_home_id.name or '',
                'location_id' : emp_id.location_id or '',
                'gender' : emp_id.gender or '',
                'marital' : emp_id.marital or '',
                'children' : emp_id.children or '',
                'ethnic_id' : emp_id.ethnic_id or '',
                'smoker' : emp_id.smoker or '',
                'birthday' : emp_id.birthday or '',
                'place_of_birth' : emp_id.place_of_birth or '',
                'birth_country' : emp_id.birth_country.name or '',
                'age' : emp_id.age or '',
                'verify_checkbox' : emp_id.verify or '',
                'work_authorization' : emp_id.work_authorization or '',
                'document_no' : emp_id.document_no or '',
                'expiration_date' : emp_id.expiration_date or '',
                'document_A' : emp_id.document_A or '',
                'document_B' : emp_id.document_B or '',
                'document_C' : emp_id.document_C or '',
                'visa_type' : emp_id.visa_type or '',
                'visa_exp' : emp_id.visa_exp or '',
                'country' : emp_id.country.name or '',
                'ref_id' : emp_id.ref_id or '',
                'application_date' : emp_id.application_date or '',
                'approval_date' : emp_id.approval_date or '',
                'exp_date' : emp_id.exp_date or '',
                'veteran' : emp_id.veteran or '',
                'veteran_of' : emp_id.veteran_of or '',
                'branch' : emp_id.branch or '',
                'separation_date' : emp_id.separation_date or '',
                'service_medal' : emp_id.service_medal or '',
                'disabled_veteran' : emp_id.disabled_veteran or '',
                'actv_wartime' : emp_id.actv_wartime or '',
                'disabled' : emp_id.disabled or '',
                'disablity_type' : emp_id.disablity_type or '',
                'timesheet_cost' : emp_id.timesheet_cost or '',
                'account_id' : emp_id.account_id.name or '',
                'product_id' : emp_id.product_id.name or '',
                'journal_id' : emp_id.journal_id.name or '',
                'project_task' : emp_id.project_task.name or '',
                'company_id' : emp_id.company_id.name or '',
                'user_id' : emp_id.user_id.name or '',
                'benefit_status' : emp_id.benefit_status or '',
                'scheduled_hours' : emp_id.scheduled_hours or '',
                'enrollment_deadline' : emp_id.enrollment_deadline or '',
                'barcode' : emp_id.barcode or '',
                'pin' : emp_id.pin or '',
                'manual_attendance_checkbox' : emp_id.manual_attendance or '',
                'medic_exam' : emp_id.medic_exam or '',
                'vehicle' : emp_id.vehicle or '',
                'vehicle_distance' : emp_id.vehicle_distance or '',
                'pay_type' : emp_id.pay_type or '',
                'overtime_pay' : emp_id.overtime_pay or '',
                'start_date' : emp_id.start_date or '',
                'benefit_seniority_date' : emp_id.benefit_seniority_date or '',
                'hire_date' : emp_id.hire_date or '',
                'termination_date' : emp_id.termination_date or '',
                'termination_type' : emp_id.termination_type.name or '',
                'termination_reason' : emp_id.termination_reason or '',
                'rehire_eligible_checkbox' : emp_id.rehire_eligible or '',
                'cobra_eligible_checkbox' : emp_id.cobra_eligible or '',
                'employee_id' : emp_id.employee_id or '',
                'time_clock' : emp_id.time_clock or '',
                'hr_status' : emp_id.hr_status or '',
                'direct_deposit' : emp_id.direct_deposit or '',
                'date_added' : emp_id.date_added or '',
                'date_modified' : emp_id.date_modified or '',
                'remaining_leaves' : emp_id.remaining_leaves or '',
                'timesheet_validated' : emp_id.timesheet_validated or '',
                'credit_card_id' : emp_id.credit_card_id or '',
                'emergency_contact_name' : emp_id.emergency_contact_name or '',
                'emergency_contact_phone' : emp_id.emergency_contact_phone or '',
                'emergency_contact_relationship' : emp_id.emergency_contact_relationship or '',
                'first_name_alias' : emp_id.first_name_alias or '',
                'middle_name_alias' : emp_id.middle_name_alias or '',
                'last_name_alias' : emp_id.last_name_alias or '',
                }
        
        # if employee_summary_obj.substate_id=='ben_survey' and employee_summary_obj.state_id == 'contract':
        #     employee_summary_obj.substate_id = 'emp_summary'
        # else:
        #     raise ValidationError('Status is not updated please contact support team')

        return employee_info_dict

    def employee_view(self,form_id):
        emp_obj = self.env['hr.employee.onboarding'].search([('id' , '=' , form_id)])

        res = emp_obj.new_employee_id.id

        return res
    
    def create_contract_via_link(self,form_id):

        create_contract_obj = self.env['hr.employee.onboarding'].search([('id' , '=' , form_id)])
        # if create_contract_obj.substate_id=='contract':
        #     create_contract_obj.substate_id = 'con_summary'
        # else:
        #     raise ValidationError('Status is not updated please contact support team')
        contract_id_exist = self.env['hr.contract'].search([('employee_id','=',create_contract_obj.new_employee_id.id)])
        if contract_id_exist:
            return contract_id_exist.id
        else:
            if create_contract_obj.pay_type == 'hourly':
#                 current_hourly_rate =  "%.2f" % float(create_contract_obj.pay_rate)
                hourly_class = self.env['hr.hourly.rate.class'].search([('name' , '=' , create_contract_obj.pay_rate)])
                if not hourly_class:
                    hourly_class_id = self.env['hr.hourly.rate.class'].create({
                        'name' : str(create_contract_obj.pay_rate),
                        'line_ids': [(0, 0, {
                                'date_start': '2017-12-31',
                                'rate': create_contract_obj.pay_rate,
                            })],
                        })
                    job_list = [(0,0,{
                        'job_id' : create_contract_obj.applied_job.id,
                        'seniority_id' : create_contract_obj.job_seniority_title.id,
                        'hourly_rate_class_id' : hourly_class_id.id,
                        'is_main_job' : True,
                        'is_bonus' : True
                        })]

                else:
                    job_list = [(0,0,{
                        'job_id' : create_contract_obj.applied_job.id,
                        'seniority_id' : create_contract_obj.job_seniority_title.id,
                        'hourly_rate_class_id' : hourly_class.id,
                        'is_main_job' : True,
                        'is_bonus' : True
                        })]
            else:
                job_list = [(0,0,{
                    'job_id' : create_contract_obj.applied_job.id,
                    'seniority_id' : create_contract_obj.job_seniority_title.id,
                    'is_main_job' : True,
                    'is_bonus' : True
                    })]
            contract_id = self.env['hr.contract'].create({
                'employee_id' : create_contract_obj.new_employee_id.id,
                'type_id' : create_contract_obj.contract_type.id,
                'salary_computation_method' : create_contract_obj.pay_type,
                'wage' : create_contract_obj.proposed_salary,
                'state' : 'draft',
                'contract_job_ids' : job_list,
                })
            create_contract_obj.new_contract_id = contract_id.id
            return contract_id.id 
    
    def contract_info(self,form_id):
        form_info_obj = self.env['hr.employee.onboarding'].search([('id' , '=' , form_id)])
        contract_info_obj = self.env['hr.contract'].search([('id' , '=' , form_info_obj.new_contract_id.id)])
        
        if contract_info_obj:
            job_position_list=[]
            for line in contract_info_obj.contract_job_ids:
                job_position_list.append({
                    'job_position_tree_id' : line.id or '',
                    'job_id' : line.job_id.name or '',
                    'seniority_id' : line.seniority_id.name or '',
                    'hourly_rate' : line.hourly_rate or 0.00,
                    'hourly_rate_class_id' : line.hourly_rate_class_id.name or '',
                    'is_main_job' : line.is_main_job or False,
                    'is_bonus' : line.is_bonus or False,
                })
            production_list=[]
            for line in contract_info_obj.staff_bonus_ids:
                production_list.append({
                    'production_tree_id' : line.id or '',
                    'job_id' : line.job_id.name or '',
                    'code_id' : line.code_id or '',
                    'production_tag_id' : line.production_tag_id.name or '',
                    'type_id' : line.type_id.name or '',
                    'rate_id' : line.rate_id or 0.00,
                    'sub_amount' : line.sub_amount or False,
                    'payout_period' : line.payout_period or 0,
                    'validation' : line.validation or False,
                    'deduct_draw' : line.deduct_draw or False,
                    'is_bonus' : line.is_bonus or False,
                })

            benefits_list=[]
            for line in contract_info_obj.benefit_line_ids:
                benefits_list.append({
                    'benefits_tree_id' : line.id or '',
                    'category_id' : line.category_id.name or '',
                    'rate_id' : line.rate_id.name or '',
                    'employee_amount' : line.employee_amount or '',
                    'employer_amount' : line.employer_amount or '',
                    'amount_type' : line.amount_type or '',
                    'date_start' : line.date_start or '',
                    'date_end' : line.date_end or '',
                })
            summary_view=0
            # print form_info_obj.substate_id,'--',form_info_obj.state_id
            # if form_info_obj.substate_id=='contract' and form_info_obj.state_id == 'contract':
            #     summary_view=1
            #     form_info_obj.substate_id = 'con_summary'
            # else:
            #     raise ValidationError('Status is not updated please contact support team')
                
            contract_info_dict = {
                'name' : contract_info_obj.name or '',
                'employee_id' : contract_info_obj.employee_id.name or '',
                'job_id' : contract_info_obj.job_id.name or '',
                'schedule_pay' : contract_info_obj.schedule_pay or '',
                'job_seniority_title' : contract_info_obj.job_seniority_title.name or '',
                'leave_holiday_plan' : contract_info_obj.leave_holiday_plan.name or '',
                'type_id' : contract_info_obj.type_id.name or '',
                'trial_date_start' : contract_info_obj.trial_date_start or '',
                'trial_date_end' : contract_info_obj.trial_date_end or '',
                'date_start' : contract_info_obj.date_start or '',
                'date_end' : contract_info_obj.date_end or '',
                'notice' : contract_info_obj.notice or '',
                'draw_type_id' : contract_info_obj.draw_type_id.draw_type or '',
                'production_basis' : contract_info_obj.production_basis or 0.00,
                'production_rate' : contract_info_obj.production_rate or 0.00,
                'discount_rate' : contract_info_obj.discount_rate or 0.00,
                'annual_draw' : contract_info_obj.annual_draw or 0.00,
                'payout_delay' : contract_info_obj.payout_delay or '',
                'wage' : contract_info_obj.wage or '',
                'salary_computation_method' : contract_info_obj.salary_computation_method or '',
                'struct_id' : contract_info_obj.struct_id.name or '',
                'notes' : contract_info_obj.notes or '',
                'job_position_list' : job_position_list,
                'production_list' : production_list,
#                 'click_next' : form_info_obj.substate_id if summary_view==1 else 'contract',
                'click_next' : 'con_summary',
                'benefits_list' : benefits_list
            }

            return contract_info_dict

        else:
            raise ValidationError(_('Please create contract by clicking "Click Here to Create Contract"'))

    def get_sub_state_id(self,form_id):
        complete_state_obj = self.env['hr.employee.onboarding'].search([('id' , '=' , form_id)]) 
        sub_state=[('started', 'GetStarted0'),
                                 ('personal', 'PersonalInformation1'),
                                 ('experience', 'ExperienceandCertifications2'),
                                 ('employement', 'EmployementInformation3'),
                                 ('offer_summary', 'Summary4'),
                                 ('consent', 'BackgroundCheckConsent5'),
                                 ('background', 'BackgroundCheck6'),
                                 ('back_summary', 'Summary7'),
                                 ('adverse', 'AdverseAction8'),
                                 ('inine', 'i99'),
                                 ('everify', 'E-Verify10'),
                                 ('app_summary', 'ApplicantSummary/Hire11'),
                                 ('ben_eligiblity', 'BenefitsEligibility12'),
                                 ('welcome', 'WelcomeEmail13'),
                                 ('appraisal', 'AppraisalPlan14'),
                                 ('hire_summary', 'Summary15'),
                                 ('ben_survey', 'BenefitsSurveyResults16'),
                                 ('emp_summary', 'EmployeeSummary17'),
                                 ('contract', 'CreateContract18'),
                                 ('con_summary', 'ContractSummary19'),
                                 ('completed', 'Complete20')]   
         
        return [item[1] for item in sub_state if item[0] == complete_state_obj.substate_id][0]
       
    def complete_state(self,form_id):
        complete_state_obj = self.env['hr.employee.onboarding'].search([('id' , '=' , form_id)])  

        # if complete_state_obj.substate_id=='con_summary':
            # complete_state_obj.state_id = 'complete'
            # complete_state_obj.substate_id = 'completed'
            
        template_id = self.env.ref('vitalpet_onboarding.onboarding_complete_mail_template').id
        mail_template = self.env['mail.template'].browse(template_id)

        if mail_template:
            mail_template.send_mail(complete_state_obj.id, force_send=True)
        # else:
        #     raise ValidationError('Status is not updated please contact support team')
       

    def reject_applicant_from_planner(self,form_id):
        complete_state_obj = self.env['hr.employee.onboarding'].search([('id' , '=' , form_id)])   
        complete_state_obj.reject_date = fields.datetime.today().date()    

        complete_state_obj.state_id = 'reject'



    def smart_buttons(self,form_id):
        button_obj = self.env['hr.employee.onboarding'].search([('id' , '=' , form_id)])
        smart_button_dict={
            'applicant_id' : button_obj.applicant_id,
        }

        return smart_button_dict

    def remove_record(self,form_id,tree_id,current_model):
        if tree_id:
            remove_obj = self.env[current_model].search([('id','=',tree_id)])
            if current_model=='background.check.package':
                if remove_obj:
                    for rec in remove_obj.item.services:
                        check_id=self.env['background.check'].search([('item','=',rec.id),('background_check_id','=',int(form_id))], limit=1)
                        if check_id:
                            check_id.unlink()

            
            if remove_obj:
                for rec in remove_obj:
                    download=self.env['background.check.download'].search([('item','=',rec.item.id),('background_check_download_id','=',int(form_id))], limit=1)
                    if download:
                        download.unlink()
            remove_obj.unlink()
               
    def remainder_email_cron(self):

        onboarding_obj = self.env['hr.employee.onboarding'].search([])

        today = datetime.now().date()
        hiring_manager_template_id = self.env.ref('vitalpet_onboarding.hiring_manager_email_remainder_mail_template').id
        hiring_manager_mail_template = self.env['mail.template'].browse(hiring_manager_template_id)

        hr_supervisor_template_id =  self.env.ref('vitalpet_onboarding.hr_manager_email_remainder_mail_template').id
        hr_supervisor_mail_template = self.env['mail.template'].browse(hr_supervisor_template_id)

        for rec in onboarding_obj:
            doc_lst = []
            if rec.action_form_ids:
                for line in rec.action_form_ids:
                    if line.status_id != 'draft':
                        if line.date_sent:
                            if abs((today-datetime.strptime(str(line.date_sent), "%Y-%m-%d").date()).days) == 7:
                                doc_lst.append(({'document' : line.action_form.attachment_id.name,
                            'expiration' : line.expiration or''}))
                print doc_lst,'----'
                if rec.company.hr_supervisor:  
                    if doc_lst != []: 
                        hr_supervisor_mail_template.with_context(doc_list=doc_lst).send_mail(rec.id, force_send=True)
                if rec.company.manager_user_id:   
                    if doc_lst != []:
                        hiring_manager_mail_template.with_context(doc_list=doc_lst).send_mail(rec.id, force_send=True)


    def documents_expiration_cron(self):
        onboarding_obj = self.env['hr.employee.onboarding'].search([('state_id' , '!=' , 'complete')])
        today_date = datetime.now().date()

        # template_id = self.env.ref('vitalpet_onboarding.document_expired_remainder_mail_template').id
        # mail_template = self.env['mail.template'].browse(template_id)

        for record in onboarding_obj:
            # doc_lst = []
            for rec in record.applicant_background_ids:
                if rec.expiration:
                    if rec.expiration < str(today_date):
                        rec.request_id.state = 'canceled'
                        # doc_lst.append(rec.document.attachment_id.name)

            for rec in record.employer_background_ids:
                if rec.expiration:
                    if rec.expiration < str(today_date):
                        rec.request_id.state = 'canceled'
                        # doc_lst.append(rec.document.attachment_id.name)

            for rec in record.consent_form_ids:
                if rec.expiration:
                    if rec.expiration < str(today_date):
                        rec.request_id.state = 'canceled'
                        # doc_lst.append(rec.consent_form.attachment_id.name)

            for rec in record.welcome_mail_ids:
                if rec.expiration:
                    if rec.expiration < str(today_date):
                        rec.request_id.state = 'canceled'
                        # doc_lst.append(rec.document.attachment_id.name)

            # if doc_lst != []:
            #     if mail_template:
            #         mail_template.with_context(doc_list=doc_lst).send_mail(record.id, force_send=True)


    def remainder_mail_about_expiration(self):
        onboarding_obj = self.env['hr.employee.onboarding'].search([('state_id' , '!=' , 'complete')])        
        today_date = datetime.now().date()

        template_id = self.env.ref('vitalpet_onboarding.document_complete_remainder_mail_template').id
        mail_template = self.env['mail.template'].browse(template_id)

        for record in onboarding_obj:
            doc_lst = []

            for rec in record.applicant_background_ids:
                if rec.status_id != 'signed' and rec.status_id != 'canceled':
                    if str(today_date) <= rec.expiration or rec.date_sent:
                        doc_lst.append(({'document' : rec.document.attachment_id.name,
                            'expiration' : rec.expiration or''}))

            for rec in record.employer_background_ids:
                if rec.status_id != 'signed' and rec.status_id != 'canceled':
                    if str(today_date) <= rec.expiration or rec.date_sent:
                        doc_lst.append(({'document' : rec.document.attachment_id.name,
                            'expiration' : rec.expiration or''}))

            for rec in record.consent_form_ids:
                if rec.status_id != 'signed' and rec.status_id != 'canceled':
                    if str(today_date) <= rec.expiration or rec.date_sent:
                        doc_lst.append(({'document' : rec.consent_form.attachment_id.name,
                            'expiration' : rec.expiration or''}))

            for rec in record.welcome_mail_ids:
                if rec.status_id != 'signed' and rec.status_id != 'canceled':
                    if str(today_date) <= rec.expiration or rec.date_sent:
                        doc_lst.append(({'document' : rec.document.attachment_id.name,
                            'expiration' : rec.expiration or''}))

            if doc_lst != []:
                if mail_template:
                    mail_template.with_context(doc_list=doc_lst).send_mail(record.id, force_send=True)


    def everify_state(self,form_id):
        everify_obj = self.env['hr.employee.onboarding'].search([('id' , '=' , form_id)])
        everify_obj.e_verify = 'completed'

        return everify_obj.e_verify

# class EverifyCaseResult(models.Model):
#     _name = "everify.case.result"

#     case_number = fields.Char("Case Number")
#     status = fields.Char("Status")
#     message_code = fields.Integer("Message Code")
#     eligiblity_statement = fields.Char("Eligiblity Statement")
#     statement_details = fields.Char("Statement Details")
#     date_sent = fields.Date("Date Sent")
#     date_received = fields.Date("Date Received")
#     case_status = fields.Selection([
#         ("eelig", "EELIG - The employee continues to work for the employer after receiving an Employement Authorization results"),
#         ("efnc", "EFNC - The employee continues to work for the employer after receiving an Final Nonconfirmation results"),
#         ("enoact", "ENOACT - The employee continues to work for the employer after receiving an No Show results.Employer retains Employee"),
#         ("euncnt", "EUNCNT - The employee continues to work for the employer after choosing not to consent a tentative Nonconfirmation"),
#         ("trmfnc", "TRMFNC - The employee was teerminated by the employer for receiving Final Nonconfirmation results"),
#         ("equit", "EQUIT - The employee voluntarily quit working for the employer"),
#         ("trem", "TERM - The employee was terminated by the employer for reason other than E-Verify"),
#         ("noact", "NOACT - The employee was terminated by the employer for receiving an No Show results"),
#         ("uncnt", "UNCNT - The employee was terminated by the employer for choosing not to consent a tentative Nonconfirmation"),
#         ("dup", "DUP - The case is invalid because another case with the same data already exists"),
#         ("incdat", "INCDAT - The case is invalid because the data entered is incorrect"),
#         ("teciss", "TECISS - The case is being closed because of technical issues with E-Verify"),
#         ("isdp", "ISDP - The case is duplicate because the employer created a case with the same data within the pase 30 days")
#     ], string='Closure Reason')
#     everify_download_url = fields.Char('Everify Download URL')
#     everify_case_result_id = fields.Many2one('hr.employee.onboarding',string="Everify Case Result Ref")

      
class BenefitsSurvey(models.Model):
    _name = "welcome.survey"

    request_id = fields.Many2one('survey.user_input', string="Request Ref")
    survey = fields.Many2one('survey.survey', string="Survey")
    survey_link = fields.Char("Link")
    status_id = fields.Selection([
        ("new", "Not Yet Started"),
        ("skip", "Partially Completed"),
        ("done", "Completed")
    ], default='new',string='Status',related='request_id.state')
    date_sent = fields.Date("Date Sent")
    expiration = fields.Date("Expiration")
    welcome_benefit_survey_id = fields.Many2one('hr.employee.onboarding', string="Welcome Mail Ref")

class WelcomeMail(models.Model):
    _name = "welcome.mail"

    request_id = fields.Many2one('signature.request', string="Request Ref")
    document = fields.Many2one('signature.request.template', string="Document")
    doc_link = fields.Char("Link")
    status_id = fields.Selection([
        ("draft", "Draft"),
        ("sent", "Signatures in Progress"),
        ("signed", "Fully Signed"),
        ("canceled", "Cancelled")
    ], default='draft',string='Status',related='request_id.state')
    date_sent = fields.Date("Date Sent")
    expiration = fields.Date("Expiration")
    welcome_mail_id = fields.Many2one('hr.employee.onboarding', string="Welcome Mail Ref")

 
class ConsentForm(models.Model):
    _name = "consent.form"
    
    request_id = fields.Many2one('signature.request', string="Request Ref")
    consent_form = fields.Many2one('signature.request.template', string="Consent Form")
    form_link = fields.Char("Link")
    status_id = fields.Selection([
        ("draft", "Draft"),
        ("sent", "Signatures in Progress"),
        ("signed", "Fully Signed"),
        ("canceled", "Cancelled")
    ], default='draft',string='Status',related='request_id.state')
    date_sent = fields.Date("Date Sent")
    expiration = fields.Date("Expiration")
    consent_form_id = fields.Many2one('hr.employee.onboarding', string="Consent Form Ref")

    
class AdverseAction(models.Model):
    _name = "adverse.action"
    
    request_id = fields.Many2one('signature.request', string="Request Ref")
    action_form = fields.Many2one('signature.request.template', string="Action Form")
    form_link = fields.Char("Link")
    status_id = fields.Selection([
        ("draft", "Draft"),
        ("sent", "Signatures in Progress"),
        ("signed", "Fully Signed"),
        ("canceled", "Cancelled")
    ], default='draft',string='Status',related='request_id.state')
    date_sent = fields.Date("Date Sent")
    expiration = fields.Date("Expiration")
    action_form_id = fields.Many2one('hr.employee.onboarding', string="Adverse Action Ref")


class ApplicantBackground(models.Model):
    _name = "applicant.background"
    
    request_id = fields.Many2one('signature.request', string="Request Ref")
    document = fields.Many2one('signature.request.template', string="Document")
    doc_link = fields.Char("Link")
    status_id = fields.Selection([
        ("draft", "Draft"),
        ("sent", "Signatures in Progress"),
        ("signed", "Fully Signed"),
        ("canceled", "Cancelled")
    ], default='draft',string='Status',related='request_id.state')
    date_sent = fields.Date("Date Sent")
    expiration = fields.Date("Expiration")
    applicant_background_id = fields.Many2one('hr.employee.onboarding', string="Applicant Background Ref")

  

class EmployerBackground(models.Model):
    _name = "employer.background"
    
    request_id = fields.Many2one('signature.request', string="Request Ref")
    document = fields.Many2one('signature.request.template', string="Document")
    doc_link = fields.Char("Link")
    status_id = fields.Selection([
        ("draft", "Draft"),
        ("sent", "Signatures in Progress"),
        ("signed", "Fully Signed"),
        ("canceled", "Cancelled")
    ], default='draft',string='Status',related='request_id.state')
    date_sent = fields.Date("Date Sent")
    expiration = fields.Date("Expiration")
    employer_background_id = fields.Many2one('hr.employee.onboarding', string="Employer Background Ref")


class BackgroundCheck(models.Model):
    _name = "background.check"
    
    item = fields.Many2one('background.config', string="Item")
    status_id = fields.Selection([
        ("open", "Open"),
        ("record", "Record"),
        ("norecord", "No Record"),
        ("completed", "Completed")
    ],string='Status')
    background_check_id = fields.Many2one('hr.employee.onboarding', string="Background Check Ref")

class BackgroundCheckPackage(models.Model):
    _name = "background.check.package"
    
    item = fields.Many2one('background.config', string="Package")
    background_check_package_id = fields.Many2one('hr.employee.onboarding', string="Background Check Package Ref") 


class BackgroundCheckDownload(models.Model):
    _name = "background.check.download"
    
    item = fields.Many2one('background.config', string="Item")
    attachment=fields.Char('Attachment URL')
    background_check_download_id = fields.Many2one('hr.employee.onboarding', string="Background Check Download Ref")    


class AcademicExperience(models.Model):
    _name = "academic.experience"
    
    academic_experience = fields.Char("Academic Experience")
    institute = fields.Char("Institution")
    diploma = fields.Char("Diploma")
    field_of_study = fields.Char("Field of Study")
    start_date = fields.Date("Start Date")
    end_date = fields.Date("End Date")
    academic_experience_id = fields.Many2one('hr.employee.onboarding', string="Academic Experience Ref")

class ProfessionalExperience(models.Model):
    _name = "professional.experience"
    
    position = fields.Char("Position")
    employer = fields.Char("Employer")
    start_date = fields.Date("Start Date")
    end_date = fields.Date("End Date")
    professional_experience_id = fields.Many2one('hr.employee.onboarding', string="Professional Experience Ref")

class CertificationDetails(models.Model):
    _name = "certification.details"
    
    certifications = fields.Char("Certifications")
    certificate_code = fields.Char("Certification #")
    issued_by = fields.Char("Issued By")
    professional_license = fields.Boolean("Professional License")
    state_issued_id = fields.Many2one('res.country.state',"State Issued")
    start_date = fields.Date("Start Date")
    end_date = fields.Date("End Date")
    certification_id = fields.Many2one('hr.employee.onboarding', string="Certification Ref")

class EmployeeSettings(models.Model):
    _name = "employee.settings"
    _rec_name = "calendar_year"
    
    calendar_year = fields.Char("Calendar Year")
    country = fields.Many2one('res.country', string="Country")
    emp_tax_doc = fields.Many2many('signature.request.template', 'emp_tax_documents', string="Employee Tax Document", domain=[('archived', '=', False)])
    non_emp_tax_doc = fields.Many2many('signature.request.template', 'non_emp_tax_documents',string="Non Employee Tax Document", domain=[('archived', '=', False)])
    welcome_email = fields.Many2one('mail.template', string="Welcome Email")
    direct_deposit_template = fields.Many2one('signature.request.template', string="Direct Deposit Template")
    emp_contract_type = fields.Many2many('hr.contract.type','emp_con_type' , string="Employee Contract Types")
    non_emp_contract_type = fields.Many2many('hr.contract.type','non_emp_con_type' , string="Non Employee Contract Types")
    emp_consent_form = fields.Many2many('signature.request.template','emp_consent_form' , string="Employee Consent Form")
    emp_config_ids = fields.One2many('employee.config', 'emp_details_id', string="Employee Rules")
    personal_info_template = fields.Many2one('signature.request.template',string="Personal Information Email")
    applicant_i9_template_id = fields.Many2one('signature.request.template',string="Applicant Citizenship Form")
    employer_i9_template_id = fields.Many2one('signature.request.template',string="Employer Citizenship Form")

    _sql_constraints = [
        ('employee_settings_uniq', 'unique (calendar_year,country,emp_contract_type)',
         'You can not create for same Calendar Year/Country/Employee Contract Type')]
    
class EmployeeConfig(models.Model):
    _name = "employee.config"
    

    emp_details_id = fields.Many2one('employee.settings', string="Employee Setting Ref")
    seq_id = fields.Integer("ID",compute='_compute_sno')
    state_name = fields.Many2one('res.country.state', string="State Name")
    min_wage = fields.Float("Minimum Wage")
    overtime_min_wage = fields.Float("Overtime Minimum Wage")
    overtime_wage_factor = fields.Float("Overtime Wage Factor")
    week_overtime = fields.Integer("Weekly Overtime Hours")
    daily_overtime = fields.Integer("Daily Overtime Hours")
    emp_tax_document = fields.Many2many('signature.request.template', 'emp_signature_request_template',string="Employee Tax Document")
    non_emp_tax_document = fields.Many2many('signature.request.template', 'non_emp_signature_request_template', string="Non Employee Tax Document")
    employee_consent_document = fields.Many2many('signature.request.template', 'emp_consent_doc', string="Employee Consent Form")
    notes = fields.Char("Notes")

    def _compute_sno(self):
        i = 1
        for line in self:
            line.seq_id = i
            i+=1
    
class BackgroungCheck(models.Model):
    _name = "background.check.settings"
     
    name = fields.Many2one('res.partner', string="Related Partner",required=True)
    master_acc = fields.Many2one('account.account', string="Master Account")
    background_config_ids = fields.One2many('background.config', 'background_config_id', string="Reports")
    
    _sql_constraints = [
        ('background.check.settings_uniq', 'unique (name)',
         'This Related Partner is already exist')]
     
class BackgroundConfig(models.Model):
    _name = "background.config"
    
    seq_id = fields.Integer("ID",compute='_compute_sno') 
    sequence = fields.Integer("Sequence")
    code = fields.Char("Code",required=True)
    name = fields.Char("Name",required=True)
    description = fields.Char("Description")
    default = fields.Boolean("Default")
    basic_package = fields.Boolean("Basic Package")
    email = fields.Char("Email")
    services = fields.Many2many('background.config','name_rel','name_relation',string='Service Code')
    background_config_id = fields.Many2one('background.check.settings', string="Background Check Ref")


    def _compute_sno(self):
        i = 1
        for line in self:
            line.seq_id = i
            i+=1