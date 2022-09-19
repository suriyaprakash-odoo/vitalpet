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

class LoanPayment(models.TransientModel):

    _name = 'loan.payment'

    @api.model
    def default_get(self, fields_name):
        res = super(LoanPayment, self).default_get(fields_name)
        if self._context.get('loan_id'):
            res.update({'loan_id': self._context.get('loan_id')})
            loan = self.env['partner.loan'].browse(self._context.get('loan_id'))
            for emi in loan.emi_lines:
                if emi.state == 'draft':
                    res.update({'emi_id': emi.id})
                    break
        return res

    loan_id = fields.Many2one('partner.loan', 'Loan')
    emi_id = fields.Many2one('loan.emi.line', 'Installment', required=True)
    amount = fields.Float('Payment', required=True)
    payment_date = fields.Date('Payment Date', required=True, default=fields.Date.context_today)
    transaction_date = fields.Date('Transaction Date')
#    pay_type = fields.Selection([('1', 'Cash'), ('2', 'Cheque'), ('3', 'Demand Draft')], defaullt='1', string="Payment Type", required=True)

    @api.onchange('emi_id')
    def onchange_emi(self):
        if self.emi_id:
            self.amount = self.emi_id.funding_amount
            self.transaction_date = self.emi_id.transaction_date
            self.payment_date = self.emi_id.due_date

    @api.multi
    def confirm_int_pa_emi(self, total_pay, pa_pay, int_pay):
        bank_account_vals = {
            'name': '[ ' + self.loan_id.partner_id.name + ' ] ' + self.loan_id.name,
            'debit': pa_pay,
            'credit': 0.0,
            'account_id': self.loan_id.loan_account.id,
            'product_id': self.loan_id.loan_product.id or False,
            'date_maturity': self.emi_id.due_date,
            'partner_id': self.loan_id.partner_id.id,
        }


        interest_receivable_vals = {
            'name': '[ ' + self.loan_id.partner_id.name + ' ] ' + self.loan_id.name,
            'debit': int_pay,
            'credit': 0.0,
            'account_id': self.loan_id.loan_int_account.id,
            'product_id': self.loan_id.interest_product.id or False,
            'date_maturity': self.emi_id.due_date,
            'partner_id': self.loan_id.partner_id.id,
        }
    
        ir_parameter = self.env['ir.property'].search([('company_id', '=', self.loan_id.bank_journal_id.company_id.id),
                                                ('name', '=', 'property_account_payable_id'),
                                               ('res_id', '=', 'res.partner,' + str(self.loan_id.partner_id.id))])
        
        account_id=None
        if ir_parameter.value_reference:
                ref_account_id = (ir_parameter.value_reference).split(',')[1]
                account = self.env['account.account'].search([('id', '=', ref_account_id)])
                if account:
                    account_id = account.id
        

        if account_id==None:
            raise ValidationError(_("Payable and Receivable account is not configured for the current employee"))
        else:            
            customer_receivable_vals = {
                'name': '[ ' + self.loan_id.partner_id.name + ' ] ' + self.loan_id.name,
                'debit': 0.0,
                'credit': total_pay,
                'account_id': account_id,
#                 'account_id': self.loan_id.partner_id.property_account_payable_id.id,
                'date_maturity': self.emi_id.due_date,
                'partner_id': self.loan_id.partner_id.id,
            }
        now = datetime.now()
        vals = {
            'journal_id': self.loan_id.bank_journal_id.id,
            'date': self.transaction_date,
            'state': 'draft',
            'line_ids': [(0, 0, bank_account_vals), (0, 0, interest_receivable_vals), (0, 0, customer_receivable_vals)]
        }
        move = self.env['account.move'].create(vals)
        move.post()
        return move.id

    @api.multi
    def confirm_int_only_int(self, total_pay, int_pay):
        interest_receivable_vals = {
            'name': '[ ' + self.loan_id.partner_id.name + ' ] ' + self.loan_id.name,
            'debit': int_pay,
            'credit': 0.0,
            'account_id': self.loan_id.loan_int_account.id,
            'product_id': self.loan_id.interest_product.id or False,
            'date_maturity': self.emi_id.due_date,
            'partner_id': self.loan_id.partner_id.id,
            'company_id': self.loan_id.bank_journal_id.company_id.id,
        }
        ir_parameter = self.env['ir.property'].search([('company_id', '=', self.loan_id.bank_journal_id.company_id.id),
                                                ('name', '=', 'property_account_payable_id'),
                                               ('res_id', '=', 'res.partner,' + str(self.loan_id.partner_id.id))])
        
        account_id=None
        if ir_parameter.value_reference:
                ref_account_id = (ir_parameter.value_reference).split(',')[1]
                account = self.env['account.account'].search([('id', '=', ref_account_id)])
                if account:
                    account_id = account.id


        if account_id==None:
            raise ValidationError(_("Payable and Receivable account is not configured for the current employee"))
        else:                    
            customer_receivable_vals = {
                'name': '[ ' + self.loan_id.partner_id.name + ' ] ' + self.loan_id.name,
                'debit': 0.0,
                'credit': total_pay,
#                 'account_id': self.loan_id.partner_id.property_account_payable_id.id,
                'account_id': account_id,
                'date_maturity': self.emi_id.due_date,
                'partner_id': self.loan_id.partner_id.id,
                'company_id': self.loan_id.bank_journal_id.company_id.id,           
            }
        now = datetime.now()
        vals = {
            'journal_id': self.loan_id.bank_journal_id.id,
            'date': self.transaction_date,
            'state': 'draft',
            'line_ids': [(0, 0, interest_receivable_vals), (0, 0, customer_receivable_vals)]
        }
        move = self.env['account.move'].create(vals)
        move.post()
        return move.id

    @api.multi
    def confirm_int_only_pa(self, total_pay, pa_pay):
        bank_account_vals = {
            'name': '[ ' + self.loan_id.partner_id.name + ' ] ' + self.loan_id.name,
            'debit': pa_pay,
            'credit': 0.0,
            'account_id': self.loan_id.loan_account.id,
            'product_id': self.loan_id.loan_product.id or False,
            'date_maturity': self.emi_id.due_date,
            'partner_id': self.loan_id.partner_id.id,
            }
        
        ir_parameter = self.env['ir.property'].search([('company_id', '=', self.loan_id.bank_journal_id.company_id.id),
                                                ('name', '=', 'property_account_payable_id'),
                                               ('res_id', '=', 'res.partner,' + str(self.loan_id.partner_id.id))])
        
        account_id=None
        if ir_parameter.value_reference:
                ref_account_id = (ir_parameter.value_reference).split(',')[1]
                account = self.env['account.account'].search([('id', '=', ref_account_id)])
                if account:
                    account_id = account.id
                    
        if account_id==None:
            raise ValidationError(_("Payable and Receivable account is not configured for the current employee"))
        else:
            customer_receivable_vals = {
                'name': '[ ' + self.loan_id.partner_id.name + ' ] ' + self.loan_id.name,
                'debit': 0.0,
                'credit': total_pay,
                'account_id': account_id,
                'date_maturity': self.emi_id.due_date,
                'partner_id': self.loan_id.partner_id.id,
            }
        now = datetime.now()
        vals = {
            'journal_id': self.loan_id.bank_journal_id.id,
            'date': self.transaction_date,
            'state': 'draft',
            'line_ids': [(0, 0, bank_account_vals), (0, 0, customer_receivable_vals)]
        }
        move = self.env['account.move'].create(vals)
        move.post()
        return move.id


    @api.one
    def do_payment(self):
        if self.emi_id:
            self.emi_id.write({
#                'payment_method': self.pay_type,
                'payment_date': self.payment_date,
                'payment_amt' : self.amount >= self.emi_id.funding_amount and self.emi_id.funding_amount or self.amount,
                'state': round(self.amount,2) >= round(self.emi_id.funding_amount,2) and 'done' or 'draft'
        })
        get_move_id = False
        if not self.env['loan.emi.line'].search([('loan_id', '=', self.loan_id.id), ('state', '!=', 'done')]):
            self.loan_id.write({'state': 'done'})

        if self.loan_id.loan_type == 'interest_only' and (self.emi_id.fund_type.find("Installment") != -1 or self.emi_id.fund_type.find("Instalment") != -1):
            tot_pay = self.emi_id.funding_amount
            int_pay = self.emi_id.interest_payment
            get_move_id = self.confirm_int_only_int(tot_pay, int_pay)

        if self.loan_id.loan_type == 'interest_only' and self.emi_id.fund_type.find("Principal Amount") != -1:
            tot_pay = self.emi_id.funding_amount
            pa_pay = self.emi_id.principle_payment
            get_move_id = self.confirm_int_only_pa(tot_pay, pa_pay)

        if self.loan_id.loan_type == 'interest_principle' and (self.emi_id.fund_type.find("Installment") != -1 or self.emi_id.fund_type.find("Instalment") != -1):
            tot_pay = self.emi_id.funding_amount
            pa_pay = self.emi_id.principle_payment
            int_pay = self.emi_id.interest_payment
            get_move_id = self.confirm_int_pa_emi(tot_pay, pa_pay, int_pay)
        
        if self.emi_id:
            if get_move_id == False:
                raise UserError("Loan Type and Fund Type not matched properly")
            else:
                self.emi_id.write({
                    'account_move': get_move_id,
                })
            
        return True


