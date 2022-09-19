from odoo import api, fields, models, tools, _
import odoo
from passlib.tests.utils import limit
from odoo.exceptions import ValidationError,UserError


# // class to inherit HrOnboarding
class HrOnboarding(models.Model):
    _inherit = "hr.employee.onboarding"    
     
    @api.multi
    def write(self,vals):
        res = super(HrOnboarding, self).write(vals)
        if self.new_employee_id:
            consent_obj = self.env['consent.form'].search([('consent_form_id','=',self.id)])
            for rec in consent_obj:
                if len(self.env['hr.employee.document'].search([('document_temp','=',rec.request_id.id)]))==0:
                    
                    if rec.status_id != 'draft' and rec.status_id != False:
                        check_obj = self.env['employee.checklist'].search([('name','=',rec.consent_form.attachment_id.name),
                                                                          ('document_type','=','entry')],limit=1)
                        if check_obj:
                            checklist_obj=check_obj
                        else:
                            checklist_obj= self.env['employee.checklist'].create({
                                'name' : rec.consent_form.attachment_id.name,
                                'document_type' : 'entry'
                                })
                        if self.env['employee.checklist'].search([('name','!=',rec.consent_form.attachment_id.name)]):
                            record_obj = self.env['hr.employee.document'].create({

#                                      'expiry_date': rec.expiration or False,
                                     'issue_date':rec.date_sent or False,
                                     'document_name':checklist_obj.id or False,
                                     'employee_ref':self.new_employee_id.id or False,
                                     'name' : rec.consent_form.attachment_id.name or False,
                                     'document_temp' : rec.request_id.id or False,
                            })
                            record_obj.write({
                                'expiry_date':rec.expiration or False
                                }) 
                        
        if self.new_employee_id:
            adverse_act = self.env['adverse.action'].search([('action_form_id','=',self.id)])
            for rec in adverse_act:
                if len(self.env['hr.employee.document'].search([('document_temp','=',rec.request_id.id)]))==0:
                      
                    if rec.status_id != 'draft' and rec.status_id != False:
                        check_obj = self.env['employee.checklist'].search([('name','=',rec.action_form.attachment_id.name),
                                                                          ('document_type','=','entry')],limit=1)
                        if check_obj:
                            checklist_obj=check_obj
                        else:
                            checklist_obj= self.env['employee.checklist'].create({
                                'name' : rec.action_form.attachment_id.name,
                                'document_type' : 'entry'
                                })
                        if self.env['employee.checklist'].search([('name','!=',rec.action_form.attachment_id.name)]):
                            record_obj1 = self.env['hr.employee.document'].create({
                                 
#                                      'expiry_date':rec.expiration or False,
                                     'issue_date':rec.date_sent or False,
                                     'document_name':checklist_obj.id or False,
                                     'employee_ref':self.new_employee_id.id or False,
                                     'name' : rec.action_form.attachment_id.name or False,
                                     'document_temp' : rec.request_id.id or False,
                            }) 
                            record_obj1.write({
                                'expiry_date':rec.expiration or False
                                })               
#                       
        if self.new_employee_id:
            applicant_back = self.env['applicant.background'].search([('applicant_background_id','=',self.id)])
            for rec in applicant_back:
                if len(self.env['hr.employee.document'].search([('document_temp','=',rec.request_id.id)]))==0:
                      
                    if rec.status_id != 'draft' and rec.status_id != False:
                        check_obj = self.env['employee.checklist'].search([('name','=',rec.document.attachment_id.name),
                                                                          ('document_type','=','entry')],limit=1)
                        if check_obj:
                            checklist_obj=check_obj
                        else:
                            checklist_obj= self.env['employee.checklist'].create({
                                'name' : rec.document.attachment_id.name,
                                'document_type' : 'entry'
                                })
                        if self.env['employee.checklist'].search([('name','!=',rec.document.attachment_id.name)]):
                            record_obj2 = self.env['hr.employee.document'].create({
                                 
#                                      'expiry_date':rec.expiration or False,
                                     'issue_date':rec.date_sent or False,
                                     'document_name':checklist_obj.id or False,
                                     'employee_ref':self.new_employee_id.id or False,
                                     'name' : rec.document.attachment_id.name or False,
                                     'document_temp' : rec.request_id.id or False,
                            }) 
                            record_obj2.write({
                                'expiry_date':rec.expiration or False
                                })      
                         
        if self.new_employee_id:
            employer_back = self.env['employer.background'].search([('employer_background_id','=',self.id)])
            for rec in employer_back:
                if len(self.env['hr.employee.document'].search([('document_temp','=',rec.request_id.id)]))==0:
                      
                    if rec.status_id != 'draft' and rec.status_id != False:
                        check_obj = self.env['employee.checklist'].search([('name','=',rec.document.attachment_id.name),
                                                                          ('document_type','=','entry')],limit=1)
                        if check_obj:
                            checklist_obj=check_obj
                        else:
                            checklist_obj= self.env['employee.checklist'].create({
                                'name' : rec.document.attachment_id.name,
                                'document_type' : 'entry'
                                })
                        if self.env['employee.checklist'].search([('name','!=',rec.document.attachment_id.name)]):
                            record_obj3 = self.env['hr.employee.document'].create({
                                 
#                                     'expiry_date':rec.expiration or False,
                                    'issue_date':rec.date_sent or False,
                                    'document_name':checklist_obj.id or False,
                                    'employee_ref':self.new_employee_id.id or False,
                                    'name' : rec.document.attachment_id.name or False,
                                    'document_temp' : rec.request_id.id or False,
                            })
                            record_obj3.write({
                                'expiry_date':rec.expiration or False
                                })              
                         
        if self.new_employee_id :
            welcome_email = self.env['welcome.mail'].search([('welcome_mail_id','=',self.id)])
            for rec in welcome_email:
                if len(self.env['hr.employee.document'].search([('document_temp','=',rec.request_id.id)]))==0:
                    if rec.status_id != 'draft' and rec.status_id != False :
                        check_obj = self.env['employee.checklist'].search([('name','=',rec.document.attachment_id.name),
                                                                          ('document_type','=','entry')],limit=1)
                        if check_obj:
                            checklist_obj=check_obj
                        else:
                            checklist_obj= self.env['employee.checklist'].create({
                                'name' : rec.document.attachment_id.name,
                                'document_type' : 'entry'
                                })
                        if self.env['employee.checklist'].search([('name','!=',rec.document.attachment_id.name)]):
                            record_obj4 = self.env['hr.employee.document'].create({
                                
#                                     'expiry_date':rec.expiration or False,
                                    'issue_date':rec.date_sent or False,
                                    'document_name':checklist_obj.id or False,
                                    'employee_ref':self.new_employee_id.id or False,
                                    'name' : rec.document.attachment_id.name or False,
                                    'document_temp' : rec.request_id.id or False,
                            })
                            record_obj4.write({
                                'expiry_date':rec.expiration or False
                                })                                                                     
        return res
        
        