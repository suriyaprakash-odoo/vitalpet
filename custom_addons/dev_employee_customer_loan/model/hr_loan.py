# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 Devintelle Software Solutions (<http://devintellecs.com>).
#
##############################################################################

import time
from datetime import datetime, timedelta, date
import openerp.addons.decimal_precision as dp
from odoo import models, fields, api , _
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError


class hr_loan(models.Model):
    _name = 'hr.loan'
    _description = "Employee Loan Request Form"
    

    @api.multi
    @api.depends('installment_lines')
    def _calculate_amounts(self):
        
        ##TO_FIX :: Calculation for amount_to_pay should be done for loan with interest
        res = {}
        paid_amount=0.0
        for loan in self:
            if loan.installment_lines:
                for installment in loan.installment_lines:
                    paid_amount += installment.amount
            loan.amount_paid = paid_amount
            loan.amount_to_pay = loan.loan_amount - paid_amount
        return True


    def _get_employee_id(self):
        employee_ids = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)])
        if employee_ids:
            for emp in employee_ids:
                return emp.id
        return False

    name = fields.Char('Name', size=64, required=True)
    request_date= fields.Date('Loan Request Date', required=True, default=fields.Datetime.now)
    start_date = fields.Date('Loan Payment Start Date', default=fields.Datetime.now)
    due_date= fields.Date('Loan Payment End Date')
    loan_amount = fields.Float('Loan Amount', digits=dp.get_precision('Account'), required=True)
    duration = fields.Integer('Payment Duration(Months)')
    loan_interest = fields.Float('Loan Interest', digits=dp.get_precision('Account'))
    deduction_amount= fields.Float('Deduction Amount', digits=dp.get_precision('Account'))
    employee_id = fields.Many2one('hr.employee', 'Employee', required=True, default=_get_employee_id)
    loan_type= fields.Selection([('salary','Loan Against Salary'),('service', 'Loan Against Service')], string="Loan Type", required=True, default='salary')
    description = fields.Text('Purpose For Loan', required=True,)
    job_id= fields.Many2one( related='employee_id.job_id', string='Job Title')
    department_id = fields.Many2one(related='employee_id.department_id', string="Department", store=True)
    state = fields.Selection([('draft', 'Draft'), ('open', 'Waiting Approval'), ('refuse', 'Refused'), ('confirm', 'Approved'), ('done', 'Done'), ('cancel', 'Cancelled')], string="Status",required=True, default='draft')
    emi_based_on = fields.Selection([('duration', 'By Duration'), ('amount', 'By Amount'), ('percentage', 'By Percentage of Gross')], string='EMI based on', required=True, default='duration')
    percentage_of_gross = fields.Float('Percentage of Gross', digits=dp.get_precision('Account'))
    installment_lines= fields.One2many('installment.line','loan_id','Installments')
    amount_paid = fields.Float(compute='_calculate_amounts',string='Amount Paid',digits=dp.get_precision('Account'),multi='amount',readonly=True)
    amount_to_pay= fields.Float(compute='_calculate_amounts',string='Amount to Pay',digits=dp.get_precision('Account'),multi='amount',readonly=True)
    user_id = fields.Many2one('res.users', string='User', index=True, track_visibility='onchange', default=lambda self: self.env.user)
    
    
    
    @api.onchange('department_id','job_id','employee_id')
    def onchange_employee_id(self):
        if not self.employee_id:
            result = {'value': {'department_id': False, 'job_id': False}}
        else:
            self.write({'department_id': self.employee_id.department_id.id, 'job_id': self.employee_id.job_id.id})
            
    @api.onchange('start_date','emi_based_on','duration')
    def onchange_start_date(self):
        if self.emi_based_on != 'percentage':
            if not self.start_date:
                raise UserError(_('Please Enter Start Date.'))
            if self.start_date and self.duration:
                self.due_date = (datetime.strptime(self.start_date,'%Y-%m-%d') + timedelta(self.duration * 365 / 12)).strftime('%Y-%m-%d')

    @api.multi
    def make_calculation(self):
        for loan in self:
            if not loan.loan_amount or loan.loan_amount < 0:
                raise UserError(_('Please enter proper value for Loan Amount & Loan Interest.'))
            if loan.emi_based_on == 'duration':
                if not loan.duration or loan.duration < 0:
                    raise UserError(_('Please enter proper value for Payment Duration'))
                if loan.loan_interest <= 0:
                    installment = loan.loan_amount / loan.duration
                else:
                    r = (loan.loan_interest / 12) / 100
                    installment = loan.loan_amount * r * pow((1 + r),loan.duration) / (pow((1 + r),loan.duration) - 1)
                loan.write({'deduction_amount': installment})
            elif loan.emi_based_on == 'amount':
                if not loan.deduction_amount or loan.deduction_amount < 0:
                    raise UserError(_('Please enter proper value for Deduction Amount'))
                count = 0
                r = (loan.loan_interest / 12) / 100
                loan_amount = loan.loan_amount
                while loan_amount > 0:
                    rate = loan_amount * r
                    loan_amount = loan_amount - (loan.deduction_amount - rate)
                    count += 1
                loan.write({'duration': count})
        return True
    
    
    @api.multi
    def send_loan_request_mail(self):
        res_partner_obj = self.env['res.partner']
        mail_mail = self.env['mail.mail']
        partner_ids = []
        browse_group=self.env.ref('hr.group_hr_manager')
        
        if browse_group:
            for user in browse_group.users:
                partner_ids.append(user.partner_id.id)
        if partner_ids:
            subject  =  'Loan Request : '+ self.name + ' For the '+ self.employee_id.name
            for partner in res_partner_obj.browse(partner_ids):
                if partner.email:
                    body = '''
                        Dear ''' " %s," % (partner.name) + '''
                        <p></p>
                        <p> Loan request from ''' "%s" % self.employee_id.name + '''</p> 
                        <p><b>Loan Detail</b></p>
                        <p><b> Loan Name :</b>''' "%s" % self.name + '''.</p> 
                        <p><b>Loan amount :</b>''' "%s" % self.loan_amount + '''.</p> 
                        <p><b>Loan Duratation(Months):</b>''' "%s" % self.duration + ''' .</p> 
                        <p></p>                                 
                        <p><b>Regards,</b><br/>''' "%s" % self.employee_id.name +''' </p> 
                        ''' 
                    mail_values = {
                        'email_from': self.user_id.partner_id.email,
                        'email_to': partner.email,
                        'subject': subject,
                        'body_html': body,
                        'state': 'outgoing',
                        'type': 'email',
                    }
                    mail_id = mail_mail.create(mail_values)
                    mail_id.send(True)
        return True
        
    @api.multi
    def confirm_loan(self):
        for loan in self:
            due_date = False
            if loan.emi_based_on != 'percentage':
                due_date = (datetime.strptime(loan.start_date,'%Y-%m-%d') + timedelta(loan.duration * 365 / 12)).strftime('%Y-%m-%d')
            loan.write({'state': 'open', 'due_date': due_date})
            loan.send_loan_request_mail()
        return True
    
    def send_loan_approval_mail(self):
        mail_mail = self.env['mail.mail']
        if self.user_id.partner_id:
            subject  =  'Loan approved :'+ self.name + 'For the '+ self.employee_id.name
            if self.user_id.partner_id.email:
                body = '''
                    Dear ''' " %s," % (self.employee_id.name) + '''
                    <p></p>
                    <p>Your loan request is approved by ''' "%s " % self.env.user.name + ''' Manager</p> 
                    <p><b>Loan Details:</b></p>
                    <p><b>Loan Name : </b>''' "%s" % self.name + '''.</p> 
                    <p><b>Loan amount : </b>''' "%s" % self.loan_amount + '''.</p> 
                    <p><b>Loan Duratation(Months): </b>''' "%s" % self.duration + ''' .</p> 
                    <p></p>                                 
                    <p><b>Regards,</b><br/>''' "%s" % self.env.user.name +''' </p> 
                    ''' 
                mail_values = {
                    'email_from': self.env.user.partner_id.email,
                    'email_to': self.user_id.partner_id.email,
                    'subject': subject,
                    'body_html': body,
                    'state': 'outgoing',
                    'type': 'email',
                }
                mail_id = mail_mail.create(mail_values)
                mail_id.send(True)
        return True
        
    @api.multi
    def approve_loan(self):
        due_date = False
        if self.emi_based_on != 'percentage':
            due_date = (datetime.strptime(self.start_date,'%Y-%m-%d') + timedelta(self.duration * 365 / 12)).strftime('%Y-%m-%d')
        self.write({'state': 'confirm', 'due_date': due_date})
        self.send_loan_approval_mail()
        return True
    
    def done_loan(self):
        self.write({'state':'done'})
        return True
    
    def refuse_loan(self):
        if self.installment_lines:
            raise UserError(_('You can not refuse a loan having any installment!'))
        self.write({'state': 'refuse'})
        return True
    
    def set_to_draft(self):
        self.write({'state': 'draft'})
        return True
    
    def set_to_cancel(self):
        return self.write({'state': 'cancel'})
    
    def unlink(self):
        for rec in self:
            if rec.state not in ['draft', 'refuse']:
                raise UserError(_('You cannot delete a loan which is in %s state.')%(rec.state))
        return super(hr_loan, self).unlink()


