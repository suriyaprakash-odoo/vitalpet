# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError, UserError
import operator
from operator import itemgetter
import itertools
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT



class AccountMove(models.Model):
    _inherit = 'account.move'

    payslip_id = fields.Many2one('hr.payslip', 'Payslip')
    split_percentage = fields.Float('Split (%)')


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'


    @api.multi
    @api.depends()
    def _calculate_total_hours(self):
        for record in self:
            total_hours = 0.0
            for line in record.worked_days_line_ids:
                total_hours += line.number_of_hours
            record.total_hours = total_hours


    move_ids = fields.One2many('account.move', 'payslip_id', 'Payroll Split')
    total_hours = fields.Float('Total Hours', compute='_calculate_total_hours')

    
    def calculate_split(self, slip, period_start, period_stop):
        worked_days = []
        total_hours = slip.total_hours
        for line in slip.worked_days_line_ids:
            worked_days.append({'period_start': period_start, 'period_stop': period_stop, 'date': line.date, 'job_id': line.activity_id.job_id, 'company': line.activity_id.job_id.company_id.name, 'company_id': line.activity_id.job_id.company_id, 'hours': line.number_of_hours, 'total': line.total})

        worked_days.sort(key=operator.itemgetter('company'))
        
        group_lines = []
        for key, items in itertools.groupby(worked_days, operator.itemgetter('company')):
            group_lines.append(list(items))

        grouped_list = []
        for item in group_lines:
            company_id = item[0]['company_id']
            tmp_period_start = item[0]['period_start']
            tmp_period_stop = item[0]['period_stop']
            size = len(item)
            company_hours = 0
            for k in range(size):
                company_hours += item[k]['hours']
            split_percentage = round(((company_hours / total_hours) * 100), 3)
            if self.env.context.get('no_period', False):
                split_percentage = round((split_percentage / 2), 3)
            grouped_list.append({'company_id': company_id, 'company_hours': company_hours, 'split_percentage': split_percentage, 'period_start': tmp_period_start, 'period_stop': tmp_period_stop})  

        if self.env.context.get('no_period', False):
            return grouped_list
        return [[period_start, period_stop]], grouped_list


    def calculate_period_split(self, slip):
        periods = []
        period_grouped_list = []
        period_start = datetime.strptime(
                slip.hr_period_id.date_start, DEFAULT_SERVER_DATE_FORMAT)
        period_stop = datetime.strptime(
                slip.hr_period_id.date_stop,
                DEFAULT_SERVER_DATE_FORMAT) + relativedelta(days=1)

        while not (period_start + relativedelta(days=6) > period_stop):
            split_result = self.with_context({'no_period': True}).calculate_split(slip, str(period_start)[:10], str(period_start + relativedelta(days=6))[:10])
            period_grouped_list += split_result
            periods.append([str(period_start)[:10], str(period_start + relativedelta(days=6))[:10]])
            period_start = period_start + relativedelta(weeks=1)
        return periods, period_grouped_list

    @api.multi
    def compute_sheet(self):
        res = super(HrPayslip, self).compute_sheet()
        for payslip in self:
            payslip.move_ids.unlink()
            payslip.compute_move()
        return res

    @api.multi
    def process_sheet(self):
        res = super(HrPayslip, self).process_sheet()
        for payslip in self:
            payslip.move_ids.post()
        return res

    @api.multi
    def compute_move(self):
        move_pool = self.env['account.move']
        precision = self.env['decimal.precision'].precision_get('Payroll')

        for slip in self:
            line_ids = []
            debit_sum = 0.0
            credit_sum = 0.0
            split_periods = []
            split_results = []
            parent_move_vals = []
            employee_partner = slip.employee_id.address_home_id
            name = _('Payslip of %s') % (slip.employee_id.name)
            
            
            if slip.hr_period_id.payroll_split:
                split_periods, split_results = slip.calculate_period_split(slip)
            else:
                split_periods, split_results = slip.calculate_split(slip, slip.hr_period_id.date_start, slip.hr_period_id.date_stop)
            
            for period in split_periods:
                parent_line_ids = []
                parent_move_vals = {
                    'narration': name,
                    'date': period[1],
                    'ref': slip.hr_period_id.name or '',
                    'journal_id': slip.company_id.parent_journal_id.id,
                    'company_id': slip.company_id.payroll_company_id.id,
                    'payslip_id': slip.id,
                    'split_percentage': 100.00,
                }

                for result in split_results:
                    if period[0] != result['period_start'] and period[1] != result['period_stop']:
                        continue

                    line_ids = []
                    company_id = result['company_id']
                    if not company_id.journal_id:
                        raise ValidationError(('Payroll Journal is not configured for the Company - %s.')% company_id.name)

                    period_date_stop = result['period_stop']
                    journal_id = company_id.journal_id

                    move_vals = {
                        'narration': name,
                        'date': period_date_stop,
                        'ref': slip.hr_period_id.name or '',
                        'journal_id': journal_id.id,
                        'company_id': company_id.id,
                        'payslip_id': slip.id,
                        'split_percentage': result['split_percentage'],
                    }    
                    for line in slip.details_by_salary_rule_category:
                        line_amount = (line.amount * float(result['split_percentage'])) / 100

                        if not line.salary_rule_id.inc_payroll_account:
                            continue

                        rule = line.salary_rule_id.with_context({'force_company': company_id.id})
                        
                        if not rule.acc_product_id: 
                                raise UserError(('Product is not configured in the rule : %s')% rule.name)

                        if rule.debit_acc_rule != 'no_acc':
                            if (rule.debit_acc_rule in ('product_exp_acc', 'product_inc_acc')):
                                if rule.debit_acc_rule == 'product_exp_acc':
                                    name = "property_account_expense_categ_id"
                                elif rule.debit_acc_rule == 'product_inc_acc':
                                    name = "property_account_income_categ_id"
                                ir_parameter = self.env['ir.property'].search([('company_id', '=', company_id.id),
                                                            ('name', '=', name),
                                                           ('res_id', '=', 'product.category,' + str(rule.acc_product_id.categ_id.id))])
                                if ir_parameter.value_reference:
                                    ref_account_id = (ir_parameter.value_reference).split(',')[1]
                                    account = self.env['account.account'].search([('id', '=', ref_account_id)])
                            if (rule.debit_acc_rule in ('product_exp_acc', 'product_inc_acc') and not account) or (rule.credit_acc_rule in ('product_exp_acc', 'product_inc_acc') and not account):
                                raise UserError(('Income/Expense Account is not configured in the product : %s')% rule.acc_product_id.name)
                            
                            if not journal_id.default_debit_account_id or not journal_id.default_credit_account_id:
                                raise UserError(('Debit/Credit Account is not configured in the Journal : %s')% journal_id.name)

                            if rule.debit_acc_rule == 'product_exp_acc':
                                debit_account_id = account.id
                            elif rule.debit_acc_rule == 'product_inc_acc':
                                debit_account_id = account.id
                            elif rule.debit_acc_rule == 'journal_debit_acc':
                                debit_account_id = journal_id.default_debit_account_id.id
                            elif rule.debit_acc_rule == 'journal_credit_acc':
                                debit_account_id = journal_id.default_credit_account_id.id

                            debit_line = (0, 0, {
                                'name': rule.name,
                                'date': period_date_stop,
                                'partner_id': rule.partner_id and rule.partner_id.id or slip.employee_id.address_home_id.id,
                                'account_id': debit_account_id,
                                'product_id': rule.acc_product_id.id,
                                'journal_id': journal_id.id,
                                'debit': line_amount > 0.0 and line_amount or 0.0,
                                'credit': line_amount < 0.0 and line_amount*-1 or 0.0,
                                })
                            line_ids.append(debit_line)
                        

                        if rule.credit_acc_rule != 'no_acc':
                            if (rule.credit_acc_rule in ('product_exp_acc', 'product_inc_acc')):
                                if rule.credit_acc_rule == 'product_exp_acc':
                                    name = "property_account_expense_categ_id"
                                elif rule.credit_acc_rule == 'product_inc_acc':
                                    name = "property_account_income_categ_id"
                                ir_parameter = self.env['ir.property'].search([('company_id', '=', company_id.id),
                                                            ('name', '=', name),
                                                           ('res_id', '=', 'product.category,' + str(rule.acc_product_id.categ_id.id))])
                                if ir_parameter.value_reference:
                                    ref_account_id = (ir_parameter.value_reference).split(',')[1]
                                    account = self.env['account.account'].search([('id', '=', ref_account_id)])
                            if (rule.debit_acc_rule in ('product_exp_acc', 'product_inc_acc') and not account) or (rule.credit_acc_rule in ('product_exp_acc', 'product_inc_acc') and not account):
                                raise UserError(('Income/Expense Account is not configured in the product : %s')% rule.acc_product_id.name)
                            
                            if not journal_id.default_debit_account_id or not journal_id.default_credit_account_id:
                                raise UserError(('Debit/Credit Account is not configured in the Journal : %s')% journal_id.name)

                            if rule.credit_acc_rule == 'product_exp_acc':
                                credit_account_id = account.id
                            elif rule.credit_acc_rule == 'product_inc_acc':
                                credit_account_id = account.id
                            elif rule.credit_acc_rule == 'journal_debit_acc':
                                credit_account_id = journal_id.default_debit_account_id.id
                            elif rule.credit_acc_rule == 'journal_credit_acc':
                                credit_account_id = journal_id.default_credit_account_id.id
                            
                                                 
                            credit_line = (0, 0, {
                                'name': rule.name,
                                'date': period_date_stop,
                                'partner_id': rule.partner_id and rule.partner_id.id or slip.employee_id.address_home_id.id,
                                'account_id': credit_account_id,
                                'product_id': rule.acc_product_id.id,
                                'journal_id': journal_id.id,
                                'debit': line_amount < 0.0 and line_amount*-1 or 0.0,
                                'credit': line_amount > 0.0 and line_amount or 0.0,
                                })
                            line_ids.append(credit_line)

                            if rule.book_parent_level:
                                parent_line_ids += [{
                                        'name': rule.name,
                                        'date': period[1],
                                        'partner_id': rule.partner_id and rule.partner_id.id or slip.employee_id.address_home_id.id,
                                        'account_id': rule.parent_debit_acc_id.id,
                                        'product_id': rule.acc_product_id.id,
                                        'journal_id': slip.company_id.parent_journal_id.id,
                                        'debit': line_amount > 0.0 and line_amount or 0.0,
                                        'credit': line_amount < 0.0 and line_amount*-1 or 0.0,
                                    },{
                                        'name': rule.name,
                                        'date': period[1],
                                        'partner_id': rule.partner_id and rule.partner_id.id or slip.employee_id.address_home_id.id,
                                        'account_id': rule.parent_credit_acc_id.id,
                                        'product_id': rule.acc_product_id.id,
                                        'journal_id': slip.company_id.parent_journal_id.id,
                                        'debit': line_amount < 0.0 and line_amount*-1 or 0.0,
                                        'credit': line_amount > 0.0 and line_amount or 0.0,
                                    }]
                    
                    move_vals.update({'line_ids': line_ids})
                    move = move_pool.create(move_vals)
                if parent_line_ids:
                    parent_line_ids.sort(key=operator.itemgetter('date', 'name'))
        
                    jl_lines = []
                    for key, items in itertools.groupby(parent_line_ids, operator.itemgetter('date', 'name')):
                        jl_lines.append(list(items))
                    grouped_jl_lines = []
                    for jl_item in jl_lines:
                        debit = 0
                        credit = 0
                        debit_account = 0
                        credit_account = 0
                        inc=0
                        for tmp in jl_item:
                            name = tmp['name']
                            date = tmp['date']
                            product_id = tmp['product_id']
                            partner_id = tmp['partner_id']
                            journal_id = tmp['journal_id']
                            account_id = tmp['account_id']
                            debit += tmp['debit']
                            credit += tmp['credit']
                            if tmp['debit']<=0 and tmp['credit']<=0:
                                if inc==0:
                                    credit_account=tmp['account_id']
                                    inc=1
                                if inc==1:
                                    debit_account=tmp['account_id']
                            elif tmp['debit']<=0:
                                credit_account=tmp['account_id']
                            else:
                                debit_account=tmp['account_id']
                        
                        if debit<0:
                            debit_account_new=credit_account
                            credit_account=debit_account
                            debit_account=debit_account_new
                            debit=debit*-1
                            credit=credit*-1
                            
                        grouped_jl_lines += [(0, 0, {
                                'name': name,
                                'date': date,
                                'partner_id': partner_id,
                                'account_id': debit_account,
                                'product_id': product_id,
                                'journal_id': journal_id,
                                'debit': debit,
                                'credit': 0.0,
                            }), (0, 0, {
                                'name': name,
                                'date': date,
                                'partner_id': partner_id,
                                'account_id': credit_account,
                                'product_id': product_id,
                                'journal_id': journal_id,
                                'debit': 0.0,
                                'credit': credit,
                            })]
                    parent_move_vals.update({'line_ids': grouped_jl_lines})
                    moves = move_pool.create(parent_move_vals)

        return True