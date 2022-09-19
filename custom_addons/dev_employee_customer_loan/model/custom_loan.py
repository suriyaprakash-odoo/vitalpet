from odoo import fields, models, api
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError

class loan_emi_month(models.Model):
    _name = 'loan.emi.month'

    transaction_date = fields.Date('Transaction Date')
    fund_type = fields.Char('Funding')
    funding_amount = fields.Float('Amount')
    loan_id = fields.Many2one('partner.loan', 'Loan')
    is_journal = fields.Boolean('Journal', readonly=True)
    principle_payment = fields.Float('Principal Payment')
    interest_payment = fields.Float('Interest Payment')
    payment_id = fields.Many2one('account.move', string='Payment JE Ref')
    outstanding_amount = fields.Float('Outstanding Amount')
    emi_id = fields.Many2one('account.move', string='EMI JE Ref')
    invoice_id = fields.Many2one('account.move', string='Invoice JE Ref')
    
    
    def create_journal(self):
        if not self.funding_amount == 0:
            if self.loan_id.product_id:
                product_id = self.loan_id.product_id.id 
            else:
                product_id = False
            journal_list = []
            accounts_payable = ({
                    'account_id':self.loan_id.partner_id.property_account_payable_id.id,
                    'name':self.loan_id.partner_id.name + self.loan_id.name,
                    'debit':0,
                    'credit':self.funding_amount,
                    'product_id':False,
                    'partner_id':self.loan_id.partner_id.id,
                    })
            journal_list.append((0, 0, accounts_payable))
            interest_expense = ({
                    'account_id':self.loan_id.interest_acc_id.id,
                    'name':self.loan_id.partner_id.name + self.loan_id.name,
                    'debit':self.interest_payment,
                    'credit':0,
                    'product_id':self.loan_id.product_id.id or False,
                    'partner_id':self.loan_id.partner_id.id,
                    })
            journal_list.append((0, 0, interest_expense))
            note_payable = ({
                    'account_id':self.loan_id.loan_acc_debit_id.id,
                    'name':self.loan_id.partner_id.name + self.loan_id.name,
                    'debit':self.principle_payment,
                    'credit':0,
                    'product_id':self.loan_id.product_debit_id.id or False,
                    'partner_id':self.loan_id.partner_id.id,
                    })
            print note_payable,'note_payable'
            journal_list.append((0, 0, note_payable))
            account_move = self.env['account.move'].create({
                                                            'journal_id':self.loan_id.journal_principle_id.id,
                                                            'date':self.transaction_date,
                                                            'line_ids':journal_list,
                                                            'loan_journal_id':self.id,
                                                            'ref':self.loan_id.name + ' ' + self.fund_type
                                                         })
            if account_move:
                self.is_journal = True
                self.emi_id = account_move.id    
                
                
    @api.multi
    def action_partner_loan_journal(self):
        loan_month_obj = self.env['loan.emi.month'].search([('transaction_date','=',date.today() + relativedelta(days=10)),('is_journal','=',False),('funding_amount','>', 0)])
        for line in loan_month_obj:
            line.create_journal()                        
    
