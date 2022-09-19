# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 Devintelle Software Solutions (<http://devintellecs.com>).
#
##############################################################################

from odoo import fields, models, api, _
from openerp.exceptions import UserError, ValidationError
from datetime import datetime
from dateutil.relativedelta import relativedelta


class AccountLoanProofType(models.Model):
    _name = 'loan.proof.type'

    name = fields.Char(string='Proof Type Name ', required=True)
    short_name = fields.Char(string='Shortcut ', size=32, required=True)
    loan_id = fields.Many2one('loan_id', 'Loan Id')
    p_document = fields.Binary('Attachment')
    p_name = fields.Char('File Name')


class partner_loan(models.Model):
    _name = 'partner.loan'

    name = fields.Char('Loan Application', default='New')
    partner_id = fields.Many2one('res.partner', 'Lender', required=True)
    loan_release_date = fields.Date('Loan Release Date', required=True,help="This is the contract date of the loan for reference purposes. This field will not be used in any calculations.")
    remarks = fields.Text('Remarks')
    state = fields.Selection([('draft','Draft'), ('confirm','Confirmed'), ('done','Done')], 'State', default='draft')

    loan_type = fields.Selection([('interest_only','EMI with Interest Only'),
                                  ('interest_principle','EMI with Interest and Principal')], 'Loan Type', default='interest_principle')

    calc_principle_amount = fields.Integer('Principal Amount')
    calc_interest_rate = fields.Float('Interest Rate',help="Annual interest rate for loan. Enter 0 for a principal only loan.")
    calc_months = fields.Integer('Installment')
    calc_monthly_emi = fields.Float('Monthly EMI',help="This is the calculated monthly payment based on Principal Amount, Number of Installments and Interest Rate.")

    bank_journal_id = fields.Many2one('account.journal', 'Purchase Journal', required=True)
    loan_int_account = fields.Many2one('account.account', 'Interest Account', required=True)
    loan_account = fields.Many2one('account.account', 'Loan Account', required=True)
    loan_product = fields.Many2one('product.product', 'Loan Product')
    interest_product = fields.Many2one('product.product', 'Interest Product')

    process_fee_ids = fields.One2many('loan.process.fee', 'loan_id', 'Process Fees')
    emi_lines = fields.One2many('loan.emi.line', 'loan_id', 'EMI Lines')
    proof_ids = fields.One2many('loan.proof.type', 'loan_id', 'Proofs')
    
    product_id = fields.Many2one('product.product', 'Product')
    product_se_id = fields.Many2one('product.product', 'Product 2')
    # laon_account_id = fields.Many2one('account.account', 'Loan Account')

    loan_maturity_date = fields.Date('Loan Maturity Date',help="This is the contract date of the loan maturity for reference purposes. This field will not be used in any calculations.")
    accounting_commencement_date = fields.Date('Accounting Commencement Date',help="This is the first installment date for which accounting entries are created. Some users choose the 15th to accommodate multiple accounting fiscal period types.")
    due_every_month = fields.Integer('Due Every', required=True,help="Enter the number of months that payments are due. Example 3 is for a loan that is paid quarterly and 1 is for a loan that is paid monthly.")
    payment_delay = fields.Integer('Payment Delay (Loan Commence)', required=True,help="Enter the number of months past the Accounting Commencement Date the first payment is due.")

    @api.model
    def create(self, values):
        values['name'] = self.env['ir.sequence'].next_by_code('partner.loan') or _('New')
        return super(partner_loan, self).create(values)
            
    
     
    @api.constrains('due_every_month')
    def _check_month(self):
        if self.due_every_month<=0:
            raise ValidationError(_('please enter the Due Every Month.'))
     
    @api.constrains('calc_principle_amount')
    def _check_principle(self):
        if  self.calc_principle_amount<=0:
            raise ValidationError(_('Please enter the Principal Amount.'))
             
    @api.constrains('calc_months')
    def _check_months(self):
        if self.calc_months<=0:
            raise ValidationError(_('Please enter the Installment.'))
            
    # @api.constrains('calc_interest_rate')
    # def _check_rate(self):
    #     if self.calc_interest_rate<=0:
    #         raise ValidationError(_('Please enter the Interest Rate.'))
        
    @api.constrains('accounting_commencement_date')
    def _check_date(self):
        if not self.accounting_commencement_date:
            raise ValidationError(_('please enter Accounting Commencement Date.'))
                                 
    def emi_calc(self):
        pa = self.calc_principle_amount
        ir = self.calc_interest_rate
        months = self.calc_months
        loan_type = self.loan_type
        if(loan_type == 'interest_only'):
            due = 12/self.due_every_month
            if ir > 0:
                monthly_ir = (ir / due) / 100.0
                monthly_emi = pa * monthly_ir
                self.calc_monthly_emi = monthly_emi
                rate = pow(1 + monthly_ir, months)
                top = (pa * monthly_ir) * rate
                bottom = rate - 1
                monthly_emi = top / bottom
            else:
                monthly_emi = pa / months
                self.calc_monthly_emi = monthly_emi
        elif(loan_type == 'interest_principle'):      
            due = 12/self.due_every_month
            if ir > 0:
                monthly_ir = (ir / due) / 100
                rate = pow(1 + monthly_ir, months)
                top = (pa * monthly_ir) * rate
                bottom = rate - 1
                monthly_emi = top / bottom
                self.calc_monthly_emi = monthly_emi
            else:
                monthly_emi = pa / months
                self.calc_monthly_emi = monthly_emi
        else:
            raise UserError('Please select Loan Type.')

    @api.multi
    def confirm_loan_account_move(self, total_pay, pa_pay, int_pay):
        customer_receivable_vals = {
            'name': '[ ' + self.partner_id.name + ' ] ' + self.name,
            'debit': total_pay,
            'credit': 0.0,
            'account_id': self.partner_id.property_account_payable_id.id,
        }
        bank_account_vals = {
            'name': '[ ' + self.partner_id.name + ' ] ' + self.name,
            'debit': 0.0,
            'credit': pa_pay,
            'account_id': self.bank_journal_id.default_credit_account_id.id,
        }
        interest_receivable_vals = {
            'name': '[ ' + self.partner_id.name + ' ] ' + self.name,
            'debit': 0.0,
            'credit': int_pay,
            'account_id': self.loan_int_account.id,
        }
        now = datetime.now()
        vals = {
            'journal_id': self.bank_journal_id.id,
            'date': now.strftime('%Y-%m-%d'),
            'state': 'draft',
            'line_ids': [(0, 0, customer_receivable_vals), (0, 0, bank_account_vals), (0, 0, interest_receivable_vals)]
        }
        move = self.env['account.move'].create(vals)
        move.post()
        return move.id

    def generate_emi_lines(self):
        self.emi_calc()
        emi_line_obj = self.env['loan.emi.line']
        if self.calc_monthly_emi > 0:
            loan_type = self.loan_type
            emi_line = {
                'loan_id':self.id,
                'transaction_date':self.loan_release_date,
                'partner_id': self.partner_id.id,
                'sequence': 0,
                'fund_type': 'Payment Released',
                'funding_amount':0,
                'outstanding_amount':self.calc_principle_amount,
                'principle_payment':0,
                'outstanding_Interest': 0,
                'interest_payment':0,
                'state':'',
            }
            self.env['loan.emi.line'].create(emi_line)

            # if (loan_type == 'interest_only'):
            #     tot_pay = self.calc_principle_amount + (self.calc_monthly_emi * self.calc_months)
            #     pa_pay = self.calc_principle_amount
            #     int_pay = self.calc_monthly_emi * self.calc_months
            #     self.confirm_loan_account_move(tot_pay, pa_pay, int_pay)

            # if (loan_type == 'interest_principle'):
            #     tot_pay = self.calc_monthly_emi * self.calc_months
            #     pa_pay = self.calc_principle_amount
            #     int_pay = (self.calc_monthly_emi * self.calc_months) - self.calc_principle_amount
            #     self.confirm_loan_account_move(tot_pay, pa_pay, int_pay)


            if(loan_type == 'interest_only'):
                monthly_emi = self.calc_monthly_emi
                installments = self.calc_months
                total_interest = monthly_emi * installments
                transaction_date = datetime.strptime(self.accounting_commencement_date, '%Y-%m-%d') 
                outstanding_interest = total_interest
                pa = self.calc_principle_amount
                inst = 0
                z=0
                for i in range(0, installments):
                    j=1
                    for line in range(0, self.due_every_month):
                        inst = z+j
                        num = str(inst).zfill(2)                        
                        funding = 'Installment ' + num
                        t_date = datetime.strftime(transaction_date, '%Y-%m-%d')
                        due_date = transaction_date
                        month_per = transaction_date.month%self.due_every_month
                        if month_per == 1:
                            due_date = transaction_date + relativedelta(months=2)
                        elif month_per == 2:
                            due_date = transaction_date + relativedelta(months=1)
                        elif month_per == 0:
                            due_date = transaction_date
                        monthly_pa = self.calc_monthly_emi 
                        out_inst=outstanding_interest-(monthly_pa/self.due_every_month*(j))
                        emi_line = {
                            'loan_id':self.id,
                            'transaction_date':t_date,
                            'partner_id': self.partner_id.id,
                            'sequence': inst,
                            'fund_type': funding,
                            'funding_amount':monthly_pa/self.due_every_month,
                            'outstanding_amount':pa,
                            'principle_payment':0,
                            'outstanding_Interest': out_inst,
                            'interest_payment':monthly_pa/self.due_every_month,
                            'due_date':due_date.replace(day=15)
                        }
                        
                        transaction_date = transaction_date + relativedelta(months=1)
                        self.env['loan.emi.line'].create(emi_line)
                        j+=1
                    z+=self.due_every_month
                    outstanding_interest = outstanding_interest - monthly_emi
                t_date = datetime.strftime(transaction_date, '%Y-%m-%d')
                principle_emi_line = {
                    'loan_id': self.id,
                    'sequence': inst,
                    'transaction_date': t_date,
                    'partner_id': self.partner_id.id,
                    'fund_type': 'Principle Amount',
                    'funding_amount': self.calc_principle_amount,
                    'outstanding_amount': 0.0,
                    'principle_payment': self.calc_principle_amount,
                    'outstanding_Interest': 0.0,
                    'interest_payment': 0.0,
                }
                emi_line_obj.create(principle_emi_line)
                self.update({'state': 'confirm'})
                
            elif (loan_type == 'interest_principle'):
                installments = self.calc_months
                monthly_emi = self.calc_monthly_emi
                total_payable_amount = monthly_emi * installments
                transaction_date = datetime.strptime(self.accounting_commencement_date, '%Y-%m-%d')
                outstanding_amount = total_payable_amount
                pa = self.calc_principle_amount
                ir = self.calc_interest_rate
                monthly_ir=0
                due = 12/self.due_every_month
                monthly_ir = (ir /due) / 100.0
                tot_payment = monthly_emi * installments
                outstanding_loan_interest = tot_payment - pa
                z=0
                for i in range(0, installments):
                    monthly_interest = pa * monthly_ir
                    monthly_pa_val = self.calc_monthly_emi
                    monthly_pa = self.calc_monthly_emi - monthly_interest
                    j=1
                    for line in range(0, self.due_every_month):
                        inst = z+j
                        num = str(inst).zfill(2)
                        funding = 'Installment ' + num
                        t_date = datetime.strftime(transaction_date, '%Y-%m-%d')
                        due_date = transaction_date
                        month_per = transaction_date.month%self.due_every_month
                        if month_per == 1:
                            due_date = transaction_date + relativedelta(months=2)
                        elif month_per == 2:
                            due_date = transaction_date + relativedelta(months=1)
                        elif month_per == 0:
                            due_date = transaction_date

                        out_amt=pa-((abs(monthly_pa)/self.due_every_month)*(j))
                        out_inst=abs(outstanding_loan_interest)-(monthly_interest/self.due_every_month*(j))
                        if out_amt < 0:
                            out_amt=0.00
                        emi_line = {
                            'loan_id': self.id,
                            'partner_id': self.partner_id.id,
                            'sequence': inst,
                            'transaction_date': t_date,
                            'fund_type': funding,
                            'funding_amount': monthly_pa_val/self.due_every_month,
                            'outstanding_amount': out_amt,
                            'principle_payment': abs(monthly_pa)/self.due_every_month,
                            'outstanding_Interest': out_inst,
                            'interest_payment': monthly_interest/self.due_every_month,
                            'due_date':due_date.replace(day=15),
                        }
                        transaction_date = transaction_date + relativedelta(months=1)
                        emi_line_obj.create(emi_line)
                        j+=1
                    z+=self.due_every_month
                    outstanding_amount = outstanding_amount - monthly_emi
                    outstanding_loan_interest -= monthly_interest
                    
                    pa -= monthly_pa
                self.update({'state': 'confirm'})
            else:
                raise UserError('Please select Loan Type. ')
        else:
            raise UserError('Please generate Monthly EMI. ')


