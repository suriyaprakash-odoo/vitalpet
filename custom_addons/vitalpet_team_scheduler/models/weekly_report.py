from odoo import api, fields, models, tools, _
import datetime
from odoo.exceptions import UserError, ValidationError
from babel.util import missing
import itertools
import operator
import re
# from matplotlib.testing.jpl_units import day


class ActualLaborWeekly(models.Model):
    _name = 'actual.labor.weekly'    
    _order = 'id desc'
                
    def time_to_float(self, hours):
        list = [x.strip() for x in hours.split(':')]
        hrs = int(list[0])
        if int(list[1]) > 0:
            mins = float(list[1]) * 100 / 60
            mins = mins / 100
        else:
            mins = 0
        return hrs + mins
    
    company_id = fields.Many2one("res.company", "Company")
    year = fields.Char("Year")
    quarter = fields.Char("Fiscal Quarter")
    month = fields.Char("Month")
    week = fields.Char("Week")
    fin_week = fields.Many2one('account.fiscal.period.week', 'Fiscal Week')  
    fin_month = fields.Many2one('account.fiscal.period.lines', 'Fiscal Month') 
    fin_year = fields.Many2one('account.fiscal.periods', 'Fiscal Year')
    revenue_budget = fields.Float("Budget Net Revenue",  default=0.0)
    revenue_actual = fields.Float("Actual Net Revenue",  default=0.0)
    actual_labor_weekly = fields.Float("Actual Labor Cost",  default=0.0)
    labor_budget_per = fields.Float("Budget Labor %",  default=0.0,group_operator="avg")
    actual_labor_per = fields.Float("Actual Labor %",  default=0.0,group_operator="avg")
    variance_revenue = fields.Float("Variance %",  default=0.0,group_operator="avg")
    variance_labor = fields.Float("Labor Variance %",  default=0.0,group_operator="avg")

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        result = super(ActualLaborWeekly, self).read_group(domain, fields, groupby, offset, limit=limit,orderby=orderby,lazy=True)
        res = result
        cusRes=[]
        for re in reversed(res):                
            if re['revenue_actual'] > 0:
                re['actual_labor_per'] = (re['actual_labor_weekly']/re['revenue_actual'])*100
            if re['labor_budget_per'] > 0:
                re['variance_labor'] = ((re['labor_budget_per'] - re['actual_labor_per'])/re['labor_budget_per'])
            if re['revenue_budget'] > 0:
                re['variance_revenue'] = ((re['revenue_actual'] - re['revenue_budget'])/re['revenue_budget'])*100
            cusRes.append(re)
        return cusRes

    @api.multi
    def redirect_actual(self):
        hr_period= self.env['hr.period'].search([('company_id','=',self.company_id.id),('date_start', '<=', self.fin_week.date_start),('date_stop', '>=', self.fin_week.date_start)])
        if hr_period:
            actual_id=self.env['actual.labour.cost'].search([('name','=',hr_period.id)])

            if actual_id:
            
                return {
                    'name': ('Actual labor cost'),
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'actual.labour.cost',
                    'view_id': self.env.ref('vitalpet_team_scheduler.actual_labour_form').id,                    
                    'res_id': actual_id.id,
                    'type': 'ir.actions.act_window',
                    'target': "new",
                    'context': self.env.context,
                    'flags': {'initial_mode': 'view'},
                }
            else:
                raise UserError(_('Actual labor cost is not found'))
        
        
    @api.multi
    def get_month_by_date(self,day): 
        day_start=1
        date=datetime.datetime.strptime(str(day), "%Y-%m-%d")+ datetime.timedelta(days=day_start)
        weekNumber = date.isocalendar()[1]   
        if weekNumber<=4:
            month=1
        elif weekNumber<=8:
            month=2
        elif weekNumber<=13:
            month=3
        elif weekNumber<=17:
            month=4
        elif weekNumber<=21:
            month=5
        elif weekNumber<=26:
            month=6
        elif weekNumber<=30:
            month=7
        elif weekNumber<=34:
            month=8
        elif weekNumber<=39:
            month=9
        elif weekNumber<=43:
            month=10
        elif weekNumber<=47:
            month=11
        else:
            month=12
            
        if month<=3:
            quarter=1
        elif month<=6:
            quarter=2
        elif month<=9:
            quarter=3
        else:
            quarter=4
            
        year=date.isocalendar()[0]
        
        
        return [year,quarter,month,weekNumber]
    
   
    @api.multi
    def check_active_contracts(self, job_id, start_date, end_date):        
        vals=[]
        contract_lists=self.env['hr.contract'].sudo().search([
                ('contract_job_ids.job_id', 'in', [job_id]),
                ('salary_computation_method', 'in', ['hourly','yearly']),
                ('state', '!=', 'draft'),
                ('date_end', '=', False),
                ('date_start', '<=', end_date)
            ])
        
        if contract_lists:
            for contract_list in contract_lists:
                vals.append(contract_list)
                
        contract_lists=self.env['hr.contract'].sudo().search([
                ('contract_job_ids.job_id', 'in', [job_id]),
                ('salary_computation_method', 'in', ['hourly','yearly']),
                ('state', '!=', 'draft'),
                ('date_end', '!=', False),
                ('date_start', '<=', end_date),
                ('date_end', '>=', start_date)
            ])
        
        if contract_lists:
            for contract_list in contract_lists:                
                vals.append(contract_list)
        
        return vals
                            

    def cron_act_labor_weekly(self):
        date=datetime.date.today()
