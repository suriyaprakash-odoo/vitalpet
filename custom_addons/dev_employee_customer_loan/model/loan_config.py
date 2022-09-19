# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
#from odoo import models
from odoo import api, fields, models


class LoanConfigSettings(models.TransientModel):

    _name = 'loan.config.settings'
    _inherit = 'res.config.settings'

    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)
    journal_principle_id = fields.Many2one('account.journal', string='Journal', required=True, related='company_id.journal_principle_id')
    loan_acc_debit_id = fields.Many2one('account.account', string='Principle Loan Account DR', required=True, related='company_id.loan_acc_debit_id')
    loan_acc_credit_id = fields.Many2one('account.account', string='Principle Loan Account CR', required=True, related='company_id.loan_acc_credit_id')
    product_debit_id = fields.Many2one('product.product', string='Product DR', related='company_id.product_debit_id') 
    product_credit_id = fields.Many2one('product.product', string='Product CR', related='company_id.product_credit_id') 
    journal_interest_id = fields.Many2one('account.journal', string='Journal', required=True, related='company_id.journal_interest_id')
    interest_acc_id = fields.Many2one('account.account', string='Interest Account', required=True, related='company_id.interest_acc_id')
    product_id = fields.Many2one('product.product', string='Product', related='company_id.product_id')
    
class Company(models.Model):
    _inherit = 'res.company'
    
    journal_principle_id = fields.Many2one('account.journal', string='Journal')
    loan_acc_debit_id = fields.Many2one('account.account', string='Principle Loan Account DR')
    loan_acc_credit_id = fields.Many2one('account.account', string='Principle Loan Account CR')
    product_debit_id = fields.Many2one('product.product', string='Product DR') 
    product_credit_id = fields.Many2one('product.product', string='Product CR') 
    journal_interest_id = fields.Many2one('account.journal', string='Journal')
    interest_acc_id = fields.Many2one('account.account', string='Interest Account')
    product_id = fields.Many2one('product.product', string='Product')   
