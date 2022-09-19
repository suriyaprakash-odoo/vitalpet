from odoo import api, fields, models, tools, _
import odoo
from datetime import datetime,date, timedelta
from odoo.exceptions import ValidationError,UserError


# // class to inherit HrOnboarding
class HrEmployeeDocument(models.Model):
    _name = "hr.employee.document"   
    _inherit = ['hr.employee.document','mail.thread'] 

    name = fields.Char(string='Document Number', required=True, copy=False,track_visibility='onchange')
    document_name = fields.Many2one('employee.checklist', string='Document', required=True,track_visibility='onchange')
    description = fields.Text(string='Description', copy=False,track_visibility='onchange')
    expiry_date = fields.Date(string='Expiry Date', copy=False,track_visibility='onchange')
    doc_attachment_id = fields.Many2many('ir.attachment', 'doc_attach_rel', 'doc_id', 'attach_id3', string="Attachment",
                                         help='You can attach the copy of your document', copy=False,track_visibility='onchange')
    issue_date = fields.Date(string='Issue Date', default=fields.datetime.now(), copy=False,track_visibility='onchange')

    document_temp = fields.Many2one("signature.request",string="Document Template")
    is_active = fields.Boolean(string="Active", default=True,track_visibility='onchange')
    emp_name = fields.Many2one(related='employee_ref',string="Employee Name",store=True)
    seniority_id = fields.Many2one(related='employee_ref.job_seniority_title',string="Job Title",store=True)
    position_id = fields.Many2one(related='employee_ref.job_id',string="job",store=True)
    type_id = fields.Selection([('entry', 'Entry Process'),
                                      ('exit', 'Exit Process'),
                                      ('other', 'Other'),
                                      ('license', 'License'),
                                      ('skill','Skills'),
                                      ('disciplinary','Disciplinary')], string='Document Type', related='document_name.document_type',store=True)
    encrypt_id = fields.Boolean(related='document_temp.template_id.encrypt', string ="Encrypt",track_visibility='onchange')
    state = fields.Selection([("open", "Open"),
        ("record", "Record"),
        ("norecord", "No Record"),
        ("completed", "Completed")
    ],string='Status',related='document_temp.state')


    def open_document(self):

        if self.document_temp:
            self.document_temp.ensure_one()
            request_item = self.document_temp.request_item_ids.filtered(lambda r: r.partner_id and r.partner_id.id == self.document_temp.env.user.partner_id.id)
            return {
                'name': "Document \"%(name)s\"" % {'name': self.document_temp.reference},
                'type': 'ir.actions.client',
                'tag': 'website_sign.Document',
                'context': {
                    'id': self.document_temp.id,
                    'token': self.document_temp.access_token,
                    'sign_token': request_item.access_token if request_item and request_item.state == "sent" else None,
                    'create_uid': self.document_temp.create_uid.id,
                    'state': self.document_temp.state,
                },
            }
        else:
            # return {
            #       'target': 'self',
            #       'url': '#',
            #       'type': 'ir.actions.act_url',
            #     }
            raise ValidationError("No Document exists, to add an attachment please click on Upload Attachment")
    
    @api.constrains('expiry_date')
    def check_expr_date(self):
        for each in self:
            if each.expiry_date:
                exp_date = fields.Date.from_string(each.expiry_date)
                # if exp_date < date.today():
                #     raise Warning('Your Document Is Expired.')

    def documents_date_expiration_cron(self):
        document_id = self.env['hr.employee.document'].search([])
        
        if document_id: 
            for rec in document_id:
                onboarding_emp_id = self.env['hr.employee.onboarding'].search([('employee_id','=',rec.employee_ref.id)])
                if rec.is_active != False and rec.expiry_date != False:
                    date_t=datetime.strptime(str(rec.expiry_date), '%Y-%m-%d').date()
                    diff_days=(date_t-datetime.now().date()).days
                    if diff_days<=0:
                        rec.is_active=False
                    elif diff_days in [30,25,5]:
                        template_id = self.env.ref('vitalpet_employee_documents.document_expiration_mail_template')
                        if rec:
                            if template_id:
                                if onboarding_emp_id.state_id != 'complete':
                                    template_id.with_context(diff_days = diff_days).send_mail(rec.id, force_send=True)
    @api.multi
    def employee_documents_exist(self):
        doc_obj = self.env['signature.request'].search([])

        for rec in doc_obj:
            for record in rec.request_item_ids:
                if record.role_id.name == 'Employee':
                    if record.partner_id:
                        employee_obj = self.env['hr.employee'].search([('address_home_id','=',record.partner_id.id)])
                        if employee_obj:
                            if len(self.env['hr.employee.document'].search([('document_temp','=',rec.id)]))==0:
                                checklist_obj= self.env['employee.checklist'].create({
                                    'name' : rec.reference,
                                    'document_type' : 'license'
                                    })
                                
                                doc_obj = self.env['hr.employee.document'].create({

                                         'expiry_date': False,
                                         'issue_date':rec.create_date or False,
                                         'document_name':checklist_obj.id or False,
                                         'employee_ref':employee_obj.id or False,
                                         'name' : rec.reference or False,
                                         'document_temp' : rec.id or False,
                            })
                if record.role_id.name == 'Onboarding':
                    if record.partner_id:
                        onboarding_obj = self.env['hr.employee.onboarding'].search([('partner_id','=',record.partner_id.id)])
                        if onboarding_obj.new_employee_id:
                            for onboard in onboarding_obj:
                                consent_obj = self.env['consent.form'].search([('consent_form_id','=',onboard.id)])
                                for rec_line in consent_obj:
                                    print rec_line.request_id,'----'
                                    print self.env['hr.employee.document'].search([('document_temp','=',rec_line.request_id.id)]),'----'
                                    if len(self.env['hr.employee.document'].search([('document_temp','=',rec_line.request_id.id)]))==0:
                                        
                                        if rec_line.status_id != 'draft' and rec_line.status_id != False:
                                            check_obj = self.env['employee.checklist'].search([('name','=',rec_line.consent_form.attachment_id.name),
                                                                                              ('document_type','=','entry')],limit=1)
                                            if check_obj:
                                                checklist_obj=check_obj
                                            else:
                                                checklist_obj= self.env['employee.checklist'].create({
                                                    'name' : rec_line.consent_form.attachment_id.name,
                                                    'document_type' : 'entry'
                                                    })
                                            if self.env['employee.checklist'].search([('name','!=',rec_line.consent_form.attachment_id.name)]):
                                                self.env['hr.employee.document'].create({

                                                         'expiry_date': rec_line.expiration or False,
                                                         'issue_date':rec_line.date_sent or False,
                                                         'document_name':checklist_obj.id or False,
                                                         'employee_ref':rec_line.consent_form_id.new_employee_id.id or False,
                                                         'name' : rec_line.consent_form.attachment_id.name or False,
                                                         'document_temp' : rec_line.request_id.id or False,
                                                })

                                adverse_act = self.env['adverse.action'].search([('action_form_id','=',onboard.id)])
                                for rec_line in adverse_act:
                                    if len(self.env['hr.employee.document'].search([('document_temp','=',rec_line.request_id.id)]))==0:
                                          
                                        if rec_line.status_id != 'draft' and rec_line.status_id != False:
                                            check_obj = self.env['employee.checklist'].search([('name','=',rec_line.action_form.attachment_id.name),
                                                                                              ('document_type','=','entry')],limit=1)
                                            if check_obj:
                                                checklist_obj=check_obj
                                            else:
                                                checklist_obj= self.env['employee.checklist'].create({
                                                    'name' : rec_line.action_form.attachment_id.name,
                                                    'document_type' : 'entry'
                                                    })
                                            if self.env['employee.checklist'].search([('name','!=',rec_line.action_form.attachment_id.name)]):
                                                self.env['hr.employee.document'].create({
                                                     
                                                         'expiry_date':rec_line.expiration or False,
                                                         'issue_date':rec_line.date_sent or False,
                                                         'document_name':checklist_obj.id or False,
                                                         'employee_ref':rec_line.action_form_id.new_employee_id.id or False,
                                                         'name' : rec_line.action_form.attachment_id.name or False,
                                                         'document_temp' : rec_line.request_id.id or False,
                                                })  

                                applicant_back = self.env['applicant.background'].search([('applicant_background_id','=',onboard.id)])
                                for rec_line in applicant_back:
                                    if len(self.env['hr.employee.document'].search([('document_temp','=',rec_line.request_id.id)]))==0:
                                          
                                        if rec_line.status_id != 'draft' and rec_line.status_id != False:
                                            check_obj = self.env['employee.checklist'].search([('name','=',rec_line.document.attachment_id.name),
                                                                                              ('document_type','=','entry')],limit=1)
                                            if check_obj:
                                                checklist_obj=check_obj
                                            else:
                                                checklist_obj= self.env['employee.checklist'].create({
                                                    'name' : rec_line.document.attachment_id.name,
                                                    'document_type' : 'entry'
                                                    })
                                            if self.env['employee.checklist'].search([('name','!=',rec_line.document.attachment_id.name)]):
                                                self.env['hr.employee.document'].create({
                                                     
                                                         'expiry_date':rec_line.expiration or False,
                                                         'issue_date':rec_line.date_sent or False,
                                                         'document_name':checklist_obj.id or False,
                                                         'employee_ref':rec_line.applicant_background_id.new_employee_id.id or False,
                                                         'name' : rec_line.document.attachment_id.name or False,
                                                         'document_temp' : rec_line.request_id.id or False,
                                                })  

                                employer_back = self.env['employer.background'].search([('employer_background_id','=',onboard.id)])
                                for rec_line in employer_back:
                                    if len(self.env['hr.employee.document'].search([('document_temp','=',rec_line.request_id.id)]))==0:
                                          
                                        if rec_line.status_id != 'draft' and rec_line.status_id != False:
                                            check_obj = self.env['employee.checklist'].search([('name','=',rec_line.document.attachment_id.name),
                                                                                              ('document_type','=','entry')],limit=1)
                                            if check_obj:
                                                checklist_obj=check_obj
                                            else:
                                                checklist_obj= self.env['employee.checklist'].create({
                                                    'name' : rec_line.document.attachment_id.name,
                                                    'document_type' : 'entry'
                                                    })
                                            if self.env['employee.checklist'].search([('name','!=',rec_line.document.attachment_id.name)]):
                                                self.env['hr.employee.document'].create({
                                                     
                                                        'expiry_date':rec_line.expiration or False,
                                                        'issue_date':rec_line.date_sent or False,
                                                        'document_name':checklist_obj.id or False,
                                                        'employee_ref':rec_line.employer_background_id.new_employee_id.id or False,
                                                        'name' : rec_line.document.attachment_id.name or False,
                                                        'document_temp' : rec_line.request_id.id or False,
                                                }) 

                                welcome_email = self.env['welcome.mail'].search([('welcome_mail_id','=',onboard.id)])
                                for rec_line in welcome_email:
                                    if len(self.env['hr.employee.document'].search([('document_temp','=',rec_line.request_id.id)]))==0:
                                        print '!!!!',rec_line.status_id,'!!!!'
                                        if rec_line.status_id != 'draft' and rec_line.status_id != False :
                                            check_obj = self.env['employee.checklist'].search([('name','=',rec_line.document.attachment_id.name),
                                                                                              ('document_type','=','entry')],limit=1)
                                            if check_obj:
                                                checklist_obj=check_obj
                                            else:
                                                checklist_obj= self.env['employee.checklist'].create({
                                                    'name' : rec_line.document.attachment_id.name,
                                                    'document_type' : 'entry'
                                                    })
                                            if self.env['employee.checklist'].search([('name','!=',rec_line.document.attachment_id.name)]):
                                                self.env['hr.employee.document'].create({
                                                    
                                                        'expiry_date':rec_line.expiration or False,
                                                        'issue_date':rec_line.date_sent or False,
                                                        'document_name':checklist_obj.id or False,
                                                        'employee_ref':rec_line.welcome_mail_id.new_employee_id.id or False,
                                                        'name' : rec_line.document.attachment_id.name or False,
                                                        'document_temp' : rec_line.request_id.id or False,
                                                })     
               
               
