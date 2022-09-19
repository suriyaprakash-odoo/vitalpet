# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, tools, _
import datetime
from odoo.exceptions import UserError, ValidationError
from babel.util import missing
import itertools
import operator
from collections import defaultdict
import re

class ActualLaborCost(models.Model):
    _name = 'actual.labour.cost'
    
        
    def time_to_float(self, hours):
        list = [x.strip() for x in hours.split(':')]
        hrs = int(list[0])
        if int(list[1]) > 0:
            mins = float(list[1]) * 100 / 60
            mins = mins / 100
        else:
            mins = 0
        return hrs + mins
    
    def float_time(self,time_value):  
        hours, minutes = ([int(x)]  for x in str(time_value).split(".",1))
        minutes=minutes[0]
        hours=hours[0]
        
        if minutes > 0:
            minutes = minutes*60/100
        
        if len(str(hours))==1:
            hours="0"+str(hours)        
        if len(str(minutes))==1:
            minutes="0"+str(minutes)
        
        formated_time = str(hours)+":"+str(minutes)
        return formated_time
    
    def add_time(self, time, time2):
        list = [x.strip() for x in time.split(':')]
        list2 = [x.strip() for x in time2.split(':')]

        hrs = int(list[0]) + int(list2[0])
        mins = int(list[1]) + int(list2[1])

        if mins > 59:
            hrs = hrs + 1
            mins = mins - 60

        if len(str(hrs)) == 1:
            hrs = "0" + str(hrs)
        if len(str(mins)) == 1:
            mins = "0" + str(mins)

        tot = str(hrs) + ":" + str(mins)
        return tot

    def amount_cals(self, hours, rate):
        list = [x.strip() for x in hours.split(':')]
        hrs = int(list[0])
        if int(list[1]) > 0:
            mins = float(list[1]) * 100 / 60
            mins = mins / 100
        else:
            mins = 0
        return rate * (hrs + mins)

    @api.multi
    def get_week_by_date(self,day): 
        day_start=1
        date=datetime.datetime.strptime(str(day), "%Y-%m-%d %H:%M:%S")+ datetime.timedelta(days=day_start)
        weekNumber = date.isocalendar()[1]    
        return weekNumber
    
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

        return month
    
    @api.multi
    def get_year_by_date(self,day): 
        day_start=1
        date=datetime.datetime.strptime(str(day), "%Y-%m-%d")+ datetime.timedelta(days=day_start)
        return date.isocalendar()[0]
    
    
    def ot_time(self, time):
        list = [x.strip() for x in time.split(':')]
        hrs = int(list[0])
        mins = int(list[1])
        
        if hrs >= 40:
            hrs = hrs-40
            mins = mins
        else:
            hrs=0
            mins=0
        if len(str(hrs)) == 1:
            hrs = "0" + str(hrs)
        if len(str(mins)) == 1:
            mins = "0" + str(mins)

        tot = str(hrs) + ":" + str(mins)
        return tot
    
    def actual_list(self, from_date, to_date, company_id,timesheet_period,week_no):
        if week_no==1:
            result=self.actual_list_cal(from_date, to_date, company_id,timesheet_period,week_no)
            
                
            result['line_color1']='normal'     
            if result['week1'][3] <result['week1'][4]:
                result['line_color1']='red'
                
            result1=self.actual_list_cal(from_date, to_date, company_id,timesheet_period,week_no+1)
            result['week2']=result1['week1']
                
            result['line_color2']='normal'     
            if result1['week1'][3] <result1['week1'][4]:
                result['line_color2']='red'
                
            return result
        else:
            result=self.actual_list_cal(from_date, to_date, company_id,timesheet_period,week_no)
            result['week2']=result['week1']
            
                
            result['line_color2']='normal'     
            if result['week1'][3] <result['week1'][4]:
                result['line_color2']='red'
                
            result1=self.actual_list_cal(from_date, to_date, company_id,timesheet_period,week_no-1)
            result['week1']=result1['week1']  
            result['line_color1']='normal'     
            if result['week1'][3] <result['week1'][4]:
                result['line_color1']='red'                
            return result
        
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
    
    def actual_list_cal(self, from_date, to_date, company_id,timesheet_period,week_no):
        result = {}
        dates = []
        budget = []
        budget_rev = []
        act_rev = []
        act_rev_val = []
        bud_lab_forecast=[]
        rev_budget = []
        rev_budget_act=[]
        net_rev_act = []
        
        from_date = datetime.datetime.strptime(from_date, "%Y-%m-%d")
        to_date = datetime.datetime.strptime(to_date, "%Y-%m-%d")
        
        if week_no==1:
            to_date = from_date + datetime.timedelta(days=6)
        else:
            from_date = from_date + datetime.timedelta(days=7)
            
        date_from = from_date
        date_to = to_date      
        
        sheet_id_list= self.env['staff.planning'].search([('name', '=', timesheet_period)])

        sheet_id=sheet_id_list.id
        result['week_no']=week_no
        result['sheet_id']=sheet_id
        
        if week_no==1:
            percent = sheet_id_list.week1_per
        else:
            percent = sheet_id_list.week2_per
            
        if not percent>0:
            raise UserError(_('Labor Budget Percentage is 0.'))
        
        result['percent'] =  str("{:.2f}".format(percent))   
        rev_budget_act_tot=budget_rev_tot=bud_lab_forecast_tot=net_rev_tot=overall_ot_total=0.0
        
        while (date_to >= date_from):
            date_new_antr = {}
            date_new_antr['d1'] = date_from.strftime('%a <br />%b %d')
            date_new_antr['d2'] = date_from.strftime('%Y-%m-%d')
            
            holiday=self.env['hr.holidays.public.line'].sudo().search_count([('year_id.company_id','=',company_id),('date','=',date_from.strftime('%Y-%m-%d'))])            
            date_new_antr['holiday']=0
            if holiday>=1:
                date_new_antr['holiday']=1
            
            dates.append(date_new_antr)

            budget_val = {}
            cost =lab_forecast= rev_budget=0.0
            budget_list = self.env['labor.budget.list'].sudo().search([('sheet_id', '=', sheet_id),('date', '=', date_from.strftime('%Y-%m-%d'))])            
            if budget_list:
                cost=budget_list.amount
                lab_forecast=budget_list.forcast_amount
                rev_budget=budget_list.bud_revenue_amount
            if cost>0 and percent>0:
                budget_rev_val=cost*100/percent
            else:
                budget_rev_val=0
                
        
            net_rev=0
            sales_summary = self.env['sales.summary'].sudo().search([('company_id', '=', company_id),
                                                              ('date', '=', date_from.strftime('%Y-%m-%d'))])

            for total_sales in sales_summary:
                net_rev+=total_sales.dTotal
                net_rev_tot+=total_sales.dTotal
            
            rev_budget_act_tot+=rev_budget
            budget_rev_tot+=cost
            bud_lab_forecast_tot+=lab_forecast
            
            
            act_rev_val.append(net_rev) 
            cost=str("{:.2f}".format(cost))
            lab_forecast= str("{:.2f}".format(lab_forecast))
            budget.append(cost)
            rev_budget_act.append( str("{:.2f}".format(rev_budget)))
            bud_lab_forecast.append(lab_forecast)                        
            budget_rev.append(str("{:.2f}".format(budget_rev_val)))
            net_rev_act.append( str("{:.2f}".format(net_rev)))
              
            date_from = date_from + datetime.timedelta(days=1)
            
        if week_no==1:
            result['ot_amount']= str("{:.2f}".format(sheet_id_list.week1_ot))
            bud_lab_forecast_tot+=sheet_id_list.week1_ot
        else:
            result['ot_amount']=str("{:.2f}".format(sheet_id_list.week2_ot))
            bud_lab_forecast_tot+=sheet_id_list.week2_ot
        result['budget'] = budget
        result['budget_rev'] = budget_rev
        result['bud_lab_forecast'] = bud_lab_forecast
        result['rev_budget_act'] = rev_budget_act
        result['net_rev_act'] = net_rev_act
        result['rev_budget_act_tot'] = str("{:.2f}".format(rev_budget_act_tot))
        result['budget_rev_tot'] = str("{:.2f}".format(budget_rev_tot))
        result['bud_lab_forecast_tot'] = str("{:.2f}".format(bud_lab_forecast_tot))
        result['net_rev_act_tot'] = str("{:.2f}".format(net_rev_tot))
        result['dates'] = dates
        
        hours_list = []
        act_list = []
         
        job_list = self.env['timesheet.config'].search([('company_id', '=', company_id)])
        if job_list:
            for job in job_list.hr_job_ids:     
                tot_sun = "00:00"
                tot_mon = "00:00"
                tot_tues = "00:00"
                tot_wed = "00:00"
                tot_thurs = "00:00"
                tot_fri = "00:00"
                tot_sat = "00:00"
                hrs_job={}
                hrs_job['job']=job.name.name
                hrs_job['list']=[]
                
                act_job={}
                act_job['list']=[]
                job_total_costs=0.0
                
                

                contract_lists=self.check_active_contracts(job.name.id, from_date, to_date)
