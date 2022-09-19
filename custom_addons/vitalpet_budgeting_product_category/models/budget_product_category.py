# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import babel.dates
from odoo import api, fields, models, _
from odoo.tools import ustr
from odoo.exceptions import UserError, ValidationError
import time
import datetime
from datetime import date
from datetime import timedelta
from dateutil.relativedelta import relativedelta
import re
from odoo.workflow.instance import _update_end
from calendar import monthrange

import logging
_logger = logging.getLogger(__name__)

def strToDate(dt):
    dt_date = date(int(dt[0 :4]), int(dt[5 :7]), int(dt[8 :10]))
    return dt_date



class IncomeExpenseDetails(models.Model):
    _name = "income.expense.details"
    _order = 'type_seq'

    @api.multi
    @api.depends('parent_id')
    def _get_level(self):
        '''Returns a dictionary with key=the ID of a record and value = the level of this
           record in the tree structure.'''
        for report in self:
            level = 0
            if report.parent_id:
                level = 1
            report.level = level


    name = fields.Many2one('product.product', string='Product')
    parent_id = fields.Many2one("income.expense.details","Income ID")
    account_fiscal_periods_id = fields.Many2one('account.fiscal.period.lines', string="Account Fiscal Period")
    child_ids = fields.One2many("income.expense.details","parent_id",string="Income IDS",select=True)
    product_category = fields.Char("Category")
    category_id = fields.Many2one('product.category', string='Product Category')
    planned_amount = fields.Float('Planned Amount', digits=0)
    actual_amount = fields.Float('Actual Amount', digits=0)
    variance = fields.Float('Variance', digits=0)
    level = fields.Integer(compute='_get_level', string='Level')
    currency_id = fields.Many2one('res.currency', string="Currency")
    company_id = fields.Many2one("res.company",string="Company")
    type_seq = fields.Char("Sequence", select=1)
    type = fields.Char(string="Type")
    categ_type= fields.Char("")
    product_id = fields.Many2one('product.product')
    account_id = fields.Many2one('account.account', 'Account')
    date_from = fields.Date('Start Date', required=False)
    date_to = fields.Date('End Date', required=False)


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    product_id = fields.Many2one('product.product', string='Product')
    category_id = fields.Many2one('product.category', related='product_id.categ_id', string="Product Category")
    state = fields.Selection(related='move_id.state', string="State", store=True)

    @api.model
    def search_read(self, domain=None, fields=None, offset=0,limit=None, order=None):
        context = self.env.context
        move_lst = []
        if str(self)[:17] == 'account.move.line':
            res = super(AccountMoveLine, self).search_read(domain, fields, offset, limit, order)

        if context.has_key("active_model"):
            if context['active_model'] == 'income.expense.details':
                income_obj = self.env['income.expense.details']
                move_obj = self.env['account.move.line']
                income_br = income_obj.browse(context['active_id'])
                move_sr = move_obj.search([('account_id','=',income_br.account_id.id),('product_id', '=', income_br.name.id),('date', '>=', income_br.date_from),('date', '<=', income_br.date_to),('company_id', '=', income_br.company_id.id)])
                for loop in move_sr:
                    move_lst.append(loop.id)
                domain = [['id', 'in', move_lst]]
                res = super(AccountMoveLine, self).search_read(domain, fields, offset, limit, order)

        return res



class BudgetProductCategory(models.Model):
    _name = "budget.product.category"
    _description = "Budget Product Category"
    _inherit = ['mail.thread']

    @api.model
    def create(self, vals):
        company_code = self.env["res.company"].search([('id','=',vals.get("company_id"))]).code
        fiscal_yr=self.env["account.fiscal.periods"].search([('id', '=', vals.get("account_fiscal_period_id"))]).name
        budget_vr = self.env["budget.version"].search([('id', '=', vals.get("budget_version"))]).name
        scenario = vals.get("budget_scenario").title()
        if fiscal_yr:
            vals["name"] = "["+company_code+"]"+" "+fiscal_yr+" "+scenario+" "+budget_vr
        elif vals["fiscal_period"]:
            vals["name"] = "["+company_code+"]"+" "+vals["fiscal_period"]+" "+scenario+" "+budget_vr
        return super(BudgetProductCategory,self).create(vals)

    name = fields.Char('Budget Name', states={'done': [('readonly', True)]})
    creating_user_id = fields.Many2one('res.users', 'Responsible', default=lambda self: self.env.user)
    budget_category_line = fields.One2many('budget.category.lines', 'budget_category_id', 'Budget Lines',
        states={'done': [('readonly', True)]}, copy=True)
    company_id = fields.Many2one('res.company', 'Company', required=True,
        default=lambda self: self.env['res.company']._company_default_get('budget.product.category'))
    custom_calendar = fields.Boolean(related='company_id.custom_calendar', string='Custom Calendar')
    parent_budget_code = fields.Char("Budget Code")
    budget_version = fields.Many2one("budget.version", "Version")
    account_fiscal_period_id = fields.Many2one('account.fiscal.periods', string="Fiscal Year", ondelete="restrict")
    fiscal_period = fields.Char(string="Fiscal Year")

    state = fields.Selection([
        ('draft', 'Draft'),
        ('cancel', 'Cancelled'),
        ('confirm', 'Active'),
        ('validate', 'Validated'),
        ('done', 'Done')
        ], 'Status', default='draft', index=True, required=True, readonly=True, copy=False, track_visibility='always')
    
    budget_scenario = fields.Selection([
        ('minimum', 'Minimum'),
        ('budget', 'Budget'),
        ('stretch', 'Stretch'),
    ],default='budget', string='Scenario', track_visibility='always', help="You may load up to three budgets per practice. Minimum, Budget, or Stretch, Some user may choose only to have one budget")


    @api.multi
    def action_budget_confirm(self):
        budget_lines=self.env['budget.product.category'].search([('account_fiscal_period_id', '=', self.account_fiscal_period_id.id),
                                                    ('budget_scenario', '=', self.budget_scenario),
                                                    ('budget_version', '!=', self.budget_version.id),
                                                    ('company_id', '=', self.company_id.id),
                                                                ])
        for budget in budget_lines:
            budget.state='draft'
        self.write({'state': 'confirm'})



    @api.multi
    def action_budget_draft(self):
        self.write({'state': 'draft'})

    @api.multi
    def action_budget_validate(self):
        self.write({'state': 'validate'})

    @api.multi
    def action_budget_cancel(self):
        self.write({'state': 'cancel'})

    @api.multi
    def action_budget_done(self):
        self.write({'state': 'done'})


class BudgetVersion(models.Model):
    _name = "budget.version"

    name = fields.Char("Budget Version")


class BudgetProductCategoryLines(models.Model):
    _name = "budget.category.lines"
    _description = "Budget Product Category Line"
    _order = 'sequence'


    @api.multi
    def validate_budget_lines(self,budget=None):
        if budget==1:                                                
            action_rec = self.env['ir.model.data'].xmlid_to_object('vitalpet_budgeting_product_category.action_budget_category_quarterly')
        elif budget==2:
            action_rec = self.env['ir.model.data'].xmlid_to_object('vitalpet_budgeting_product_category.action_budget_category_yearly')
        else:
            action_rec = self.env['ir.model.data'].xmlid_to_object('vitalpet_budgeting_product_category.act_budget_category_quarter_view_dashboard')
        if action_rec:
            return action_rec.id
        

    def budget_calc(self, year, month, company):
        