#         date=datetime.datetime.strptime("2018-09-28", "%Y-%m-%d")
        
        
        for i in range(10):
            company= self.env['res.company'].search([('daily_report','=',True)])
            for company_id in company:
                day_week=(i*7)*-1
                date_new=date+ datetime.timedelta(days=day_week)
#                date_details=self.get_month_by_date(date_new)        

                account_fiscal_periods = self.env['account.fiscal.periods'].search([('calendar_type', '=', company_id.calendar_type.id)])
                
                tid_week = self.env['account.fiscal.period.week'].search([('account_fiscal_period_week_id','in',[a.id for a in account_fiscal_periods]),('date_start', '<=', date_new),('date_end', '>=', date_new)])
                tid_period = self.env['account.fiscal.period.lines'].search([('account_fiscal_period_id','in',[a.id for a in account_fiscal_periods]),('date_start', '<=', date_new),('date_end', '>=', date_new)])
                 
                year=tid_period.account_fiscal_period_id.id
                year_str = tid_period.year
                
                quarter_split = re.split('-',tid_period.quarter)
                quarter_num = quarter_split[0]
                quarter=quarter_num[1:] 
                
                month=tid_period.id
                
                week_id = tid_week.id
                week=tid_week.name
                week_split = re.split('-',week) 
                week_num = int(week_split[1])
                                
                dtotal=dtotal_budget=0                
                if int(year_str)>=2018:
                    sales_summary=self.env['sales.summary'].search([('company_id', '=',company_id.id),('account_fiscal_periods_year','=',year),('fiscal_week','=',week_id)])
                    for summary in sales_summary:
                        rev_actual=self.env['labor.budget.list'].search([('sheet_id.company_id', '=',company_id.id),('date','=',summary.date)])
                        if rev_actual:
                            rev_actual.a_actual_rev=summary.dTotal
                            dtotal+=summary.dTotal
                               
                    date_from = datetime.datetime.strptime(tid_week.date_start, "%Y-%m-%d")
                    date_to = datetime.datetime.strptime(tid_week.date_end, "%Y-%m-%d")
                    while (date_to >= date_from):
                        rev_actuals=self.env['labor.budget.list'].search([('sheet_id.company_id', '=',company_id.id),('date','=',date_from)])
                        if rev_actuals:
                            for rev_actual in rev_actuals:
                                dtotal_budget+=rev_actual.amount                         
                        date_from = date_from + datetime.timedelta(days=1)
    
                    labor_budget=self.env['labor.budget.list'].search([('sheet_id.company_id', '=',company_id.id),('year','=',year_str),('week','=',week_num)])                
                    rate=0.0
                    
                    
                    date_from = datetime.datetime.strptime(tid_week.date_start, "%Y-%m-%d")
                    date_to = datetime.datetime.strptime(tid_week.date_end, "%Y-%m-%d")
                    
                    job_list = self.env['timesheet.config'].search([('company_id', '=', company_id.id)])
                    if job_list:
                        for job in job_list.hr_job_ids:
                            contract_lists=self.check_active_contracts(job.name.id, date_from, date_to)