class installment_line(models.Model):
    _name = 'installment.line'

    loan_id= fields.Many2one('hr.loan','Loan',required=True)
    payslip_id= fields.Many2one('hr.payslip','Payslip',required=True)
    employee_id= fields.Many2one('hr.employee','Employee',required=True)
    date= fields.Date('Date',required=True)
    amount = fields.Float('Installment Amount', digits=dp.get_precision('Account'), required=True)

#class hr_skip_installment(models.Model):
#    _name = 'hr.skip.installment'

#    name= fields.Char('Reason to Skip',required=True)
#    loan_id = fields.Many2one('hr.loan','Loan',domain="[('employee_id','=',employee_id)]",required=True)
#    employee_id = fields.Many2one('hr.employee','Employee',required=True)
#    date= fields.Date('Date',required=True)
#    state= fields.Selection([('draft', 'Draft'), ('open', 'Waiting Approval'), ('refuse', 'Refused'), ('confirm', 'Approved'), ('cancel', 'Cancelled')], string="Status",required=True)

#    _defaults = {
#        'employee_id': employee_get,
#        'state': 'draft',
#        'date': time.strftime('%Y-%m-%d'),
#    }
#    
#    def confirm_request(self, cr, uid, ids, context=None):
#        return self.write(cr, uid, ids, {'state': 'open'}, context=context)
#    
#    def approve_request(self, cr, uid, ids, context=None):
#        self.write(cr, uid, ids, {'state': 'confirm'}, context=context)
#        return True
#    
#    def refuse_request(self, cr, uid, ids, context=None):
#        self.write(cr, uid, ids, {'state': 'refuse'}, context=context)
#        return True
#    
#    def set_to_draft(self, cr, uid, ids, context=None):
#        self.write(cr, uid, ids, {'state': 'draft'}, context=context)
#        return True
#    
#    def set_to_cancel(self, cr, uid, ids, context=None):
#        return self.write(cr, uid, ids, {'state': 'cancel'}, context=context)
#    
#    def unlink(self, cr, uid, ids, context=None):
#        for rec in self.browse(cr, uid, ids, context=context):
#            if rec.state not in ['draft', 'refuse']:
#                raise osv.except_osv(_('Warning!'),_('You cannot delete a skip installment request which is in %s state.')%(rec.state))
#        return super(hr_skip_installment, self).unlink(cr, uid, ids, context)


