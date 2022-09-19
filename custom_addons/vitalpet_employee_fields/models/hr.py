# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo import SUPERUSER_ID
from datetime import datetime
from dateutil.relativedelta import relativedelta
from datetime import date
import base64
from odoo.exceptions import ValidationError, UserError


class Employee(models.Model):

    _inherit = "hr.employee"
    
    start_date = fields.Date(string="Start Date")
    termination_date = fields.Date(string="Termination Date")
    benefit_seniority_date = fields.Date(string="Benefits Seniority Date")
    termination_type = fields.Many2one('termination.type', string='Termination Type', readonly=1)
    termination_reason = fields.Many2one('termination.reason', string='Termination Reason', readonly=1)
    rehire_eligible = fields.Boolean(string='Eligible for Rehire?', readonly=1)
    cobra_eligible = fields.Boolean(string='Cobra eligible?', readonly=1)
    admin_user_id = fields.Boolean(string="Super User", compute="_get_super_user_id")
    employment_status = fields.Many2one("hr.contract.type", string="Contract Type")
    job_seniority_title = fields.Many2one('hr.job.seniority.title',string="Job Seniority Title")    
    benefit_status = fields.Selection([
        ('not_eligible', 'Not Eligible'),
        ('immediate_enroll', 'Immediate Enroll'),
        ('pending_elections', 'Pending Elections'),
        ('to_approve', 'To Approve'), ('send_to_provider', 'Send to Provider'), ('enrolled', 'Enrolled')
    ], string='Benefits Status')
    pay_type = fields.Selection([
        ('yearly', 'Annual Wage'),
        ('monthly', 'Monthly Wage'),
        ('hourly', 'Hourly Wage'),
    ], string='Pay Type')
    overtime_pay = fields.Selection([
        ('exempt', 'Exempt'),
        ('non_exempt', 'NonExempt'),
    ], string='Exempt from Overtime Pay')
    
    location_id = fields.Char(string="Location ID") 
    ethnic_id = fields.Char(string="Ethnic ID") 
    smoker = fields.Char(string="Smoker") 
    birth_country = fields.Many2one('res.country', string="Birth Country") 
    age = fields.Char(string="Age") 
    verify = fields.Boolean(string='Verified')
    work_authorization = fields.Char(string="Work Authorization") 
    document_no = fields.Char(string="Document Number") 
    expiration_date = fields.Date(string="I-9 Expiration Date") 
    document_A = fields.Char(string="Document A") 
    document_B = fields.Char(string="Document B") 
    document_C = fields.Char(string="Document C") 
    visa_type = fields.Char(string="Visa Type") 
    visa_exp = fields.Date(string="Visa Expiration") 
    country = fields.Many2one('res.country.state', string="Country") 
    ref_id = fields.Char(string="Reference ID")
    application_date = fields.Date(string="Application Date") 
    approval_date = fields.Date(string="Approval Date") 
    exp_date = fields.Date(string="Expiration Date") 
    veteran = fields.Char(string="Veteran")
    veteran_of = fields.Char(string="Veteran Of")
    branch = fields.Char(string="Branch")
    separation_date = fields.Date(string="Separation Date")
    service_medal = fields.Char(string="Armed Forces Services Medal")
    disabled_veteran = fields.Char(string="Special Disable Veteran")
    actv_wartime = fields.Char(string="Actv Wartime or cmpgn Badge VET ")
    disabled = fields.Char(string="Disable")
    disablity_type = fields.Char(string="Disablity Type")
    scheduled_hours = fields.Integer(string="Scheduled Hours")
    enrollment_deadline = fields.Date(string="Enrollment Deadline")
    employee_id = fields.Char(string="Employee ID")
    time_clock = fields.Integer(string="Timeclock")
    hr_status = fields.Char(string="HR Status")
    direct_deposit = fields.Char(string="Direct Deposit Status")
    date_added = fields.Datetime(string="Date Added")
    date_modified = fields.Datetime(string="Date Modified")
    encrypt_value = fields.Boolean(string="Encrypted",default=False)
    sequence = fields.Integer('Sequence')
    emergency_contact_name = fields.Char("Name")
    emergency_contact_phone = fields.Char("Phone")
    emergency_contact_relationship = fields.Char("Relationship")
    hire_date = fields.Date(string="Hire Date")
    first_name_alias = fields.Char("First Name")
    middle_name_alias = fields.Char("Middle Name")
    last_name_alias = fields.Char("Last Name")
    dl_number = fields.Char("Driving License Number")
    filing_staus = fields.Selection([('single', 'Single'), 
                                    ('married', 'Married'),
                                    ('widower', 'Married, but withhold at higher Single rate'),], string="Filing Status")
    
    identification_id_decrypt = fields.Char(string="Identification No Decrypt", compute="identification_decrypt", groups="hr.group_hr_manager")    
    passport_id_decrpt = fields.Char(string="Passport No Decrypt", compute="identification_decrypt", groups="hr.group_hr_manager")
    