#         scenario = ['budget', 'minimum', 'stretch']  
        if year>=2018:
            scenario = ['budget']        
            product_obj = self.env['product.product']
            crossovered_budget_obj = self.env['budget.category.lines']
            move_line_obj = self.env['account.move.line']

            for company_list in company:
                company_loop=self.env['res.company'].search([('id','=',company_list)])
                
                
                lst = ['grossrevenue', 'discounts', 'netrevenue', 'costofgoods', 'grossmargin', 'EXP', 'EBITDA', 'depreciation']
                res = {}
                actual = {}
                s = str('M' + str(int(month)) + '-' + str(year))
                s_month = str('M0' + str(int(month)) + '-' + str(year))
                fiscal = self.env['account.fiscal.period.lines'].search([('name', 'in', [s,s_month]),('account_fiscal_period_id.calendar_type','=',company_loop.calendar_type.id)])

                if fiscal:
                    to_date = strToDate(fiscal.date_end)
                    mid_date = to_date - timedelta(days=15)
                    year = mid_date.year
                    month = mid_date.month
                    quarter = (mid_date.month - 1) // 3 + 1
                    year_month = str(mid_date.year) + str("-") + str('%02d' % mid_date.month)
                    year_quarter = str(mid_date.year) + str("-") + str('%02d' % quarter)
                    startdate = strToDate(fiscal.date_start)
                    enddate = strToDate(fiscal.date_end)

                else:
                    _,num_days = monthrange(int(year), int(month))
                    first_day = datetime.date(int(year), int(month), 1)
                    startdate = first_day.strftime('%Y-%m-%d')            
                    _,num_days = monthrange(int(year), int(month))
                    last_day = datetime.date(int(year), int(month), num_days)
                    enddate = last_day.strftime('%Y-%m-%d')
                
                _logger.info((company_loop.code,s,s_month,'----'))
                
                for type_loop in scenario:                
                    sr_revenue_calc = crossovered_budget_obj.search(
                        [('month', 'in', [s,s_month]), ('calc_tag', '!=', False), ('company_id', '=', company_loop.id),('budget_scenario', '=', type_loop)])

                    sr_revenue = crossovered_budget_obj.search(
                        [('month', 'in', [s,s_month]), ('calc_tag', '=', False),('company_id', '=', company_loop.id), ('budget_scenario', '=', type_loop)])

                    prod_lst = []
                    grossrevenue = 0.0
                    expenses = 0.0
                    discounts = 0.0
                    costofgoods = 0.0
                    grossmargin = 0.0
                    netrevenue = 0.0
                    depreciation = 0.0
                    EXP = 0.0
                    EBITDA = 0.0
                    actual=0.0
                    if sr_revenue:
                        for loop in sr_revenue:
                            _logger.info((s_month,loop.name,'----'))
                            actual_amount = 0.00     
                            account=0                                    
                            if loop.type == 'revenue':                                    
                                                                                                    
                                ir_parameter = self.env['ir.property'].search([('company_id', '=', company_list),
                                                                                ('name', '=', 'property_account_income_categ_id'),
                                                                               ('res_id', '=', 'product.category,' + str(loop.product_category.id))])
                                if ir_parameter.value_reference:
                                    ref_account_id = (ir_parameter.value_reference).split(',')[1]
                                    account_id = self.env['account.account'].search([('id', '=', ref_account_id)])
                                    if account_id:
                                        account = account_id.id
            
                            if loop.type == 'expense':                                
                                                                                                    
                                ir_parameter = self.env['ir.property'].search([('company_id', '=', company_list),
                                                                                ('name', '=', 'property_account_expense_categ_id'),
                                                                               ('res_id', '=', 'product.category,' + str(loop.product_category.id))])
                                if ir_parameter.value_reference:
                                    ref_account_id = (ir_parameter.value_reference).split(',')[1]
                                    account_id = self.env['account.account'].search([('id', '=', ref_account_id)])
                                    if account_id:
                                        account = account_id.id
                            

                            move_line_sr = move_line_obj.search([('date', '>=', startdate),('date', '<=', enddate),
                                                                 ('company_id', '=', company_loop.id),
                                                                 ('account_id', '=', account),
                                                                 ('product_id.categ_id', '=', loop.product_category.id)])

                            for loop_line in move_line_sr:
                                if loop.type == 'revenue':
                                    actual_amount +=loop_line.credit
                                    actual_amount -=loop_line.debit
                                if loop.type == 'expense':
                                    actual_amount +=loop_line.debit
                                    actual_amount -=loop_line.credit
                            loop.write({'actual_amount': actual_amount, 'variance': actual_amount - loop.planned_amount,'growth_ly':((actual_amount-loop.actuals_previous_year)/loop.actuals_previous_year)*100 if loop.actuals_previous_year != 0 else 0.00})
                            loop._get_var_amount()
                            update_other_budgets = crossovered_budget_obj.search(
                                    [('month', 'in', [s,s_month]), 
                                     ('calc_tag', '=', False),
                                     ('company_id', '=', company_loop.id), 
                                     ('budget_scenario', '!=', type_loop), 
                                     ('type', '=', loop.type), 
                                     ('product_category', '=', loop.product_category.id)])
                            if update_other_budgets:
                                for update_budget in update_other_budgets:
                                    update_budget.write({'actual_amount': actual_amount, 'variance': actual_amount - update_budget.planned_amount})
                                    update_budget._get_var_amount()

                    if sr_revenue_calc:
                        for loop_parent in sr_revenue_calc:   
                            _logger.info((s_month,loop_parent.name,'----'))

                            total_val = total_dec = 0.0
                            if loop_parent.calc_tag:
                                for tags_list_split in loop_parent.calc_tag.split(','):
                                    for rows in crossovered_budget_obj.search([('budget_scenario','=',type_loop),
                                                                               ('company_id','=',company_loop.id),
                                                                               ('month', 'in', [s,s_month]),
                                                                               ('tag', '=', tags_list_split),
                                                                               ('budget_category_id.state','=','confirm'),
                                                                               ]):
                                        total_val+=rows.actual_amount
                            if loop_parent.calc_tag_offset:
                                for tags_list_split in loop_parent.calc_tag_offset.split(','):
                                    for rows in crossovered_budget_obj.search([('budget_scenario','=',type_loop),
                                                                               ('company_id','=',company_loop.id),
                                                                               ('month', 'in', [s,s_month]),
                                                                               ('tag', '=', tags_list_split),
                                                                               ('budget_category_id.state','=','confirm'),
                                                                               ]):
                                        total_dec+=rows.actual_amount
                                
                            act_value= total_val-total_dec

                            loop_parent.write({'actual_amount': act_value, 'variance': act_value - loop_parent.planned_amount,'growth_ly':((act_value-loop_parent.actuals_previous_year)/loop_parent.actuals_previous_year)*100 if loop_parent.actuals_previous_year != 0 else 0.00})
                            loop_parent._get_var_amount()
                            update_other_budgets = crossovered_budget_obj.search(
                                    [('month', 'in', [s,s_month]), 
                                     ('calc_tag', '!=', False),
                                     ('company_id', '=', company_loop.id), 
                                     ('budget_scenario', '!=', type_loop), 
                                     ('type', '=', loop_parent.type), 
                                     ('product_category', '=', loop_parent.product_category.id)])
                            
                            if update_other_budgets:
                                for update_budget in update_other_budgets:
                                    update_budget.write({'actual_amount': act_value, 'variance': act_value - update_budget.planned_amount})
                                    update_budget._get_var_amount() 
                    
                    if sr_revenue:
                        for names in ["Dietary","Laboratory"]:
                            expense_pln = revenue_pln = expense_act = revenue_act = 0
                            for lines in sr_revenue:
                                if lines.name == names:
                                    if lines.type == "revenue":
                                        revenue_act += lines.actual_amount
                                        revenue_pln += lines.planned_amount
                                    if lines.type == "expense":
                                        expense_act += lines.actual_amount
                                        expense_pln += lines.planned_amount
                            if revenue_act != 0:
                                total_act = ((revenue_act-expense_act)/revenue_act) *100
                            else:
                                total_act = 0
                            if revenue_pln != 0:
                                total_pln = ((revenue_pln-expense_pln)/revenue_pln) *100
                            else:
                                total_pln = 0
                            if total_pln != 0:
                                total_margin = ((total_act-total_pln)/total_pln) *100
                            else:
                                total_margin = 0

                            for lines in sr_revenue:
                                if lines.name == names:
                                    lines.actual_margin = total_act
                                    lines.plan_margin = total_pln
                                    lines.var_margin = total_margin
        return True

    @api.multi
    def _get_var_amount(self):
        formulas = self.env['budget.formula'].search([])
        VAR_INC = VAR_REV = VAR_EXP = PLAN_PCT_NR = ACT_PCT_NR = YOY = PLAN_MARGIN_C = ACTUAL_MARGIN_C = VAR_MGN = ""
        for formula in formulas:
            if formula.name=='VAR' and formula.budget_type=='all':
                VAR_INC=VAR_REV=VAR_EXP=formula.formula_single
            elif formula.name=='VAR' and formula.budget_type=='income':
                VAR_INC = formula.formula_single
            elif formula.name=='VAR' and formula.budget_type=='revenue':
                VAR_REV = formula.formula_single
            elif formula.name=='VAR' and formula.budget_type=='expense':
                VAR_EXP = formula.formula_single

            elif formula.name=='PLAN_PCT_NR':
                PLAN_PCT_NR=formula.formula_single
            elif formula.name=='ACT_PCT_NR':
                ACT_PCT_NR=formula.formula_single
            elif formula.name=='YOY':
                YOY=formula.formula_single
            elif formula.name=='PLAN_MARGIN':
                PLAN_MARGIN_C=formula.formula_single
            elif formula.name=='ACTUAL_MARGIN':
                ACTUAL_MARGIN_C=formula.formula_single
            elif formula.name=='VAR_MGN':
                VAR_MGN=formula.formula_single

        for lines in self:
            ACTUAL=float(lines.actual_amount)
            PLAN=float(lines.planned_amount)
            ACTUAL_NET=0.00
            PLAN_NET=0.00
            actual_net_cal=self.env['budget.category.lines'].search([('name','=','Net Revenue'),('account_fiscal_periods_id','=',lines.account_fiscal_periods_id.id),('company_id','=',lines.company_id.id),('month','=',lines.month),('budget_scenario','=',lines.budget_scenario)],limit=1)
            if actual_net_cal:
                if actual_net_cal.actual_amount:
                    ACTUAL_NET=float(actual_net_cal.actual_amount)
                if actual_net_cal.planned_amount:
                    PLAN_NET=float(actual_net_cal.planned_amount)
                
            ACTUAL_LAST=float(lines.actuals_previous_year)
            plan_offset=float(lines.plan_offset)
            actual_offset=float(lines.actuals_offset)
                
            if lines.type=='income':
                try:
                    lines.var_amount = eval(VAR_INC)
                except:
                    lines.var_amount = 0
            elif lines.type=='revenue':
                try:
                    lines.var_amount = eval(VAR_REV)
                except:
                    lines.var_amount = 0
            elif lines.type=='expense':
                try:
                    lines.var_amount = eval(VAR_EXP)
                except:
                    lines.var_amount = 0
            else:
                    lines.var_amount = 0
            
            
              
            try:
                lines.plan_margin = eval(PLAN_MARGIN_C)
            except:
                lines.plan_margin = 0
            try:
                lines.actual_margin = eval(ACTUAL_MARGIN_C)
            except:
                lines.actual_margin = 0
            PLAN_MARGIN=lines.plan_margin
            ACTUAL_MARGIN=lines.actual_margin
            try:
                lines.var_margin = eval(VAR_MGN)
            except:
                lines.var_margin = 0

            try:
                lines.plan_pct_nr = eval(PLAN_PCT_NR)
            except:
                lines.plan_pct_nr = 0

            try:
                lines.act_pct_nr = eval(ACT_PCT_NR)
            except:
                lines.act_pct_nr = 0

            try:
                lines.yoy = eval(YOY)
            except:
                lines.yoy = 0
            
    def _search_upper(self, operator, value):
        if operator == 'like':
            operator = 'ilike'
        return [('id', 'in',  [312,2])]

    @api.depends('planned_amount')
    def _compute_upper(self):
        for record in self:
            record.upper_name = "test"
    
    
    @api.depends('actual_amount')
    def _get_company_last_actual(self):        
        for line in self:
            actual_net_cal=self.env['budget.category.lines'].search([
                    ('product_category','=',line.product_category.id),
                    ('type','=',line.type),
                    ('company_id','=',line.company_id.id),
                    ('company_month','=',[x.strip() for x in line.company_month.split('-')][0]+'-'+str(int(line.fin_yr)-1)),
                    ('fin_yr','=',str(int(line.fin_yr)-1)),
                    ('budget_scenario','=',line.budget_scenario)
                    ])
            if actual_net_cal:
                line.actuals_previous_year=actual_net_cal.actual_amount
                
        
    @api.depends('budget_category_id','month')
    def _get_company_period(self):
        for line in self:
            if line.month:
                year_list = []
                month_list = re.split('-',line.month) 
                       
                quarter = ''      
                if month_list[0] in ('M1', 'M2','M3','M01', 'M02','M03'):
                    quarter = 'Q1'
                elif month_list[0] in ('M4', 'M5','M6','M04', 'M05','M06'):
                    quarter = 'Q2'
                elif month_list[0] in ('M7', 'M8','M9','M07', 'M08','M09'):
                    quarter = 'Q3'
                elif month_list[0] in ('M10', 'M11','M12'):
                    quarter = 'Q4'
                    
                code = line.budget_category_id.company_id.code
                year = month_list[1]
                month = month_list
                budget_name = line.budget_category_id.budget_scenario.title()
                
        
                if line.month[2]=="-":
                    line.company_month = line.month[:1] + '0' + line.month[1:]
                else:
                    line.company_month = line.month
                
                line.quarter=quarter
                line.fin_yr=str(year)
                line.company_year = str(code) + ' ' + str(year)
                line.company_quarter = str(code) + ' ' + str(year) + '-' + quarter
                line.company_month = str(code) + ' ' +month[0]+'-'+ str(year)
                line.general_budget_id = str(code) + ' ' + str(budget_name)
        
        
    budget_category_id = fields.Many2one('budget.product.category', 'Budget', ondelete='cascade', index=True, required=True)
    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account')
    month = fields.Char('Month', required=True)
    date_from = fields.Date('Start Date', required=False)
    date_to = fields.Date('End Date', required=False)
    paid_date = fields.Date('Paid Date')
    planned_amount = fields.Float('Planned Amount', required=True, digits=0)
    company_id = fields.Many2one(related='budget_category_id.company_id', comodel_name='res.company',
        string='Company', store=True, readonly=True)
    current_company = fields.Many2one('res.company',string="Current company", compute="_compute_current_company", search="_search_current_company")
    current_month = fields.Char(string="Current month", compute='_compute_current_month', search="_search_current_month")
    last_year_current_month = fields.Char(string="Last Year Current month", compute='_last_year_current_month', search="_search_last_year_current_month")
    name = fields.Char(related='product_category.name', string='Name', store=True)
    general_budget_id = fields.Char(string='Budget Name', compute='_get_company_period')
    account_fiscal_periods_id = fields.Many2one('account.fiscal.period.lines', string="Account Fiscal Period")
    account_fiscal_periods_quarterly = fields.Char(string="Account Fiscal Period Quarterly")
    budget_version = fields.Many2one("budget.version","Version")
    product_category = fields.Many2one("product.category","Category")
    category_name = fields.Char(related='product_category.name', string='Category Name')
    visibility = fields.Boolean("Visibility")
    margin = fields.Boolean("Margin")
    type = fields.Selection([
        ('revenue', 'Revenue'),
        ('income', 'Income'),
        ('expense', 'Expense'),
        ], 'Budget Type', track_visibility='always')
    sequence = fields.Integer("Sequence",index=True)
    tag = fields.Char("Tag")
    calc_tag = fields.Char("Calc Tag")
    calc_tag_offset = fields.Char("Call Tag Offset")
    plan_margin_pct = fields.Char("Plan Margin")
    actual_margin_pct = fields.Char("Actual Margin PCT")
    actual_amount = fields.Float('Actual Amount')
    plan_offset = fields.Char("Plan Offset")
    actuals_offset = fields.Char("Actuals Offset")
    actuals_previous_year = fields.Float("Actuals Previous Year", compute='_get_company_last_actual')
    company_year = fields.Char("Company Year", compute='_get_company_period')
    company_quarter = fields.Char("Company Quarter", compute='_get_company_period')
    company_month = fields.Char("Company Month", compute='_get_company_period', store=True)
    quarter = fields.Char("Quarter")

    state = fields.Selection(related='budget_category_id.state', store=True)
    
    var_amount = fields.Float(String='Var',group_operator="avg")
    plan_margin = fields.Float(String="Plan Margin",group_operator="avg")
    actual_margin = fields.Float(String='Actual Margin',group_operator="avg")
    var_margin = fields.Float(String='Var Margin',group_operator="avg")
    plan_pct_nr = fields.Float(String='Plan NR',group_operator="avg")
    act_pct_nr = fields.Float(String='Actual NR',group_operator="avg")
    yoy = fields.Float(String='YOY')

    parent_id = fields.Many2one("budget.category.lines","Parent")
    fin_yr = fields.Char("Year")
    variance = fields.Float('Variance',digits=0)
    company_id = fields.Many2one(related='budget_category_id.company_id', comodel_name='res.company',
                                 string='Company', store=True, readonly=True)
    status = fields.Selection([
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ], 'Status', track_visibility='always')

    parent_scenario = fields.Selection(related='budget_category_id.budget_scenario',string='Scenario', store=True)
    budget_scenario = fields.Selection(related='budget_category_id.budget_scenario',string='Budget Scenario', store=True)

    upper_name = fields.Char(compute='_compute_upper', search='_search_upper') 
    account_fiscal_period_id = fields.Many2one('account.fiscal.periods', store=True, string="Fiscal Year", related='budget_category_id.account_fiscal_period_id')
    fiscal_period = fields.Char(string="Fiscal Year", related='budget_category_id.fiscal_period', store=True) 
    move_month_year = fields.Char("Fiscal Date", compute = '_convert_move_month_year', store=True)
    company_type = fields.Char("Company and Type", compute = '_company_any_type')
    is_margin = fields.Char("Is Margin", compute = '_is_margin')
    is_visible = fields.Char("Is Visible", compute = '_is_margin')
    
    var_amount_higher = fields.Char("Amount higher", compute = '_compute_var_amount')
    var_margin_higher = fields.Char("Margin higher", compute = '_compute_var_margin')
    var_yoy_higher = fields.Char("Yoy higher", compute = '_compute_var_yoy')
    check_variance_high = fields.Char("Check variance high", compute = '_compute_check_variance')
    growth_ly = fields.Float("Growth LY",group_operator="avg")
    
    
    # def _compute_growth_last_yr(self):
    #     for rec in self.env['budget.category.lines'].search([]):
    #         if rec.actuals_previous_year == 0:
    #             rec.growth_ly = 0.00
    #         else:
    #             rec.growth_ly = ((rec.actual_amount-rec.actuals_previous_year)/rec.actuals_previous_year)*100

    def budget_cron_drop(self):
        query="""DROP TABLE budget_cron_rel;
                 DROP TABLE budget_cron_lines;
                 DROP TABLE budget_cron"""
        self._cr.execute(query)

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        today = date.today()
        lastyear = today.year - 1
        period = []
        year = []
        company = []
        scenario = []
        for loop in domain:
            for in_loop in loop:
                if in_loop == 'current_company':
                    cur_company = self.env.user.company_id.id
                    company.append(cur_company)
                if in_loop == 'budget':
                    scenario.append(in_loop)
                if in_loop == 'minimum':
                    scenario.append(in_loop)
                if in_loop == 'stretch':
                    scenario.append(in_loop)
                if in_loop == 'current_month':
                    period.append('M'+str('%02d' % today.month)+'-'+str(today.year))
                if in_loop == 'last_year_current_month':
                    period.append('M'+str('%02d' % today.month)+'-'+str(lastyear))
                if in_loop == str(today.year):
                    year.append(in_loop)
                if in_loop == str(lastyear):
                    year.append(in_loop)
        ft_domain = [dom_loop for dom_loop in domain if "|" not in dom_loop and "budget_scenario" not in dom_loop
                         and "fin_yr" not in dom_loop and "current_month" not in dom_loop 
                         and "last_year_current_months" not in dom_loop and "current_company" not in dom_loop]
        del domain[:]    
        if period or year or company or scenario:                             
            if period :
                domain.append(['month', 'in', period])
            if year :
                domain.append(['fin_yr', 'in', year])
            if company :
                domain.append(['company_id', 'in', company])
            if scenario :
                domain.append(['budget_scenario', 'in', scenario])    
        else :
            domain = domain
        if not '&' in ft_domain:     
            for add_or in range(0,len(ft_domain)-1):
                domain.append('|')
        domain+=ft_domain

        if "&" in domain:
            domain = [loop for loop in domain if "&" not in loop]

        return super(BudgetProductCategoryLines, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)

            
    @api.multi
    @api.depends('company_id')
    def _compute_current_company(self):
        for recs in self:
            recs.current_company=self.env.user.company_id.id
    @api.multi
    def _compute_current_month(self):
        for recs in self:
            recs.current_month='M'+datetime.datetime.today().strftime('%m')+'-'+datetime.datetime.today().strftime('%Y')
    @api.multi
    def _last_year_current_month(self):
        for recs in self:
            recs.last_year_current_month='M'+datetime.datetime.today().strftime('%m')+'-'+ str(int(datetime.datetime.today().strftime('%Y'))-1)
            
    @api.multi
    def _search_current_company(self, operator, value):
        recs = self.search([('company_id', '=', self.env.user.company_id.id)])  
        return [('id', 'in', [x.id for x in recs])]
    @api.multi
    def _search_current_month(self, operator, value):
        recs = self.search([('month', '=', 'M'+datetime.datetime.today().strftime('%m')+'-'+datetime.datetime.today().strftime('%Y'))])  
        return [('id', 'in', [x.id for x in recs])]
    @api.multi
    def _search_last_year_current_month(self, operator, value):
        recs = self.search([('month', '=', 'M'+datetime.datetime.today().strftime('%m')+'-'+ str(int(datetime.datetime.today().strftime('%Y'))-1))])  
        return [('id', 'in', [x.id for x in recs])]


    @api.multi
    def _company_any_type(self):
        for line in self:
            line.company_type=line.company_id.code+" - "+line.budget_scenario
            
    @api.multi
    def _is_margin(self):
        for line in self:
            if line.visibility==True:
                line.is_visible="Yes"
            else:
                line.is_visible="No"
            if line.margin==True:
                line.is_margin= 1   
