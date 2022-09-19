
import re

import logging
from odoo import fields, models, api, _
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import ValidationError, UserError
from odoo.tools import email_split

_logger = logging.getLogger(__name__)

class Applicant_inherit(models.Model):
    _name = "hr.applicant"
    _inherit = ['hr.applicant','mail.thread', 'ir.needaction_mixin']

    response_interviewer_id = fields.Many2one('survey.user_input', "Response", ondelete="set null", oldname="response")
    score = fields.Float("Score", compute="_compute_score", default=0.0)

    @api.model
    def get_from_email(self):
        alias_name = self.env.ref('vitalpet_custom_hr_recruitment.mail_alias_recruitment').alias_name
        alias_domain = self.env["ir.config_parameter"].get_param("mail.catchall.domain")
#         return alias_name+"@"+alias_domain

    # @api.constrains('salary_proposed')
    # def _check_proposed_salary(self):
    #     if self.salary_proposed<=0:
    #         raise ValidationError(_('Proposed Salary cannot be 0.00')) 

    @api.model
    def create(self, vals):
        

        if "company_id" in vals:
            job=self.env['hr.job'].search([("id","=",vals["job_id"])])
            vals["company_id"]=job.company_id.id

        res_id=super(Applicant_inherit, self).create(vals)
# Send welcome invitaiton to applicant
        # if res_id:
        #     mails_to_send = self.env['mail.mail']
        #     rendering_context = dict(self._context)
        #     invitation_template = self.env.ref('vitalpet_custom_hr_recruitment.email_hr_recruitment_welcome')
        #     invitation_template = invitation_template.with_context(rendering_context)
        #     mail_id = invitation_template.send_mail(res_id.id)
        #     current_mail = self.env['mail.mail'].browse(mail_id)
        #     mails_to_send |= current_mail
        #     if mails_to_send :
        #         mails_to_send.send()
        
        return res_id

    @api.depends('response_interviewer_id')
    def _compute_score(self):
        for user_input in self:
            if user_input.response_id.token:
                user_input.score = self.env['survey.user_input'].search([('token','=',user_input.response_id.token)]).quizz_score
            
    @api.multi
    def action_start_survey(self):
        self.ensure_one()
        # create a response and link it to this applicant
        if not self.response_interviewer_id:
            response = self.env['survey.user_input'].create({'survey_id': self.survey_id.id, 'partner_id': self.partner_id.id})
            self.response_interviewer_id = response.id
        else:
            response = self.response_interviewer_id
        # grab the token of the response and start surveying
        return self.survey_id.with_context(survey_token=response.token).action_start_survey()
    
    @api.multi
    def action_print_survey(self):
        """ If response is available then print this response otherwise print survey form (print template of the survey) """
        self.ensure_one()
        if not self.response_interviewer_id:
            if self.survey_id:
                return self.survey_id.action_print_survey()
            else:                
                raise ValidationError(_('Survey is not configured'))
        else:
            response = self.response_interviewer_id
            return self.survey_id.with_context(survey_token=response.token).action_print_survey()
        
    @api.multi
    def action_start_survey_applicant(self):
        self.ensure_one()
        # create a response and link it to this applicant
        if not self.response_id:
            response = self.env['survey.user_input'].create({'survey_id': self.job_id.application_survey_id.id, 'partner_id': self.partner_id.id})
            self.response_id = response.id
        else:
            response = self.response_id
        # grab the token of the response and start surveying
        return self.job_id.application_survey_id.with_context(survey_token=response.token).action_start_survey()        
    

    @api.multi
    def action_viewAnswers(self):
        """ This opens Meeting's calendar view to schedule meeting on current applicant
            @return: Dictionary value for created Meeting view
        """
        self.ensure_one()
        partners = self.partner_id | self.user_id.partner_id | self.department_id.manager_id.user_id.partner_id

        category = self.env.ref('hr_recruitment.categ_meet_interview')
        res = self.env['ir.actions.act_window'].for_xml_id('calendar', 'action_calendar_event')
        res['context'] = {
            'search_default_partner_ids': self.partner_id.name,
            'default_partner_ids': partners.ids,
            'default_user_id': self.env.uid,
            'default_name': self.name,
            'default_categ_ids': category and [category.id] or False,
        }
        return res

#     @api.model
#     def message_new(self, msg_dict, custom_values=None):
#         if custom_values is None:
#             custom_values = {}
# 
#         email_subject = msg_dict.get('subject', '')
#         pattern = '\[([APP^)]*)\]'
#         applicant_id = re.search(pattern, email_subject)
#         if applicant_id is None:
#             return super(Applicant_inherit, self).message_new(msg_dict, custom_values)
#         else:
#             applicant = self.env['hr.applicant'].search([('id', '=', applicant_id)])
#             if applicant:
#                 applicant._post_messages_line_items("text")
# 
# 
#         return super(Applicant_inherit, self).message_new(msg_dict, custom_values)

    def website_job_reapply(self,email, job_id):
        applicant_ids = self.env['hr.applicant'].search([('email_from','=',email),('job_id.id','=',job_id)])
        result = 0
        for recs in applicant_ids:
            if recs:
                result = 1
        return result  
                  