#                 contract_lists=self.env['hr.contract'].sudo().search([('contract_job_ids.job_id', 'in', [job.name.id]),('salary_computation_method', 'in', ['hourly','yearly']), ('state', 'in', ['open','pending'])])
                if contract_lists:
                    date_from = from_date
                    date_to = to_date
                    
                    bi_weekly=self.env['hr.work.hours'].sudo().search_count([('date', '>=', date_from),('date', '<=', date_to),('job_id.company_id', '=', company_id)])
                    
                    
                    for contract_list in contract_lists:
                        emp=contract_list.employee_id
                        date_from = from_date
                        date_to = to_date
                        hrs_emp={}
                        hrs_emp['name']=emp.name
                        hrs_emp['hours']=[]
                        
                        emp_total=0.0
                        emp_total_hrs=0.0
                        pto_hrs=0.0
                        pto_total_hrs=0.0 
                        pto_rate=0.0                         
                        act_rate=[]
                        
                        emp_ot_rate=0  
                        while (date_to >= date_from):   
                            rate=0.0                         
                            emp_hrs=0.0
                            pto_hrs_current=0
                            
                            paid_hours_leaves=unpaid_hours_leaves=0
                            hr_paid_holidays=self.env['hr.holidays'].sudo().search([('employee_id', '=', emp.id),('holiday_status_id.paid_leave', '=', True),('date_from', '<=', date_from),('date_to', '>=', date_from)], limit=1)
                            if hr_paid_holidays:                    
                                paid_days=(datetime.datetime.strptime(hr_paid_holidays.date_to, "%Y-%m-%d")-datetime.datetime.strptime(hr_paid_holidays.date_from, "%Y-%m-%d")).days
                                paid_days+=1
                                pto_hrs_current=hr_paid_holidays.number_of_hours_temp/paid_days
                                pto_hrs+=pto_hrs_current
                            if pto_hrs_current>0: 
                                if job.salary_applicable: 
