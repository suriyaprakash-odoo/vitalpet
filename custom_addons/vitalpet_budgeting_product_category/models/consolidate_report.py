# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import date
from dateutil.relativedelta import relativedelta
import datetime

import re

class BudgetConsolidateMonthly(models.Model):
    _name = "budget.consolidate.monthly"
    _description = "Budget Product Category Consolidate Monthly view"
    _order = 'sequence'
    
    @api.multi
    def validate_budget_consolidate(self,budget=None):
        if budget==1:                                                
            action_rec = self.env['ir.model.data'].xmlid_to_object('vitalpet_budgeting_product_category.action_budget_consolidate_quarterly')
        elif budget==2:
            action_rec = self.env['ir.model.data'].xmlid_to_object('vitalpet_budgeting_product_category.action_budget_consolidate_yearly')
        else:
            action_rec = self.env['ir.model.data'].xmlid_to_object('vitalpet_budgeting_product_category.action_budget_consolidate_monthly')
        if action_rec:
            return action_rec.id


    budget_category_id = fields.Many2one('budget.product.category', 'Budget', ondelete='cascade')
    name = fields.Char(string='Name')
    actual_amount = fields.Float('Actual Amount')
    planned_amount = fields.Float('Planned Amount')
    sequence = fields.Integer('Sequence')
    fin_yr = fields.Char("Year")
    month = fields.Char("Month")
    quarter = fields.Char("Quarter")
    var_amount = fields.Float(String='Var')
    plan_margin = fields.Float(String="Plan Margin")
    actual_margin = fields.Float(String='Actual Margin')
    var_margin = fields.Float(String='Var Margin')
    plan_pct_nr = fields.Float(String='Plan NR')
    act_pct_nr = fields.Float(String='Actual NR')
    yoy = fields.Float(String='YOY')
    plan_offset = fields.Float(String='Plan Offset')
    actual_offset = fields.Float(String='Actual Offset')
    budget_scenario = fields.Selection([
        ('minimum', 'Minimum'),
        ('budget', 'Budget'),
        ('stretch', 'Stretch'),
        ], 'Scenario')
    margin = fields.Boolean("Margin")
    month_year = fields.Char('Month Year')
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
    current_month = fields.Char(string="Current month", compute='_compute_current_month', search="_search_current_month")
    last_year_current_month = fields.Char(string="Last Year Current month", compute='_last_year_current_month', search="_search_last_year_current_month")
    visibility = fields.Boolean("Visibility")
    is_visible = fields.Char("Is Visible", compute = '_is_margin')
    

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        today = date.today()
        lastyear = today.year - 1
        period = []
        year = []
        scenario = []
        for loop in domain:
            for in_loop in loop:
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
                         and "last_year_current_month" not in dom_loop]
        del domain[:]    
        if period or year or scenario:                             
            if period :
                domain.append(['month_year', 'in', period])
            if year :
                domain.append(['fin_yr', 'in', year])
            if scenario :
                domain.append(['budget_scenario', 'in', scenario])    
        else :
            domain = domain
        for add_or in range(0,len(ft_domain)-1):
            domain.append('|')
        domain+=ft_domain
        return super(BudgetConsolidateMonthly, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)

    @api.multi
    def _compute_current_month(self):
        for recs in self:
            recs.current_month='M'+date.today().strftime('%m')+'-'+date.today().strftime('%Y')
    @api.multi
    def _last_year_current_month(self):
        for recs in self:
            recs.last_year_current_month='M'+date.today().strftime('%m')+'-'+ str(int(date.today().strftime('%Y'))-1)

    @api.multi
    def _search_current_month(self, operator, value):
        recs = self.search([('month', '=', 'M'+date.today().strftime('%m')+'-'+date.today().strftime('%Y'))])  
        return [('id', 'in', [x.id for x in recs])]
    
    @api.multi
    def _search_last_year_current_month(self, operator, value):
        recs = self.search([('month', '=', 'M'+date.today().strftime('%m')+'-'+ str(int(date.today().strftime('%Y'))-1))])  
        return [('id', 'in', [x.id for x in recs])]

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
    def action_create_budget_consolidate_month(self,month_count):
        scenario_type=['budget','minimum','stretch']
        name_list=[]
        type_list = ['revenue','income','expense']