class ProductionType(models.Model):
    _name = "hr.job.seniority.title"
    _order= 'sequence asc'

    name = fields.Char("Display Title",required=True)
    sequence = fields.Integer("Sequence")

    _sql_constraints = [
        ('sequence_uniq', 'unique (sequence)','Sequence Number must be unique')]
   
    
    @api.model
    def create(self, vals):
        if vals['sequence']<1:
            raise UserError('Sequence Number must be greater than 0')
        line = super(ProductionType, self).create(vals)
        return line

    @api.multi
    def write(self, vals):
        if vals.get('sequence'):
            sequence = vals.get('sequence')
        else:
            sequence = self.sequence
        for employee in self.env['hr.employee'].search([('job_seniority_title','=',self.id)]):
            employee.sequence = sequence
        
        return super(ProductionType, self).write(vals)


    
class JobTemplate(models.Model):
    _name = "hr.job.template"
        
#     @api.model
#     def _default_account(self):
#         settings=self.env['hr.recruitment.settings.new'].search([])
#         if settings.production_account_id:
#             return settings.production_account_id
#     @api.onchange('production_account_id')
#     def onchange_production_account_id(self):
#         if self.production_account_id:
#             domain_tags = "[('id', 'in', "+ str([i.id for i in self.production_account_id.tag_ids]) +")]"
#             return {'domain': {'production_type_ids': domain_tags}}
#     @api.model
#     def default_get(self, fields):
#         res = super(JobTemplate, self).default_get(fields)
#         if self.env['ir.values'].get_default('hr.job.template',company_id=self.env.user.company_id.id):
#             return res
#         else:
#             raise UserError('Please configure production account in configuration')

    name = fields.Char("Name",required=True)   
    active_state = fields.Boolean("Active")
    survey_job_position = fields.Boolean("Survey on Job Position")
   
    job_description = fields.Text("Job Description")
    application_survey_id = fields.Many2one("survey.survey",string="Applicant Survey")
    interviewer_survey_id = fields.Many2one("survey.survey",string="Interviewer Survey")
    email_template_id = fields.Many2one("mail.template",string="Offer Email Template")
#     production_account_id = fields.Many2one("account.analytic.account","Production Account",readonly=True)
#     domain_production_type_ids = fields.Many2many("hr.production.tag",  string="Domain Production Type")
    production_type_ids = fields.Many2many("hr.production.tag",string="Production Type",required=True)
    job_seniority_id = fields.Many2many("hr.job.seniority.title",string="Job seniority title",required=True)
    career_goals_survey = fields.Many2one("survey.survey",string="Career Goals Survey")
    short_survey_id = fields.Many2one("survey.survey",string="Short Review Survey")
    long_survey_id = fields.Many2one("survey.survey",string="Long Review Survey")
    colleague_survey_id = fields.Many2one("survey.survey",string="Colleague Review Survey")
    
#     @api.multi
#     @api.onchange('city_state')   
#     def _onchange_city_state(self):
#         if self.city_state == True:
#             form_id = self.env.ref('vitalpet_custom_hr_recruitment.view_overwrite_city_state').id
#             print form_id
#             return {
#                         'name': _('Over Write City and State'),
#                         'type': 'ir.actions.act_window',
#                         'view_type': 'form',
#                         'view_mode': 'form',
#                         'res_model': 'overwrite.city.state',
#                         'view_id': False,
#                         'views': [(form_id, 'form')],
#                         'target': 'new',
#                         
#                     }
    @api.multi
    def write(self, vals):
        res=super(JobTemplate, self).write(vals)
        if vals.get('application_survey_id'):
            job_obj = self.env['hr.job'].search([('job_template' , '=' , self.id)])
            for rec in job_obj:
                rec.sudo().application_survey_id = vals.get('application_survey_id')

        if vals.get('interviewer_survey_id'):
            job_obj = self.env['hr.job'].search([('job_template' , '=' , self.id)])
            for rec in job_obj:
                rec.sudo().survey_id = vals.get('interviewer_survey_id')

        if vals.get('career_goals_survey'):
            job_obj = self.env['hr.job'].search([('job_template' , '=' , self.id)])
            for rec in job_obj:
                rec.sudo().career_goals_survey = vals.get('career_goals_survey')

        if vals.get('short_survey_id'):
            job_obj = self.env['hr.job'].search([('job_template' , '=' , self.id)])
            for rec in job_obj:
                rec.sudo().short_survey_id = vals.get('short_survey_id')

        if vals.get('long_survey_id'):
            job_obj = self.env['hr.job'].search([('job_template' , '=' , self.id)])
            for rec in job_obj:
                rec.sudo().long_survey_id = vals.get('long_survey_id')

        if vals.get('colleague_survey_id'):
            job_obj = self.env['hr.job'].search([('job_template' , '=' , self.id)])
            for rec in job_obj:
                rec.sudo().colleague_survey_id = vals.get('colleague_survey_id')

        return res

    @api.multi
    def survey_write(self):
        template_obj = self.env['hr.job.template'].search([])

        for rec in template_obj:
            job_obj = self.env['hr.job'].search([('job_template' , '=' , rec.id)])
            for record in job_obj:
                record.sudo().application_survey_id = rec.application_survey_id if rec.application_survey_id else None
                record.sudo().survey_id = rec.interviewer_survey_id if rec.interviewer_survey_id else None
                record.sudo().career_goals_survey = rec.career_goals_survey if rec.career_goals_survey else None
                record.sudo().short_survey_id = rec.short_survey_id if rec.short_survey_id else None 
                record.sudo().long_survey_id = rec.long_survey_id if rec.long_survey_id else None 
                record.sudo().colleague_survey_id = rec.colleague_survey_id if rec.colleague_survey_id else None
                
                print rec,'--',rec.application_survey_id,'--',rec.interviewer_survey_id,'--',rec.career_goals_survey,'--',rec.short_survey_id,'--',rec.long_survey_id,'--',rec.colleague_survey_id