#             else:
#                 line.is_margin= ''
        
    @api.multi
    def _compute_var_amount(self):
        for line in self:
            if line.type == "expense":
                if line.plan_pct_nr > line.act_pct_nr:
                    line.var_amount_higher = "#c7d5ff"
                else:
                    line.var_amount_higher = "#ffc7c7"
            else:
                if line.planned_amount > line.actual_amount:
                    line.var_amount_higher = "#ffc7c7"
                else:
                    line.var_amount_higher = "#c7d5ff"

    @api.multi
    def _compute_var_margin(self):
        for line in self:
            if line.type == "expense":
                if line.plan_pct_nr > line.act_pct_nr:
                    line.var_margin_higher = "#c7d5ff"
                else:
                    line.var_margin_higher = "#ffc7c7"
            else:
                if line.plan_margin > line.actual_margin:
                    line.var_margin_higher = "#ffc7c7"
                else:
                    line.var_margin_higher = "#c7d5ff"

    @api.multi
    def _compute_var_yoy(self):
        for line in self:
            if line.type == "expense":
                if line.plan_pct_nr > line.act_pct_nr:
                    line.var_yoy_higher = "#c7d5ff"
                else:
                    line.var_yoy_higher = "#ffc7c7"
            else:
                if line.plan_pct_nr > line.act_pct_nr:
                    line.var_yoy_higher = "#ffc7c7"
                else:
                    line.var_yoy_higher = "#c7d5ff"

    @api.multi
    def _compute_check_variance(self):
        for line in self:
            if line.type == "expense":
                if line.plan_pct_nr > line.act_pct_nr:
                    line.check_variance_high = "#c7d5ff"
                else:
                    line.check_variance_high = "#ffc7c7"
            else:
                if line.margin==True:
                    if line.planned_amount > line.actual_amount and line.plan_margin > line.actual_margin and line.plan_pct_nr > line.act_pct_nr:
                        line.check_variance_high = "#ffc7c7"
                    else:
                        line.check_variance_high = "#c7d5ff"
                else:
                    if line.planned_amount > line.actual_amount and line.plan_pct_nr > line.act_pct_nr:
                        line.check_variance_high = "#ffc7c7"
                    else:
                        line.check_variance_high = "#c7d5ff"

            
    @api.one
    @api.depends('date_from','date_to', 'company_id','actual_amount')
    def _convert_move_month_year(self):
        locale = self._context.get('lang', 'en_US')
        for line in self:
            company_id = ''
            if line.date_from:
                if not line.company_id:
    #Note: do not assign yourself journal company as journal
                    if not line.budget_category_id.company_id:
                        raise UserError(_('Please assign company for the Budget.'))
    # Check is 445 enabled for the company
                if line.company_id and line.company_id.custom_calendar == False:
    # if not 445 used for the company conver the move date to sting month_year
                    value = datetime.datetime.strptime(line.date_from, '%Y-%m-%d')
                    string_date_year = babel.dates.format_date(value, format = 'MMMM yyyy', locale = locale)
                    line.move_month_year = string_date_year
                else:
                    account_fiscal_periods = self.env['account.fiscal.periods'].search(['&', ('name', 'ilike', line.date_from[:4]), ('calendar_type', '=', line.company_id.calendar_type.id)])
                    if account_fiscal_periods :
                        # Get period based on account move line
                        period = self.env['account.fiscal.period.lines'].search([('account_fiscal_period_id', '=', account_fiscal_periods.id), ('date_start', '<=', line.date_from),('date_end', '>=', line.date_to)])
    
                        if period:      
                            if period.name:
                                if period.name[2]=="-":
                                    line.move_month_year = period.name[:1] + '0' + period.name[1:]
                                else:
                                    line.move_month_year = period.name

    @api.multi
    def change_month(self):
        budget_list=self.env['budget.category.lines'].search([])
        for budget in budget_list:
            if budget.month[2]=="-":
                budget.company_month = budget.company_id.code+" "+budget.month[:1] + '0' + budget.month[1:]
            else:
                budget.company_month = budget.company_id.code+" "+budget.month
                
    @api.multi
    def remove_quarter_year_reports(self):        
        query="""DELETE FROM budget_category_quarterly;
                 DELETE FROM budget_category_yearly"""
        self._cr.execute(query)
        
    
    @api.model
    def create(self, vals):
        budget_id = vals['budget_category_id']        
        company_id=self.env['budget.product.category'].search([('id','=',budget_id)]).company_id
        
        if vals.get('month'):
            budget_obj = self.env['account.fiscal.period.lines'].search([('name','=',vals.get('month')),('account_fiscal_period_id.calendar_type','=',company_id.calendar_type.id)])
            if budget_obj:
                vals.update({
                        'account_fiscal_periods_id':budget_obj.id,
                        'quarter':re.split('-',budget_obj.quarter)[0],
                        'fin_yr':budget_obj.year,
                        'date_from':budget_obj.date_start,
                        'date_to':budget_obj.date_end,
                        })
            else:
                raise ValidationError(_('Month not found'))
        else:
            raise ValidationError(_('Month is Required'))
        
        return super(BudgetProductCategoryLines, self).create(vals)
    
    @api.multi
    def write(self, vals):
        
        company_id=self.company_id
        if vals.get('budget_category_id'):
            budget_id = vals.get('budget_category_id')            
            company_id=self.env['budget.product.category'].search([('id','=',budget_id)]).company_id
        
        if vals.get('month'):
            fy_month = vals.get('month')        
        
            budget_obj = self.env['account.fiscal.period.lines'].search([('name','=',fy_month),('account_fiscal_period_id.calendar_type','=',company_id.calendar_type.id)])
            if budget_obj:
                vals.update({
                        'account_fiscal_periods_id':budget_obj.id,
                        'quarter':re.split('-',budget_obj.quarter)[0],
                        'fin_yr':budget_obj.year,
                        'date_from':budget_obj.date_start,
                        'date_to':budget_obj.date_end,
                        })
            else:
                raise ValidationError(_('Month not found'))

        return super(BudgetProductCategoryLines, self).write(vals)

    @api.onchange('account_fiscal_periods_id')
    def onchange_account_fiscal_periods_id(self):
        if self.account_fiscal_periods_id:
            fiscal_period = self.env["account.fiscal.period.lines"].search([('id','=',self.account_fiscal_periods_id.id)])
            self.account_fiscal_periods_quarterly = fiscal_period.quarter
            self.fin_yr = fiscal_period.year

    def get_budget_lines(self):
        self.env.cr.execute("""SELECT DISTINCT name FROM budget_category_lines """)
        rec=self.env.cr.fetchall()
        return rec