#                                     contracts = self.env['hr.contract'].sudo().search(
#                                                                 [('employee_id', '=', emp.id),
#                                                                  ('salary_computation_method', 'in', ['hourly']), ('state', 'in', ['open','pending'])])
#                                     
                                    for contract in contract_list.contract_job_ids:
                                        if contract.job_id.id == job.name.id:
                                            holiday_rate=0
                                            if contract_list.salary_computation_method=='hourly':
                                                emp_ot_rate=contract.hourly_rate
                                                holiday_rate=contract.hourly_rate*pto_hrs_current
                                            rate=rate+holiday_rate
                                            pto_rate=pto_rate+holiday_rate
                            attendance_i=0  
                            work_hours=[]
                            if bi_weekly >0:
                                work_hours=self.env['hr.work.hours'].sudo().search([('date', '=', date_from),('employee_id', '=', emp.id),('job_id', '=', job.name.id)])
                                attendance_i=0   
                            else:
                                                                                        
                                time1 = date_from + datetime.timedelta(hours=00, minutes=00, seconds=00)
                                time2 = date_from + datetime.timedelta(hours=23, minutes=59, seconds=59)
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
                                    
                                    emp_hrs=emp_hrs+hr_atten_work_hours
                                    emp_total_hrs=emp_total_hrs+hr_atten_work_hours
                                    
                                    
                                    if job.salary_applicable: 