#         date_now  = date.today()
        previous_month = []
        for line in range(0,month_count):
            new_date=datetime.datetime.now()-relativedelta(months=line)
            cur_month = "M" + str('%02d' %new_date.month) + '-' + str(new_date.year)
            previous_month.append(cur_month)
            
        del_pre_obj = self.env['budget.consolidate.monthly'].search([('month_year','in',previous_month)])
        del_pre_obj.unlink()
    
#         previous_month = ['M09-2018']
        
        for line_month in previous_month:
            for line_names in self.env['budget.category.lines'].search([('budget_category_id.budget_scenario','=','budget'),('month','=',line_month),('name','=','Net Revenue')]):
                name_list.append(line_names.name)
            name_list = list(set(name_list))
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
                        for line_names in self.env['budget.category.lines'].search([('type','=',budget_type),
                            ('budget_scenario','=',scenario),
                            ('month','=',line_month),('name','=',category)]):
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
                        print plan_offset,'---',actual_offset
                        if i>0:
                            tid = self.env['budget.consolidate.monthly'].search([
                                ('budget_scenario','=',scenario),
                                ('month_year','=',line_month),
                                ('name','=',category),('type','=',budget_type)], limit=1)
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
                                           'type':line_names.type,
                                           'margin':line_names.margin,
                                           'visibility':line_names.visibility,
                                           })
                            else:
                                self.env['budget.consolidate.monthly'].create({
                                                                            'budget_category_id':line_names.budget_category_id.id,
                                                                            'name':line_names.name,
                                                                            'actual_amount':actual_amount,
                                                                            'planned_amount':planned_amount,
                                                                            'sequence':line_names.sequence,
                                                                            'fin_yr':line_names.fin_yr,
                                                                            'month':re.split('-',line_month)[0],
                                                                            'budget_scenario':line_names.budget_scenario,
                                                                            'var_amount':var_amount/i if i>0 else 0.00,
                                                                            'plan_margin':plan_margin/i if i>0 else 0.00,
                                                                            'actual_margin':actual_margin/i if i>0 else 0.00, 
                                                                            'var_margin':var_margin/i if i>0 else 0.00, 
                                                                            'plan_pct_nr':plan_pct_nr/i if i>0 else 0.00,
                                                                            'act_pct_nr':act_pct_nr/i if i>0 else 0.00,
                                                                            'yoy':yoy/i if i>0 else 0.00,
                                                                            'plan_offset':plan_offset/i if i>0 else 0.00,
                                                                            'actual_offset':actual_offset/i if i>0 else 0.00,
                                                                            'month_year':line_month,
                                                                            'quarter':line_names.quarter,
                                                                            'type':line_names.type,
                                                                            'margin':line_names.margin,
                                                                            'visibility':line_names.visibility,
                                                                            })
        for line_month in previous_month:
            for line_names in self.env['budget.category.lines'].search([('budget_category_id.budget_scenario','=','budget'),('month','=',line_month),('name','!=','Net Revenue')]):
                name_list.append(line_names.name)
            name_list = list(set(name_list))
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
                        i=0      
                        for line_names in self.env['budget.category.lines'].search([('type','=',budget_type),
                            ('budget_scenario','=',scenario),
                            ('month','=',line_month),('name','=',category)]):
                            planned_amount += line_names.planned_amount
                            actual_amount += line_names.actual_amount