#                             contract_lists=self.env['hr.contract'].sudo().search([('contract_job_ids.job_id', 'in', [job.name.id]),('salary_computation_method', 'in', ['hourly','yearly']), ('state', 'in', ['open','pending'])])
                            if contract_lists:               
                                bi_weekly=self.env['hr.work.hours'].sudo().search_count([('date', '>=', date_from),('date', '<=', date_to),('job_id.company_id', '=', company_id.id)])
                                
                                for contract_list in contract_lists:
                                    emp=contract_list.employee_id 
                                    emp_hours=emp_ot_rate=pto_hrs=0                               
                                    for budget in labor_budget:
                                        
                                        pto_hrs=0.0                                              
                                                                               
                                        date_of_col=datetime.datetime.strptime(budget.date, "%Y-%m-%d")                                            
                                        paid_hours_leaves=unpaid_hours_leaves=0
                                        hr_paid_holidays=self.env['hr.holidays'].search([('employee_id', '=', emp.id),('holiday_status_id.paid_leave', '=', True),('date_from', '<=', date_of_col),('date_to', '>=', date_of_col)], limit=1)
                                        if hr_paid_holidays:                    
                                            paid_days=(datetime.datetime.strptime(hr_paid_holidays.date_to, "%Y-%m-%d")-datetime.datetime.strptime(hr_paid_holidays.date_from, "%Y-%m-%d")).days
                                            paid_days+=1
                                            pto_hrs+=hr_paid_holidays.number_of_hours_temp/paid_days                                            
                                        
                                        if pto_hrs>0:
                                            if job.salary_applicable: 
                                                    for contract in contract_list.contract_job_ids:
                                                        if contract.job_id.id == job.name.id:
                                                            holiday_rate=0
                                                            if contract_list.salary_computation_method=='hourly':
                                                                emp_ot_rate=contract.hourly_rate
                                                                holiday_rate=contract.hourly_rate*pto_hrs
                                                            rate=rate+holiday_rate
                                                            
                                        attendance_i=0  
                                        work_hours=[]
                                        if bi_weekly >0:                                             
                                            work_hours=self.env['hr.work.hours'].search([('date', '=', date_of_col),('employee_id', '=', emp.id),('job_id', '=', job.name.id)])
                                            attendance_i=0
                                        else:                                                             
                                            time1 =  date_of_col+ datetime.timedelta(hours=00, minutes=00, seconds=00)
                                            time2 = date_of_col + datetime.timedelta(hours=23, minutes=59, seconds=59)                                        
                                            work_hours=self.env['hr.attendance'].sudo().search([
                                                    ('check_in', '>=', str(time1)), ('check_out', '<=', str(time2)),
                                                    ('employee_id', '=', emp.id),('activity_id.job_id', '=', job.name.id)])   
                                            attendance_i=1
                                        if work_hours:
                                            mutliple_hrs=0
                                            for work_hr in work_hours:        
                                                hr_atten_work_hours=0.0
                                                if attendance_i==0:
                                                    hr_atten_work_hours=work_hr.work_hours
                                                else:
                                                    hr_atten_work_hours=self.time_to_float(work_hr.time_difference)
                                                emp_hours+=hr_atten_work_hours                    
                                                if job.salary_applicable: 