class partner_loan(models.Model):
    _inherit = 'partner.loan'
    
    emi_lines_month_ids = fields.One2many('loan.emi.month', 'loan_id', 'EMI Month')
    company_id  = fields.Many2one('res.company', string='Company', readonly=True, default=lambda self: self.env.user.company_id.id)
    due_every_month = fields.Integer('Due Every (Months)', required=True, readonly=True, states={'draft': [('readonly', False)]})
    first_payment_month = fields.Integer('First Payment (Months)', required=True, readonly=True, states={'draft': [('readonly', False)]})
    loan_maturity_date = fields.Date('Loan Maturity Date')
    
    @api.model
    def create(self, vals): 
        if not vals.get('interest_acc_id') and not vals.get('journal_principle_id'):
            raise UserError('Please configure Account details in Loan Configuration Setting.')
        else:
            vals.update({'loan_int_account':vals.get('interest_acc_id'),
                         'bank_journal_id':vals.get('journal_principle_id'),
                        })
        if not vals.get('calc_principle_amount'):
            raise UserError('Please enter Principle Amount.')
        elif not vals.get('calc_interest_rate'):
            raise UserError('Please enter Interest Rate.')
        
        if vals.get('installment_type') == 'monthly': 
            if not vals.get('calc_months'):
                raise UserError('Please enter Installment (Months).')
        else:
            if not vals.get('calc_quarter'):
                raise UserError('Please enter Installment (Quarter).')
             
        return super(partner_loan, self).create(vals)     
    
   

    def generate_journal_lines(self):
        pay_id = self.generate_loan_journal()
        emi_line_obj = self.env['loan.emi.month']
        loan_type = self.loan_type
        emi_line = {
            'loan_id':self.id,
            'transaction_date':self.loan_release_date,
            'partner_id': self.partner_id.id,
            'fund_type': 'Principle Amount',
            'funding_amount':0,
            'outstanding_amount':self.calc_principle_amount,
            'principle_payment':0,
            'interest_payment':0,
            'emi_id':pay_id.id
        }
        emi_line_obj.create(emi_line)
        
        for emi in self.env['loan.emi.line'].search([('loan_id','=',self.id)]):
            t_date = datetime.strptime(emi.transaction_date, "%Y-%m-%d")
            emi_line = {
                        'loan_id': self.id,
                        'partner_id': self.partner_id.id,
                        'transaction_date': t_date.replace(day=15),
                        'fund_type': emi.fund_type,
                        'funding_amount': emi.funding_amount,
                        'outstanding_amount': emi.outstanding_amount,
                        'principle_payment': emi.principle_payment,
                        'interest_payment': emi.interest_payment,
                    }

            emi_line_obj.create(emi_line)
        self.update({'state': 'confirm'})
        
    def compute_emi_lines(self):
        self.emi_calc()
        emi_line_obj = self.env['loan.emi.line']
        if self.calc_monthly_emi > 0:
            loan_type = self.loan_type
            emi_line = {
                'loan_id':self.id,
                'transaction_date':self.loan_release_date,
                'partner_id': self.partner_id.id,
                'sequence': 0,
                'fund_type': 'Principle Amount',
                'funding_amount':0,
                'outstanding_amount':self.calc_principle_amount,
                'principle_payment':0,
                'outstanding_Interest': 0,
                'interest_payment':0,
                'state':'done',
            }