class BudgetProductCategoryQuarterly(models.Model):
    _name = "budget.category.quarterly"
    _description = "Budget Product Category Quarterly view"
    _order = 'sequence'
    
    budget_category_id = fields.Many2one('budget.product.category', 'Budget', ondelete='cascade')
    company_id = fields.Many2one('res.company',string='Company')
    current_company = fields.Many2one('res.company',string="Current company", compute="_compute_current_company", search="_search_current_company")
    current_quarter = fields.Char('Current Quarter', compute="_compute_current_quarter", search="_search_current_quarter")
    last_year_current_quarter = fields.Char('Current Quarter', compute="_compute_last_year_current_quarter", search="_search_last_year_current_quarter")
    name = fields.Char(string='Name')
    actual_amount = fields.Float('Actual Amount')
    planned_amount = fields.Float('Planned Amount')
    sequence = fields.Integer('Sequence')
    fin_yr = fields.Char("Year")
    quarter = fields.Char("Quarter")
    var_amount = fields.Float(String='Var')
    plan_margin = fields.Float(String="Plan Margin")
    actual_margin = fields.Float(String='Actual Margin')
    plan_offset = fields.Float(String="Plan Offset")
    actual_offset = fields.Float(String='Actual Offset')
    var_margin = fields.Float(String='Var Margin')
    plan_pct_nr = fields.Float(String='Plan NR')
    act_pct_nr = fields.Float(String='Actual NR')
    yoy = fields.Float(String='YOY')
    budget_scenario = fields.Selection([
        ('minimum', 'Minimum'),
        ('budget', 'Budget'),
        ('stretch', 'Stretch'),
        ], 'Scenario')
    margin = fields.Boolean("Margin")
    quarter_year = fields.Char('Quarter Year')
    company_type = fields.Char("Company and Type", compute = '_company_any_type')
    type = fields.Selection([
        ('revenue', 'Revenue'),
        ('income', 'Income'),
        ('expense', 'Expense'),
        ], 'Budget Type')   
    
    var_amount_higher = fields.Char("Amount higher", compute = '_compute_var_amount')
    var_margin_higher = fields.Char("Margin higher", compute = '_compute_var_margin')
    var_yoy_higher = fields.Char("Yoy higher", compute = '_compute_var_yoy')
    check_variance_high = fields.Char("Check variance high", compute = '_compute_check_variance')
    margin = fields.Boolean("Margin")
    is_margin = fields.Char("Is Margin", compute = '_is_margin')
    visibility = fields.Boolean("Visibility")
    is_visible = fields.Char("Is Visible", compute = '_is_margin')
    
    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        today = date.today()
        lastyear = today.year - 1
        month = today.month
        if month<=3:
            qua=1
        elif month<=6:
            qua=2
        elif month<=9:
            qua=3
        else:
            qua=4
        quarter = []
        year = []
        company = []
        scenario = []
        for loop in domain:
            for in_loop in loop:
                if in_loop == 'current_company':
                    cur_company = self.env.user.company_id.id
                    company.append(cur_company)
                if in_loop == 'budget':
                    scenario.append(in_loop)
                if in_loop == 'minimum':
                    scenario.append(in_loop)
                if in_loop == 'stretch':
                    scenario.append(in_loop)
                if in_loop == 'current_quarter':
                    quarter.append('Q'+str(qua)+'-'+str(today.year))
                if in_loop == 'last_year_current_quarter':
                    quarter.append('Q'+str(qua)+'-'+str(lastyear))
                if in_loop == str(today.year):
                    year.append(in_loop)
                if in_loop == str(lastyear):
                    year.append(in_loop)
        ft_domain = [dom_loop for dom_loop in domain if "|" not in dom_loop and "budget_scenario" not in dom_loop
                         and "fin_yr" not in dom_loop and "current_quarter" not in dom_loop 
                         and "last_year_current_quarter" not in dom_loop and "current_company" not in dom_loop]
        del domain[:]    
        if quarter or year or company or scenario:                             
            if quarter :
                domain.append(['quarter_year', 'in', quarter])
            if year :
                domain.append(['fin_yr', 'in', year])
            if company :
                domain.append(['company_id', 'in', company])
            if scenario :
                domain.append(['budget_scenario', 'in', scenario])    
        else :
            domain = domain
        for add_or in range(0,len(ft_domain)-1):
            domain.append('|')
        domain+=ft_domain

        return super(BudgetProductCategoryQuarterly, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)

    @api.multi
    def _is_margin(self):
        for line in self:
            if line.visibility==True:
                line.is_visible="Yes"
            else:
                line.is_visible="No"
            if line.margin==True:
                line.is_margin= 1   


    @api.multi
    def _compute_var_amount(self):
        for line in self:
            if line.type == "expense":
                if line.plan_pct_nr > line.act_pct_nr:
                    line.var_amount_higher = "#c7d5ff"
                else:
                    line.var_amount_higher = "#ffc7c7"
            else:
                if line.planned_amount > line.actual_amount:
                    line.var_amount_higher = "#ffc7c7"
                else:
                    line.var_amount_higher = "#c7d5ff"

    @api.multi
    def _compute_var_margin(self):
        for line in self:
            if line.type == "expense":
                if line.plan_pct_nr > line.act_pct_nr:
                    line.var_margin_higher = "#c7d5ff"
                else:
                    line.var_margin_higher = "#ffc7c7"
            else:
                if line.plan_margin > line.actual_margin:
                    line.var_margin_higher = "#ffc7c7"
                else:
                    line.var_margin_higher = "#c7d5ff"

    @api.multi
    def _compute_var_yoy(self):
        for line in self:
            if line.type == "expense":
                if line.plan_pct_nr > line.act_pct_nr:
                    line.var_yoy_higher = "#c7d5ff"
                else:
                    line.var_yoy_higher = "#ffc7c7"
            else:
                if line.plan_pct_nr > line.act_pct_nr:
                    line.var_yoy_higher = "#ffc7c7"
                else:
                    line.var_yoy_higher = "#c7d5ff"

    @api.multi
    def _compute_check_variance(self):
        for line in self:
            if line.type == "expense":
                if line.plan_pct_nr > line.act_pct_nr:
                    line.check_variance_high = "#c7d5ff"
                else:
                    line.check_variance_high = "#ffc7c7"
            else:
                if line.margin==True:
                    if line.planned_amount > line.actual_amount and line.plan_margin > line.actual_margin and line.plan_pct_nr > line.act_pct_nr:
                        line.check_variance_high = "#ffc7c7"
                    else:
                        line.check_variance_high = "#c7d5ff"
                else:
                    if line.planned_amount > line.actual_amount and line.plan_pct_nr > line.act_pct_nr:
                        line.check_variance_high = "#ffc7c7"
                    else:
                        line.check_variance_high = "#c7d5ff"
                
    @api.multi
    def _company_any_type(self):
        for line in self:
            line.company_type=line.company_id.code
            
    @api.multi
    @api.depends('company_id')
    def _compute_current_company(self):
        for recs in self:
            recs.current_company=self.env.user.company_id.id
    @api.multi
    def _compute_current_quarter(self):
        today = 'M'+datetime.datetime.today().strftime('%m')+'-'+ datetime.datetime.today().strftime('%Y')
        quarter_year = self.env['account.fiscal.period.lines'].search([('name','=',today)]).quarter
        quarter = re.split('-',quarter_year)
        for recs in self:
            recs.current_quarter=quarter
            
    @api.multi
    def _compute_last_year_current_quarter(self):
        today = 'M'+datetime.datetime.today().strftime('%m')+'-'+ datetime.datetime.today().strftime('%Y')
        year = int(datetime.datetime.today().strftime('%Y'))-1
        quarter_year = self.env['account.fiscal.period.lines'].search([('name','=',today)]).quarter
        quarter = re.split('-',quarter_year)
        for recs in self:
            recs.current_quarter=quarter+str(year)

    @api.multi
    def _search_current_company(self, operator, value):
        recs = self.search([('company_id', '=', self.env.user.company_id.id)])  
        return [('id', 'in', [x.id for x in recs])]
    @api.multi
    def _search_current_quarter(self, operator, value):
        month= 'M'+datetime.datetime.today().strftime('%m')+'-'+ str(int(datetime.datetime.today().strftime('%Y')))
        quarter_year = self.env['account.fiscal.period.lines'].search([('name','=',month)]).quarter