#     create_boolean = fields.Boolean()

    @api.onchange('job_id')
    def on_change_job_id(self):
        res = {'domain': {
            'job_seniority_id': "[('id', '=', False)]",
        }}
        if self.job_id and self.job_id.job_seniority_id:
            job_seniority_id = self.job_id.job_template.job_seniority_id.ids
            res['domain']['job_seniority_title'] = "[('id', 'in', %s)]" % job_seniority_id

        return res



    @api.onchange('birthday')
    def set_age(self):
        if self.birthday:
            for rec in self:
                if rec.birthday:
                    dt = rec.birthday
                    d1 = datetime.strptime(dt, "%Y-%m-%d").date()
                    d2 = date.today()
                    rd = relativedelta(d2, d1)
                rec.age = str(rd.years) 

    def _get_super_user_id(self):
        for i in self:
            i.admin_user_id = False
            if i.env.uid == SUPERUSER_ID:
                i.admin_user_id = True
    
    @api.multi
    def terminate_team_members(self):
        button_name = _('Terminate Team Members')
        return ({
             'name': button_name,
             'type': 'ir.actions.act_window',
             'res_model': 'terminate.member',
             'view_type': 'form',
             'context': "{}",
             'view_mode':'form',
             'target': 'new',
             'auto_refresh':1
        })

    # def generate_demographics_file(self):

    #     return ({
    #         'name': _('Generate Demographics File'),
    #         'type':'ir.actions.act_window',
    #         'view_type':'form',
    #         'view_mode':'form',
    #         'res_model':'demographics.file.wizard',
    #         'views_id':False,
    #         'views':[(self.env.ref('vitalpet_employee_fields.demographics_file_wizard_form').id or False, 'form')],
    #         'target':'new',
    #         # 'context':ctx,
    #         })
         
            
    @api.multi
    def write(self, vals):
        hr_contracts = self.env['hr.contract'].search([('employee_id', '=', self.id)])
        for hr_contract in hr_contracts:
            if 'job_id' in vals:
                if hr_contract:
                    if hr_contract.job_id.id!=vals['job_id']:
                        raise UserError('Please Update The Contract For This Job.')
                     
            if 'employment_status' in vals:
                if hr_contract:
                    if hr_contract.type_id.id!=vals['employment_status']:
                        raise UserError('Please Update The Contract For This Contract Type.')
                           
            if 'start_date' in vals:
                if hr_contract:
                    if hr_contract.date_start!=vals['start_date']:
                        raise UserError('Please Update The Contract For This Start Date.')
            if 'pay_type' in vals:
                if hr_contract:
                    if hr_contract.salary_computation_method!=vals['pay_type']:
                        raise UserError('Please Update The Contract For This Pay Type.')
     
            if self.encrypt_value == True:
                if vals.get('identification_id'):
                    vals['identification_id'] =  base64.b64encode(vals.get('identification_id'))
                if vals.get('passport_id'):
                    vals['passport_id'] =  base64.b64encode(vals.get('passport_id'))
                 
            if vals.get('birthday'):
                dt = vals.get('birthday')
                d1 = datetime.strptime(dt, "%Y-%m-%d").date()
                d2 = date.today()
                rd = relativedelta(d2, d1)
                vals.update({'age': str(rd.years)})
            elif self.birthday:
                dt = self.birthday
                d1 = datetime.strptime(dt, "%Y-%m-%d").date()
                d2 = date.today()
                rd = relativedelta(d2, d1)
                vals.update({'age': str(rd.years)}) 
                
            if vals.get('termination_date'):
                termination_date = vals.get('termination_date')
                if termination_date:
                    date_today = date.today().strftime('%Y-%m-%d')
                    if termination_date < date_today:
                        self.toggle_active()
        if vals.get('job_seniority_title'):
            sequence = self.env['hr.job.seniority.title'].search([('id','=',vals.get('job_seniority_title'))])
            vals.update({'sequence': sequence.sequence})    
        return super(Employee, self).write(vals)
     
    @api.model
    def create(self, vals):

        if vals.get('identification_id'):
            vals['identification_id'] =  base64.b64encode(vals.get('identification_id'))
        if vals.get('passport_id'):
            vals['passport_id'] =  base64.b64encode(vals.get('passport_id'))
            
        vals['encrypt_value'] = True
        if vals.get('birthday'):
            dt = vals.get('birthday')
            d1 = datetime.strptime(dt, "%Y-%m-%d").date()
            d2 = date.today()
            rd = relativedelta(d2, d1)
            vals.update({'age': str(rd.years)}) 
            
            