#                             var_amount += line_names.var_amount
#                             plan_margin += line_names.plan_margin
#                             actual_margin += line_names.actual_margin 
#                             var_margin += line_names.var_margin 
#                             plan_pct_nr += line_names.plan_pct_nr
#                             act_pct_nr += line_names.act_pct_nr
#                             yoy += line_names.yoy
                            i+=1
                        if i>0:
                            tid = self.env['budget.consolidate.monthly'].search([
                                ('budget_scenario','=',scenario),
                                ('month_year','=',line_month),
                                ('name','=',category),('type','=',budget_type)], limit=1)
                            if tid:                    
                                tid.write({'planned_amount':planned_amount,
                                           'actual_amount':actual_amount,
                                           'sequence':line_names.sequence,
                                           'type':line_names.type,
                                           'margin':line_names.margin,
                                           'visibility':line_names.visibility,
                                           })
                            else:
                                res=self.env['budget.consolidate.monthly'].create({
                                                                            'budget_category_id':line_names.budget_category_id.id,
                                                                            'name':line_names.name,
                                                                            'actual_amount':actual_amount,
                                                                            'planned_amount':planned_amount,
                                                                            'sequence':line_names.sequence,
                                                                            'fin_yr':line_names.fin_yr,
                                                                            'month':re.split('-',line_month)[0],
                                                                            'budget_scenario':line_names.budget_scenario,
                                                                            'month_year':line_month,
                                                                            'quarter':line_names.quarter,
                                                                            'type':line_names.type,
                                                                            'margin':line_names.margin,
                                                                            'visibility':line_names.visibility,
                                                                            })
                                res._get_var_amount()
                                
                       
            for scenario in scenario_type:  
                for names in ["Dietary","Laboratory"]:
#                             print company.code, quarter,year, names,  scenario, budget_type
                    budget_mar_update = self.env['budget.consolidate.monthly'].search([
                                        ('budget_category_id.budget_scenario','=',scenario),
                                        ('month_year','=',line_month),
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
    def _change_margin_vals(self,month_count):
        scenario_type=['budget','minimum','stretch']
        name_list=[]
        type_list = ['revenue','income','expense']
#         date_now  = date.today()
        previous_month = []
        for line in range(0,month_count):
            new_date=datetime.datetime.now()-relativedelta(months=line)
            cur_month = "M" + str('%02d' %new_date.month) + '-' + str(new_date.year)
            previous_month.append(cur_month)
            
        
        for line_month in previous_month:
            
            for scenario in scenario_type:  
                print line_month
                for names in ["Dietary","Laboratory"]:
#                             print company.code, quarter,year, names,  scenario, budget_type
                    budget_mar_update = self.env['budget.consolidate.monthly'].search([
                                        ('budget_category_id.budget_scenario','=',scenario),
                                        ('month_year','=',line_month),
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
                print formula.formula_single
                PLAN_PCT_NR=formula.formula_single
            elif formula.name=='ACT_PCT_NR':
                print formula.formula_single
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
            plan_offset=float(lines.plan_offset)
            actual_offset=float(lines.actual_offset)
            ACTUAL_NET=0.00
            PLAN_NET=0.00

            actual_net_cal=self.env['budget.consolidate.monthly'].search([('name','=','Net Revenue'),('budget_scenario','=',lines.budget_scenario),('month_year','=',lines.month_year)])
            if actual_net_cal:
                if actual_net_cal.actual_amount:
                    ACTUAL_NET=float(actual_net_cal.actual_amount)
                if actual_net_cal.planned_amount:
                    PLAN_NET=float(actual_net_cal.planned_amount)
                
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

                
class BudgetConsolidateQuarterly(models.Model):
    _name = "budget.consolidate.quarterly"
    _description = "Budget Product Category Consolidate Quarterly view"
    _order = 'sequence'
     
    budget_category_id = fields.Many2one('budget.product.category', 'Budget', ondelete='cascade')
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
    current_quarter = fields.Char('Current Quarter', compute="_compute_current_quarter", search="_search_current_quarter")
    last_year_current_quarter = fields.Char('Current Quarter', compute="_compute_last_year_current_quarter", search="_search_last_year_current_quarter")
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
        scenario = []
        for loop in domain:
            for in_loop in loop:
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
                         and "last_year_current_quarter" not in dom_loop]
        del domain[:]    
        if quarter or year or scenario:                             
            if quarter :
                domain.append(['quarter_year', 'in', quarter])
            if year :
                domain.append(['fin_yr', 'in', year])
            if scenario :
                domain.append(['budget_scenario', 'in', scenario])    
        else :
            domain = domain
        for add_or in range(0,len(ft_domain)-1):
            domain.append('|')
        domain+=ft_domain
            
        return super(BudgetConsolidateQuarterly, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)

    @api.multi
    def _compute_current_quarter(self):
        today = 'M'+date.today().strftime('%m')+'-'+ date.today().strftime('%Y')
        quarter_year = self.env['account.fiscal.period.lines'].search([('name','=',today)]).quarter
        quarter = re.split('-',quarter_year)
        for recs in self:
            recs.current_quarter=quarter
            
    @api.multi
    def _compute_last_year_current_quarter(self):
        today = 'M'+date.today().strftime('%m')+'-'+ date.today().strftime('%Y')
        year = int(date.today().strftime('%Y'))-1
        quarter_year = self.env['account.fiscal.period.lines'].search([('name','=',today)]).quarter
        quarter = re.split('-',quarter_year)
        for recs in self:
            recs.current_quarter=quarter+str(year)

    @api.multi
    def _search_current_quarter(self, operator, value):
        month= 'M'+date.today().strftime('%m')+'-'+ str(int(date.today().strftime('%Y')))
        quarter_year = self.env['account.fiscal.period.lines'].search([('name','=',month)]).quarter
        print quarter_year
        recs = self.search([('quarter_year', '=', quarter_year)])  
        return [('id', 'in', [x.id for x in recs])]
    
    @api.multi
    def _search_last_year_current_quarter(self, operator, value):
        month = 'M'+date.today().strftime('%m')+'-'+ str(int(date.today().strftime('%Y'))-1)
        year = int(date.today().strftime('%Y'))-1
        quarter_year = self.env['account.fiscal.period.lines'].search([('name','=',month)]).quarter
        quarter = re.split('-',quarter_year) 
        recs = self.search([('quarter_year', '=', quarter_year),('fin_yr','=',year)])  
        return [('id', 'in', [x.id for x in recs])]

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
    def action_create_budget_consolidate_quarter(self,quarter_count):
        scenario_type=['budget','minimum','stretch']
        name_list=[]
        type_list = ['revenue','income','expense']
        quarter_list = []
        for line in range(0,quarter_count):
            print line,'dfrfrd'
            new_date=datetime.datetime.now()-relativedelta(months=line*3)
            month = new_date.month
            year = new_date.year
            print new_date,'trtr'        
            if month<=3:
                cur_qua = 'Q'+str(1)+'-'+str(year), 'Q'+str(1)
                quarter_list.append((cur_qua))
            elif month<=6:
                cur_qua = 'Q'+str(2)+'-'+str(year), 'Q'+str(2)
                quarter_list.append((cur_qua))
            elif month<=9:
                cur_qua = 'Q'+str(3)+'-'+str(year), 'Q'+str(3)
                quarter_list.append((cur_qua))
            else:
                cur_qua = 'Q'+str(4)+'-'+str(year), 'Q'+str(4)
                quarter_list.append((cur_qua))       
        for qua, quarter in quarter_list:
            del_pre_obj = self.env['budget.consolidate.quarterly'].search([('quarter_year','=',qua)])            
            del_pre_obj.unlink()  
        
        for scenario in scenario_type:
            for budget_type in type_list:
                for qua, quarter in quarter_list:   
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
                    for line_names in self.env['budget.category.quarterly'].search([
                        ('budget_scenario','=',scenario),
                        ('quarter_year','=',qua),('name','=','Net Revenue'),('type','=',budget_type)]):
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
                        actual_offset += float(line_names.actual_offset)
                        i+=1
                    if i>0:
                        tid = self.env['budget.consolidate.quarterly'].search([
                            ('budget_scenario','=',scenario),
                            ('quarter_year','=',qua),
                            ('name','=','Net Revenue'),('type','=',budget_type)], limit=1)
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
                                       'type':line_names.type,
                                       'margin':line_names.margin,
                                       'visibility':line_names.visibility,
                                       })
                        else:
                            res = self.env['budget.consolidate.quarterly'].create({
                                                                        'budget_category_id':line_names.budget_category_id.id,
                                                                        'name':line_names.name,
                                                                        'actual_amount':actual_amount,
                                                                        'planned_amount':planned_amount,
                                                                        'sequence':line_names.sequence,
                                                                        'fin_yr':line_names.fin_yr,
                                                                        'quarter':quarter,
                                                                        'budget_scenario':line_names.budget_scenario,
                                                                        # 'var_amount':var_amount/i if i>0 else 0.00,
                                                                        # 'plan_margin':plan_margin/i if i>0 else 0.00,
                                                                        # 'actual_margin':actual_margin/i if i>0 else 0.00, 
                                                                        # 'var_margin':var_margin/i if i>0 else 0.00, 
                                                                        # 'plan_pct_nr':plan_pct_nr/i if i>0 else 0.00,
                                                                        # 'act_pct_nr':act_pct_nr/i if i>0 else 0.00,
                                                                        # 'yoy':yoy/i if i>0 else 0.00,
                                                                        'plan_offset':plan_offset/i if i>0 else 0.00,
                                                                        'actual_offset':actual_offset/i if i>0 else 0.00,
                                                                        'quarter_year':qua,
                                                                        'type':line_names.type,
                                                                        'margin':line_names.margin,
                                                                        'visibility':line_names.visibility,
                                                                        })
  
        for qua, quarter in quarter_list:    
            for line_names in self.env['budget.category.lines'].search([('budget_category_id.budget_scenario','=','budget'),('month','=','M01-'+ str(new_date.year))]):
                name_list.append(line_names.name)
            name_list = list(set(name_list))
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
                        for line_names in self.env['budget.category.quarterly'].search([
                            ('budget_scenario','=',scenario),
                            ('quarter_year','=',qua),('name','=',category),('type','=',budget_type)]):
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
                            actual_offset += float(line_names.actual_offset)
                            i+=1
                        if i>0:
                            tid = self.env['budget.consolidate.quarterly'].search([
                                ('budget_scenario','=',scenario),
                                ('quarter_year','=',qua),
                                ('name','=',category),('type','=',budget_type)], limit=1)
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
                                           'type':line_names.type,
                                           'margin':line_names.margin,
                                           'visibility':line_names.visibility,
                                           })
                            else:
                                res = self.env['budget.consolidate.quarterly'].create({
                                                                            'budget_category_id':line_names.budget_category_id.id,
                                                                            'name':line_names.name,
                                                                            'actual_amount':actual_amount,
                                                                            'planned_amount':planned_amount,
                                                                            'sequence':line_names.sequence,
                                                                            'fin_yr':line_names.fin_yr,
                                                                            'quarter':quarter,
                                                                            'budget_scenario':line_names.budget_scenario,
             
                                                                            'quarter_year':qua,
                                                                            'type':line_names.type,
                                                                            'margin':line_names.margin,
                                                                            'visibility':line_names.visibility,
                                                                            })
                                res._get_var_amount()             
            for scenario in scenario_type:
                    
                    for names in ["Dietary","Laboratory"]:
#                             print company.code, quarter,year, names,  scenario, budget_type
                        budget_mar_update = self.env['budget.consolidate.quarterly'].search([
                                            ('budget_category_id.budget_scenario','=',scenario),
                                            ('quarter','=',quarter),
                                            ('quarter_year','=',qua),
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
        
        scenario_type=['budget','minimum','stretch']
        name_list=[]
        type_list = ['revenue','income','expense']
        quarter_list = []
        for line in range(0,quarter_count):
            print line,'dfrfrd'
            new_date=datetime.datetime.now()-relativedelta(months=line*3)
            month = new_date.month
            year = new_date.year
            print new_date,'trtr'        
            if month<=3:
                cur_qua = 'Q'+str(1)+'-'+str(year), 'Q'+str(1)
                quarter_list.append((cur_qua))
            elif month<=6:
                cur_qua = 'Q'+str(2)+'-'+str(year), 'Q'+str(2)
                quarter_list.append((cur_qua))
            elif month<=9:
                cur_qua = 'Q'+str(3)+'-'+str(year), 'Q'+str(3)
                quarter_list.append((cur_qua))
            else:
                cur_qua = 'Q'+str(4)+'-'+str(year), 'Q'+str(4)
                quarter_list.append((cur_qua))       
        
        for qua, quarter in quarter_list: 
            for scenario in scenario_type:
                        for names in ["Dietary","Laboratory"]:
#                             print company.code, quarter,year, names,  scenario, budget_type
                            budget_mar_update = self.env['budget.consolidate.quarterly'].search([
                                                ('budget_category_id.budget_scenario','=',scenario),
                                                ('quarter','=',quarter),
                                                ('quarter_year','=',qua),
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
                                print total_act
                                        
     
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
                print formula.formula_single
                PLAN_PCT_NR=formula.formula_single
            elif formula.name=='ACT_PCT_NR':
                print formula.formula_single
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
            actual_net_cal=self.env['budget.consolidate.quarterly'].search([('name','=','Net Revenue'),('budget_scenario','=',lines.budget_scenario),('quarter','=',lines.quarter),('quarter_year','=',lines.quarter_year)])
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

class BudgetConsolidateYearly(models.Model):
    _name = "budget.consolidate.yearly"
    _description = "Budget Product Category Consolidate yearly view"
    _order = 'sequence'
     
    budget_category_id = fields.Many2one('budget.product.category', 'Budget', ondelete='cascade')
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
        year = []
        scenario = []
        for loop in domain:
            for in_loop in loop:
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
                         and "fin_yr" not in dom_loop]
        del domain[:]    
        if year or scenario:
            if year :
                domain.append(['fin_yr', 'in', year])
            if scenario :
                domain.append(['budget_scenario', 'in', scenario])    
        else :
            domain = domain
        for add_or in range(0,len(ft_domain)-1):
            domain.append('|')
        domain+=ft_domain
            
        return super(BudgetConsolidateYearly, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)

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
    def action_create_budget_consolidate_year(self):
        scenario_type=['budget','minimum','stretch']
        name_list=[]
        type_list = ['revenue','income','expense']
        date_now  = date.today()
        year_list = []
        cur_year = date_now.year
        year_list.append(cur_year)
        pre_year = date_now.year-1
        year_list.append(pre_year)

        del_pre_obj = self.env['budget.consolidate.yearly'].search([('fin_yr','in',year_list)])
        del_pre_obj.unlink()
        for year in year_list:
            for scenario in scenario_type:
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
                    print self.env['budget.category.yearly'].search([
                        ('budget_scenario','=',scenario),
                        ('year','=',year),('name','=','Net Revenue'),('type','=',budget_type)]),'----'
                    for line_names in self.env['budget.category.yearly'].search([
                        ('budget_scenario','=',scenario),
                        ('year','=',year),('name','=','Net Revenue'),('type','=',budget_type)]):
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
                        actual_offset += float(line_names.actual_offset)
                        i+=1
                    if i>0:
                        tid = self.env['budget.consolidate.yearly'].search([
                            ('budget_scenario','=',scenario),
                            ('fin_yr','=',year),
                            ('name','=','Net Revenue'),('type','=',budget_type)])
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
                                       'type':line_names.type,
                                       'margin':line_names.margin,
                                       'visibility':line_names.visibility,
                                       })
                        else:
                            res = self.env['budget.consolidate.yearly'].create({
                                                                        'budget_category_id':line_names.budget_category_id.id,
                                                                        'name':line_names.name,
                                                                        'actual_amount':actual_amount,
                                                                        'planned_amount':planned_amount,
                                                                        'sequence':line_names.sequence,
                                                                        'fin_yr':line_names.year,
                                                                        'budget_scenario':line_names.budget_scenario,
                                                                        # 'var_amount':var_amount/i if i>0 else 0.00,
                                                                        # 'plan_margin':plan_margin/i if i>0 else 0.00,
                                                                        # 'actual_margin':actual_margin/i if i>0 else 0.00, 
                                                                        # 'var_margin':var_margin/i if i>0 else 0.00, 
                                                                        # 'plan_pct_nr':plan_pct_nr/i if i>0 else 0.00,
                                                                        # 'act_pct_nr':act_pct_nr/i if i>0 else 0.00,
                                                                        # 'yoy':yoy/i if i>0 else 0.00,
                                                                        'plan_offset':plan_offset/i if i>0 else 0.00,
                                                                        'actual_offset':actual_offset/i if i>0 else 0.00,
                                                                        'quarter':line_names.quarter,
                                                                        'type':line_names.type,
                                                                        'margin':line_names.margin,
                                                                        'visibility':line_names.visibility,
                                                                        })

        for year in year_list:
            for line_names in self.env['budget.category.lines'].search([('budget_category_id.budget_scenario','=','budget'),('month','=','M01-'+ str(date_now.year))]):
                name_list.append(line_names.name)
            name_list = list(set(name_list))
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
                        for line_names in self.env['budget.category.yearly'].search([
                            ('budget_scenario','=',scenario),
                            ('year','=',year),('name','=',category),('type','=',budget_type)]):
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
                            actual_offset += float(line_names.actual_offset)
                            i+=1
                        if i>0:
                            tid = self.env['budget.consolidate.yearly'].search([
                                ('budget_scenario','=',scenario),
                                ('fin_yr','=',year),
                                ('name','=',category),('type','=',budget_type)], limit=1)
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
                                           'type':line_names.type,
                                           'margin':line_names.margin,
                                           'visibility':line_names.visibility,
                                           })
                            else:
                                res     = self.env['budget.consolidate.yearly'].create({
                                                                            'budget_category_id':line_names.budget_category_id.id,
                                                                            'name':line_names.name,
                                                                            'actual_amount':actual_amount,
                                                                            'planned_amount':planned_amount,
                                                                            'sequence':line_names.sequence,
                                                                            'fin_yr':line_names.year,
                                                                            'budget_scenario':line_names.budget_scenario,
                                                                            # 'var_amount':var_amount/i if i>0 else 0.00,
                                                                            # 'plan_margin':plan_margin/i if i>0 else 0.00,
                                                                            # 'actual_margin':actual_margin/i if i>0 else 0.00, 
                                                                            # 'var_margin':var_margin/i if i>0 else 0.00, 
                                                                            # 'plan_pct_nr':plan_pct_nr/i if i>0 else 0.00,
                                                                            # 'act_pct_nr':act_pct_nr/i if i>0 else 0.00,
                                                                            # 'yoy':yoy/i if i>0 else 0.00,
                                                                            'plan_offset':plan_offset/i if i>0 else 0.00,
                                                                            'actual_offset':actual_offset/i if i>0 else 0.00,
                                                                            'quarter':line_names.quarter,
                                                                            'type':line_names.type,
                                                                            'margin':line_names.margin,
                                                                            'visibility':line_names.visibility,
                                                                            })
                                
                                res._get_var_amount(line_names.year)
            for scenario in scenario_type:  
                for names in ["Dietary","Laboratory"]:
    #                             print company.code, quarter,year, names,  scenario, budget_type
                    budget_mar_update = self.env['budget.consolidate.yearly'].search([
                                        ('budget_category_id.budget_scenario','=',scenario),
                                        ('fin_yr','=',str(year)),
                                        ('name','in',[names])
                                        ])
                    print budget_mar_update
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
                        print total_act
                                
    
    @api.multi
    def _change_margin_vals(self):
        
        scenario_type=['budget','minimum','stretch']
        name_list=[]
        date_now  = date.today()
        year_list = []
        cur_year = date_now.year
        year_list.append(cur_year)
        pre_year = date_now.year-1
        year_list.append(pre_year)  
        for year in year_list:
            print year
            for scenario in scenario_type:  
                for names in ["Dietary","Laboratory"]:
    #                             print company.code, quarter,year, names,  scenario, budget_type
                    budget_mar_update = self.env['budget.consolidate.yearly'].search([
                                        ('budget_category_id.budget_scenario','=',scenario),
                                        ('fin_yr','=',str(year)),
                                        ('name','in',[names])
                                        ])
                    print budget_mar_update
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
                        print total_act
                    
                        
    @api.multi
    def _get_var_amount(self,year):
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
#             date_now  = date.today()
            cur_year = year
            actual_net_cal=self.env['budget.consolidate.yearly'].search([('name','=','Net Revenue'),('budget_scenario','=',lines.budget_scenario),('fin_yr','=',cur_year)])
            if actual_net_cal:
                if actual_net_cal.actual_amount:
                    ACTUAL_NET=float(actual_net_cal.actual_amount)
                if actual_net_cal.planned_amount:
                    PLAN_NET=float(actual_net_cal.planned_amount)
                
#             ACTUAL_LAST=float(lines.actuals_previous_year)
            plan_offset=float(lines.plan_offset)
            actual_offset=float(lines.actual_offset)
            print cur_year,ACTUAL_NET
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