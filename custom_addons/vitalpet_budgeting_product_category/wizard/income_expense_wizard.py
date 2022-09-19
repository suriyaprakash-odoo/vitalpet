# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import time
import datetime
from datetime import date
from calendar import monthrange


class WizardIncomeExpense(models.TransientModel):
    """
    For Income and Expense Detail
    """
    _name = "wizard.income.expense"
    _description = "Account income expense"

    draft = fields.Boolean(string='Draft')
    confirm = fields.Boolean(string='Confirm')
    

    @api.multi
    def set_confirm(self):
        budget_obj = self.env['crossovered.budget']
        for loop in self.env.context['active_ids']:
            budget = budget_obj.search([('id', '=', loop)])
            if budget.state == 'draft':
                budget.state = 'confirm'
        return True
    
    
    @api.multi
    def set_draft(self):
        budget_obj = self.env['crossovered.budget']
        for loop in self.env.context['active_ids']:
            budget = budget_obj.search([('id', '=', loop)])
            if budget.state in ['confirm','cancel','validate','done']:
                budget.state = 'draft'
        return True
        


class AccountIncomeExpense(models.TransientModel):
    """
    For Income and Expense Detail
    """
    _name = "account.income.expense"
    _description = "Account income expense"
    

    @api.model
    def default_get(self, fields):
        today = datetime.datetime.now().date()
        year = datetime.datetime.today().year
        period = str('445-'+str(year))
        res = super(AccountIncomeExpense, self).default_get(fields)
        #company = res['company_id']
        #company_br = self.env['res.company'].browse(company)
        account_fiscal_periods = self.env['account.fiscal.periods'].search([('calendar_type', '=', self.company_id.calendar_type.id),('name', '=', period)])
        if account_fiscal_periods:
            period = self.env['account.fiscal.period.lines'].search([('account_fiscal_period_id','in',[a.id for a in account_fiscal_periods]),('name', '=', 'M1-'+str(year))])
            res.update({
                'fiscalyear': account_fiscal_periods.id,
                'period_from': period.id,
                'period_to': period.id
            })
        return res


    company_id = fields.Many2one('res.company',string="Company", default=lambda self: self.env['res.company']._company_default_get('account.income.expense'))
    date = fields.Date(string='Date', default=lambda self: fields.datetime.now())    
    fiscalyear = fields.Many2one('account.fiscal.periods', 
                                    'Fiscal year',
                                    help='Keep empty for all open fiscal years')
    period_from = fields.Many2one('account.fiscal.period.lines', 'Start period')
    period_to = fields.Many2one('account.fiscal.period.lines', 'End period')
    target_move = fields.Selection([('posted', 'All Posted Entries'),
                                    ('all', 'All Entries')],'Target Moves', required=True, default='posted')
    scenario = fields.Selection([
        ('minimum', 'Minimum'),
        ('budget', 'Budget'),
        ('stretch', 'Stretch'),
        ], 'Scenario', track_visibility='always',help="You may load up to three budgets per practice. Minimum, Budget, or Stretch, Some user may choose only to have one budget")
    
    custom_calendar = fields.Boolean(string='Custom Calendar',compute="_compute_display_name")
    fiscal_year = fields.Char('Fiscal Year')
    fiscalyear_start_month = fields.Selection([(1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'), (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'), (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')], default=1)
    fiscalyear_end_month = fields.Selection([(1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'), (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'), (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')], default=1)
    
    
        
    @api.depends('company_id')
    def _compute_display_name(self):
        for line in self:
            line.custom_calendar = line.company_id.custom_calendar
            
    
#     @api.multi
#     def open_income_expense(self):
#         context = self._context
#         if context is None:
#             context = {}
#         grossrevenue = 0.0
#         expenses = 0.0
#         discounts = 0.0
#         costofgoods = 0.0
#         grossmargin = 0.0
#         netrevenue = 0.0
#         EBITDA = 0.0
#         depreciation = 0.0
#         category_obj = self.env['product.category']
#         act_obj = self.env['ir.actions.act_window']
#         fy_obj = self.env['account.fiscal.periods']
#         move_line_obj = self.env['account.move.line']
#         income_expense_obj = self.env['income.expense.details']
#         income_sr = income_expense_obj.search([])
#         income_sr.unlink()
#         data = self.read()[0]
#         view_id =  self.env.ref('vitalpet_budgeting_product_category.view_budget_tree_view').id
#         fiscalyear_id = data.get('fiscalyear', False) and data['fiscalyear'][0] or False
#         crossovered_budget_obj = self.env['budget.category.lines']        
#         hierarchy_obj = self.env['income.expense.hierarchy']
#         product_obj = self.env['product.product']
#         regular_hierarchy = hierarchy_obj.search([('include', '=', True),('view_type', '=', 'regular')])
#         view_hierarchy = hierarchy_obj.search([('include', '=', True),('view_type', '=', 'view')])
#         act_parent_tot = 0.0
#         reverse = '-'
#         if not self.custom_calendar:
#             if self.fiscalyear_start_month:
#                 _,num_days = monthrange(int(self.fiscal_year), int(self.fiscalyear_start_month))
# 
#                 first_day = datetime.date(int(self.fiscal_year), int(self.fiscalyear_start_month), 1)
#                 startdate = first_day.strftime('%Y-%m-%d')
# 
#                 
#             if self.fiscalyear_end_month:
#                 _,num_days = monthrange(int(self.fiscal_year), int(self.fiscalyear_start_month))
# 
#                 last_day = datetime.date(int(self.fiscal_year), int(self.fiscalyear_start_month), num_days)
#                 enddate = last_day.strftime('%Y-%m-%d')
#         else:
#             startdate = self.period_from.date_start
#             enddate = self.period_to.date_end
#             
#         account = False
#         for regular_loop in regular_hierarchy:
#             tot = 0.0
#             if self.custom_calendar:
#                 self.env.cr.execute("SELECT sum(planned_amount) FROM budget_category_lines WHERE company_id = %s and state='confirm' and budget_scenario ='budget' and product_category = %s and date_from >= %s AND date_to <= %s", (str(self.company_id.id),str(regular_loop.category_id.id),str(startdate),str(enddate)))
#             else:
#                 self.env.cr.execute("SELECT sum(planned_amount) FROM budget_category_lines WHERE company_id = %s and state='confirm' and budget_scenario ='budget' and product_category = %s and date_from >= %s and date_to <= %s", (str(self.company_id.id),str(regular_loop.category_id.id),str(startdate),str(enddate)))
#             planned = self.env.cr.fetchone()
#             plan = 0.0
#             if planned[0]:
#                 plan = planned[0]
#             else:
#                 plan = 0.0
#             if regular_loop.include:
#                 vals = {
#                     'type': regular_loop.category_id.name,
#                     'type_seq': regular_loop.sequence,
#                     'company_id': self.company_id.id,
#                     'currency_id': self.company_id.currency_id.id,
#                     'planned_amount':plan,
#                     'actual_amount':0.0,
#                     'variance': 0.0,
#                     }
#             income_line_parent_id = income_expense_obj.create(vals)
# 
#             for hierarchy_line_loop in regular_loop.hierarchy_line:
#                 if hierarchy_line_loop.include == True:
#                     self.env.cr.execute("SELECT sum(planned_amount) FROM budget_category_lines WHERE company_id = %s and state='confirm' and budget_scenario ='budget' and product_category = %s and date_from >= %s and date_to <= %s", (str(self.company_id.id),str(hierarchy_line_loop.category_id.id),str(startdate),str(enddate)))
#                     planned = self.env.cr.fetchone()
#                     plan = 0.0
#                     if planned[0]:
#                         plan = planned[0]
#                     else:
#                         plan = 0.0
#                     prod_sr = product_obj.search([('categ_id', '=', hierarchy_line_loop.category_id.id)])
#                     categ_vals = {
#                         'type':hierarchy_line_loop.category_id.name,
#                         'type_seq': hierarchy_line_loop.sequence,
#                         'company_id': self.company_id.id,
#                         'currency_id': self.company_id.currency_id.id,
#                         'planned_amount': plan,
#                         'actual_amount':0.0,
#                         'variance': 0.0,
#                         'parent_id' :income_line_parent_id.id,
#                         }
#                     category_id = income_expense_obj.create(categ_vals)
#                     pr_code = str(hierarchy_line_loop.sequence) + "001"
#                     act_tot = 0.0
#                     planned_tot = 0.0
#                     account=False
#                     for prod_loop in prod_sr:
#                         act = 0.0
#                         actual_amount = 0.0
#                         if prod_loop.id:
#                             if hierarchy_line_loop.type == 'revenue':
#                                 account = hierarchy_line_loop.category_id.property_account_income_categ_id.id
#                             if hierarchy_line_loop.type == 'expense':
#                                 account = hierarchy_line_loop.category_id.property_account_expense_categ_id.id
#                             
#                             move_line_sr = move_line_obj.search([('date', '>=', startdate),('date', '<=', enddate),
#                             ('product_id', '=', prod_loop.id),
#                             ('company_id', '=', self.company_id.id)])
#                             for loop_line in move_line_sr:
#                                 if hierarchy_line_loop.type == 'revenue':
#                                     actual_amount = actual_amount + loop_line.credit
#                                 if hierarchy_line_loop.type == 'expense':
#                                     actual_amount = actual_amount + loop_line.debit
# 
#                             if actual_amount != 0.0:
#                                 categ_vals = {
#                                     'type':prod_loop.name,
#                                     'type_seq': pr_code,
#                                     'company_id': self.company_id.id,
#                                     'currency_id': self.company_id.currency_id.id,
#                                     'planned_amount':0.0,
#                                     'actual_amount':actual_amount,
#                                     'variance': 0.0,
#                                     'parent_id' :category_id.id,
#                                     'name': prod_loop.id,
#                                     'account_id': loop_line.account_id.id
#                                     }
#                                 act_tot = act_tot + actual_amount
#                                 income_expense_obj.create(categ_vals)
#                                 pr_code = int(pr_code) + 1
#                                 planned_tot = planned_tot + category_id.planned_amount
#                     variance = act_tot - plan
#                     if regular_loop.sign == 'reverse':
#                         variance = -(act_tot - plan)
#                     if regular_loop.sign == 'preserve':
#                         variance = variance
#                     #plan_tot = plan_tot + income_line_parent_id.planned_amount
#                     category_id.write({'actual_amount': act_tot, 'planned_amount':plan, 'variance': variance})
#                 tot = tot + act_tot
#                 if regular_loop.tag == 'grossrevenue':
#                     grossrevenue = tot
#                 if regular_loop.tag == 'expenses':
#                     expenses = tot
#                 if regular_loop.tag == 'costofgoods':
#                     costofgoods = tot
#                 if regular_loop.tag == 'discounts':
#                     discounts = tot
# 
#                 if regular_loop.tag == 'depreciation':
#                     depreciation = tot
# 
#             #tot = tot + act_tot
#                 variance = tot - income_line_parent_id.planned_amount
#                 if regular_loop.sign == 'reverse':
#                     variance = -variance
#                 if regular_loop.sign == 'preserve':
#                     variance = variance
#                 income_line_parent_id.write({'actual_amount': tot, 'variance': variance})
# 
#         for view_loop in view_hierarchy:
#             tot = 0.0
#             self.env.cr.execute("SELECT sum(planned_amount) FROM budget_category_lines WHERE company_id = %s and state = 'confirm' and budget_scenario ='budget' and product_category = %s and date_from >= %s and date_to <= %s", (str(self.company_id.id),str(view_loop.category_id.id),str(startdate),str(enddate)))
#             planned = self.env.cr.fetchone()
#             plan = 0.0
#             if planned[0]:
#                 plan = planned[0]
#             else:
#                 plan = 0.0
#             if view_loop.include:
#                 vals = {
#                     'type': view_loop.category_id.name,
#                     'type_seq': view_loop.sequence,
#                     'company_id': self.company_id.id,
#                     'currency_id': self.company_id.currency_id.id,
#                     'planned_amount':plan,
#                     'actual_amount':0.0,
#                     'variance': 0.0,
#                     }
#             income_line_parent_id = income_expense_obj.create(vals)
#             act_parent_tot = 0.0
#             
#             #prod_sr = product_obj.search([('categ_id', '=', hierarchy_line_loop.category_id.id)])
# 
# 
#             if view_loop.tag == 'costofgoods':
#                 if view_loop.hierarchy_line:
#                     for loop in view_loop.hierarchy_line:
#                         prod_sr = product_obj.search([('categ_id', '=', loop.category_id.id)])
#                         if prod_sr:
#                             actual_amount = 0.0
#                             for prod_loop in prod_sr:
#                                 if loop.type == 'revenue':
#                                     account = loop.category_id.property_account_income_categ_id.id
#                                 if loop.type == 'expense':
#                                     account = loop.category_id.property_account_expense_categ_id.id
#                                 move_line_sr = move_line_obj.search([('date', '>=', startdate),('date', '<=', enddate),
#                                     ('product_id', '=', prod_loop.id),
#                                     ('company_id', '=', self.company_id.id),
#                                     ('account_id', '=', account)])
#                                 for loop_line in move_line_sr:
#                                     if loop_line:
#                                         if view_loop.type == 'revenue':
#                                             actual_amount = actual_amount + loop_line.credit
#                                         if view_loop.type == 'expense':
#                                             actual_amount = actual_amount + loop_line.debit
#                                     if actual_amount != 0.0:
#                                         categ_vals = {
#                                             'type':prod_loop.name,
#                                             'type_seq': pr_code,
#                                             'company_id': self.company_id.id,
#                                             'currency_id': self.company_id.currency_id.id,
#                                             'planned_amount':0.0,
#                                             'actual_amount':actual_amount,
#                                             'variance': 0.0,
#                                             'parent_id' :category_id.id,
#                                             'name': prod_loop.id,
#                                             }
#                                     costofgoods = actual_amount
#                             variance = costofgoods - income_line_parent_id.planned_amount
#                             if view_loop.sign == 'reverse':
#                                 variance = -variance
#                             if view_loop.sign == 'preserve':
#                                 variance = variance 
#                             income_line_parent_id.write({'actual_amount': costofgoods, 'variance': variance})
# 
# 
#             if view_loop.tag == 'discounts':
#                 prod_sr = product_obj.search([('categ_id', '=', view_loop.category_id.id)])
#                 actual_amount = 0.0
#                 if prod_sr:
#                     for prod_loop in prod_sr:
#                         if view_loop.type == 'revenue':
#                             account = view_loop.category_id.property_account_income_categ_id.id
#                         if view_loop.type == 'expense':
#                             account = view_loop.category_id.property_account_expense_categ_id.id
#                         move_line_sr = move_line_obj.search([('date', '>=', startdate),('date', '<=', enddate),
#                             ('product_id', '=', prod_loop.id),
#                             ('company_id', '=', self.company_id.id),
#                             ('account_id', '=', account)])
#                         for loop_line in move_line_sr:
#                             if loop_line:
#                                 if view_loop.type == 'revenue':
#                                     actual_amount = actual_amount + loop_line.credit
#                                 if view_loop.type == 'expense':
#                                     actual_amount = actual_amount + loop_line.debit
#                         discounts = actual_amount
#                         variance = actual_amount - income_line_parent_id.planned_amount
#                         if view_loop.sign == 'reverse':
#                             variance = -variance
#                         if view_loop.sign == 'preserve':
#                             variance = variance 
#                         income_line_parent_id.write({'actual_amount': actual_amount, 'variance':variance}) 
# 
# 
#             if view_loop.tag == 'depreciation':
#                 prod_sr = product_obj.search([('categ_id', '=', view_loop.category_id.id)])
#                 actual_amount = 0.0
#                 if prod_sr:
#                     for prod_loop in prod_sr:
#                         if view_loop.type == 'revenue':
#                             account = view_loop.category_id.property_account_income_categ_id.id
#                         if view_loop.type == 'expense':
#                             account = view_loop.category_id.property_account_expense_categ_id.id
#                         move_line_sr = move_line_obj.search([('date', '>=', startdate),('date', '<=', enddate),
#                             ('product_id', '=', prod_loop.id),
#                             ('company_id', '=', self.company_id.id),
#                             ('account_id', '=', account)])
#                         for loop_line in move_line_sr:
#                             if loop_line:
#                                 if view_loop.type == 'revenue':
#                                     actual_amount = actual_amount + loop_line.credit
#                                 if view_loop.type == 'expense':
#                                     actual_amount = actual_amount + loop_line.debit
#                         depreciation = actual_amount
#                         variance = depreciation - income_line_parent_id.planned_amount
# 
#                         if view_loop.sign == 'reverse':
#                             variance = -variance
#                         if view_loop.sign == 'preserve':
#                             variance = variance   
#                         income_line_parent_id.write({'actual_amount': depreciation, 'variance': variance})
# 
# 
#             if view_loop.tag == 'netrevenue':
#                 netrevenue = grossrevenue - discounts
#                 variance = netrevenue - income_line_parent_id.planned_amount
#                 if view_loop.sign == 'reverse':
#                     variance = -variance
#                 if view_loop.sign == 'preserve':
#                     variance = variance 
#                 income_line_parent_id.write({'actual_amount': netrevenue, 'variance': variance})
# 
#      
#             # For grossmargin
# 
#             if view_loop.tag == 'grossmargin':
#                 grossmargin = netrevenue - costofgoods
#                 variance = grossmargin - income_line_parent_id.planned_amount
#                 if view_loop.sign == 'reverse':
#                     variance = -variance
#                 if view_loop.sign == 'preserve':
#                     variance = variance 
#                 income_line_parent_id.write({'actual_amount': grossmargin, 'variance': variance})
# 
#             #For EBITDA
# 
#             if view_loop.tag == 'EBITDA':
#                 EBITDA = netrevenue - (costofgoods + expenses)
#                 variance = EBITDA - income_line_parent_id.planned_amount
#                 if view_loop.sign == 'reverse':
#                     variance = -variance
#                 if view_loop.sign == 'preserve':
#                     variance = variance 
#                 income_line_parent_id.write({'actual_amount': EBITDA, 'variance': variance})
#         return {
#                 'type': 'ir.actions.act_window',
#                 'name': ('Income Expense Detail'),
#                 'res_model': 'income.expense.details',
#                 'res_id': False,
#                 'domain':[('parent_id','=',False)],
#                 'view_type': 'tree',
#                 'view_mode': 'tree',
#                 'view_id': view_id,
#                 'target': 'current',
#                 'nodestroy': True,
#         }       
        
    @api.multi
    def open_income_expense(self):
        context = self._context
        if context is None:
            context = {}
        move_line_obj = self.env['account.move.line']
        income_expense_obj = self.env['income.expense.details']
        income_sr = income_expense_obj.search([])
        income_sr.unlink()
        view_id =  self.env.ref('vitalpet_budgeting_product_category.view_budget_tree_view').id
        hierarchy_obj = self.env['income.expense.hierarchy']
        product_obj = self.env['product.product']
        hierarchy_obj = hierarchy_obj.search([('include', '=', True)])
        if not self.custom_calendar:
            if self.fiscalyear_start_month:
                _,num_days = monthrange(int(self.fiscal_year), int(self.fiscalyear_start_month))

                first_day = datetime.date(int(self.fiscal_year), int(self.fiscalyear_start_month), 1)
                startdate = first_day.strftime('%Y-%m-%d')

                
            if self.fiscalyear_end_month:
                _,num_days = monthrange(int(self.fiscal_year), int(self.fiscalyear_start_month))

                last_day = datetime.date(int(self.fiscal_year), int(self.fiscalyear_start_month), num_days)
                enddate = last_day.strftime('%Y-%m-%d')
        else:
            startdate = self.period_from.date_start
            enddate = self.period_to.date_end
            
        for regular_loop in hierarchy_obj:
            tot = 0.0
            sub_tot = 0.0
            add_tot = 0.0
            if self.custom_calendar:
                self.env.cr.execute("SELECT sum(planned_amount) FROM budget_category_lines WHERE company_id = %s and state='confirm' and budget_scenario ='budget' and product_category = %s and date_from >= %s and date_to <= %s and type = %s", (str(self.company_id.id),str(regular_loop.category_id.id),str(startdate),str(enddate),str(regular_loop.type)))
            else:
                self.env.cr.execute("SELECT sum(planned_amount) FROM budget_category_lines WHERE company_id = %s and state='confirm' and budget_scenario ='budget' and product_category = %s and date_from >= %s and date_to <= %s and type = %s", (str(self.company_id.id),str(regular_loop.category_id.id),str(startdate),str(enddate),str(regular_loop.type)))
            planned = self.env.cr.fetchone()
            plan = 0.0
            if planned[0]:
                plan = planned[0]
            else:
                plan = 0.0
            if regular_loop.include:
                vals = {
                    'type': regular_loop.category_id.name,
                    'type_seq': regular_loop.sequence,
                    'company_id': self.company_id.id,
                    'currency_id': self.company_id.currency_id.id,
                    'planned_amount':plan,
                    'actual_amount':0.0,
                    'variance': 0.0,
                    }
            income_line_parent_id = income_expense_obj.create(vals)
            for hierarchy_line_loop in regular_loop.hierarchy_line:                
                
                self.env.cr.execute("SELECT sum(planned_amount) FROM budget_category_lines WHERE company_id = %s and state='confirm' and budget_scenario ='budget' and product_category = %s and date_from >= %s and date_to <= %s and type = %s", (str(self.company_id.id),str(hierarchy_line_loop.category_id.id),str(startdate),str(enddate),str(hierarchy_line_loop.type)))
                planned = self.env.cr.fetchone()
                plan = 0.0
                if planned[0]:
                    plan = planned[0]
                else:
                    plan = 0.0
                prod_sr = product_obj.search([('categ_id', '=', hierarchy_line_loop.category_id.id)])
                if hierarchy_line_loop.include == True:
                    categ_vals = {
                        'type':hierarchy_line_loop.category_id.name,
                        'type_seq': hierarchy_line_loop.sequence,
                        'company_id': self.company_id.id,
                        'currency_id': self.company_id.currency_id.id,
                        'planned_amount': plan,
                        'actual_amount':0.0,
                        'variance': 0.0,
                        'parent_id' :income_line_parent_id.id,
                        }
                if hierarchy_line_loop.include == True:
                    category_id = income_expense_obj.create(categ_vals)
                pr_code = str(hierarchy_line_loop.sequence) + "001"
                act_tot = 0.0
                planned_tot = 0.0
                for prod_loop in prod_sr:
                    actual_amount = actual_credit = actual_debit = 0.0
                    if prod_loop.id:

                        # print hierarchy_line_loop.category_id.property_account_income_categ_id.company_id.name,'---',hierarchy_line_loop.category_id.property_account_expense_categ_id.company_id.name
                        # if hierarchy_line_loop.type == 'revenue':
                        #     account = hierarchy_line_loop.category_id.property_account_income_categ_id.id
                        # if hierarchy_line_loop.type == 'expense':
                        #     account = hierarchy_line_loop.category_id.property_account_expense_categ_id.id

                        account = False

                        if hierarchy_line_loop.type == 'revenue':                                    
                                                                                                
                            ir_parameter = self.env['ir.property'].search([('company_id', '=', self.company_id.id),
                                                                            ('name', '=', 'property_account_income_categ_id'),
                                                                           ('res_id', '=', 'product.category,' + str(hierarchy_line_loop.category_id.id))])
                            if ir_parameter.value_reference:
                                ref_account_id = (ir_parameter.value_reference).split(',')[1]
                                account_id = self.env['account.account'].search([('id', '=', ref_account_id)])
                                if account_id:
                                    account = account_id.id
        
                        if hierarchy_line_loop.type == 'expense':                                
                                                                                                
                            ir_parameter = self.env['ir.property'].search([('company_id', '=', self.company_id.id),
                                                                            ('name', '=', 'property_account_expense_categ_id'),
                                                                           ('res_id', '=', 'product.category,' + str(hierarchy_line_loop.category_id.id))])
                            if ir_parameter.value_reference:
                                ref_account_id = (ir_parameter.value_reference).split(',')[1]
                                account_id = self.env['account.account'].search([('id', '=', ref_account_id)])
                                if account_id:
                                    account = account_id.id

                        
                        move_line_sr = move_line_obj.search([('date', '>=', startdate),('date', '<=', enddate),
                        ('product_id', '=', prod_loop.id),
                        ('company_id', '=', self.company_id.id),('account_id','=',account)])
                        for loop_line in move_line_sr:
                            actual_credit = actual_credit + loop_line.credit
                            actual_debit = actual_debit + loop_line.debit
                        
                        if hierarchy_line_loop.type == 'revenue':
                            actual_amount = actual_credit - actual_debit
                        if hierarchy_line_loop.type == 'expense':
                            actual_amount = actual_debit - actual_credit
                        if move_line_sr:
                            if hierarchy_line_loop.include == True:
                                categ_vals = {
                                    'type':prod_loop.name,
                                    'type_seq': pr_code,
                                    'company_id': self.company_id.id,
                                    'currency_id': self.company_id.currency_id.id,
                                    'planned_amount':0.0,
                                    'actual_amount':actual_amount,
                                    'variance': 0.0,
                                    'parent_id' :category_id.id,
                                    'name': prod_loop.id,
                                    'account_id': loop_line.account_id.id,
                                    'date_from' : startdate,
                                    'date_to' : enddate,
                                    }
                                act_tot = act_tot + actual_amount
                                
                                income_expense_obj.create(categ_vals)
                                pr_code = int(pr_code) + 1
                                planned_tot = planned_tot + category_id.planned_amount
                variance = act_tot - plan
                if regular_loop.sign == 'reverse':
                    variance = -(act_tot - plan)
                if regular_loop.sign == 'preserve':
                    variance = variance
                #plan_tot = plan_tot + income_line_parent_id.planned_amount
                if hierarchy_line_loop.include == True:
                    category_id.write({'actual_amount': act_tot, 'planned_amount':plan, 'variance': variance})
                
                
                
                actual = 0.00
                
                if prod_sr:
                    actual = act_tot
                else:
                    self.env.cr.execute("SELECT sum(actual_amount) FROM budget_category_lines WHERE company_id = %s and state='confirm' and budget_scenario ='budget' and product_category = %s and date_from >= %s and date_to <= %s", (str(self.company_id.id),str(hierarchy_line_loop.category_id.id),str(startdate),str(enddate)))
                    actual = self.env.cr.fetchone()[0]
                    if not actual:
                        actual=0.00
                if hierarchy_line_loop.subtract == True:
                    sub_tot = sub_tot + actual
                else:
                    add_tot = add_tot + actual
                tot = add_tot - sub_tot      
                variance = tot - income_line_parent_id.planned_amount
                if regular_loop.sign == 'reverse':
                    variance = -variance
                if regular_loop.sign == 'preserve':
                    variance = variance
                income_line_parent_id.write({'actual_amount': tot, 'variance': variance})

        
        return {
                'type': 'ir.actions.act_window',
                'name': ('Income Expense Detail'),
                'res_model': 'income.expense.details',
                'res_id': False,
                'domain':[('parent_id','=',False)],
                'view_type': 'tree',
                'view_mode': 'tree',
                'view_id': view_id,
                'target': 'current',
                'nodestroy': True,
        }
        