#         quarter = re.split('-',quarter_year) 
        
        recs = self.search([('quarter_year', '=', quarter_year)])  
        return [('id', 'in', [x.id for x in recs])]
    
    @api.multi
    def _search_last_year_current_quarter(self, operator, value):
        month = 'M'+datetime.datetime.today().strftime('%m')+'-'+ str(int(datetime.datetime.today().strftime('%Y'))-1)
        year = int(datetime.datetime.today().strftime('%Y'))-1
        quarter_year = self.env['account.fiscal.period.lines'].search([('name','=',month)]).quarter
        quarter = re.split('-',quarter_year) 
        recs = self.search([('quarter_year', '=', quarter_year),('fin_yr','=',year)])  
        return [('id', 'in', [x.id for x in recs])]
    
#     @api.model
#     def create(self, vals):
#         if (vals['fin_yr'] and vals['quarter']):
#             qua_yr = str(vals['quarter'] + '-' + str(vals['fin_yr']))
#             vals['quarter_year']=qua_yr
#             
#             return super(BudgetProductCategoryQuarterly, self).create(vals)
        
    @api.multi
    def action_create_budget_category_quarter(self,quarter_count):
        res_company=self.env['res.company'].search([])
        for line in range(0,quarter_count):
            new_date=datetime.datetime.now()-relativedelta(months=line*3)
            quarter="Q1"
            year=new_date.year
            if int(new_date.month)<=3:
                quarter="Q1"
            elif int(new_date.month)<=6:
                quarter="Q2"
            elif int(new_date.month)<=9:
                quarter="Q3"
            else:
                quarter="Q4"                          
            for company in res_company:
                company_id=company.id
                del_pre_obj = self.env['budget.category.quarterly'].search([
                                    ('company_id','=',company_id),
                                    ('quarter','=',company.code+" "+quarter+"-"+str(year))])
                del_pre_obj.unlink()
                scenario_types=['budget','minimum','stretch']
                total_type=['revenue','income','expense']
                for scenarios in scenario_types:     
                    for budget_types in total_type:
                        planned_amount = 0.00
                        actual_amount = 0.00
                        var_amount = 0.00
                        plan_margin = 0.00
                        actual_margin = 0.00
                        var_margin = 0.00
                        plan_pct_nr = 0.00
                        act_pct_nr = 0.00
                        yoy = 0.00
                        plan_offset = 0.00
                        actual_offset = 0.00
                        i=0 
                        cat_vals=[
                            ('company_id','=',company_id),
                            ('budget_category_id.budget_scenario','=',scenarios),
                            ('quarter','=',quarter),
                            ('fin_yr','=',str(year)),
                            ('name','=','Net Revenue'),('type','=',budget_types)]
                        for line_name in self.env['budget.category.lines'].search(cat_vals):    
                            planned_amount += line_name.planned_amount
                            actual_amount += line_name.actual_amount
                            var_amount += line_name.var_amount
                            plan_margin += line_name.plan_margin
                            actual_margin += line_name.actual_margin 
                            var_margin += line_name.var_margin 
                            plan_pct_nr += line_name.plan_pct_nr
                            act_pct_nr += line_name.act_pct_nr
                            yoy += line_name.yoy
                            plan_offset += line_name.plan_offset
                            actual_offset += line_name.actuals_offset
                            i+=1         
                        if i>0:
                            tid = self.env['budget.category.quarterly'].search([
                                ('company_id','=',company_id),
                                ('budget_category_id.budget_scenario','=',scenarios),
                                ('quarter','=',company.code+" "+quarter+"-"+str(year)),
                                ('name','=','Net Revenue'),('type','=',budget_types)])
                            if tid:    
                                tid.write({'planned_amount':planned_amount,
                                           'actual_amount':actual_amount,
                                           'sequence':line_name.sequence,
                                           'var_amount':var_amount/i if i>0 else 0.00,
                                           'plan_margin':plan_margin/i if i>0 else 0.00,
                                           'actual_margin':actual_margin/i if i>0 else 0.00, 
                                           'var_margin':var_margin/i if i>0 else 0.00, 
                                           'plan_pct_nr':plan_pct_nr/i if i>0 else 0.00,
                                           'act_pct_nr':act_pct_nr/i if i>0 else 0.00,
                                           'yoy':yoy/i if i>0 else 0.00,
                                           'plan_offset':plan_offset/i if i>0 else 0.00,
                                           'actual_offset':actual_offset/i if i>0 else 0.00,
                                           'quarter':tid.company_id.code+" "+quarter+"-"+str(year),
                                           'quarter_year':quarter+"-"+str(year),
                                           'type':line_name.type,
                                           'margin':line_name.margin,
                                           'visibility':line_name.visibility,
                                           })
                            else:
                                res = self.env['budget.category.quarterly'].create({
                                                                            'budget_category_id':line_name.budget_category_id.id,
                                                                            'company_id':company_id,
                                                                            'name':line_name.name,
                                                                            'actual_amount':actual_amount,
                                                                            'planned_amount':planned_amount,
                                                                            'sequence':line_name.sequence,
                                                                            'fin_yr':line_name.fin_yr,
                                                                            'quarter':company.code+" "+quarter+"-"+str(year),
                                                                            'budget_scenario':line_name.budget_scenario,
        #                                                                                 'var_amount':var_amount/i if i>0 else 0.00,
        #                                                                                 'plan_margin':plan_margin/i if i>0 else 0.00,
        #                                                                                 'actual_margin':actual_margin/i if i>0 else 0.00, 
        #                                                                                 'var_margin':var_margin/i if i>0 else 0.00, 
        #                                                                                 'plan_pct_nr':plan_pct_nr/i if i>0 else 0.00,
        #                                                                                 'act_pct_nr':act_pct_nr/i if i>0 else 0.00,
        #                                                                                 'yoy':yoy/i if i>0 else 0.00,
                                                                            'plan_offset':plan_offset/i if i>0 else 0.00,
                                                                            'actual_offset':actual_offset/i if i>0 else 0.00,
                                                                            'quarter_year':quarter+"-"+str(year),
                                                                            'type':line_name.type,
                                                                            'margin':line_name.margin,
                                                                            'visibility':line_name.visibility,
                                                                            })
        
                    
                scenario_type=['budget','minimum','stretch']
                name_list=[]
                list_cat=[]
                type_list = ['revenue','income','expense']
                if self.env['budget.category.lines'].search_count([('company_id','=',company_id),('budget_category_id.budget_scenario','=','budget'),('month','in',['M1-'+str(year),'M01-'+str(year)])])==0:
                    list_cat=self.env['budget.category.lines'].search([('company_id','=',company_id),('budget_category_id.budget_scenario','=','budget'),('month','in',['M012-'+str(year),'M12-'+str(year)])])
                else:
                    list_cat=self.env['budget.category.lines'].search([('company_id','=',company_id),('budget_category_id.budget_scenario','=','budget'),('month','in',['M1-'+str(year),'M01-'+str(year)])])
                for line_names in list_cat:
                    name_list.append(line_names.name)
                for scenario in scenario_type:     
                    for category in name_list:
                        for budget_type in type_list:
                            planned_amount = 0.00
                            actual_amount = 0.00
                            var_amount = 0.00
                            plan_margin = 0.00
                            actual_margin = 0.00
                            var_margin = 0.00
                            plan_pct_nr = 0.00
                            act_pct_nr = 0.00
                            yoy = 0.00 
                            plan_offset = 0.00
                            actual_offset = 0.00        
                            i=0
                            for line_names in self.env['budget.category.lines'].search([
                                ('company_id','=',company_id),
                                ('budget_category_id.budget_scenario','=',scenario),
                                ('quarter','=',quarter),
                                ('fin_yr','=',str(year)),
                                ('name','=',category),('type','=',budget_type)]):
                                
                                planned_amount += line_names.planned_amount
                                actual_amount += line_names.actual_amount
                                var_amount += line_names.var_amount
                                plan_margin += line_names.plan_margin
                                actual_margin += line_names.actual_margin 
                                var_margin += line_names.var_margin 
                                plan_pct_nr += line_names.plan_pct_nr
                                act_pct_nr += line_names.act_pct_nr
                                yoy += line_names.yoy
                                plan_offset += float(line_names.plan_offset)
                                actual_offset += float(line_names.actuals_offset)
                                i+=1
                            if i>0:
                                tid = self.env['budget.category.quarterly'].search([
                                    ('company_id','=',company_id),
                                    ('budget_category_id.budget_scenario','=',scenario),
                                    ('quarter','=',company.code+" "+quarter+"-"+str(year)),
                                    ('name','=',category),('type','=',budget_type)])
                                
                                if tid:  
                                    tid.write({'planned_amount':planned_amount,
                                               'actual_amount':actual_amount,
                                               'sequence':line_names.sequence,
                                               'var_amount':var_amount/i if i>0 else 0.00,
                                               'plan_margin':plan_margin/i if i>0 else 0.00,
                                               'actual_margin':actual_margin/i if i>0 else 0.00, 
                                               'var_margin':var_margin/i if i>0 else 0.00, 
                                               'plan_pct_nr':plan_pct_nr/i if i>0 else 0.00,
                                               'act_pct_nr':act_pct_nr/i if i>0 else 0.00,
                                               'yoy':yoy/i if i>0 else 0.00,
                                               'plan_offset':plan_offset/i if i>0 else 0.00,
                                               'actual_offset':actual_offset/i if i>0 else 0.00,
                                               'quarter':tid.company_id.code+" "+quarter+"-"+str(year),
                                               'quarter_year':quarter+"-"+str(year),
                                               'type':line_names.type,
                                               'margin':line_names.margin,
                                               'visibility':line_names.visibility,
                                               })

                                else:
                                    res = self.env['budget.category.quarterly'].create({
                                                                                'budget_category_id':line_names.budget_category_id.id,
                                                                                'company_id':company_id,
                                                                                'name':line_names.name,
                                                                                'actual_amount':actual_amount,
                                                                                'planned_amount':planned_amount,
                                                                                'sequence':line_names.sequence,
                                                                                'fin_yr':line_names.fin_yr,
                                                                                'quarter':company.code+" "+quarter+"-"+str(year),
                                                                                'budget_scenario':line_names.budget_scenario,
#                                                                                 'var_amount':var_amount/i if i>0 else 0.00,
#                                                                                 'plan_margin':plan_margin/i if i>0 else 0.00,
#                                                                                 'actual_margin':actual_margin/i if i>0 else 0.00, 
#                                                                                 'var_margin':var_margin/i if i>0 else 0.00, 
#                                                                                 'plan_pct_nr':plan_pct_nr/i if i>0 else 0.00,
#                                                                                 'act_pct_nr':act_pct_nr/i if i>0 else 0.00,
#                                                                                 'yoy':yoy/i if i>0 else 0.00,
                                                                                'plan_offset':plan_offset/i if i>0 else 0.00,
                                                                                'actual_offset':actual_offset/i if i>0 else 0.00,
                                                                                'quarter_year':quarter+"-"+str(year),
                                                                                'type':line_names.type,
                                                                                'margin':line_names.margin,
                                                                                'visibility':line_names.visibility, 
                                                                                })
                                    res._get_var_amount()
                                    
                for scenario in scenario_type:  
                    for names in ["Dietary","Laboratory"]:
#                             print company.code, quarter,year, names,  scenario, budget_type
                        budget_mar_update = self.env['budget.category.quarterly'].search([
                                            ('company_id','=',company_id),
                                            ('budget_category_id.budget_scenario','=',scenario),
                                            ('quarter','=',company.code+" "+quarter+"-"+str(year)),
                                            ('name','in',[names])
                                            ])
                        expense_pln = revenue_pln = expense_act = revenue_act = 0
                        for margin_recs in budget_mar_update:
                            if margin_recs.type == "revenue":
                                revenue_act += margin_recs.actual_amount
                                revenue_pln += margin_recs.planned_amount
                                
                            if margin_recs.type == "expense":
                                expense_act += margin_recs.actual_amount
                                expense_pln += margin_recs.planned_amount
                            
                        for margin_recs in budget_mar_update:
                               
                            total_act = (((revenue_act-expense_act)/revenue_act) *100) if revenue_act!=0 else 0
                            total_pln = (((revenue_pln-expense_pln)/revenue_pln) *100) if revenue_pln!=0 else 0                    
                            total_margin = (((total_act-total_pln)/total_pln) *100) if total_pln!=0 else 0                    
                            margin_recs.actual_margin = total_act
                            margin_recs.plan_margin = total_pln
                            margin_recs.var_margin = total_margin
                        
                   
    @api.multi
    def _change_margin_vals(self,quarter_count):
        res_company=self.env['res.company'].search([])
        for line in range(0,quarter_count):
            new_date=datetime.datetime.now()-relativedelta(months=line*3)
            quarter="Q1"
            year=new_date.year
            if int(new_date.month)<=3:
                quarter="Q1"
            elif int(new_date.month)<=6:
                quarter="Q2"
            elif int(new_date.month)<=9:
                quarter="Q3"
            else:
                quarter="Q4"                 
            scenario_type=['budget','minimum','stretch']      
            for company in res_company:
                company_id=company.id                
                for scenario in scenario_type:  
                        for names in ["Dietary","Laboratory"]:
#                             print company.code, quarter,year, names,  scenario, budget_type
                            budget_mar_update = self.env['budget.category.quarterly'].search([
                                                ('company_id','=',company_id),
                                                ('budget_category_id.budget_scenario','=',scenario),
                                                ('quarter','=',company.code+" "+quarter+"-"+str(year)),
                                                ('name','in',[names])
                                                ])
                            expense_pln = revenue_pln = expense_act = revenue_act = 0
                            for margin_recs in budget_mar_update:
                                if margin_recs.type == "revenue":
                                    revenue_act += margin_recs.actual_amount
                                    revenue_pln += margin_recs.planned_amount
                                    
                                if margin_recs.type == "expense":
                                    expense_act += margin_recs.actual_amount
                                    expense_pln += margin_recs.planned_amount
                                
                            for margin_recs in budget_mar_update:
                                   
                                total_act = (((revenue_act-expense_act)/revenue_act) *100) if revenue_act!=0 else 0
                                total_pln = (((revenue_pln-expense_pln)/revenue_pln) *100) if revenue_pln!=0 else 0                    
                                total_margin = (((total_act-total_pln)/total_pln) *100) if total_pln!=0 else 0                    
                                margin_recs.actual_margin = total_act
                                margin_recs.plan_margin = total_pln
                                margin_recs.var_margin = total_margin
                                        
    @api.multi
    def _get_var_amount(self):
        formulas = self.env['budget.formula'].search([])
        VAR_INC = VAR_REV = VAR_EXP = PLAN_PCT_NR = ACT_PCT_NR = YOY = PLAN_MARGIN_C = ACTUAL_MARGIN_C = VAR_MGN = ""
        for formula in formulas:
            if formula.name=='VAR' and formula.budget_type=='all':
                VAR_INC=VAR_REV=VAR_EXP=formula.formula_single
            elif formula.name=='VAR' and formula.budget_type=='income':
                VAR_INC = formula.formula_single
            elif formula.name=='VAR' and formula.budget_type=='revenue':
                VAR_REV = formula.formula_single
            elif formula.name=='VAR' and formula.budget_type=='expense':
                VAR_EXP = formula.formula_single

            elif formula.name=='PLAN_PCT_NR':
                PLAN_PCT_NR=formula.formula_single
            elif formula.name=='ACT_PCT_NR':
                ACT_PCT_NR=formula.formula_single
            elif formula.name=='YOY':
                YOY=formula.formula_single
            elif formula.name=='PLAN_MARGIN':
                PLAN_MARGIN_C=formula.formula_single
            elif formula.name=='ACTUAL_MARGIN':
                ACTUAL_MARGIN_C=formula.formula_single
            elif formula.name=='VAR_MGN':
                VAR_MGN=formula.formula_single

        for lines in self:
            ACTUAL=float(lines.actual_amount)
            PLAN=float(lines.planned_amount)
            ACTUAL_NET=0.00
            PLAN_NET=0.00
            actual_net_cal=self.env['budget.category.quarterly'].search([('name','=','Net Revenue'),('company_id','=',lines.company_id.id),('budget_scenario','=',lines.budget_scenario),('quarter','=',lines.quarter),('quarter_year','=',lines.quarter_year)])
            if actual_net_cal:
                if actual_net_cal.actual_amount:
                    ACTUAL_NET=float(actual_net_cal.actual_amount)
                if actual_net_cal.planned_amount:
                    PLAN_NET=float(actual_net_cal.planned_amount)
                
#             ACTUAL_LAST=float(lines.actuals_previous_year)
            plan_offset=float(lines.plan_offset)
            actual_offset=float(lines.actual_offset)
                
            if lines.type=='income':
                try:
                    lines.var_amount = eval(VAR_INC)
                except:
                    lines.var_amount = 0
            elif lines.type=='revenue':
                try:
                    lines.var_amount = eval(VAR_REV)
                except:
                    lines.var_amount = 0
            elif lines.type=='expense':
                try:
                    lines.var_amount = eval(VAR_EXP)
                except:
                    lines.var_amount = 0
            else:
                    lines.var_amount = 0
            
            

            try:
                lines.plan_margin = eval(PLAN_MARGIN_C)
            except:
                lines.plan_margin = 0
            try:
                lines.actual_margin = eval(ACTUAL_MARGIN_C)
            except:
                lines.actual_margin = 0
            PLAN_MARGIN=lines.plan_margin
            ACTUAL_MARGIN=lines.actual_margin
            try:
                lines.var_margin = eval(VAR_MGN)
            except:
                lines.var_margin = 0

            try:
                lines.plan_pct_nr = eval(PLAN_PCT_NR)
            except:
                lines.plan_pct_nr = 0

            try:
                lines.act_pct_nr = eval(ACT_PCT_NR)
            except:
                lines.act_pct_nr = 0

            try:
                lines.yoy = eval(YOY)
            except:
                lines.yoy = 0                                                                                       