class Job(models.Model):

    _inherit = "hr.job"
    
#     @api.model
#     def default_get(self, fields):
#         res = super(Job, self).default_get(fields)
#         print 'ttrt'
#         if self.job_template:
#             print 'tete'
#             if self.job_template.job_seniority_id:
#                 print 'ghb'
#                 res.update({'job_seniority_value': [(6, 0, self.job_template.job_seniority_id.ids)]})  
# #                 self.job_seniority_value = self.job_template.job_seniority_id.ids        
#         return res
    
#     @api.depends('job_template')
#     def _get_seniority_titles(self):
#         print "something"      
#         if self.job_template:
#             if self.job_template.job_seniority_id:  
#                 self.job_seniority_value = self.job_template.job_seniority_id.ids  
#         else:
#             self.job_seniority_value = None 
    city_state = fields.Boolean("Over Write City and State")
    overwrite_city_ids = fields.One2many('over_write.city', 'job_temp_id',string="")
    city_wizard= fields.Char("City")
    state_wizard_id = fields.Many2one("res.country.state",string='State')
    short_survey_id = fields.Many2one("survey.survey",string="Short Review Survey")
    long_survey_id = fields.Many2one("survey.survey",string="Long Review Survey" )
    colleague_survey_id = fields.Many2one("survey.survey",string="Colleague Review Survey")
    career_goals_survey = fields.Many2one("survey.survey",string="Career Goals Survey")
    job_template = fields.Many2one("hr.job.template",string="Job Template",required=True,domain=[('active_state', '=', True)])
    job_seniority_id = fields.Many2one("hr.job.seniority.title",string="Job seniority title",required=True)
    application_survey_id = fields.Many2one("survey.survey",string="Applicant Survey")
    job_type= fields.Many2one('hr.contract.type',string="Job Type")
    description_box = fields.Boolean()
    introduction = fields.Text(string="Introduction",help="Provide a brief introduction to the position.  Some users use this space to introduce their company to the candidate.")
    introduction_box = fields.Boolean()
    description = fields.Text(string="Job Description", help="Enter in your own job description if you prefer to use different text than the standard job description.")
    final_paragraph = fields.Text(string="Final Paragraph", help="Enter any closing remarks. Some users use this space to describe their parent company.")
    final_paragraph_box = fields.Boolean(string="Final Paragraph")
#     production_account_id = fields.Many2one("account.analytic.account","Production Account",readonly=True)
#     domain_production_type_ids = fields.Many2many("hr.production.tag", "domain_job_production_tags_new", "template_id", "tag_id", related="job_template.production_type_ids", string="Domain Production Type")
    production_type_ids = fields.Many2many("hr.production.tag",string="Bonus")
    site_key = fields.Char("Site Key")
    secret_key = fields.Char("Secret key")
    survey_id = fields.Many2one('survey.survey', "Interviewer Survey")
#     career_goals_survey = fields.Many2one("survey.survey",string="Career Goals Survey")
    job_seniority_value = fields.Many2many("hr.job.seniority.title", string="Job Domain")
    survey_job_position = fields.Boolean("Survey Job Position",compute = "_compute_job_position")
    
    @api.multi
    def _compute_job_position(self):
        job_obj = self.env['hr.job.template'].search([('id' , '=' , self.job_template.id)])
        if job_obj.survey_job_position == True:
            self.survey_job_position = True
        else:
            self.survey_job_position = False    
            
    @api.multi
    def action_print_applicant_survey(self):
        return self.application_survey_id.action_print_survey()
    
   
           
    # @api.onchange('job_template')
    # def on_change_job_template(self):
    #     print 123
    #     if self.job_template:
    #         if self.job_template.job_seniority_id:  
    #             self.job_seniority_value = self.job_template.job_seniority_id.ids  
    #     else:
    #         self.job_seniority_value = None

    #     job_seniority_id = False
    #     res = {'domain': {
    #     'job_seniority_id': "[('id', '=', False)]",
    #     }}
    #     if self.job_template and self.job_template.job_seniority_id:
    #         jrl_ids = self.job_template.job_seniority_id.ids
    #         res['domain']['job_seniority_id'] = "[('id', 'in', %s)]" % jrl_ids
    #     self.job_seniority_id = job_seniority_id
    #     return res   

    @api.onchange('job_template')
    def on_change_job_template(self):

        res = {'domain': {
        'job_seniority_id': "[('id', '=', False)]",
        }}
        
        if self.job_template:
            if self.job_template.job_seniority_id:  
                res['domain']['job_seniority_id'] = "[('id', 'in', %s)]" % self.job_template.job_seniority_id.ids
            else:
                res['domain']['job_seniority_id'] = []
        return res

    @api.multi
    def write(self, vals):
        res=super(Job, self).write(vals)
        if vals.get('job_template'):
            template_obj = self.env['hr.job.template'].search([('id' , '=' , vals.get('job_template'))])

            if template_obj.application_survey_id:
                self.sudo().application_survey_id = template_obj.application_survey_id
            else:
                self.sudo().application_survey_id = False

            if template_obj.interviewer_survey_id:
                self.sudo().survey_id = template_obj.interviewer_survey_id
            else:
                self.sudo().survey_id = False

            if template_obj.short_survey_id:
                self.sudo().short_survey_id = template_obj.short_survey_id
            else:
                self.sudo().short_survey_id = False

            if template_obj.long_survey_id:
                self.sudo().long_survey_id = template_obj.long_survey_id
            else:
                self.sudo().long_survey_id = False

            if template_obj.colleague_survey_id:
                self.sudo().colleague_survey_id = template_obj.colleague_survey_id
            else:
                self.sudo().colleague_survey_id = False

            if template_obj.career_goals_survey:
                self.sudo().career_goals_survey = template_obj.career_goals_survey
            else:
                self.sudo().career_goals_survey = False
        
        return res
      
              