# class MultiLoanPayment(models.TransientModel):
#     _name = 'multi.loan.payment'

# #     @api.model
# #     def default_get(self, fields_name):
# #         res = super(MultiLoanPayment, self).default_get(fields_name)
# #         if self._context.get('active_ids'):
# #             amount_list = []
# #             date_list = []
# #             for emis in self._context.get('active_ids'):
# #                 emi_obj = self.env['loan.emi.line'].search([('id','=',emis)])
# #                 amount_list.append(emi_obj.funding_amount)
# #                 date_list.append(emi_obj.due_date)
# #             amount_uniq = list(set(amount_list))
# #             date_uniq = list(set(date_list))
# #             if len(amount_uniq) > 1:
# #                 raise UserError('Amount Error. ')
# #             else:
# #                 res.update({'amount': amount_uniq[0]})

# # #             if len(date_uniq) > 1:
# # #                 raise UserError('Date Error. ')
# # #             else:
# #             res.update({'payment_date': date_uniq[0]})  
# #         return res

#     amount = fields.Float('Payment')
#     payment_date = fields.Date('Payment Date', default=fields.Date.context_today)
#     emi_id = fields.Many2one('loan.emi.line', 'Installment')
#     loan_id = fields.Many2one('partner.loan', 'Loan')

#     @api.multi
#     def do_payment(self):
#         for emis in self._context.get('active_ids'):
#             emi_obj = self.env['loan.emi.line'].search([('id','=',emis)])
            