class BudgetProductCategoryYearly(models.Model):
    _name = "budget.category.yearly"
    _description = "Budget Product Category Yearly view"
    _order = 'sequence'
     
 
    budget_category_id = fields.Many2one('budget.product.category', 'Budget', ondelete='cascade')
    company_id = fields.Many2one('res.company',string='Company')
    current_company = fields.Many2one('res.company',string="Current company", compute="_compute_current_company", search="_search_current_company")
    name = fields.Char(string='Name')
    actual_amount = fields.Float('Actual Amount')
    planned_amount = fields.Float('Planned Amount')
    sequence = fields.Integer('Sequence')
    fin_yr = fields.Char("Year")
    year = fields.Char("Year")
    quarter = fields.Char("Quarter")
    var_amount = fields.Float(String='Var')
    plan_margin = fields.Float(String="Plan Margin")
    actual_margin = fields.Float(String='Actual Margin')
    plan_offset = fields.Float(String="Plan Offset")
    actual_offset = fields.Float(String='Actual Offset')
    var_margin = fields.Float(String='Var Margin')
    plan_pct_nr = fields.Float(String='Plan NR')
    act_pct_nr = fields.Float(String='Actual NR')
    yoy = fields.Float(String='YOY')
    budget_scenario = fields.Selection([
        ('minimum', 'Minimum'),
        ('budget', 'Budget'),
        ('stretch', 'Stretch'),
        ], 'Scenario')
    margin = fields.Boolean("Margin")    
    company_type = fields.Char("Company and Type", compute = '_company_any_type')
    type = fields.Selection([
        ('revenue', 'Revenue'),
        ('income', 'Income'),
        ('expense', 'Expense'),
        ], 'Budget Type')

    var_amount_higher = fields.Char("Amount higher", compute = '_compute_var_amount')
    var_margin_higher = fields.Char("Margin higher", compute = '_compute_var_margin')
    var_yoy_higher = fields.Char("Yoy higher", compute = '_compute_var_yoy')
    check_variance_high = fields.Char("Check variance high", compute = '_compute_check_variance')
    margin = fields.Boolean("Margin")
    is_margin = fields.Char("Is Margin", compute = '_is_margin')
    visibility = fields.Boolean("Visibility")
    is_visible = fields.Char("Is Visible", compute = '_is_margin')
    

    @api.multi
    def _is_margin(self):
        for line in self:
            if line.visibility==True:
                line.is_visible="Yes"
            else:
                line.is_visible="No"
            if line.margin==True:
                line.is_margin= 1   

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        today = date.today()
        lastyear = today.year - 1
        year = []
        company = []
        scenario = []
        for loop in domain:
            for in_loop in loop:
                if in_loop == 'current_company':
                    cur_company = self.env.user.company_id.id
                    company.append(cur_company)
                if in_loop == 'budget':
                    scenario.append(in_loop)
                if in_loop == 'minimum':
                    scenario.append(in_loop)
                if in_loop == 'stretch':
                    scenario.append(in_loop)
                if in_loop == str(today.year):
                    year.append(in_loop)
                if in_loop == str(lastyear):
                    year.append(in_loop)
        ft_domain = [dom_loop for dom_loop in domain if "|" not in dom_loop and "budget_scenario" not in dom_loop
                         and "year" not in dom_loop and "current_company" not in dom_loop]
        del domain[:]    
        if year or company or scenario:
            if year :
                domain.append(['year', 'in', year])
            if company :
                domain.append(['company_id', 'in', company])
            if scenario :
                domain.append(['budget_scenario', 'in', scenario])    
        else :
            domain = domain
        for add_or in range(0,len(ft_domain)-1):
            domain.append('|')
        domain+=ft_domain
            
        return super(BudgetProductCategoryYearly, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)
       
       
    @api.multi
    def _compute_var_amount(self):
        for line in self:
            if line.type == "expense":
                if line.plan_pct_nr > line.act_pct_nr:
                    line.var_amount_higher = "#c7d5ff"
                else:
                    line.var_amount_higher = "#ffc7c7"
            else:
                if line.planned_amount > line.actual_amount:
                    line.var_amount_higher = "#ffc7c7"
                else:
                    line.var_amount_higher = "#c7d5ff"

    @api.multi
    def _compute_var_margin(self):
        for line in self:
            if line.type == "expense":
                if line.plan_pct_nr > line.act_pct_nr:
                    line.var_margin_higher = "#c7d5ff"
                else:
                    line.var_margin_higher = "#ffc7c7"
            else:
                if line.plan_margin > line.actual_margin:
                    line.var_margin_higher = "#ffc7c7"
                else:
                    line.var_margin_higher = "#c7d5ff"

    @api.multi
    def _compute_var_yoy(self):
        for line in self:
            if line.type == "expense":
                if line.plan_pct_nr > line.act_pct_nr:
                    line.var_yoy_higher = "#c7d5ff"
                else:
                    line.var_yoy_higher = "#ffc7c7"
            else:
                if line.plan_pct_nr > line.act_pct_nr:
                    line.var_yoy_higher = "#ffc7c7"
                else:
                    line.var_yoy_higher = "#c7d5ff"

    @api.multi
    def _compute_check_variance(self):
        for line in self:
            if line.type == "expense":
                if line.plan_pct_nr > line.act_pct_nr:
                    line.check_variance_high = "#c7d5ff"
                else:
                    line.check_variance_high = "#ffc7c7"
            else:
                if line.margin==True:
                    if line.planned_amount > line.actual_amount and line.plan_margin > line.actual_margin and line.plan_pct_nr > line.act_pct_nr:
                        line.check_variance_high = "#ffc7c7"
                    else:
                        line.check_variance_high = "#c7d5ff"
                else:
                    if line.planned_amount > line.actual_amount and line.plan_pct_nr > line.act_pct_nr:
                        line.check_variance_high = "#ffc7c7"
                    else:
                        line.check_variance_high = "#c7d5ff"
                
    @api.multi
    def _company_any_type(self):
        for line in self:
            line.company_type=line.company_id.code
            
    @api.multi
    @api.depends('company_id')
    def _compute_current_company(self):
        for recs in self:
            recs.current_company=self.env.user.company_id.id
            
    @api.multi
    def _search_current_company(self, operator, value):
        recs = self.search([('company_id', '=', self.env.user.company_id.id)]) 

        return [('id', 'in', [x.id for x in recs])]
    
    @api.multi
    def action_create_budget_category_yearly(self,year_count):
        
        res_company=self.env['res.company'].search([])
        for line in range(0,year_count):
            new_date=datetime.datetime.now()-relativedelta(years=line)
            year=new_date.year
            
            for company in res_company:
                company_id=company.id
                del_pre_obj = self.env['budget.category.yearly'].search([('company_id','=',company_id),('fin_yr','=',company.code+" "+str(year))])
                del_pre_obj.unlink()               
                scenario_types=['budget','minimum','stretch']
#                 name_lists=[]
                type_lists = ['revenue','income','expense']
#                 for line_name in self.env['budget.category.lines'].search([('company_id','=',company_id),('budget_category_id.budget_scenario','=','budget'),('month','in',['M1-'+str(year),'M01-'+str(year)])]):
#                         name_lists.append(line_name.name)
                for scenarios in scenario_types:
#                     for category_value in name_lists:
                        for budget_value in type_lists:   
                            planned_amount = 0.00
                            actual_amount = 0.00
                            var_amount = 0.00
                            plan_margin = 0.00
                            actual_margin = 0.00
                            var_margin = 0.00
                            plan_pct_nr = 0.00
                            act_pct_nr = 0.00
                            yoy = 0.00    
                            plan_offset = 0.00    
                            actual_offset = 0.00    
                            i=0 
                            for line_name in self.env['budget.category.lines'].search([('type','=',budget_value),('company_id','=',company_id),
                                ('budget_category_id.budget_scenario','=',scenarios),('fin_yr','=',year),('name','=','Net Revenue')]):
                                planned_amount += line_name.planned_amount
                                actual_amount += line_name.actual_amount
                                var_amount += line_name.var_amount
                                plan_margin += line_name.plan_margin
                                actual_margin += line_name.actual_margin 
                                var_margin += line_name.var_margin 
                                plan_pct_nr += line_name.plan_pct_nr
                                act_pct_nr += line_name.act_pct_nr
                                yoy += line_name.yoy
                                plan_offset += line_name.plan_offset
                                actual_offset += line_name.actuals_offset
                                i+=1
                            if i>0:                        
                                tid = self.env['budget.category.yearly'].search([('company_id','=',company_id),('type','=','revenue'),
                                ('budget_category_id.budget_scenario','=','budget'),('fin_yr','=',line_name.company_id.code+" "+str(year)),
                                ('name','=','Net Revenue')])      
                                if tid:
                                    tid.write({'planned_amount':planned_amount,
                                               'actual_amount':actual_amount,
                                               'sequence':line_name.sequence,
                                               'var_amount':var_amount/i if i>0 else 0.00,
                                               'plan_margin':plan_margin/i if i>0 else 0.00,
                                               'actual_margin':actual_margin/i if i>0 else 0.00, 
                                               'var_margin':var_margin/i if i>0 else 0.00, 
                                               'plan_pct_nr':plan_pct_nr/i if i>0 else 0.00,
                                               'act_pct_nr':act_pct_nr/i if i>0 else 0.00,
                                               'yoy':yoy/i if i>0 else 0.00,
                                               'plan_offset':plan_offset/i if i>0 else 0.00,
                                               'actual_offset':actual_offset/i if i>0 else 0.00,
                                               'fin_yr':tid.company_id.code+" "+str(year),
                                               'year':year,
                                               'type':line_name.type,
                                               'margin':line_name.margin,
                                               'visibility':line_name.visibility,
                                               })
                                else:
                                    res = self.env['budget.category.yearly'].create({
                                                                                'budget_category_id':line_name.budget_category_id.id,
                                                                                'company_id':line_name.company_id.id,
                                                                                'name':line_name.name,
                                                                                'actual_amount':actual_amount,
                                                                                'planned_amount':planned_amount,
                                                                                'sequence':line_name.sequence,
                                                                                'fin_yr':line_name.company_id.code+" "+line_name[0].fin_yr,
                                                                                'quarter':line_name.quarter,
                                                                                'budget_scenario':line_name.budget_scenario,
            #                                                                                 'var_amount':var_amount/i if i>0 else 0.00,
            #                                                                                 'plan_margin':plan_margin/i if i>0 else 0.00,
            #                                                                                 'actual_margin':actual_margin/i if i>0 else 0.00, 
            #                                                                                 'var_margin':var_margin/i if i>0 else 0.00, 
            #                                                                                 'plan_pct_nr':plan_pct_nr/i if i>0 else 0.00,
            #                                                                                 'act_pct_nr':act_pct_nr/i if i>0 else 0.00,
            #                                                                                 'yoy':yoy/i if i>0 else 0.00,
                                                                                'plan_offset':plan_offset/i if i>0 else 0.00,
                                                                                'actual_offset':actual_offset/i if i>0 else 0.00,
                                                                                'year':year,
                                                                                'type':line_name.type,
                                                                                'margin':line_name.margin,
                                                                                'visibility':line_name.visibility,
                                                                                })
        
        
        
        
                scenario_type=['budget','minimum','stretch']
                name_list=[]
                type_list = ['revenue','income','expense']
                
                list_cat=[]
                if self.env['budget.category.lines'].search_count([('company_id','=',company_id),('budget_category_id.budget_scenario','=','budget'),('month','in',['M1-'+str(year),'M01-'+str(year)])])==0:
                    list_cat=self.env['budget.category.lines'].search([('company_id','=',company_id),('budget_category_id.budget_scenario','=','budget'),('month','in',['M12-'+str(year),'M012-'+str(year)])])
                else:
                    list_cat=self.env['budget.category.lines'].search([('company_id','=',company_id),('budget_category_id.budget_scenario','=','budget'),('month','in',['M1-'+str(year),'M01-'+str(year)])])
                for line_names in list_cat:
                    name_list.append(line_names.name)
                for scenario in scenario_type:     
                    for category in name_list:
                        for budget_type in type_list:
                            planned_amount = 0.00
                            actual_amount = 0.00
                            var_amount = 0.00
                            plan_margin = 0.00
                            actual_margin = 0.00
                            var_margin = 0.00
                            plan_pct_nr = 0.00
                            act_pct_nr = 0.00
                            yoy = 0.00 
                            plan_offset = 0.00 
                            actual_offset = 0.00    
                            i=0 
                            for line_names in self.env['budget.category.lines'].search([('type','=',budget_type),('company_id','=',company_id),('budget_category_id.budget_scenario','=',scenario),('fin_yr','=',year),('name','=',category)]):
                                planned_amount += line_names.planned_amount
                                actual_amount += line_names.actual_amount
                                var_amount += line_names.var_amount
                                plan_margin += line_names.plan_margin
                                actual_margin += line_names.actual_margin 
                                var_margin += line_names.var_margin 
                                plan_pct_nr += line_names.plan_pct_nr
                                act_pct_nr += line_names.act_pct_nr
                                yoy += line_names.yoy
                                plan_offset += line_names.plan_offset
                                actual_offset += line_names.actuals_offset
                                i+=1                                   
                            if i>0:                        
                                tid = self.env['budget.category.yearly'].search([('company_id','=',company_id),('type','=',budget_type),('budget_category_id.budget_scenario','=',scenario),('fin_yr','=',line_names.company_id.code+" "+str(year)),('name','=',category)])               
                                if tid:
                                    tid.write({'planned_amount':planned_amount,
                                               'actual_amount':actual_amount,
                                               'sequence':line_names.sequence,
                                               'var_amount':var_amount/i if i>0 else 0.00,
                                               'plan_margin':plan_margin/i if i>0 else 0.00,
                                               'actual_margin':actual_margin/i if i>0 else 0.00, 
                                               'var_margin':var_margin/i if i>0 else 0.00, 
                                               'plan_pct_nr':plan_pct_nr/i if i>0 else 0.00,
                                               'act_pct_nr':act_pct_nr/i if i>0 else 0.00,
                                               'yoy':yoy/i if i>0 else 0.00,
                                               'plan_offset':plan_offset/i if i>0 else 0.00,
                                               'actual_offset':actual_offset/i if i>0 else 0.00,
                                               'fin_yr':tid.company_id.code+" "+str(year),
                                               'year':year,
                                               'type':line_names.type,
                                               'margin':line_names.margin,
                                               'visibility':line_names.visibility,
                                               })
                                else:
                                    res = self.env['budget.category.yearly'].create({
                                                                                'budget_category_id':line_names.budget_category_id.id,
                                                                                'company_id':line_names.company_id.id,
                                                                                'name':line_names.name,
                                                                                'actual_amount':actual_amount,
                                                                                'planned_amount':planned_amount,
                                                                                'sequence':line_names.sequence,
                                                                                'fin_yr':line_names.company_id.code+" "+line_names[0].fin_yr,
                                                                                'quarter':line_names.quarter,
                                                                                'budget_scenario':line_names.budget_scenario,
#                                                                                 'var_amount':var_amount/i if i>0 else 0.00,
#                                                                                 'plan_margin':plan_margin/i if i>0 else 0.00,
#                                                                                 'actual_margin':actual_margin/i if i>0 else 0.00, 
#                                                                                 'var_margin':var_margin/i if i>0 else 0.00, 
#                                                                                 'plan_pct_nr':plan_pct_nr/i if i>0 else 0.00,
#                                                                                 'act_pct_nr':act_pct_nr/i if i>0 else 0.00,
#                                                                                 'yoy':yoy/i if i>0 else 0.00,
                                                                                'plan_offset':plan_offset/i if i>0 else 0.00,
                                                                                'actual_offset':actual_offset/i if i>0 else 0.00,
                                                                                'year':year,
                                                                                'type':line_names.type,
                                                                                'margin':line_names.margin,
                                                                                'visibility':line_names.visibility,
                                                                                })
                                    res._get_var_amount()
                for scenario in scenario_type:  
                    for names in ["Dietary","Laboratory"]:
#                             print company.code, quarter,year, names,  scenario, budget_type
                        budget_mar_update = self.env['budget.category.yearly'].search([
                                            ('company_id','=',company_id),
                                            ('budget_category_id.budget_scenario','=',scenario),
                                            ('fin_yr','=',str(year))
                                            ])
                        expense_pln = revenue_pln = expense_act = revenue_act = 0
                        for margin_recs in budget_mar_update:
                            if margin_recs.type == "revenue":
                                revenue_act += margin_recs.actual_amount
                                revenue_pln += margin_recs.planned_amount
                                
                            if margin_recs.type == "expense":
                                expense_act += margin_recs.actual_amount
                                expense_pln += margin_recs.planned_amount
                            
                        for margin_recs in budget_mar_update:
                               
                            total_act = (((revenue_act-expense_act)/revenue_act) *100) if revenue_act!=0 else 0
                            total_pln = (((revenue_pln-expense_pln)/revenue_pln) *100) if revenue_pln!=0 else 0                    
                            total_margin = (((total_act-total_pln)/total_pln) *100) if total_pln!=0 else 0                    
                            
                            margin_recs.actual_margin = total_act
                            margin_recs.plan_margin = total_pln
                            margin_recs.var_margin = total_margin
         
       
                   
    @api.multi
    def _change_margin_vals(self,quarter_count):
        res_company=self.env['res.company'].search([])
        for line in range(0,quarter_count):
            new_date=datetime.datetime.now()-relativedelta(months=line*3)
            quarter="Q1"
            year=new_date.year
            if int(new_date.month)<=3:
                quarter="Q1"
            elif int(new_date.month)<=6:
                quarter="Q2"
            elif int(new_date.month)<=9:
                quarter="Q3"
            else:
                quarter="Q4"                 
            scenario_type=['budget','minimum','stretch']      
            for company in res_company:
                company_id=company.id   
                for scenario in scenario_type:  
                    for names in ["Dietary","Laboratory"]:
#                             print company.code, quarter,year, names,  scenario, budget_type
                        budget_mar_update = self.env['budget.category.yearly'].search([
                                            ('company_id','=',company_id),
                                            ('budget_category_id.budget_scenario','=',scenario),
                                            ('fin_yr','=',str(year)),
                                            ('name','in',[names])
                                            ])
                        expense_pln = revenue_pln = expense_act = revenue_act = 0
                        for margin_recs in budget_mar_update:
                            if margin_recs.type == "revenue":
                                revenue_act += margin_recs.actual_amount
                                revenue_pln += margin_recs.planned_amount
                                
                            if margin_recs.type == "expense":
                                expense_act += margin_recs.actual_amount
                                expense_pln += margin_recs.planned_amount
                            
                        for margin_recs in budget_mar_update:
                               
                            total_act = (((revenue_act-expense_act)/revenue_act) *100) if revenue_act!=0 else 0
                            total_pln = (((revenue_pln-expense_pln)/revenue_pln) *100) if revenue_pln!=0 else 0                    
                            total_margin = (((total_act-total_pln)/total_pln) *100) if total_pln!=0 else 0                    
                            
                            margin_recs.actual_margin = total_act
                            margin_recs.plan_margin = total_pln
                            margin_recs.var_margin = total_margin
                        
    @api.multi
    def _get_var_amount(self):
        formulas = self.env['budget.formula'].search([])
        VAR_INC = VAR_REV = VAR_EXP = PLAN_PCT_NR = ACT_PCT_NR = YOY = PLAN_MARGIN_C = ACTUAL_MARGIN_C = VAR_MGN = ""
        for formula in formulas:
            if formula.name=='VAR' and formula.budget_type=='all':
                VAR_INC=VAR_REV=VAR_EXP=formula.formula_single
            elif formula.name=='VAR' and formula.budget_type=='income':
                VAR_INC = formula.formula_single
            elif formula.name=='VAR' and formula.budget_type=='revenue':
                VAR_REV = formula.formula_single
            elif formula.name=='VAR' and formula.budget_type=='expense':
                VAR_EXP = formula.formula_single

            elif formula.name=='PLAN_PCT_NR':
                PLAN_PCT_NR=formula.formula_single
            elif formula.name=='ACT_PCT_NR':
                ACT_PCT_NR=formula.formula_single
            elif formula.name=='YOY':
                YOY=formula.formula_single
            elif formula.name=='PLAN_MARGIN':
                PLAN_MARGIN_C=formula.formula_single
            elif formula.name=='ACTUAL_MARGIN':
                ACTUAL_MARGIN_C=formula.formula_single
            elif formula.name=='VAR_MGN':
                VAR_MGN=formula.formula_single

        for lines in self:
            ACTUAL=float(lines.actual_amount)
            PLAN=float(lines.planned_amount)
            ACTUAL_NET=0.00
            PLAN_NET=0.00
            actual_net_cal=self.env['budget.category.yearly'].search([('type','=',lines.type),('name','=','Net Revenue'),('company_id','=',lines.company_id.id),('budget_scenario','=',lines.budget_scenario),('year','=',lines.year)])
            if actual_net_cal:
                if actual_net_cal.actual_amount:
                    ACTUAL_NET=float(actual_net_cal.actual_amount)
                if actual_net_cal.planned_amount:
                    PLAN_NET=float(actual_net_cal.planned_amount)
                
#             ACTUAL_LAST=float(lines.actuals_previous_year)
            plan_offset=float(lines.plan_offset)
            actual_offset=float(lines.actual_offset)
                
            if lines.type=='income':
                try:
                    lines.var_amount = eval(VAR_INC)
                except:
                    lines.var_amount = 0
            elif lines.type=='revenue':
                try:
                    lines.var_amount = eval(VAR_REV)
                except:
                    lines.var_amount = 0
            elif lines.type=='expense':
                try:
                    lines.var_amount = eval(VAR_EXP)
                except:
                    lines.var_amount = 0
            else:
                    lines.var_amount = 0
            
            

            try:
                lines.plan_margin = eval(PLAN_MARGIN_C)
            except:
                lines.plan_margin = 0
            try:
                lines.actual_margin = eval(ACTUAL_MARGIN_C)
            except:
                lines.actual_margin = 0
            PLAN_MARGIN=lines.plan_margin
            ACTUAL_MARGIN=lines.actual_margin
            try:
                lines.var_margin = eval(VAR_MGN)
            except:
                lines.var_margin = 0

            try:
                lines.plan_pct_nr = eval(PLAN_PCT_NR)
            except:
                lines.plan_pct_nr = 0

            try:
                lines.act_pct_nr = eval(ACT_PCT_NR)
            except:
                lines.act_pct_nr = 0

            try:
                lines.yoy = eval(YOY)
            except:
                lines.yoy = 0                 
                 
class BudgetFormula(models.Model):
    _name = "budget.formula"

    name = fields.Char('Cell', required=True)
    budget_type = fields.Selection([('all', 'All'),('revenue', 'Revenue'),('income', 'Income'),('expense', 'Expense')], string='Type', required=True)
    formula_single = fields.Text('Single Practice', required=True)

class BudgetDashboard(models.Model):
    _name = 'budget.dashboard'

    @api.model
    def fetch_dashboard_data(self):
        result = {}
        today = datetime.datetime.now().date()  
        return True