#             self.env['loan.emi.line'].create(emi_line)

            if(loan_type == 'interest_only'):  
                if self.installment_type == 'monthly':
                    monthly_emi = self.calc_monthly_emi
                    installments = self.calc_months
                else:
                    monthly_emi = self.calc_quarterly_emi
                    installments = self.calc_quarter
                    
                total_interest = monthly_emi * installments
                transaction_date = datetime.strptime(self.payment_date, '%Y-%m-%d')+relativedelta(months=self.first_payment_month)
                outstanding_interest = total_interest
                pa = self.calc_principle_amount
                inst = 0
                emi_split=1
                for i in range(0, installments):
                    j=1
                    for line in range(0, self.due_every_month):
                        inst = i+1
                        num = str(emi_split).zfill(2)                        
                        funding = 'EMI ' + num
                        
                        t_date = datetime.strftime(transaction_date, '%Y-%m-%d')
                        if transaction_date.month%self.due_every_month==0:
                            emi_split+=1
                        
                        
                        
                        if self.installment_type == 'monthly':
                            monthly_pa = self.calc_monthly_emi 
                        else:
                            monthly_pa = self.calc_quarterly_emi 
                        # if j==1:
                        #     out_inst=outstanding_interest
                        # else:
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
                            'emi_seq':j,
                        }
                        
                        transaction_date = transaction_date + relativedelta(months=1)
                        self.env['loan.emi.line'].create(emi_line)
                        j+=1
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

            elif (loan_type == 'interest_principle'):
                if self.installment_type == 'monthly':
                    installments = self.calc_months
                    monthly_emi = self.calc_monthly_emi
                else:
                    installments = self.calc_quarter
                    monthly_emi = self.calc_quarterly_emi
                    
                total_payable_amount = monthly_emi * installments
                transaction_date = datetime.strptime(self.payment_date, '%Y-%m-%d')+relativedelta(months=self.first_payment_month)
                outstanding_amount = total_payable_amount
                pa = self.calc_principle_amount
                ir = self.calc_interest_rate
                monthly_ir=0
                # if self.installment_type == 'monthly':
                #     monthly_ir = (ir / 12.0) / 100.0
                # else:
                #     monthly_ir = (ir / 4) / 100.0
                due = 12/self.due_every_month
                monthly_ir = (ir /due) / 100.0

                    
                tot_payment = monthly_emi * installments
                outstanding_loan_interest = tot_payment - pa
                emi_split=1
                for i in range(0, installments):
                    monthly_interest = pa * monthly_ir
                    if self.installment_type == 'monthly':
                        monthly_pa_val = self.calc_monthly_emi
                        monthly_pa = self.calc_monthly_emi - monthly_interest
                    else:
                        monthly_pa_val = self.calc_quarterly_emi
                        monthly_pa = self.calc_quarterly_emi - monthly_interest
                    j=1
                    for line in range(0, self.due_every_month):
                        inst = i+1
                        num = str(emi_split).zfill(2)
                        funding = 'EMI ' + num
                        t_date = datetime.strftime(transaction_date, '%Y-%m-%d')
                        if transaction_date.month%self.due_every_month==0:
                            emi_split+=1
                        # if j==1:
                        #     out_amt=pa
                        #     out_inst=abs(outstanding_loan_interest)
                        # else:
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
                            'emi_seq':j,
                        }
                            
                        transaction_date = transaction_date + relativedelta(months=1)
                        emi_line_obj.create(emi_line)
                        j+=1
                    outstanding_amount = outstanding_amount - monthly_emi
                    outstanding_loan_interest -= monthly_interest
                    
                    pa -= monthly_pa
            else:
                raise UserError('Please select Loan Type. ')
        else:
            raise UserError('Please generate Monthly EMI. ')
        self.update({'state': 'computed'})
    
    def generate_loan_journal(self):  
        journal_list = []
        if self.product_debit_id:
            product_debit_id = self.product_debit_id.id
        else:
            product_debit_id = False
            
        if self.product_credit_id:
            product_credit_id = self.product_credit_id.id
        else:
            product_credit_id = False 
        opp_move_line = ({
                'account_id':self.loan_acc_credit_id.id,
                'name':self.partner_id.name + ' ' + self.name,
                'debit':0,
                'credit':self.calc_principle_amount,
                'product_id':False,
                'partner_id':self.partner_id.id,
                })
        journal_list.append((0, 0, opp_move_line))   
        move_line = ({
                'account_id':self.loan_acc_debit_id.id,
                'name':self.partner_id.name + ' '  + self.name,
                'debit':self.calc_principle_amount,
                'credit':0,
                'product_id':product_debit_id,
                'partner_id':self.partner_id.id,
                })
        journal_list.append((0, 0, move_line))
        account_move = self.env['account.move'].create({
                                                        'journal_id':self.journal_principle_id.id,
                                                        'date':self.loan_release_date,
                                                        'line_ids':journal_list,
                                                        'ref':self.name + ' ' + 'Principle Amount'
                                                     })
        return account_move

class AccountMove(models.Model):
    _inherit = 'account.move'
    
    loan_journal_id = fields.Many2one('loan.emi.month',string='Loan Journal')
    
    @api.model
    def write(self, values):
        for rec in self:
            if values.get('billpay_id'):
                bill_id = self.env['billpay.bills'].search([('id','=', values.get('billpay_id'))])
                for bills in bill_id.bill_line_ids:
                    if bills.payable_receivable_move_line_id:
                        bills.payable_receivable_move_line_id.move_id.loan_journal_id.invoice_id = rec.id
            
        return super(AccountMove, self).write(values)     
    
    