#     @api.onchange('job_template')
#     def on_change_job_templates(self):
#         job_seniority_id = False
#         res = {'domain': {
#         'job_seniority_id': "[('id', '=', False)]",
#         }}
#         if self.job_template and self.job_template.job_seniority_id:
#             jrl_ids = self.job_template.job_seniority_id.ids
#             res['domain']['job_seniority_id'] = "[('id', 'in', %s)]" % jrl_ids
#         self.job_seniority_id = job_seniority_id
#         return res

    @api.multi
    def set_open(self):
        self.write({'website_published': False})
        stages=self.env['hr.recruitment.stage'].search([])
        for stage in stages:
            if stage.name != 'Offer Letter' and stage.name !='Onboarding':
                applications = self.env['hr.applicant'].search([('stage_id', '=', stage.id),('job_id', '=', self.id)])
                for application in applications:
                    # if application.refuse_template:
                    #     application.refuse_template.send_mail(application.id, force_send=True, raise_exception=True)
                    # application.write({'active': False})
                    if stage.is_archive:
                        application.archive_applicant()
                    else:
                        if application.refuse_template:
                            application.refuse_template.send_mail(application.id, force_send=True, raise_exception=True)


        return super(Job, self).set_open()
          
class Applicant(models.Model):
    _inherit = "hr.applicant"
    

    
    @api.multi
    def archive_applicant(self):
        self.write({'active': False})
        print self.refuse_template

        if self.refuse_template:
            self.refuse_template.send_mail(self.id, force_send=True, raise_exception=True)  
        else:
            raise UserError(_('Regret template is not defined in settings'))
        
    
    
    
    def _default_stage_id(self):
        if self._context.get('default_job_id'):
            ids = self.env['hr.recruitment.stage'].search([
                '|',
                ('job_id', '=', False),
                ('job_id', '=', self._context['default_job_id']),
                ('fold', '=', False)
            ], order='sequence asc', limit=1).ids
            if ids:
                return ids[0]
        return False
    
    name = fields.Char(
        compute="_compute_name",
        inverse="_inverse_name_after_cleaning_whitespace",
        required=False,
        store=True)
    
    partner_name = fields.Char("First Name",required=True)
    last_name = fields.Char("Last Name",required=True)
    middle_name = fields.Char("Middle Name")
    site_key = fields.Char("Site Key")
    secret_key = fields.Char("Secret key")
    refuse_template = fields.Many2one("mail.template", string="Refuse Template")
    mail_id = fields.Many2one("mail.message")
    stage_id = fields.Many2one('hr.recruitment.stage', 'Stage', track_visibility='onchange',
                               domain="['|', ('job_id', '=', False), ('job_id', '=', job_id)]",
                               copy=False, index=True,
                               group_expand='_read_group_stage_ids',
                               default=_default_stage_id,write=['group_hr_recruitment_recruiter'])
        
    btn_score = fields.Boolean("Score", related="stage_id.score")
    btn_meetings = fields.Boolean("Meetings", related="stage_id.meetings")
    btn_start_interview = fields.Boolean("Start Interview", related="stage_id.start_interview")
    btn_print_interview = fields.Boolean("Print Interview", related="stage_id.print_interview")
    btn_documents = fields.Boolean("Documents", related="stage_id.documents")
    btn_send_offer_letter = fields.Boolean("Send Offer Letter", related="stage_id.send_offer_letter")
    is_internal = fields.Selection([
            ('yes', 'Yes'),
            ('no', 'No'),
            ],string="Are you an Internal candidate?")
    seniority_title_id = fields.Many2one("hr.job.seniority.title",string="Job Seniority Title")
    job_city= fields.Char("City")
    job_state_id = fields.Many2one("res.country.state",string='State')
    
    @api.onchange('job_id')
    def on_change_job_id(self):

        res = {'domain': {
        'seniority_title_id': "[('id', '=', False)]",
        }}

        if self.job_id:
            self.company_id=self.job_id.company_id.id
            if self.job_id.job_template: 
                if self.job_id.job_template.job_seniority_id:
                    res['domain']['seniority_title_id'] = "[('id', 'in', %s)]" % self.job_id.job_template.job_seniority_id.ids
                else:
                    res['domain']['seniority_title_id'] = []

        return res
    
    """ compute name """
    
    @api.model
    def create(self, vals):        
        """Add inverted names at creation if unavailable."""
        context = dict(self.env.context)
       
        name = vals.get("name", context.get("default_name")) 
        if name is not None:
           
            # Calculate the splitted fields
            inverted = self._get_inverse_name(
                self._get_whitespace_cleaned_name(name)
                )
            for key, value in inverted.iteritems():
                if not vals.get(key) or context.get("copy"):
                    vals[key] = value
            # Remove the combined fields
            if "name" in vals:                              
                del vals["name"]
            if "default_name" in context:                
                del context["default_name"] 

        if vals.get('job_id') and vals.get('email_from'):
            applicant_obj = self.env['hr.applicant'].search([('email_from','=',vals.get('email_from'))])
            for rec in applicant_obj:
                print vals.get('contract_type_id'),'--',rec.contract_type_id.id
                if vals.get('email_from') == rec.email_from  and vals.get('job_id') == rec.job_id.id and vals.get('contract_type_id') == rec.contract_type_id.id:
                    print vals.get('contract_type_id'),'---True---'
                    raise UserError('You have already applied for the same job position') 

        if vals.get('job_city'):
            over_write_city = self.env['over_write.city'].sudo().search([('job_temp_id', '=', vals.get('job_id')), ('city_wizard', '=', vals.get('job_city'))])
            if over_write_city:
                vals['job_state_id']=over_write_city.state_wizard_id.id
        res = super(Applicant, self.with_context(context)).create(vals)

        if res.stage_id.name=='Onboarding':
            if res.salary_proposed <= 0 :
                raise ValidationError(_('Proposed Salary cannot be 0.00')) 
        if res:            
            template_id = self.env.ref('vitalpet_custom_hr_recruitment.applicant_acknowledgement_mail_template').id
            mail_template = self.env['mail.template'].browse(template_id)

            if mail_template:
                mail_template.send_mail(res.id, force_send=True)      


        return res


    @api.multi
    def write(self, vals):

        stage_obj = self.env['hr.recruitment.stage'].search([('name' , '=' , 'New')])

        if vals.get('stage_id'):
            if vals.get('stage_id') != stage_obj.id:
                if self.salary_proposed <= 0 :
                    raise ValidationError(_('Proposed Salary cannot be 0.00')) 

        return super(Applicant,self).write(vals)
      
    
    @api.model
    def default_get(self, fields_list):
        """Invert name when getting default values."""
        result = super(Applicant, self).default_get(fields_list)
        

        inverted = self._get_inverse_name(
            self._get_whitespace_cleaned_name(result.get("name", "")))
            # result.get("is_company", False))
     
        for field in inverted.keys():
            if field in fields_list:
                result[field] = inverted.get(field)
        
        return result
    
    @api.model
    def _names_order_default(self):
        return 'last_first'

    @api.model
    def _get_names_order(self):
        """Get names order configuration from system parameters.
        You can override this method to read configuration from language,
        country, company or other"""
        return self.env['ir.config_parameter'].get_param(
            'partner_names_order', self._names_order_default())
    
    @api.model
    def _get_computed_name(self, partner_name, middle_name, last_name):
        """Compute the 'name' field according to splitted data.
        You can override this method to change the order of lastname and
        firstname the computed name"""
        order = self._get_names_order()
        if order == 'last_first_comma':
            return u" ".join((p for p in (partner_name, middle_name, last_name) if p))
        elif order == 'first_last':
            return u" ".join((p for p in (partner_name, middle_name, last_name) if p))
        else:
            return u" ".join((p for p in (partner_name, middle_name, last_name) if p))

    
    @api.multi
    @api.depends("partner_name", "middle_name", "last_name")
    def _compute_name(self):
        """Write the 'name' field according to splitted data."""
        for record in self:
            record.name = record._get_computed_name(
                record.partner_name, record.middle_name, record.last_name
            )

    @api.multi
    def _inverse_name_after_cleaning_whitespace(self):
        """Clean whitespace in :attr:`~.name` and split it.

        The splitting logic is stored separately in :meth:`~._inverse_name`, so
        submodules can extend that method and get whitespace cleaning for free.
        """
        for record in self:
            # Remove unneeded whitespace
            clean = record._get_whitespace_cleaned_name(record.name)

            # Clean name avoiding infinite recursion
            if record.name != clean:
                record.name = clean

            # Save name in the real fields
            else:
                record._inverse_name()
                
                
    @api.model
    def _get_whitespace_cleaned_name(self, name, comma=False):
        """Remove redundant whitespace from :param:`name`.

        Removes leading, trailing and duplicated whitespace.
        """
        if name:
            name = u" ".join(name.split(None))
            if comma:
                name = name.replace(" ,", ",")
                name = name.replace(", ", ",")
        return name
    
    @api.model
    def _get_inverse_name(self, name,):
        """Compute the inverted name.

        - If the partner is a company, save it in the lastname.
        - Otherwise, make a guess.

        This method can be easily overriden by other submodules.
        You can also override this method to change the order of name's
        attributes

        When this method is called, :attr:`~.name` already has unified and
        trimmed whitespace.
        """
        # Company name goes to the lastname
        if not name:
            parts = [name or False, False]
        # Guess name splitting
        else:
            order = self._get_names_order()
            # Remove redundant spaces
            name = self._get_whitespace_cleaned_name(
                name, comma=(order == 'last_first_comma'))
            parts = name.split("," if order == 'last_first_comma' else " ", 1)
            if len(parts) > 1:
                if order == 'first_last':
                    parts = [u" ".join(parts[1:]), parts[0]]
                else:
                    parts = [parts[0], u" ".join(parts[1:])]
            else:
                while len(parts) < 2:
                    parts.append(False)
        return {"last_name": parts[0], "partner_name": parts[1]}
    
    
    @api.multi
    def _inverse_name(self):
        """Try to revert the effect of :meth:`._compute_name`."""
        for record in self:
            parts = record._get_inverse_name(record.name)
            record.last_name = parts['last_name']
            record.partner_name = parts['partner_name']
            