class hr_employee(models.Model):
    _inherit = 'hr.employee'

    loan_ids= fields.One2many('hr.loan', 'employee_id', string='Loans')

class hr_payslip(models.Model):
    _inherit = "hr.payslip"
#    
    @api.multi
    def hr_verify_sheet(self):
        loan_obj = self.env['hr.loan']
        skip_installment_obj = self.env['hr.skip.installment']
        slip_line_obj = self.env['hr.payslip.line']
        installment_obj = self.env['installment.line']
#        self.compute_sheet()
#        for payslip in self.browse(cr, uid, ids, context=context):
        loan_ids = loan_obj.search([('employee_id','=',self.employee_id.id), ('state','=','confirm'), ('loan_type','=','salary')])
        for loan in loan_obj.browse(loan_ids):
            skip_installment_ids = skip_installment_obj.search([('loan_id','=',loan.id.id),('state','=','confirm'),('date','>=',self.date_from),('date','<=',self.date_to)])
            if skip_installment_ids and loan.id.emi_based_on != 'percentage':
                due_date = datetime.strptime(loan.id.due_date, '%Y-%m-%d') + relativedelta(months=1)
                loan.id.write({'due_date': due_date})
            else:
                slip_line_ids = slip_line_obj.search([('slip_id','=',self.id),('code','=','LOAN' + str(loan.id.id))])
                if slip_line_ids:
#                    amount = slip_line_obj.read(slip_line_ids.id, ['total'])[0]['total']
                    amount = slip_line_obj.browse(slip_line_ids)
                    installment_data = {
                        'loan_id': loan.id.id,
                        'payslip_id': self.id,
                        'employee_id': self.employee_id.id,
                        'amount': abs(amount.id.total),
                        'date': time.strftime('%Y-%m-%d')
                    }
                    new_id = installment_obj.create(installment_data)
                if loan.id.amount_to_pay <= 0:
                    loan_obj.write([loan.id.id.id], {'state': 'done'})
        return self.write({'state': 'verify'})

#     @api.multi
#     def unlink(self):
#         if oids:
#             raise UserError(_('You cannot delete'))
#         return super(hr_payslip, self).unlink()

    @api.multi                      
    def check_insallments_to_pay(self):
        slip_line_obj = self.env['hr.payslip.line']
        loan_obj = self.env['hr.loan']
        rule_obj = self.env['hr.salary.rule']
        skip_installment_obj = self.env['hr.skip.installment']
        for payslip in self:
            loan_ids = loan_obj.search([('employee_id','=',payslip.employee_id.id), ('state','=','confirm'), ('loan_type','=','salary')])
            rule_ids = rule_obj.search([('code','=','LOAN')])
            if rule_ids:
                rule = rule_obj.browse(rule_ids[0])
                oids = slip_line_obj.search([('slip_id','=',payslip.id),('code','=','LOAN')])
                if oids:
#                    slip_line_obj.unlink(oids)
                    slip_line_obj.unlink()
                for loan in loan_obj.browse(loan_ids):
                    skip_installment_ids = skip_installment_obj.search([('loan_id','=',loan.id.id),('state','=','confirm'),('date','>=',payslip.date_from),('date','<=',payslip.date_to)])
                    if not skip_installment_ids:
                        slip_line_data = {
                            'slip_id': payslip.id,
                            'salary_rule_id': rule.id.id,
                            'contract_id': payslip.contract_id.id,
                            'name': 'loan' + str(loan.id.id),
                            'code': 'LOAN' + str(loan.id.id),
                            'category_id': rule.id.category_id.id,
                            'sequence': rule.id.sequence + loan.id.id,
                            'appears_on_payslip': rule.id.appears_on_payslip,
                            'condition_select': rule.id.condition_select,
                            'condition_python': rule.id.condition_python,
                            'condition_range': rule.id.condition_range,
                            'condition_range_min': rule.id.condition_range_min,
                            'condition_range_max': rule.id.condition_range_max,
                            'amount_select': rule.id.amount_select,
                            'amount_fix': rule.id.amount_fix,
                            'amount_python_compute': rule.id.amount_python_compute,
                            'amount_percentage': rule.id.amount_percentage,
                            'amount_percentage_base': rule.id.amount_percentage_base,
                            'register_id': rule.id.register_id.id,
                            'amount': -(loan.id.deduction_amount),
                            'employee_id': payslip.employee_id.id,
                        }
                        if loan.id.emi_based_on == 'percentage':
                            gross_ids = slip_line_obj.search([('slip_id','=',payslip.id),('code','=','GROSS')])
                            gross_record = slip_line_obj.browse(gross_ids[0])
                            slip_line_data.update({'amount': -(gross_record.id.total * loan.id.percentage_of_gross / 100)})
                        if  abs(slip_line_data['amount']) > loan.id.amount_to_pay:
                            slip_line_data.update({'amount': loan.amount_to_pay})
                        sid = slip_line_obj.create(slip_line_data)
                        net_ids = slip_line_obj.search([('slip_id','=',payslip.id),('code','=','NET')])
                        net_record = slip_line_obj.browse(net_ids[0])
                        net_record.id.write({'amount': net_record.id.amount + slip_line_data['amount']})
        return True
#
    def compute_sheet(self):
        res = super(hr_payslip, self).compute_sheet()
        self.check_insallments_to_pay()
        self.hr_verify_sheet()
        return True
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