class AccountPaymentOrder(models.Model):
    _inherit = 'account.payment.order'
    
    @api.multi
    def generate_move(self):
        """
        Create the moves that pay off the move lines from
        the payment/debit order.
        """
        self.ensure_one()
        am_obj = self.env['account.move']
        post_move = self.payment_mode_id.post_move
        # prepare a dict "trfmoves" that can be used when
        # self.payment_mode_id.move_option = date or line
        # key = unique identifier (date or True or line.id)
        # value = bank_pay_lines (recordset that can have several entries)
        trfmoves = {}
        for bline in self.bank_line_ids:
            hashcode = bline.move_line_offsetting_account_hashcode()
            if hashcode in trfmoves:
                trfmoves[hashcode] += bline
            else:
                trfmoves[hashcode] = bline

        for hashcode, blines in trfmoves.iteritems():
            mvals = self._prepare_move(blines)
            total_company_currency = total_payment_currency = 0
            for bline in blines:
                total_company_currency += bline.amount_company_currency
                total_payment_currency += bline.amount_currency
                partner_ml_vals = self._prepare_move_line_partner_account(
                    bline)
                mvals['line_ids'].append((0, 0, partner_ml_vals))
            trf_ml_vals = self._prepare_move_line_offsetting_account(
                total_company_currency, total_payment_currency, blines)
            mvals['line_ids'].append((0, 0, trf_ml_vals))
            mvals['date'] = self.bank_line_ids[0].date
            move = am_obj.create(mvals)
            if move:
                for billpay in self.payment_line_ids:
                    if billpay.billpay_id:
                        for bill in billpay.billpay_id.bill_line_ids:
                            if bill.payable_receivable_move_line_id.move_id.loan_journal_id:
                                bill.payable_receivable_move_line_id.move_id.loan_journal_id.payment_id = move.id 
            blines.reconcile_payment_lines()
            if post_move:
                move.post()
              
class loan_emi_line(models.Model):
    _inherit = 'loan.emi.line'
    
    state = fields.Selection([('draft', 'Pending'), ('due', 'Due'), ('done', 'Paid')], 'Status', default='draft', compute='_compute_state')
    payment_date = fields.Date('Payment Date', compute='_compute_pay_date')
    
    @api.depends('loan_id', 'transaction_date')
    def _compute_state(self):
        for line in self:
            if line.loan_id:
                emi_principle_id = self.env['loan.emi.month'].search([('loan_id','=',line.loan_id.id),('fund_type','=',line.fund_type),('funding_amount','=', 0),('outstanding_amount','=',line.outstanding_amount)])
                if emi_principle_id:
                    if emi_principle_id.emi_id:
                        line.state = 'done'
                emi_month_id = self.env['loan.emi.month'].search([('loan_id','=',line.loan_id.id),('fund_type','=',line.fund_type),('funding_amount','>', 0)])
                if emi_month_id:
                    payment_list = []
                    for emi_month in emi_month_id:
                        if emi_month.payment_id:
                            payment_list.append('Paid')
                        else:
                            payment_list.append('Pending')
                    if not 'Pending' in payment_list:
                        line.state = 'done'
                            
    @api.depends('loan_id')
    def _compute_pay_date(self):
        for line in self:
            if line.loan_id:
                emi_month_id = self.env['loan.emi.month'].search([('loan_id','=',line.loan_id.id),('fund_type','=',line.fund_type)])
                if emi_month_id:
                    i=0
                    payment_date=False
                    for emi_month in emi_month_id:
                        if emi_month.payment_id:                            
                            payment_date = emi_month.sudo().payment_id.date
                        else:
                            i=1
                    if i==0:
                        line.payment_date = payment_date
 