#     @api.multi
#     @api.constrains("partner_name", "last_name")
#     def _check_name(self):
#         
#         """Ensure at least one name is set."""
#         for record in self:
#             if not (record.partner_name or record.last_name) :
#                 raise exceptions.EmptyNamesError(record)
    
    @api.onchange("partner_name", "last_name","middle_name")
    def _onchange_subnames(self):
        """Avoid recursion when the user changes one of these fields.

        This forces to skip the :attr:`~.name` inversion when the user is
        setting it in a not-inverted way.
        """
        # Modify self's context without creating a new Environment.
        # See https://github.com/odoo/odoo/issues/7472#issuecomment-119503916.
        self.env.context = self.with_context(skip_onchange=True).env.context
        
    @api.onchange("name")
    def _onchange_name(self):
        """Ensure :attr:`~.name` is inverted in the UI."""
        if self.env.context.get("skip_onchange"):
            # Do not skip next onchange
            self.env.context = (
                self.with_context(skip_onchange=False).env.context)
        else:
            self._inverse_name_after_cleaning_whitespace()
    
    
    @api.model
    def _install_partner_firstname(self):
        """Save names correctly in the database.

        Before installing the module, field ``name`` contains all full names.
        When installing it, this method parses those names and saves them
        correctly into the database. This can be called later too if needed.
        """
        # Find records with empty firstname and lastname
        records = self.search([("partner_name", "=", False),
                               ("last_name", "=", False)])

        # Force calculations there
        records._inverse_name()
        _logger.info("%d partners updated installing module.", len(records))

    # Disabling SQL constraint givint a more explicit error using a Python
    # contstraint
    _sql_constraints = [(
        'check_name',
        "CHECK( 1=1 )",
        'Contacts require a name.'
    )]
    """ finishing computing name """

    @api.one
    def copy(self, default=None):
        default = dict(default or {})        
        raise UserError('Can not duplicate Applicant')
        return super(Applicant, self).copy(default)
    
    @api.multi    
    def action_preview_offer(self):
        context = dict(self.env.context or {})
        context['active_id'] = self.mail_id.id
        compose_form = self.env.ref('mail.view_mail_form', False)
        return {
            'name': _('Email message'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.message',
            'type': 'ir.actions.act_window',
            'context': context,
            'target': 'new',
            'res_id': self.mail_id.id,
            'flags': {'form': {'options': {'mode': 'view'}}}
        }
        
    @api.multi
    def action_offer_send(self):
        '''
        This function opens a window to compose an email, with the edi sale template message loaded by default
        '''
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('vitalpet_onboarding', 'offer_letter_mail_template')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict()
 
        ctx.update({
            'default_model': 'hr.applicant',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True
        })
        mail_id={
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }  
        
        return mail_id
    
     
class RecruitmentSettings(models.TransientModel):
    _inherit = 'hr.recruitment.config.settings'

    def _default_company_id(self):
        return self.env.user.company_id.id

    company_id = fields.Many2one("res.company","Company",default=_default_company_id)
    site_key = fields.Char("Site Key")
    secret_key = fields.Char("Secret key")
    refuse_template = fields.Many2one("mail.template", string="Refuse Template")
#     production_account_id = fields.Many2one("account.analytic.account", string="Production Account")
    alias_prefix = fields.Char('From Email')  # Used to store alias email id
    alias_domain = fields.Char('Alias Domain', readonly=True, default=lambda self: self.env["ir.config_parameter"].get_param("mail.catchall.domain"))
    
    # Used to store alias domain.
#     Get and set default used to store in mail_alias table
    @api.model
    def get_default_alias_prefix(self, fields):
        alias_name = self.env.ref('vitalpet_custom_hr_recruitment.mail_alias_recruitment').alias_name
        return {'alias_prefix': alias_name}

    @api.multi
    def set_default_alias_prefix(self):
        for record in self:
            self.env.ref('vitalpet_custom_hr_recruitment.mail_alias_recruitment').write({'alias_name': record.alias_prefix})
    
    
    @api.model
    def get_default_project_id(self, fields):
        res= {'site_key': self.env['ir.values'].get_default('hr.applicant', 'site_key'),
              'secret_key': self.env['ir.values'].get_default('hr.applicant', 'secret_key'),
              'refuse_template': self.env['ir.values'].get_default('hr.applicant', 'refuse_template'),
              'site_key': self.env['ir.values'].get_default('hr.job', 'site_key'),
              'secret_key': self.env['ir.values'].get_default('hr.job', 'secret_key'),
#               'production_account_id': self.env['ir.values'].get_default('hr.job.template', 'production_account_id',company_id=self.env.user.company_id.id),
#               'production_account_id': self.env['ir.values'].get_default('hr.job', 'production_account_id',company_id=self.env.user.company_id.id),
              }
        return res
    #
    # @api.multi
    # def set_default_refuse_template(self):
    #     ir_values_obj = self.env['ir.values']
    #     if self.refuse_template:
    #         ir_values_obj.sudo().set_default('hr.applicant', "refuse_template", self.refuse_template, for_all_users=True)

    @api.multi
    def set_captcha_settings(self):
        ir_values_obj = self.env['ir.values']
#         if self.production_account_id:
#             ir_values_obj.sudo().set_default('hr.job.template', "production_account_id", self.production_account_id.id, for_all_users=True,company_id=self.env.user.company_id.id)
#             ir_values_obj.sudo().set_default('hr.job', "production_account_id", self.production_account_id.id, for_all_users=True,company_id=self.env.user.company_id.id)
        if self.site_key:
            ir_values_obj.sudo().set_default('hr.applicant', "site_key", self.site_key, for_all_users=True)
            ir_values_obj.sudo().set_default('hr.job', "site_key", self.site_key, for_all_users=True)
        if self.secret_key:
            ir_values_obj.sudo().set_default('hr.applicant', "secret_key", self.secret_key, for_all_users=True)
            ir_values_obj.sudo().set_default('hr.job', "secret_key", self.secret_key, for_all_users=True)
        if self.refuse_template:
            ir_values_obj.sudo().set_default('hr.applicant', "refuse_template", self.refuse_template.id, for_all_users=True)
#         if self.default_purchase_tax_id:
#             ir_values_obj.sudo().set_default('product.template', "supplier_taxes_id", [self.default_purchase_tax_id.id], for_all_users=True, company_id=self.company_id.id)


class MailComposer(models.TransientModel):

    _inherit = 'mail.compose.message'

    @api.multi
    def send_mail(self, auto_commit=False):
        """ Process the wizard content and proceed with sending the related
            email(s), rendering any template patterns on the fly if needed. """
        for wizard in self:
            # Duplicate attachments linked to the email.template.
            # Indeed, basic mail.compose.message wizard duplicates attachments in mass
            # mailing mode. But in 'single post' mode, attachments of an email template
            # also have to be duplicated to avoid changing their ownership.
            if wizard.attachment_ids and wizard.composition_mode != 'mass_mail' and wizard.template_id:
                new_attachment_ids = []
                for attachment in wizard.attachment_ids:
                    if attachment in wizard.template_id.attachment_ids:
                        new_attachment_ids.append(attachment.copy({'res_model': 'mail.compose.message', 'res_id': wizard.id}).id)
                    else:
                        new_attachment_ids.append(attachment.id)
                    wizard.write({'attachment_ids': [(6, 0, new_attachment_ids)]})

            # Mass Mailing
            mass_mode = wizard.composition_mode in ('mass_mail', 'mass_post')

            Mail = self.env['mail.mail']
            ActiveModel = self.env[wizard.model if wizard.model else 'mail.thread']
            if wizard.template_id:
                # template user_signature is added when generating body_html
                # mass mailing: use template auto_delete value -> note, for emails mass mailing only
                Mail = Mail.with_context(mail_notify_user_signature=False)
                ActiveModel = ActiveModel.with_context(mail_notify_user_signature=False, mail_auto_delete=wizard.template_id.auto_delete)
            if not hasattr(ActiveModel, 'message_post'):
                ActiveModel = self.env['mail.thread'].with_context(thread_model=wizard.model)
            if wizard.composition_mode == 'mass_post':
                # do not send emails directly but use the queue instead
                # add context key to avoid subscribing the author
                ActiveModel = ActiveModel.with_context(mail_notify_force_send=False, mail_create_nosubscribe=True)
            # wizard works in batch mode: [res_id] or active_ids or active_domain
            if mass_mode and wizard.use_active_domain and wizard.model:
                res_ids = self.env[wizard.model].search(safe_eval(wizard.active_domain)).ids
            elif mass_mode and wizard.model and self._context.get('active_ids'):
                res_ids = self._context['active_ids']
            else:
                res_ids = [wizard.res_id]
            print res_ids
            batch_size = int(self.env['ir.config_parameter'].sudo().get_param('mail.batch_size')) or self._batch_size
            sliced_res_ids = [res_ids[i:i + batch_size] for i in range(0, len(res_ids), batch_size)]

            if wizard.composition_mode == 'mass_mail' or wizard.is_log or (wizard.composition_mode == 'mass_post' and not wizard.notify):  # log a note: subtype is False
                subtype_id = False
            elif wizard.subtype_id:
                subtype_id = wizard.subtype_id.id
            else:
                subtype_id = self.sudo().env.ref('mail.mt_comment', raise_if_not_found=False).id

            for res_ids in sliced_res_ids:
                batch_mails = Mail
                all_mail_values = wizard.get_mail_values(res_ids)
                for res_id, mail_values in all_mail_values.iteritems():
                    if wizard.composition_mode == 'mass_mail':
                        batch_mails |= Mail.create(mail_values)
                    else:
                        mail_id=ActiveModel.browse(res_id).message_post(
                            message_type=wizard.message_type,
                            subtype_id=subtype_id,
                            **mail_values)
                        if self.env.context['active_model']=='hr.applicant':
#                             print mail_id,'=='
#                             print self.env.context['active_ids']
                            applicants=self.env['hr.applicant'].search([('id','in',self.env.context['active_ids'])])
                            for applicant in applicants:
#                                 print applicant
                                applicant.mail_id=mail_id.id
                            
                if wizard.composition_mode == 'mass_mail':
                    batch_mails.send(auto_commit=auto_commit)
        return {'type': 'ir.actions.act_window_close'}


class RecruitmentStage(models.Model):
    _inherit = "hr.recruitment.stage"
    
    score = fields.Boolean("Score", default=True)
    preview_offer = fields.Boolean("Preview Offer", default=True)
    meetings = fields.Boolean("Meetings", default=True)
    start_interview = fields.Boolean("Start Interview", default=True)
    print_interview = fields.Boolean("Print Interview", default=True)
    documents = fields.Boolean("Documents", default=True)
    send_offer_letter = fields.Boolean("Send Offer Letter", default=True)
    is_archive = fields.Boolean("Archive Applicants on Done")

# class Survey(models.Model):
#     _inherit = "survey.survey"
#
#     interviewer = fields.Boolean('Interviewer')
#     applicant = fields.Boolean('Applicant')



class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    response_id_name = fields.Many2one('res.users',"Responsible Name",compute = "_compute_responsible",store=True)
    applied_job_name = fields.Many2one('hr.job',"Applied Job",compute = "_compute_applied_job",store=True)
    company_id_name = fields.Many2one('res.company',"Company",compute = "_compute_company", store=True)
    applicant_name = fields.Many2one('hr.applicant',"Applicant Name",compute="_compute_applicant_name",store=True)

    @api.multi
    @api.depends("res_id")
    def _compute_responsible(self):
        for rec in self:
            applicant_obj = self.env['hr.applicant'].search([('id' , '=' , rec.res_id)])
            if applicant_obj:
                rec.response_id_name = applicant_obj.user_id.id

    @api.multi
    @api.depends("res_id")
    def _compute_applied_job(self):
        for rec in self:
            applicant_obj = self.env['hr.applicant'].search([('id' , '=' , rec.res_id)])
            if applicant_obj:
                rec.applied_job_name = applicant_obj.job_id.id

    @api.multi
    @api.depends("res_id")
    def _compute_company(self):
        for rec in self:
            applicant_obj = self.env['hr.applicant'].search([('id' , '=' , rec.res_id)])
            if applicant_obj:
                rec.company_id_name= applicant_obj.company_id.id

    @api.multi
    @api.depends("res_id")
    def _compute_applicant_name(self):
        for rec in self:
            applicant_obj = self.env['hr.applicant'].search([('id' , '=' , rec.res_id)])
            if applicant_obj:
                rec.applicant_name = applicant_obj.id


    @api.multi
    def view_file(self):
        context = dict(self._context or {})
        context.update({'default_attachment':self.datas})
        view_id = self.env.ref('vitalpet_custom_hr_recruitment.view_pdf_files_recruitment_form').id
        return {
            'name': _('Attachment'),           
            'view_type': 'form',
            'type': 'ir.actions.act_window',
            "views": [[view_id, "form"]],
            'target': 'new',
            'res_model': 'view.file.recruitment',
            'context':context,                
        }

    @api.multi
    def view_applicant(self):

        form_id = self.env.ref('hr_recruitment.crm_case_form_view_job').id
    
        applicant_id_obj = self.env["hr.applicant"].search([('id', '=', self.res_id)])

        return{
            'name': _('View Applicant'),
            'type':'ir.actions.act_window',
            'view_type':'form',
            'view_mode':'form',
            'res_model':'hr.applicant',
            'res_id':applicant_id_obj.id,
            'views_id':False,
            'views':[(form_id or False, 'form')],
            }


class ImageUpdateRecruitment(models.TransientModel):
    _name = 'view.file.recruitment'
    
    attachment = fields.Binary('Attachment', attachment=True)
    

class RecruitmentWizard(models.TransientModel):
    _name = 'hr.job.wizard'

    @api.multi
    def set_open_function(self):
        return self.env['hr.job'].browse(self._context.get('active_ids')).set_open()
    
    
    
    
class OverwriteCity(models.Model):
    _name = "over_write.city"  
    
    job_temp_id = fields.Many2one("hr.job")   
    city_wizard= fields.Char("City")
    state_wizard_id = fields.Many2one("res.country.state",string='State')