#         vals['create_boolean'] = True
        return super(Employee, self).create(vals)

        
    
    
    @api.multi
    def encrpyt_decrypt_values(self):
        for rec in self:
            if rec.encrypt_value:
                rec.encrypt_value = False
                if rec.identification_id:
                    rec.identification_id = base64.b64decode(rec.identification_id)
                if rec.passport_id:
                    rec.passport_id = base64.b64decode(rec.passport_id)
            else:
                rec.encrypt_value = True
                if rec.identification_id:
                    rec.identification_id = rec.identification_id
                if rec.passport_id:
                    rec.passport_id = rec.passport_id
        return True
    
    
    @api.multi
    def identification_decrypt(self):
        for rec in self:
            if rec.encrypt_value:
                if rec.identification_id:
                    try:
                        rec.identification_id_decrypt = base64.b64decode(rec.identification_id)
                    except:
                        rec.identification_id_decrypt=rec.identification_id
                if rec.passport_id:                    
                    try:
                        rec.passport_id_decrypt = base64.b64decode(rec.passport_id)
                    except:
                        rec.passport_id_decrypt=rec.passport_id
            else:
                if rec.identification_id:
                    rec.identification_id_decrypt = rec.identification_id
                if rec.passport_id:
                    rec.passport_id_decrypt = rec.passport_id
        return True
    
    
class TerminationType(models.Model):

    _name = "termination.type"
    _description = "Termination Type"

    name = fields.Char(string="Termination Type", required=True)
    
    
class TerminationReason(models.Model):

    _name = "termination.reason"
    _description = "Termination Reason"

    name = fields.Char(string="Termination Reason", required=True)
    termination_type = fields.Many2one('termination.type',string="Termination Type")
    
class HrContract(models.Model):

    _inherit = "hr.contract"
    
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user.id)
    change_date = fields.Date(string="Changed Date")
    reason = fields.Many2one('termination.reason',string="Termination Reason")
    type = fields.Many2one('termination.type',string="Termination Type")
    approved_by = fields.Many2one('res.users', string='Approved By', default=lambda self: self.env.user.id)