class EmployeeEntryDocuments(models.Model):
    _inherit = 'employee.checklist'
                   
    document_type = fields.Selection(selection_add=[('license', 'License'),
                                    ('skill','Skills'),
                                    ('disciplinary','Disciplinary')])
      
    @api.multi
    def name_get(self):
        result = []
        for each in self:
            if each.document_type == 'entry':
                name = each.name + '_en'
            elif each.document_type == 'exit':
                name = each.name + '_ex'
            elif each.document_type == 'other':
                name = each.name + '_ot'
            elif each.document_type == 'license':
                name = each.name + '_li'
            elif each.document_type == 'skill':
                name = each.name + '_sk'
            elif each.document_type == 'disciplinary':
                name = each.name + '_di'
            result.append((each.id, name))
        return result
    
    
    
# class HrEmployee(models.Model):
#     _inherit = 'hr.employee'
#     
#     @api.multi  
#     def document_view(self):
#         user_id = self.env['res.users'].search([('id', '=', self._uid)])
#         print user_id
#         if user_id.has_group('vitalpet_employee_documents.group_employee_documents_employee'):
#             raise ValidationError("You don't have access rights to view this Documents")
#         else:
#             self.ensure_one()
#             domain = [
#                 ('employee_ref', '=', self.id)]
#             return {
#                 'name': _('Documents'),
#                 'domain': domain,
#                 'res_model': 'hr.employee.document',
#                 'type': 'ir.actions.act_window',
#                 'view_id': False,
#                 'view_mode': 'tree,form',
#                 'view_type': 'form',
#                 'help': _('''<p class="oe_view_nocontent_create">
#                                Click to Create for New Documents
#                             </p>'''),
#                 'limit': 80,
#                 'context': "{'default_employee_ref': '%s'}" % self.id
#             }
#     


        