#             if emi_obj.state!='draft':
#                 raise UserError("You can post only draft EMI's. ")
#             self.emi_id = emi_obj.id
#             self.loan_id = emi_obj.loan_id.id
#             if emi_obj:
#                 emi_obj.write({'payment_date': self.payment_date,
#                             'state':'done'
#             })
#             if not self.env['loan.emi.line'].search([('loan_id', '=',emi_obj.loan_id.id), ('state', '!=', 'done')]):
#                 emi_obj.loan_id.write({'state': 'done'})

#             if emi_obj.loan_id.loan_type == 'interest_only' and emi_obj.fund_type.find("Installment") != -1:
#                 tot_pay = emi_obj.funding_amount
#                 int_pay = emi_obj.interest_payment
#                 get_move_id = self.confirm_int_only_int(tot_pay, int_pay)

#             if emi_obj.loan_id.loan_type == 'interest_only' and emi_obj.fund_type.find("Principle Amount") != -1:
#                 tot_pay = emi_obj.funding_amount
#                 pa_pay = emi_obj.principle_payment
#                 get_move_id = self.confirm_int_only_pa(tot_pay, pa_pay)

#             if emi_obj.loan_id.loan_type == 'interest_principle' and emi_obj.fund_type.find("Installment") != -1:
#                 tot_pay = emi_obj.funding_amount
#                 pa_pay = emi_obj.principle_payment
#                 int_pay = emi_obj.interest_payment
#                 get_move_id = self.confirm_int_pa_emi(tot_pay, pa_pay, int_pay)
            
#             if emi_obj:
#                 emi_obj.write({
#                     'account_move': get_move_id,
#             })
                
#         return True

