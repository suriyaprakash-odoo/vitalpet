# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError, UserError

_ACCOUNT_RULE = [
    ('product_exp_acc', 'Product Expense Account'),
    ('product_inc_acc', 'Product Income Account'),
    ('journal_debit_acc', 'Journal Debit Account'),
    ('journal_credit_acc', 'Journal Credit Account'),
    ('no_acc', 'No Account')
    ]

class HrPeriod(models.Model):
    _inherit = 'hr.period'
    _order = 'number asc'

    payroll_split = fields.Boolean('Payroll Split', default=False, help='Split payroll boolean is used at payslip runtime to  split entries for end of quarter in certain fiscal periods. If this is checked, will split the payroll by week in the journal entry instead of over 2 weeks')


class CompensationTag(models.Model):
    _name = "compensation.tag"

    name = fields.Char("Name", required=True)

    _sql_constraints = [
            ('name_uniq', 'unique (name)', "Tag name already exists !"),
    ]


class JobTemplate(models.Model):
    _inherit = "hr.job.template"

    compensation_tag_ids = fields.Many2many('compensation.tag', 'job_template_compensation', 'job_template_id', 'compensation_tag_id', 'Compensation Tag')


class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'

    compensation_tag_id = fields.Many2one('compensation.tag', 'Compensation Tag', help='Compensation Tag is used to distinguish between staff a doctor labor')
    acc_product_id = fields.Many2one('product.product', 'Product', help='Product used when accounting entries created')
    partner_id = fields.Many2one('res.partner', 'Partner')
    inc_payroll_account = fields.Boolean('Include in Payroll Accounting', default=False, help='With this checked, this rule will be used when accounting entries created')
    debit_acc_rule = fields.Selection(_ACCOUNT_RULE, 'Debit Account Rule', help='This defines which debit account will be used for the rule')
    credit_acc_rule = fields.Selection(_ACCOUNT_RULE, 'Credit Account Rule', help='This defines which credit account will be used for the rule. If both a debit and credit rule are indicated, 2 entries will be created in journal entry (one debit, and one credit)')
    book_parent_level = fields.Boolean('Book also at Parent Level', default=False, help='When this check box is enabled, then another entry will be created at the parent level.')
    parent_debit_acc_id = fields.Many2one('account.account', 'Parent Debit Account', domain=[('deprecated', '=', False)], help='Parent debit account will be used for the debit account')
    parent_credit_acc_id = fields.Many2one('account.account', 'Parent Credit Account', domain=[('deprecated', '=', False)], help='Parent credit account will be used for the credit account')