#                                                     contracts = self.env['hr.contract'].sudo().search(
#                                                                                 [('employee_id', '=', emp.id),
#                                                                                  ('salary_computation_method', 'in', ['hourly','yearly']), ('state', 'in', ['open','pending'])])
                                                    
                                                    for contract in contract_list.contract_job_ids:
                                                        if contract.job_id.id == job.name.id:
                                                            holiday_rate=0
                                                            if contract_list.salary_computation_method=='hourly':
                                                                emp_ot_rate=contract.hourly_rate
                                                                holiday=self.env['hr.holidays.public.line'].sudo().search_count([('year_id.company_id','=',company_id.id),('date','=',date_of_col.strftime('%Y-%m-%d'))])
                                                                if holiday==0:
                                                                    holiday_rate=contract.hourly_rate*hr_atten_work_hours
                                                                else:
                                                                    holiday_rate=contract.hourly_rate*hr_atten_work_hours*(job.public_holidays/100)
                                                            elif contract_list.salary_computation_method=='yearly':
                                                                if mutliple_hrs==0:
                                                                    mutliple_hrs=1                                                                                                                                                                                      
                                                                    if job_list.company_id.Sunday:
                                                                        holiday_rate=(contract_list.wage/(52*7))                                                
                                                                    elif job_list.company_id.Saturday:
                                                                        if date_of_col.weekday()<6:
                                                                            holiday_rate=(contract_list.wage/(52*6))                                                
                                                                    else:
                                                                        if date_of_col.weekday()<5:
                                                                            holiday_rate=(contract_list.wage/(52*5))                                                                    
                                                            rate=rate+holiday_rate
                                        else:
                                                                                     
                                            if job.salary_applicable: 
#                                                 contracts = self.env['hr.contract'].sudo().search(
#                                                                             [('employee_id', '=', emp.id),
#                                                                              ('salary_computation_method', 'in', ['yearly']), ('state', 'in', ['open','pending'])])
                                                for contract in contract_list.contract_job_ids:
                                                    if contract.job_id.id == job.name.id:
                                                        holiday_rate=0                                                                                                                                                                                     
                                                        if job_list.company_id.Sunday:
                                                            holiday_rate=(contract_list.wage/(52*7))                                                
                                                        elif job_list.company_id.Saturday:
                                                            if date_of_col.weekday()<6:
                                                                holiday_rate=(contract_list.wage/(52*6))                                                
                                                        else:
                                                            if date_of_col.weekday()<5:
                                                                holiday_rate=(contract_list.wage/(52*5))
                                                        rate=rate+holiday_rate
                                    if (emp_hours-pto_hrs)>40:
                                        rate+=(emp_hours-pto_hrs-40)*emp_ot_rate/2            
                    if dtotal>0:
                        actual_labor_per=(rate/dtotal)*100
                    else:
                        actual_labor_per=0
                        
                    labor_budget=self.env['labor.budget.list'].search([('sheet_id.company_id', '=',company_id.id),('year','=',year_str),('week','=',week_num)], limit=1)
                    labor_per=labor_budget.sheet_id.week1_per
                    act_week=self.env['actual.labor.weekly'].search([('company_id', '=',company_id.id),('fin_year','=',year),('fin_week','=',week_id )])
                    
                    if labor_per>0:
                        dtotal_budget=dtotal_budget*(1/labor_per)*100
                    else:
                        dtotal_budget=0
                    
                    variance_revenue=variance_labor=0
                    if dtotal_budget>0:
                        variance_revenue = ((dtotal-dtotal_budget)/dtotal_budget)*100
                    if labor_per>0:
                        variance_labor = ((labor_per-actual_labor_per)/labor_per)*100
                    if act_week:
                        act_week.revenue_actual=dtotal
                        act_week.revenue_budget=dtotal_budget
                        act_week.actual_labor_weekly=rate
                        act_week.labor_budget_per=labor_per
                        act_week.actual_labor_per=actual_labor_per
                        act_week.variance_revenue=variance_revenue
                        act_week.variance_labor=variance_labor
                    else:
                        self.env['actual.labor.weekly'].create({
                            'company_id': company_id.id,
                            'fin_year': year,
                            'quarter': str(year_str)+"-"+str(quarter),
                            'fin_month': month,
                            'fin_week': week_id,                        
                            'revenue_actual': dtotal,                        
                            'revenue_budget': dtotal_budget,                    
                            'actual_labor_weekly': rate,    
                            'labor_budget_per': labor_per,           
                            'actual_labor_per': actual_labor_per,      
                            'variance_revenue': variance_revenue,      
                            'variance_labor': variance_labor, 
                        })
    
                    

    