#                                         contracts = self.env['hr.contract'].sudo().search(
#                                                                     [('employee_id', '=', emp.id),
#                                                                      ('salary_computation_method', 'in', ['hourly','yearly']), ('state', 'in', ['open','pending'])])
#                                         
                                        for contract in contract_list.contract_job_ids:
                                            if contract.job_id.id == job.name.id:
                                                holiday_rate=0
                                                if contract_list.salary_computation_method=='hourly':
                                                    emp_ot_rate=contract.hourly_rate
                                                    holiday=self.env['hr.holidays.public.line'].sudo().search_count([('year_id.company_id','=',company_id),('date','=',date_from.strftime('%Y-%m-%d'))])
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
                                                            if date_from.weekday()<6:
                                                                holiday_rate=(contract_list.wage/(52*6))                                              
                                                        else:
                                                            if date_from.weekday()<5:
                                                                holiday_rate=(contract_list.wage/(52*5))
                                                
                                                rate=rate+holiday_rate
                                                emp_total=emp_total+holiday_rate
                                                
                            else:
                                 
                                    if job.salary_applicable: 
#                                         contracts = self.env['hr.contract'].sudo().search(
#                                                                     [('employee_id', '=', emp.id),
#                                                                      ('salary_computation_method', 'in', ['yearly']), ('state', 'in', ['open','pending'])])
                                        for contract in contract_list.contract_job_ids:
                                            if contract.job_id.id == job.name.id:
                                                holiday_rate=0                                                                                                                                                                                     
                                                if job_list.company_id.Sunday:
                                                    holiday_rate=(contract_list.wage/(52*7))                                                
                                                elif job_list.company_id.Saturday:
                                                    if date_from.weekday()<6:
                                                        holiday_rate=(contract_list.wage/(52*6))                                                
                                                else:
                                                    if date_from.weekday()<5:
                                                        holiday_rate=(contract_list.wage/(52*5))
                                                            
                                                rate=rate+holiday_rate
                                                emp_total=emp_total+holiday_rate
                                                
                                        
                            hrs_emp_fil={}
                            hrs_emp_fil['hrs']=self.float_time("{:.2f}".format(emp_hrs+pto_hrs_current))
                            hrs_emp_fil['pto_hrs']=self.float_time("{:.2f}".format(pto_hrs_current))
                            hrs_emp_fil['pto']=''
                            if pto_hrs_current>0:
                                hrs_emp_fil['pto']='Yes'
                                
                            hrs_emp['hours'].append(hrs_emp_fil)

                            act_rate.append(rate)
                            date_from = date_from + datetime.timedelta(days=1)
                            
                        hrs_emp['emp_total_hrs']= self.float_time("{:.2f}".format(emp_total_hrs+pto_hrs))
                        hrs_emp['emp_ot_hrs']= self.ot_time(self.float_time("{:.2f}".format(emp_total_hrs)))      
                        emp_ot_amount=0
                            
                        if (emp_total_hrs-pto_hrs)>40:       
                                emp_ot_amount= emp_ot_rate*(emp_total_hrs-pto_hrs-40)/2                                
                                overall_ot_total+=emp_ot_amount
                            
                        job_total_costs=job_total_costs+emp_total+emp_ot_amount+pto_rate
                        hrs_emp['emp_total']= str("{:.2f}".format(emp_total+emp_ot_amount+pto_rate))
                        
                        
                            
                        hrs_job['list'].append(hrs_emp)
                        act_list.append(act_rate) 
                        tot_sun = self.add_time(tot_sun, hrs_emp['hours'][0]['hrs'])
                        tot_mon = self.add_time(tot_mon, hrs_emp['hours'][1]['hrs'])
                        tot_tues = self.add_time(tot_tues, hrs_emp['hours'][2]['hrs'])
                        tot_wed = self.add_time(tot_wed, hrs_emp['hours'][3]['hrs'])
                        tot_thurs = self.add_time(tot_thurs, hrs_emp['hours'][4]['hrs'])
                        tot_fri = self.add_time(tot_fri, hrs_emp['hours'][5]['hrs'])
                        tot_sat = self.add_time(tot_sat, hrs_emp['hours'][6]['hrs'])

                hrs_job['sun'] = tot_sun
                hrs_job['mon'] = tot_mon
                hrs_job['tues'] = tot_tues
                hrs_job['wed'] = tot_wed
                hrs_job['thurs'] = tot_thurs
                hrs_job['fri'] = tot_fri
                hrs_job['sat'] = tot_sat
                hrs_job['job_total_costs']=str("{:.2f}".format(job_total_costs))
                hours_list.append(hrs_job)
              
        testDict = defaultdict(float)
        
        for act_lists in act_list:
            i=0
            for act_li in act_lists:
                testDict[i] += act_li
                i+=1
        i=0
        tub=[]
        rev_act_per=[]
        rev_support_act=[]
        rev_support_act_tot=0
        tot_amt=0.0
        while i<=6:
            tot_amt=tot_amt+testDict[i]
            tub.append(str("{:.2f}".format(testDict[i])))            
            if act_rev_val[i]>0:   
                rev_act_per.append(str("{:.2f}".format(testDict[i]*100/act_rev_val[i]))+"%")
            else:
                rev_act_per.append("0.00%")                
  
            rev_support_act.append(str("{:.2f}".format(testDict[i]*100/percent)))
            rev_support_act_tot+=testDict[i]*100/percent
            i+=1
        tot_amt+=overall_ot_total
        if net_rev_tot>0:
            labour_per_act=(tot_amt/net_rev_tot)*100
        else:
            labour_per_act=0
            
        result['tot_ot_costs'] = str("{:.2f}".format(overall_ot_total))
        result['tot_act_costs'] = str("{:.2f}".format(tot_amt ))
        for line in hours_list:
            job_cost = line['job_total_costs']
            tot_cost = result['tot_act_costs']
            total_job_cost=0.0
            if float(tot_cost)>0:
                total_job_cost = (float(job_cost)/float(tot_cost)) * 100
                
            line['job_per'] = str("{:.2f}".format(total_job_cost)) + "%"
        result['act_costs'] = tub 
        result['labour_per_act'] = str("{:.2f}".format(labour_per_act))+"%" 
        result['rev_act_per'] = rev_act_per
        result['rev_support_act'] = rev_support_act
        result['rev_support_act_tot'] = str("{:.2f}".format(rev_support_act_tot))
        result['hours_list'] = hours_list    
    
            
        result['week1']=["Week-"+str(self.get_week_by_date(date_to)), str("{:,.0f}".format(rev_budget_act_tot)), str("{:,.2f}".format(net_rev_tot)), str("{:.2f}".format(percent)+"%"), str("{:.2f}".format(labour_per_act))+"%"]
        
        date_from = from_date
        date_to = to_date  
        date_from=date_from + datetime.timedelta(days=7)
        week2_bud=week2_rev=week2_per=0

        return result

    name = fields.Many2one("hr.period", "Timesheet Period", required=True)
    company_id = fields.Many2one("res.company", "Company", required=True)
    from_date = fields.Date("From Date", required=True)
    to_date = fields.Date("To Date", required=True)    
    actual_plan = fields.Float("Widget", default=1.0)
        
    _sql_constraints = [
        ('_actual_payroll_period', 'unique (name)','Timesheet Period is already created')]
    
    @api.multi
    @api.onchange('name')
    def _onchange_timesheet_period(self):
        self.company_id = self.name.company_id.id
        self.from_date = self.name.date_start
        self.to_date = self.name.date_stop
        
    @api.model
    def create(self, vals):        
        job_list=self.env['hr.period'].search([('id', '=', vals['name'])])
        vals['company_id']=job_list.company_id.id
        vals['from_date']=job_list.date_start
        vals['to_date']=job_list.date_stop  

        return super(ActualLaborCost, self).create(vals)      
#         
#     def update_missed_entries(self,count):
#         
#         date=datetime.date.today()
#         date=datetime.datetime.strptime("2018-08-10", "%Y-%m-%d")
#         company_ids= self.env['res.company'].search([('daily_report','=',True),('id','=',54)])
#         for i in range(count):
#             day_week=(i*7)*-1
#             date_new=date+ datetime.timedelta(days=day_week)
#             print date_new,'---'
#             for company_id in company_ids:
#                 emp_list=[]
#                 period_id=False
#                 for staff in self.env['staff.planning'].search([('from_date', '<=', date_new),('to_date', '>=', date_new),('company_id', '=', company_id.id)]):
#                     for staff_jobs in self.env['staff.planning.display'].search([('planning_id','=', staff.id)]):
#                         for week_list in staff_jobs.week_hours:
#                             if week_list.week_type=='week1':
#                                 emp_list.append(week_list.employee_id.id)
#                     period_id=staff.name
#                 print emp_list
#                 print len(emp_list), period_id
#                 if period_id:      
#                     for work_hours in self.env['hr.work.hours'].search([('employee_id','not in', emp_list),('period_id','=',period_id.id)]): 
#                         print work_hours.employee_id.name, period_id.name
#             
    
    