class loan_emi_line(models.Model):
    _name = 'loan.emi.line'
    _rec_name = 'fund_type'

    name = fields.Char('EMI', default='New')
    partner_id = fields.Many2one('res.partner', 'Customer')
    loan_id = fields.Many2one('partner.loan', 'Loan', ondelete='cascade')
    sequence = fields.Integer('Sequence')
    transaction_date = fields.Date('Transaction Date')
    fund_type = fields.Char('Funding')
    payment_method = fields.Selection([('1', 'Cash'), ('2', 'Cheque'), ('3', 'Demand Draft')],'Payment Method')
    payment_date = fields.Date('Payment Date')
    funding_amount = fields.Float('Funding Amount')
    outstanding_amount = fields.Float('Outstanding Amount')
    principle_payment = fields.Float('Principal Payment')
    outstanding_Interest = fields.Float('Outstanding Interest')
    interest_payment = fields.Float('Interest Payment')
    payment_amt = fields.Float('Payment')
    state = fields.Selection([('draft', 'Pending'), ('due', 'Due'), ('done', 'Posted')], 'Status', default='draft')
    account_move = fields.Many2one('account.move' , string="Account Move")
    due_date = fields.Date('Due Date')
    
    @api.model
    def create(self, values):
        values['name'] = self.env['ir.sequence'].next_by_code('loan.emi.line') or _('New')
        return super(loan_emi_line, self).create(values)

    @api.multi
    def do_payment(self):
        for tid in self.ids:
            emi_obj = self.env['loan.emi.line'].search([('id','=',tid)])
            ComposePayment = self.env['loan.payment']
            values = {
                        'loan_id': emi_obj.loan_id.id,
                        'emi_id': emi_obj.id,
                        'amount': emi_obj.funding_amount,
                        'payment_date': emi_obj.due_date,
                        'transaction_date': emi_obj.transaction_date,
                    }
            compose_payment_wizard = ComposePayment.create(values)
            compose_payment_wizard.do_payment()

  
class process_fee(models.Model):
    _name = 'loan.process.fee'

    loan_id = fields.Many2one('partner.loan', 'Loan Id')
    processing_item = fields.Char('Processing Item')
    item_provider = fields.Char('Item Provider')
    item_fee = fields.Float('Item Fee')
    payable_by = fields.Char('Payable By')