#     @api.multi
#     def confirm_int_pa_emi(self, total_pay, pa_pay, int_pay):
#         bank_account_vals = {
#             'name': '[ ' + self.loan_id.partner_id.name + ' ] ' + self.loan_id.name,
#             'debit': pa_pay,
#             'credit': 0.0,
#             'account_id': self.loan_id.loan_account.id,
#             'product_id': self.loan_id.loan_product.id or False,
#             'date_maturity': self.emi_id.due_date,
#             'partner_id': self.loan_id.partner_id.id,
#         }
#         interest_receivable_vals = {
#             'name': '[ ' + self.loan_id.partner_id.name + ' ] ' + self.loan_id.name,
#             'debit': int_pay,
#             'credit': 0.0,
#             'account_id': self.loan_id.loan_int_account.id,
#             'product_id': self.loan_id.interest_product.id or False,
#             'date_maturity': self.emi_id.due_date,
#             'partner_id': self.loan_id.partner_id.id,
#         }
#         customer_receivable_vals = {
#             'name': '[ ' + self.loan_id.partner_id.name + ' ] ' + self.loan_id.name,
#             'debit': 0.0,
#             'credit': total_pay,
#             'account_id': self.loan_id.partner_id.property_account_payable_id.id,
#             'date_maturity': self.emi_id.due_date,
#             'partner_id': self.loan_id.partner_id.id,
#         }
#         now = datetime.now()
#         vals = {
#             'journal_id': self.loan_id.bank_journal_id.id,
#             'date': self.payment_date,
#             'state': 'draft',
#             'line_ids': [(0, 0, bank_account_vals), (0, 0, interest_receivable_vals), (0, 0, customer_receivable_vals)]
#         }
#         move = self.env['account.move'].create(vals)
#         move.post()
#         return move.id

#     @api.multi
#     def confirm_int_only_int(self, total_pay, int_pay):
#         interest_receivable_vals = {
#             'name': '[ ' + self.loan_id.partner_id.name + ' ] ' + self.loan_id.name,
#             'debit': int_pay,
#             'credit': 0.0,
#             'account_id': self.loan_id.loan_int_account.id,
#             'product_id': self.loan_id.interest_product.id or False,
#             'date_maturity': self.emi_id.due_date,
#             'partner_id': self.loan_id.partner_id.id,
#         }
#         customer_receivable_vals = {
#             'name': '[ ' + self.loan_id.partner_id.name + ' ] ' + self.loan_id.name,
#             'debit': 0.0,
#             'credit': total_pay,
#             'account_id': self.loan_id.partner_id.property_account_payable_id.id,
#             'date_maturity': self.emi_id.due_date,  
#             'partner_id': self.loan_id.partner_id.id,          
#         }
#         now = datetime.now()
#         vals = {
#             'journal_id': self.loan_id.bank_journal_id.id,
#             'date': self.payment_dat,
#             'state': 'draft',
#             'line_ids': [(0, 0, interest_receivable_vals), (0, 0, customer_receivable_vals)]
#         }
#         move = self.env['account.move'].create(vals)
#         move.post()
#         return move.id

#     @api.multi
#     def confirm_int_only_pa(self, total_pay, pa_pay):
#         bank_account_vals = {
#             'name': '[ ' + self.loan_id.partner_id.name + ' ] ' + self.loan_id.name,
#             'debit': pa_pay,
#             'credit': 0.0,
#             'account_id': self.loan_id.loan_account.id,
#             'product_id': self.loan_id.loan_product.id or False,
#             'date_maturity': self.emi_id.due_date,
#             'partner_id': self.loan_id.partner_id.id,
#             }

#         customer_receivable_vals = {
#             'name': '[ ' + self.loan_id.partner_id.name + ' ] ' + self.loan_id.name,
#             'debit': 0.0,
#             'credit': total_pay,
#             'account_id': self.loan_id.partner_id.property_account_payable_id.id,
#             'date_maturity': self.emi_id.due_date,
#             'partner_id': self.loan_id.partner_id.id,
#         }
#         now = datetime.now()
#         vals = {
#             'journal_id': self.loan_id.bank_journal_id.id,
#             'date': self.payment_dat,
#             'state': 'draft',
#             'line_ids': [(0, 0, bank_account_vals), (0, 0, customer_receivable_vals)]
#         }
#         move = self.env['account.move'].create(vals)
#         move.post()
#         return move.id