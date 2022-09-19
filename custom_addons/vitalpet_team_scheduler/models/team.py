# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, tools, _
import datetime
from datetime import timedelta, date
from odoo.exceptions import UserError, ValidationError
from babel.util import missing
import itertools
import operator
import collections
import re
# from matplotlib.testing.jpl_units import day

import logging
from odoo.service.server import start
from docutils.nodes import field

_logger = logging.getLogger(__name__)

class StaffPlanning(models.Model):
    _name = 'staff.planning'
    _inherit = ['mail.thread']

    def add_time(self, time, time2):
        if time==False:
            time="00:00"
        if time2==False:
            time2="00:00"
            
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
        
    def float_to_time(self, a):
        a1, a2 = str(a).split(".")
        hrs=int(a1)
        mins=0
        if int(a2)>0:
            mins=int(a2)*60/100   
#             if (int(a2)*60/100).is_integer():
#                 mins=int(a2)*60/100        
#             else:
#                 mins=int(a2)*60/100+1
            
        if len(str(hrs)) == 1:
            hrs = "0" + str(hrs)
        if len(str(mins)) == 1:
            mins = str(mins)+"0"
        if len(str(mins)) > 2:
            mins = str(mins)[0]+str(mins)[1]            
        return str(hrs)+":"+str(mins)
    
    def time_to_float(self, hours):
        list = [x.strip() for x in hours.split(':')]
        hrs = int(list[0])
        if int(list[1]) > 0:
            mins = float(list[1]) * 100 / 60
            mins = mins / 100
        else:
            mins = 0
        return hrs + mins


    @api.multi
    def get_week_by_date(self,day): 
        day_start=1
        date=datetime.datetime.strptime(str(day), "%Y-%m-%d")+ datetime.timedelta(days=day_start)
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
    
    def dates_list(self, from_date, to_date, company_id,timesheet_period, week_no):
        result = {}
        dates = []
        budget = []
        budget_rev = []
        
        result['week_no'] = week_no
        from_date = datetime.datetime.strptime(from_date, "%Y-%m-%d")
        to_date = datetime.datetime.strptime(to_date, "%Y-%m-%d")
        week_rec=""
        if week_no==1:
            to_date = from_date + datetime.timedelta(days=6)
            week_rec="week1"
        else:
            from_date = from_date + datetime.timedelta(days=7)            
            week_rec="week2"
            
        date_from = from_date
        date_to = to_date
                
        sheet_id_list = self.env['staff.planning'].search([('name', '=', timesheet_period)])
        sheet_id=sheet_id_list.id
        result['sheet_id']=sheet_id
                
        if week_no==1:
            percent = sheet_id_list.week1_per
        else:
            percent = sheet_id_list.week2_per
            
        budget_tot_cost=budget_rev_tot_cost=lab_forecast_tot=rev_support_tot=0.0
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
            cost = 0.0
            budget_list = self.env['labor.budget.list'].search([('sheet_id', '=', sheet_id),('date', '=', date_from.strftime('%Y-%m-%d'))])            
            if budget_list:
                cost=budget_list.amount
            if cost>0 and percent>0:
                budget_rev_val=cost*100/percent
            else:
                budget_rev_val=0
                
            budget_tot_cost+=cost
            budget_rev_tot_cost+=budget_rev_val
            cost="$ " + str("{:.2f}".format(cost))
            budget.append(cost)                        
            budget_rev.append("$ " + str("{:.2f}".format(budget_rev_val)))
                
            date_from = date_from + datetime.timedelta(days=1)
        result['budget'] = budget
        result['budget_tot'] = "$ "+str("{:.2f}".format(budget_tot_cost))
        result['budget_rev'] = budget_rev
        result['budget_rev_tot_cost'] = "$ "+str("{:.2f}".format(budget_rev_tot_cost))
        result['dates'] = dates

        jobs = []
        labour_forcast = []
        ot_vals=0
        
        working_days=5
        for company_work in self.env['res.company'].search([('id', '=', company_id)]):                                                                                                              
            if company_work.Sunday:
                working_days=7                                              
            elif company_work.Saturday:
                working_days=6
                
                                                    
        job_list = self.env['timesheet.config'].search([('company_id', '=', company_id)])
        if job_list:
            emp_list=[]
            for job in job_list.hr_job_ids:
                date_from = from_date
                date_to = to_date
                job_name = {}
                staff_hours= self.env['staff.planning.display'].search([('planning_id', '=', sheet_id),('name', '=', job.name.id)])                
                job_name['id'] =staff_hours.id
                job_name['name'] = job.name.name
                job_name['work_hours'] = []
                hrs_rate = pto_hrs_rate = tot_hrs_rate = total_ot_hrs="00:00"
                labour_list = {}
                labour_list['list'] = []
                date_no = 1                
                 
                for i in range(1,8):
                    
                    hrs_list = {}
                    cost_list = {}
                    current_cost = current_pto_cost = 0.0                    
                    hrs = pto_hrs = tot_hrs = "00:00"                   
                    current_work_date=(date_from + datetime.timedelta(days=(i-1))).strftime('%Y-%m-%d')
                     
                    for week_hour in staff_hours.week_hours: 
                        if week_hour.week_type==week_rec:                   
                            day_hours="week_hour.day"+str(i)         
                            if eval(day_hours):
                                hours_day=eval(day_hours)
                            else:
                                hours_day="00:00"
                                          
                            paid_hours_leaves=unpaid_hours_leaves=0
                            hr_paid_holidays=self.env['hr.holidays'].sudo().search([('employee_id', '=', week_hour.employee_id.id),('holiday_status_id.paid_leave', '=', True),('date_from', '<=', current_work_date),('date_to', '>=', current_work_date)], limit=1)
                            if hr_paid_holidays:                    
                                paid_days=(datetime.datetime.strptime(hr_paid_holidays.date_to, "%Y-%m-%d")-datetime.datetime.strptime(hr_paid_holidays.date_from, "%Y-%m-%d")).days
                                paid_days+=1
                                paid_hours_leaves=hr_paid_holidays.number_of_hours_temp/paid_days
                                
                            hrs = self.add_time(hours_day, hrs)
                            pto_hrs = self.add_time(self.float_to_time("{:.2f}".format(paid_hours_leaves)), pto_hrs)
                            tot_hrs = self.add_time(self.add_time(hours_day, pto_hrs), tot_hrs)
                            
                            if job.salary_applicable:
                                
                                if (date_from + datetime.timedelta(days=(i-1))).weekday()==1:
                                    total_ot_hrs = self.add_time(total_ot_hrs, week_hour.ot_total)
                                    ot_vals=ot_vals+self.amount_cals(week_hour.ot_total,(week_hour.hourly_rate/2))
                                    
                                holiday=self.env['hr.holidays.public.line'].sudo().search_count([('year_id.company_id','=',company_id),('date','=',current_work_date)])
                                
                                if week_hour.salary_type=='hourly':
                                    if holiday==0:
                                        current_cost = current_cost + self.amount_cals(hours_day,week_hour.hourly_rate)
                                    else:
                                        if job.public_holidays>0:
                                            current_cost = current_cost + (self.amount_cals(hours_day,week_hour.hourly_rate)*(job.public_holidays/100))
                                            
                                elif week_hour.salary_type=='yearly':
                                    if working_days==7:                                
                                        current_cost = current_cost + week_hour.wage/52/working_days
                                    elif working_days==6:
                                        if (date_from + datetime.timedelta(days=(i-1))).weekday()<6:
                                            current_cost = current_cost + week_hour.wage/52/working_days
                                    else:
                                        if (date_from + datetime.timedelta(days=(i-1))).weekday()<5:
                                            current_cost = current_cost + week_hour.wage/52/working_days
                                                                         
                    hrs_list['hrs'] = hrs
                    hrs_list['pto_hrs'] = pto_hrs
                    hrs_list['tot_hrs'] = tot_hrs
                    
            
                    hrs_rate = self.add_time(hrs, hrs_rate)
                    pto_hrs_rate = self.add_time(pto_hrs, pto_hrs_rate)
                    
                    job_name['work_hours'].append(hrs_list)  
                    
                        
                    cost_list['date'] = current_work_date
                    cost_list['cost'] = current_cost + current_pto_cost
                    labour_list['list'].append(cost_list) 
                                      
                                
                cost_hrs_list = {}
                cost_hrs_list['amt_hrs'] = str(hrs_rate)
                cost_hrs_list['amt_ot_hrs'] = str(total_ot_hrs)
                cost_hrs_list['amt_pto_hrs'] = str(pto_hrs_rate)
                cost_hrs_list['amt_tot_hrs'] = self.add_time(hrs_rate, pto_hrs_rate)
                job_name['work_hours'].append(cost_hrs_list)
                jobs.append(job_name)
                labour_forcast.append(labour_list)
     
        result['ot_vals'] = "$ "+str("{:.2f}".format(ot_vals))
        labour_forcast_cost = []
        revenue_labour_forcast = []
        for labour in labour_forcast:
            cost = [sum(d["cost"] for d in group) for key, group in
                    itertools.groupby(labour['list'], key=lambda d: d["date"])]
            labour_forcast_cost.append(cost)
            revenue_labour_forcast.append(cost)
        
   
        lab_forecast_tot="$ " + str("{:.2f}".format(sum([sum(tup) for tup in zip(*labour_forcast_cost)])++ot_vals))  
        
        if percent>0:
            rev_support_tot="$ " + str("{:.2f}".format(sum([sum(tup)* 100 / percent for tup in zip(*revenue_labour_forcast)])))
            revenue_labour_forcast = ["$ " + str("{:.2f}".format(sum(tup) * 100 / percent)) for tup in zip(*revenue_labour_forcast)]
        else:
            rev_support_tot="$ " + str("{:.2f}".format(sum([0 for tup in zip(*revenue_labour_forcast)])))
            revenue_labour_forcast = ["$ " + str("{:.2f}".format(0)) for tup in zip(*revenue_labour_forcast)]
            
        labour_forcast_cost = ["$ " + str("{:.2f}".format(sum(tup))) for tup in zip(*labour_forcast_cost)]

        
        result['labour_forcast'] = labour_forcast_cost
        result['revenue_labour_forcast'] = revenue_labour_forcast
        result['lab_forecast_tot'] = lab_forecast_tot
        result['rev_support_tot'] = rev_support_tot
        result['percent'] =  str("{:.2f}".format(percent))
        result['jobs'] = jobs
        
        return result
    

    name = fields.Many2one("hr.period", "Timesheet Period", required=True)
    company_id = fields.Many2one("res.company", "Company")
    from_date = fields.Date("From Date")
    to_date = fields.Date("To Date")
    budget = fields.Float("Budget", required=True, default=0.0)
    total_forecast = fields.Float("Total Forecast", required=True, default=0.0)
    net_rev = fields.Float("Budget Month Net Revenue", required=True, default=0.0)
    biweek_net_rev=fields.Float("Net Revenue", compute="_compute_net_rev")
    week1_per = fields.Float("Percentage Week1",  default=0.0)
    week2_per = fields.Float("Percentage Week2",  default=0.0)
    week1_forecast = fields.Float("Forecast Week1",  default=0.0)
    week2_forecast = fields.Float("Forecast Week2",  default=0.0)
    week1_ot = fields.Float("OT Week1",  default=0.0)
    week2_ot = fields.Float("OT Week2",  default=0.0)
    custom_plan = fields.Float("Widget", default=1.0)
    labor_budget = fields.One2many("labor.budget.list", "sheet_id","Budget List")
    employee_id=fields.Many2one("hr.employee", "Employee", compute="_compute_manager")
    staff_planning_ids = fields.One2many("staff.planning.display","planning_id", "Company")
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approval', 'Waiting for Approval'),
        ('validated', 'Validated'),
        ], string='Status', copy=False, index=True, track_visibility='onchange', default='draft')
    

    _sql_constraints = [
        ('_name_payroll_period', 'unique (name)','Timesheet Period is already created')]
    
        
    @api.depends('budget','week1_per')
    def _compute_net_rev(self):
        for line in self:   
            if line.week1_per>0:
                line.biweek_net_rev=(line.budget/line.week1_per)*100
                
    @api.depends('create_uid')
    def _compute_manager(self):
        for line in self:                   
            emp=self.env['hr.employee'].search([('user_id','=',self.env.user.id)])
            if emp:
                line.employee_id=emp.parent_id.id  
                
    @api.multi                           
    def find_date(self,num):        
        
        from_date = datetime.datetime.strptime(self.from_date, "%Y-%m-%d")
#         to_date = datetime.datetime.strptime(self.to_date, "%Y-%m-%d")
        
        return (from_date + datetime.timedelta(days=num)).strftime('%a (%m / %d)')
        
    @api.multi                           
    def schduler_refresh(self):                  
        self.update_total_forecast()
        self.refresh_budget()
        self.schduler_validate_refresh()
        
    @api.multi
    def refresh_scheduler(self):
        for rec in self.env['staff.planning'].search([]):
            rec.schduler_refresh()
        
    @api.multi
    def schduler_send(self):        
        res=self.update_total_forecast()        
        if res[0]>res[1]:        
            self.state="approval"                  
#             mails_to_send = self.env['mail.mail']
#             rendering_context = dict(self._context)
#             invitation_template = self.env.ref('vitalpet_team_scheduler.team_scheduler_approval_notification')
#             invitation_template = invitation_template.with_context(rendering_context)
#             mail_id = invitation_template.send_mail(self.id)
#             current_mail = self.env['mail.mail'].browse(mail_id)
#             mails_to_send |= current_mail
#             if mails_to_send :
#                 mails_to_send.send()
            
        else:
            self.schduler_validate()
        
    @api.multi
    def update_total_forecast(self):
        total_budget=self.budget   
        forcast_budget=0.0     
        for line in self.env['staff.planning.display'].search([('planning_id', '=', self.id)]):
            config=self.env['timesheet.job.seq'].search([('name', '=', line.name.id),('job_list.company_id', '=', line.company_id.id)])
            for week_hour in line.week_hours:
                if config.salary_applicable:
                    if week_hour.salary_type=='hourly':
                        forcast_budget+=self.amount_cals(week_hour.hours_total,week_hour.hourly_rate)
                        forcast_budget+=self.amount_cals(week_hour.ot_total,(week_hour.hourly_rate/2))
                         
                        for i in range(1,8):
                            current_date = datetime.datetime.strptime(week_hour.from_date, "%Y-%m-%d")
                            current_date=current_date+ datetime.timedelta(days=(i-1))
                            holiday=self.env['hr.holidays.public.line'].sudo().search_count([('year_id.company_id','=',self.company_id.id),('date','=',current_date)])
                            if holiday>0:
                                str_val="week_hour.day"+str(i)
                                val=eval(str_val)
                                if val:
                                    val=eval(str_val)
                                else:
                                    val="00:00"
                                forcast_budget+=self.amount_cals(val,((week_hour.hourly_rate*(config.public_holidays/100)-week_hour.hourly_rate)))
                                    
                    elif week_hour.salary_type=='yearly':
                        forcast_budget+=week_hour.wage/52
 
        self.total_forecast=forcast_budget
        return [forcast_budget,total_budget]  
      
                        
    @api.multi
    def schduler_resubmit(self):
        self.state="draft"

    @api.multi
    def employee_work_send_mail(self):
        for job_id in self.env['staff.planning.display'].search([('planning_id','=',self.id)]):
#             employee_list = []
            for employee in job_id.week_hours:
#                 if employee.employee_id.id not in employee_list:
#                     employee_list.append(employee.employee_id.id)
#                 if len(employee_list) > 1:
                if employee.day1 or employee.day2 or employee.day3 or employee.day4 or employee.day5 or employee.day6 or employee.day7:
                    if employee.day1 != '00:00' and employee.day2 != '00:00' and employee.day3 != '00:00' and employee.day4 != '00:00' and employee.day5 != '00:00' and employee.day6 != '00:00' and employee.day7 != '00:00':
                        if employee.week_type =='week1':             
                            template_id = self.env.ref('vitalpet_team_scheduler.team_scheduler_validation_notification')
                            if template_id:
                                template_id.send_mail(employee.id, force_send=True)
#                 else:
#                     raise UserError(_('There is an employee with two seniority title in same job position'))
    
    @api.multi
    def schduler_validate(self):
   
        self.schduler_validate_refresh()
              
#         mails_to_send = self.env['mail.mail']
#         rendering_context = dict(self._context)
#         invitation_template = self.env.ref('vitalpet_team_scheduler.team_scheduler_approved_notification')
#         invitation_template = invitation_template.with_context(rendering_context)
#         mail_id = invitation_template.send_mail(self.id)
#         current_mail = self.env['mail.mail'].browse(mail_id)
#         mails_to_send |= current_mail
#         if mails_to_send :
#             mails_to_send.send()
        
            
        self.state="validated"
        self.employee_work_send_mail()
        count=self.env['actual.labour.cost'].search_count([('name','=',self.name.id)])
        if count==0:
            self.env['actual.labour.cost'].create({
                                                'name': self.name.id,                                               
                                                 }) 
        # raise ValidationError("Test")
            
    @api.multi
    def schduler_validate_refresh(self):
        from_date=self.from_date
        to_date=self.to_date
        timesheet_period=self.name.name
        company_id=self.company_id.id        
             
        from_date=from_date1 = datetime.datetime.strptime(from_date, "%Y-%m-%d")
        to_date=to_date1 = datetime.datetime.strptime(to_date, "%Y-%m-%d")
        
        working_days=5                                                                                                             
        if self.company_id.Sunday:
            working_days=7                                              
        elif self.company_id.Saturday:
            working_days=6
                
        for num_week in range(2):                                   
            result = {}
            dates = []
            budget = []
            budget_rev = []
        
            if num_week==0:                    
                date_from=from_date = from_date1
                date_to=to_date = from_date1 + datetime.timedelta(days=6)  
            else:          
                date_from=from_date = from_date1 + datetime.timedelta(days=7)
                date_to=to_date = to_date1  
            
            sheet_id_list = self.env['staff.planning'].search([('name', '=', timesheet_period)])
            sheet_id = sheet_id_list.id
            result['sheet_id']=sheet_id
            
            week_rec=""
           
            if num_week==0:  
                percent = sheet_id_list.week1_per
                week_rec="week1"
            else:
                percent = sheet_id_list.week2_per      
                week_rec="week2"
            print percent
            if percent<=0:
                raise UserError(_('Labor Budget Percentage is 0.'))
            
            while (date_to >= date_from):
                
                budget_val = {}
                cost = 0.0
                budget_list = self.env['labor.budget.list'].search([('sheet_id', '=', sheet_id),('date', '=', date_from.strftime('%Y-%m-%d'))])            
                if budget_list:
                    cost=budget_list.amount
                    
                if cost>0 and percent>0:
                    budget_rev_val=cost*100/percent
                else:
                    budget_rev_val=0
                    
                budget.append(cost)                        
                budget_rev.append(budget_rev_val)
                    
                date_from = date_from + datetime.timedelta(days=1)
            result['budget'] = budget
            result['budget_rev'] = budget_rev
            
            ot_vals=0  
            jobs = []
            labour_forcast = []
            job_list = self.env['timesheet.config'].search([('company_id', '=', company_id)])
            if job_list:
                emp_list=[]
                for job in job_list.hr_job_ids:
                    date_from = from_date
                    date_to = to_date
                    job_name = {}
                    staff_hours= self.env['staff.planning.display'].search([('planning_id', '=', sheet_id),('name', '=', job.name.id)])                
                    job_name['id'] =staff_hours.id
                    job_name['name'] = job.name.name
                    job_name['work_hours'] = []
                    hrs_rate = pto_hrs_rate = tot_hrs_rate = "00:00"
                    labour_list = {}
                    labour_list['list'] = []
                    date_no = 1                
                       
                    for i in range(1,8):
                        
                        hrs_list = {}
                        cost_list = {}
                        current_cost = current_pto_cost = 0.0                    
                        hrs = pto_hrs = tot_hrs = "00:00"                   
                        current_work_date=(date_from + datetime.timedelta(days=(i-1))).strftime('%Y-%m-%d')
                         
                        for week_hour in staff_hours.week_hours: 
                            if week_hour.week_type==week_rec:                   
                                day_hours="week_hour.day"+str(i)         
                                if eval(day_hours):
                                    hours_day=eval(day_hours)
                                else:
                                    hours_day="00:00"
                                              
                                paid_hours_leaves=unpaid_hours_leaves=0
                                hr_paid_holidays=self.env['hr.holidays'].sudo().search([('employee_id', '=', week_hour.employee_id.id),('holiday_status_id.paid_leave', '=', True),('date_from', '<=', current_work_date),('date_to', '>=', current_work_date)], limit=1)
                                if hr_paid_holidays:                    
                                    paid_days=(datetime.datetime.strptime(hr_paid_holidays.date_to, "%Y-%m-%d")-datetime.datetime.strptime(hr_paid_holidays.date_from, "%Y-%m-%d")).days
                                    paid_days+=1
                                    paid_hours_leaves=hr_paid_holidays.number_of_hours_temp/paid_days
                                    
                                hrs = self.add_time(hours_day, hrs)
                                pto_hrs = self.add_time(self.float_to_time("{:.2f}".format(paid_hours_leaves)), pto_hrs)
                                tot_hrs = self.add_time(self.add_time(hours_day, pto_hrs), tot_hrs)
                                
                                if job.salary_applicable:
                                    
                                    if (date_from + datetime.timedelta(days=(i-1))).weekday()==1:
                                        ot_vals=ot_vals+self.amount_cals(week_hour.ot_total,(week_hour.hourly_rate/2))
                                        
                                    holiday=self.env['hr.holidays.public.line'].sudo().search_count([('year_id.company_id','=',company_id),('date','=',current_work_date)])
                                    
                                    if week_hour.salary_type=='hourly':
                                        if holiday==0:
                                            current_cost = current_cost + self.amount_cals(hours_day,week_hour.hourly_rate)
                                        else:
                                            if job.public_holidays>0:
                                                current_cost = current_cost + (self.amount_cals(hours_day,week_hour.hourly_rate)*(job.public_holidays/100))
                                                
                                    elif week_hour.salary_type=='yearly':
                                        if working_days==7:                                
                                            current_cost = current_cost + week_hour.wage/52/working_days
                                        elif working_days==6:
                                            if (date_from + datetime.timedelta(days=(i-1))).weekday()<6:
                                                current_cost = current_cost + week_hour.wage/52/working_days
                                        else:
                                            if (date_from + datetime.timedelta(days=(i-1))).weekday()<5:
                                                current_cost = current_cost + week_hour.wage/52/working_days
                                                                             
                        hrs_list['hrs'] = hrs
                        hrs_list['pto_hrs'] = pto_hrs
                        hrs_list['tot_hrs'] = tot_hrs
                        
                
                        hrs_rate = self.add_time(hrs, hrs_rate)
                        pto_hrs_rate = self.add_time(pto_hrs, pto_hrs_rate)
                        
                        job_name['work_hours'].append(hrs_list)  
                        
                            
                        cost_list['date'] = current_work_date
                        cost_list['cost'] = current_cost + current_pto_cost
                        labour_list['list'].append(cost_list) 
                                          
                                    
                    cost_hrs_list = {}
                    cost_hrs_list['amt_hrs'] = str(hrs_rate)
                    cost_hrs_list['amt_pto_hrs'] = str(pto_hrs_rate)
                    cost_hrs_list['amt_tot_hrs'] = self.add_time(hrs_rate, pto_hrs_rate)
                    job_name['work_hours'].append(cost_hrs_list)
                    jobs.append(job_name)
                    labour_forcast.append(labour_list)
         
            if num_week==0:  
                self.week1_ot=ot_vals
            else:
                self.week2_ot=ot_vals
            labour_forcast_cost = []
            revenue_labour_forcast = []
            for labour in labour_forcast:
                cost = [sum(d["cost"] for d in group) for key, group in
                        itertools.groupby(labour['list'], key=lambda d: d["date"])]
                labour_forcast_cost.append(cost)
                revenue_labour_forcast.append(cost)
    
            labour_forcast_cost = [sum(tup) for tup in zip(*labour_forcast_cost)]
            revenue_labour_forcast = [(sum(tup) * 100 / percent) for tup in
                                      zip(*revenue_labour_forcast)]
            
            result['labour_forcast'] = labour_forcast_cost
            result['revenue_labour_forcast'] = revenue_labour_forcast
            result['percent'] = percent
            result['jobs'] = jobs
            

            date_from = from_date
            date_to = to_date
            i=0
            while (date_to >= date_from):     
                labor_list=self.env['labor.budget.list'].search([('date', '=', date_from),('sheet_id', '=', self.id)])  
                if labor_list:
                    labor_list.forcast_amount=result['labour_forcast'][i]
                    labor_list.bud_revenue_amount=result['budget_rev'][i]
                    labor_list.support_forecast_amount=result['revenue_labour_forcast'][i]
                    labor_list.week=self.get_week_by_date(date_from.strftime('%Y-%m-%d'))
                    labor_list.year=self.get_year_by_date(date_from.strftime('%Y-%m-%d'))
                else:
                    self.env['labor.budget.list'].create({
                                            'amount': 0.0,
                                            'forcast_amount': result['labour_forcast'][i],
                                            'bud_revenue_amount': result['budget_rev'][i],
                                            'support_forecast_amount': result['revenue_labour_forcast'][i],
                                            'date': date_from.strftime('%Y-%m-%d'),
                                            'week': self.get_week_by_date(date_from.strftime('%Y-%m-%d')),
                                            'year': self.get_year_by_date(date_from.strftime('%Y-%m-%d')),
                                            'sheet_id': self.id,
                                             }) 
                
                i+=1
                date_from = date_from + datetime.timedelta(days=1)
        

    @api.multi
    def unlink(self):
        for line in self:
            if line.state=='validated':
                raise UserError(_('Validated schedule will not be deleted'))
            task_sr = self.env['project.task'].search([('team_scheduler_id', '=', line.id)])
            task_sr.unlink()
        return super(StaffPlanning, self).unlink()

    
    
    @api.multi
    @api.onchange('name')
    def _onchange_timesheet_period(self):
        self.company_id = self.name.company_id.id
        self.from_date = self.name.date_start
        self.to_date = self.name.date_stop
        
    @api.multi
    def _insert_budget(self, sheet_id,date,budget):
        
        self.env['labor.budget.list'].create({
            'sheet_id': sheet_id,
            'date': date,
            'amount': budget,
        })
    
    @api.multi
    def _check_budget_type(self, company_id,year,c_month):        
        i=1
        while i<=12:
            if c_month==i:
                year1=year2=year3=year
                month1=c_month-2
                if month1<1:
                    month1=12+month1
                    year1=year-1
                month2=c_month-3
                if month2<1:
                    month2=12+month2
                    year2=year-1
                month3=c_month-4
                if month3<1:
                    month3=12+month3   
                    year3=year-1             
            i=i+1
#         print c_month,year, month1,month2,month3
        #Find last three months Net Revenue
        min_gross=bud_gross=str_gross=0
        gross_act=0
        i=0  
        gross_rev_list=self.env['budget.category.lines'].search([('name', '=', "Net Revenue"),
                                                            ('company_id', '=', company_id),                
                                                            ('month', 'in', ["M"+str(month1)+"-"+str(year1),"M0"+str(month1)+"-"+str(year1)]),
                                                            ('fin_yr', '=', year1), 
                                                            ('budget_category_id.state','=','confirm')
                                                            ])
        
        for gross_rev in gross_rev_list:
            if gross_rev.budget_scenario=='minimum':
                min_gross+=gross_rev.planned_amount
            if gross_rev.budget_scenario=='budget':
                bud_gross+=gross_rev.planned_amount
            if gross_rev.budget_scenario=='stretch':
                str_gross+=gross_rev.planned_amount
                gross_act+=gross_rev.actual_amount
                i+=1
 
        gross_rev_list=self.env['budget.category.lines'].search([('name', '=', "Net Revenue"),
                                                            ('company_id', '=', company_id),                                                                       
                                                            ('month', 'in', ["M"+str(month2)+"-"+str(year2),"M0"+str(month2)+"-"+str(year2)]),
                                                            ('fin_yr', '=', year2), 
                                                            ('budget_category_id.state','=','confirm')
                                                            ])
                            
        for gross_rev in gross_rev_list:
            if gross_rev.budget_scenario=='minimum':
                min_gross+=gross_rev.planned_amount
            if gross_rev.budget_scenario=='budget':
                bud_gross+=gross_rev.planned_amount
            if gross_rev.budget_scenario=='stretch':
                str_gross+=gross_rev.planned_amount
                gross_act+=gross_rev.actual_amount
                i+=1

        gross_rev_list=self.env['budget.category.lines'].search([('name', '=', "Net Revenue"),
                                                            ('company_id', '=', company_id),                                                                                                
                                                            ('month', 'in', ["M"+str(month3)+"-"+str(year3),"M0"+str(month3)+"-"+str(year3)]),
                                                            ('fin_yr', '=', year3),
                                                            ('budget_category_id.state','=','confirm')
                                                          ])
                               
        for gross_rev in gross_rev_list:
            if gross_rev.budget_scenario=='minimum':
                min_gross+=gross_rev.planned_amount
            if gross_rev.budget_scenario=='budget':
                bud_gross+=gross_rev.planned_amount
            if gross_rev.budget_scenario=='stretch':
                str_gross+=gross_rev.planned_amount
                gross_act+=gross_rev.actual_amount
                i+=1
        
        difference=0

        
#         print min_gross, bud_gross, str_gross,"Planned"
#         print gross_act,"Actual"
        
        if gross_act>=bud_gross:
            bud_type="budget"
        else:
            bud_type="budget"
            if min_gross>0:
                difference=(((gross_act-bud_gross)/bud_gross) * 25/100)

        staff_comp_list=self.env['budget.category.lines'].search([('name', '=', "Staff Compensation"),                      
                                                            ('month', 'in', ["M"+str(c_month)+"-"+str(year),"M0"+str(c_month)+"-"+str(year)]),
                                                            ('fin_yr', '=', year),
                                                            ('budget_scenario', '=', bud_type),
                                                            ('company_id', '=', company_id),
                                                            ('budget_category_id.state','=','confirm')], limit=1)  
#         print staff_comp_list,"M"+str(c_month)+"-"+str(year),bud_type, '--'      
        value_staff_comp=0.0
        if staff_comp_list:
            value_staff_comp+=staff_comp_list.planned_amount
        if value_staff_comp<=0:
            raise UserError(_('Staff Compensation is 0'))
        value_staff_comp=value_staff_comp*(1+difference)
        return [value_staff_comp, bud_type,month1,year1]
    
    @api.model
    def create(self, vals):        
        job_list=self.env['hr.period'].search([('id', '=', vals['name'])])
        vals['company_id']=job_list.company_id.id
        vals['from_date']=job_list.date_start
        vals['to_date']=job_list.date_stop        
        res_company_id=self.env['res.company'].search([('id','=',job_list.company_id.id)])
        leaves_list=self.env['hr.holidays'].sudo().search_count([('employee_id.company_id', '=', job_list.company_id.id),('date_from', '>=', job_list.date_start),('date_to', '<=', job_list.date_stop),('state', 'not in', ['validate','refuse','cancel'])])
        if leaves_list>0:
            raise UserError(_('There are outstanding leave requests for the timesheet period. Please process them in order to build a new schedule.'))
        
        account_fiscal_periods = self.env['account.fiscal.periods'].search([('calendar_type', '=', res_company_id.calendar_type.id)])

        fiscal_period = self.env['account.fiscal.period.lines'].search([('account_fiscal_period_id','in',[a.id for a in account_fiscal_periods]),('date_start', '<=', job_list.date_start),('date_end', '>=', job_list.date_start)])
        fiscal_period_week = self.env['account.fiscal.period.week'].search([('account_fiscal_period_week_id','in',[a.id for a in account_fiscal_periods]),('date_start', '<=', job_list.date_start),('date_end', '>=', job_list.date_start)])
        
        c_year=year=int(fiscal_period.year)
        c_month=int(fiscal_period.name.split("-")[0].replace("M", "").replace("m", ""))        
        c_week=int(fiscal_period_week.name.split("-")[1])
        
        fiscal_period = self.env['account.fiscal.period.lines'].search([('account_fiscal_period_id','in',[a.id for a in account_fiscal_periods]),('date_start', '<=', job_list.date_stop),('date_end', '>=', job_list.date_stop)])
        fiscal_period_week = self.env['account.fiscal.period.week'].search([('account_fiscal_period_week_id','in',[a.id for a in account_fiscal_periods]),('date_start', '<=', job_list.date_stop),('date_end', '>=', job_list.date_stop)])

        n_year=year=int(fiscal_period.year)
        n_month=int(fiscal_period.name.split("-")[0].replace("M", "").replace("m", ""))        
        n_week=int(fiscal_period_week.name.split("-")[1])
                                   
        week_days=["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
        overall_budget=0
        #Start Week based list 
        for num_week in range(2):            
            if num_week==1:
                c_year=n_year
                c_month=n_month
                c_week=n_week        
            staff_comp_list=self._check_budget_type(job_list.company_id.id,c_year,c_month)
#             print staff_comp_list
            value_staff_comp=staff_comp_list[0]
            bud_type=staff_comp_list[1]            
            month1=staff_comp_list[2]            
            year1=staff_comp_list[3]  
            
            last_year_total=0
            last_year_lists=self.env['sales.summary'].search([('month', '=', c_month),
                                                                ('year', '=', (c_year-1)),
                                                                ('company_id', '=', job_list.company_id.id)])
              
            for last_year_list in last_year_lists:
                last_year_total+=last_year_list.dTotal
                
            day1=day2=day3=day4=day5=day6=day7=0
            last_month_total=0
            last_month_lists=self.env['sales.summary'].search([('month', '=', month1),
                                                                ('year', '=', year1),
                                                                ('company_id', '=', job_list.company_id.id)])
            
            for last_month_list in last_month_lists:
                week_day=datetime.datetime.strptime(last_month_list.date, "%Y-%m-%d").weekday()
                if week_days[week_day]=="Sunday":
                    day1+=last_month_list.dTotal
                elif week_days[week_day]=="Monday":
                    day2+=last_month_list.dTotal
                elif week_days[week_day]=="Tuesday":
                    day3+=last_month_list.dTotal
                elif week_days[week_day]=="Wednesday":
                    day4+=last_month_list.dTotal
                elif week_days[week_day]=="Thursday":
                    day5+=last_month_list.dTotal
                elif week_days[week_day]=="Friday":
                    day6+=last_month_list.dTotal
                elif week_days[week_day]=="Saturday":
                    day7+=last_month_list.dTotal
                last_month_total+=last_month_list.dTotal
            
            #Week Actual from sales summary
            week1=0
            ly_year=c_year-1
            last_year_week_lists=self.env['sales.summary'].search([('week', '=', c_week),('year', '=', ly_year),
                                                                ('company_id', '=', job_list.company_id.id)])   
            
            for last_year_list in last_year_week_lists:
                week1+=last_year_list.dTotal
            
            net_rev_list=self.env['budget.category.lines'].search([('name', '=', "Net Revenue"),
                                                                ('month', 'in', ["M"+str(c_month)+"-"+str(c_year),"M0"+str(c_month)+"-"+str(c_year)]),
                                                                ('fin_yr', '=', c_year),
                                                                ('budget_scenario', '=', 'budget'),
                                                                ('company_id', '=', job_list.company_id.id),
                                                                ('budget_category_id.state','=','confirm')], limit=1)
            if not net_rev_list:
                raise UserError(_('Net Revenue is not imported for the Period'))
            if week1==0:
                raise UserError(_('Actual Revenue is Empty'))
                
            dtotal_new=vals['net_rev']=net_rev_list.planned_amount
             
            week1_per=0 
            if last_year_total>0:
                week1_per=(value_staff_comp/dtotal_new)*100
                if num_week==0:
                    vals['week1_per']= week1_per
                    vals_week1= week1_per
#                     print vals_week1,"%"
#                     print ''
                else:
                    vals['week1_per']= week1_per
                    vals_week2= week1_per
#                     print vals_week2,"%"
#                     print ''
                  
            week1=((week1/last_year_total)*100)*dtotal_new/100
            
            if num_week==0:
                staff = super(StaffPlanning, self).create(vals)   
            days_list=[day1,day2,day3,day4,day5,day6,day7]
    
            #Insert budget of Week1
            days_count=0
            for day in days_list:
                if num_week==0:
                    days_count_new=days_count
                else:
                    days_count_new=days_count+7
                    
                if (day)>0:
                    day_val=last_month_total/day
                    day=(week1/day_val)*week1_per/100
                                        
                    date_of_line=datetime.datetime.strptime(vals['from_date'], "%Y-%m-%d")+datetime.timedelta(days=days_count_new)
                    self._insert_budget(staff.id,date_of_line,day)
                    overall_budget+=day
                else:
                    date_of_line=datetime.datetime.strptime(vals['from_date'], "%Y-%m-%d")+datetime.timedelta(days=days_count_new)
                    self._insert_budget(staff.id,date_of_line,0)
                         
                days_count+=1

        staff.week1_per=(vals_week1+vals_week2)/2
        staff.week2_per=(vals_week1+vals_week2)/2
        staff.budget=overall_budget
   
                   
        job_list=self.env['timesheet.config'].search([('company_id', '=', vals['company_id'])])        
        if job_list.hr_job_ids:
            for obj in job_list.hr_job_ids:
                planning_id=self.env['staff.planning.display'].create({
                    'name': obj.name.id,
                    'planning_id': staff.id,
                    'company_id': vals['company_id'],
                    'from_date': vals['from_date'],
                    'to_date': vals['to_date'],
                })

                contract_lists=self.sudo().env['hr.contract'].search([('contract_job_ids.job_id', 'in', [obj.name.id]),('salary_computation_method', 'in', ['hourly','yearly']), ('state', 'in', ['open','pending'])])
                if contract_lists:
                    for contract_list in contract_lists:  
                        for list in contract_list.contract_job_ids:
                            if list.job_id.id==obj.name.id:
                                self.env['staff.planning.display.week'].create({
                                    'display_id': planning_id.id,
                                    'employee_id': contract_list.employee_id.id,
                                    'job_id': obj.name.id,
                                    'from_date': staff.from_date,
                                    'to_date': datetime.datetime.strptime(staff.from_date, "%Y-%m-%d") + datetime.timedelta(days=6),
                                    'week_type': 'week1',
                                    'salary_type': contract_list.salary_computation_method,
                                    'hourly_rate': list.hourly_rate,
                                    'wage': contract_list.wage
                                })
                                self.env['staff.planning.display.week'].create({
                                    'display_id': planning_id.id,
                                    'employee_id': contract_list.employee_id.id,
                                    'job_id': obj.name.id,
                                    'from_date': datetime.datetime.strptime(staff.from_date, "%Y-%m-%d") + datetime.timedelta(days=7),
                                    'to_date': staff.to_date,
                                    'week_type': 'week2',
                                    'salary_type': contract_list.salary_computation_method,
                                    'hourly_rate': list.hourly_rate,
                                    'wage': contract_list.wage
                                })   
        return staff
    
    @api.multi
    def update_employees(self):    
                   
        planning_ids=self.env['staff.planning.display'].search([('planning_id.state','=','draft')])                
        if planning_ids:
            for planning_id in planning_ids:
                print planning_id
                contract_lists=self.sudo().env['hr.contract'].search([('contract_job_ids.job_id', 'in', [planning_id.name.id]),('salary_computation_method', 'in', ['hourly','yearly']), ('state', 'in', ['open','pending'])])
                if contract_lists:
                    for contract_list in contract_lists:  
                        for list in contract_list.contract_job_ids:
                            counts_s=self.env['staff.planning.display.week'].search_count([('display_id','=',planning_id.id),('employee_id','=',contract_list.employee_id.id)])
                            if counts_s==0:
                                if list.job_id.id==planning_id.name.id:
                                    
                                    self.env['staff.planning.display.week'].create({
                                        'display_id': planning_id.id,
                                        'employee_id': contract_list.employee_id.id,
                                        'job_id': planning_id.name.id,
                                        'from_date': planning_id.from_date,
                                        'to_date': datetime.datetime.strptime(planning_id.from_date, "%Y-%m-%d") + datetime.timedelta(days=6),
                                        'week_type': 'week1',
                                        'salary_type': contract_list.salary_computation_method,
                                        'hourly_rate': list.hourly_rate,
                                        'wage': contract_list.wage
                                    })
                                    self.env['staff.planning.display.week'].create({
                                        'display_id': planning_id.id,
                                        'employee_id': contract_list.employee_id.id,
                                        'job_id': planning_id.name.id,
                                        'from_date': datetime.datetime.strptime(planning_id.from_date, "%Y-%m-%d") + datetime.timedelta(days=7),
                                        'to_date': planning_id.to_date,
                                        'week_type': 'week2',
                                        'salary_type': contract_list.salary_computation_method,
                                        'hourly_rate': list.hourly_rate,
                                        'wage': contract_list.wage
                                    })                                       

    
    
            
    @api.multi
    def _update_budget(self, sheet_id,date,budget):        
        budget_lists=self.env['labor.budget.list'].search([('sheet_id','=',sheet_id),('date','=',date)])
        if budget_lists:
            for budget_list in budget_lists:
                budget_list.amount=budget
        else:                        
            self.env['labor.budget.list'].create({
                'sheet_id': sheet_id,
                'date': date,
                'amount': budget,
            })
            
    @api.model
    def refresh_budget(self):        
        job_list=self.name      
        res_company_id=self.env['res.company'].search([('id','=',job_list.company_id.id)])
        leaves_list=self.env['hr.holidays'].sudo().search_count([('employee_id.company_id', '=', job_list.company_id.id),('date_from', '>=', job_list.date_start),('date_to', '<=', job_list.date_stop),('state', 'not in', ['validate','refuse','cancel'])])
        if leaves_list>0:
            raise UserError(_('There are outstanding leave requests for the timesheet period. Please process them in order to build a new schedule.'))
        
        account_fiscal_periods = self.env['account.fiscal.periods'].search([('calendar_type', '=', res_company_id.calendar_type.id)])

        fiscal_period = self.env['account.fiscal.period.lines'].search([('account_fiscal_period_id','in',[a.id for a in account_fiscal_periods]),('date_start', '<=', job_list.date_start),('date_end', '>=', job_list.date_start)])
        fiscal_period_week = self.env['account.fiscal.period.week'].search([('account_fiscal_period_week_id','in',[a.id for a in account_fiscal_periods]),('date_start', '<=', job_list.date_start),('date_end', '>=', job_list.date_start)])
        
        c_year=year=int(fiscal_period.year)
        c_month=int(fiscal_period.name.split("-")[0].replace("M", "").replace("m", ""))        
        c_week=int(fiscal_period_week.name.split("-")[1])
        
        fiscal_period = self.env['account.fiscal.period.lines'].search([('account_fiscal_period_id','in',[a.id for a in account_fiscal_periods]),('date_start', '<=', job_list.date_stop),('date_end', '>=', job_list.date_stop)])
        fiscal_period_week = self.env['account.fiscal.period.week'].search([('account_fiscal_period_week_id','in',[a.id for a in account_fiscal_periods]),('date_start', '<=', job_list.date_stop),('date_end', '>=', job_list.date_stop)])

        n_year=year=int(fiscal_period.year)
        n_month=int(fiscal_period.name.split("-")[0].replace("M", "").replace("m", ""))        
        n_week=int(fiscal_period_week.name.split("-")[1])
                                   
        week_days=["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
        overall_budget=0
        #Start Week based list 
        for num_week in range(2):            
            if num_week==1:
                c_year=n_year
                c_month=n_month
                c_week=n_week        
            staff_comp_list=self._check_budget_type(job_list.company_id.id,c_year,c_month)
#             print staff_comp_list
            value_staff_comp=staff_comp_list[0]
            bud_type=staff_comp_list[1]            
            month1=staff_comp_list[2]            
            year1=staff_comp_list[3]  
            
            last_year_total=0
            last_year_lists=self.env['sales.summary'].search([('month', '=', c_month),
                                                                ('year', '=', (c_year-1)),
                                                                ('company_id', '=', job_list.company_id.id)])
              
            for last_year_list in last_year_lists:
                last_year_total+=last_year_list.dTotal
                
            day1=day2=day3=day4=day5=day6=day7=0
            last_month_total=0
            last_month_lists=self.env['sales.summary'].search([('month', '=', month1),
                                                                ('year', '=', year1),
                                                                ('company_id', '=', job_list.company_id.id)])
            
            for last_month_list in last_month_lists:
                week_day=datetime.datetime.strptime(last_month_list.date, "%Y-%m-%d").weekday()
                if week_days[week_day]=="Sunday":
                    day1+=last_month_list.dTotal
                elif week_days[week_day]=="Monday":
                    day2+=last_month_list.dTotal
                elif week_days[week_day]=="Tuesday":
                    day3+=last_month_list.dTotal
                elif week_days[week_day]=="Wednesday":
                    day4+=last_month_list.dTotal
                elif week_days[week_day]=="Thursday":
                    day5+=last_month_list.dTotal
                elif week_days[week_day]=="Friday":
                    day6+=last_month_list.dTotal
                elif week_days[week_day]=="Saturday":
                    day7+=last_month_list.dTotal
                last_month_total+=last_month_list.dTotal
            
            #Week Actual from sales summary
            week1=0
            ly_year=c_year-1
            last_year_week_lists=self.env['sales.summary'].search([('week', '=', c_week),('year', '=', ly_year),
                                                                ('company_id', '=', job_list.company_id.id)])   
         
            for last_year_list in last_year_week_lists:
                week1+=last_year_list.dTotal
            
            net_rev_list=self.env['budget.category.lines'].search([('name', '=', "Net Revenue"),
                                                                ('month', 'in', ["M"+str(c_month)+"-"+str(c_year),"M0"+str(c_month)+"-"+str(c_year)]),
                                                                ('fin_yr', '=', c_year),
                                                                ('budget_scenario', '=', 'budget'),
                                                                ('company_id', '=', job_list.company_id.id),
                                                                ('budget_category_id.state','=','confirm')], limit=1)
            if not net_rev_list:
                raise UserError(_('Net Revenue is not imported for the Period'))
            if week1==0:
                raise UserError(_('Actual Revenue is Empty'))
                
            dtotal_new=self.net_rev=net_rev_list.planned_amount
             
            week1_per=0 
            print value_staff_comp,dtotal_new,'--'
            if last_year_total>0:
                week1_per=(value_staff_comp/dtotal_new)*100
                if num_week==0:
                    vals_week1= week1_per
#                     print vals_week1,"%"
#                     print ''
                else:
                    vals_week2= week1_per
#                     print vals_week2,"%"
#                     print ''
                  
            week1=((week1/last_year_total)*100)*dtotal_new/100
            
  
            days_list=[day1,day2,day3,day4,day5,day6,day7]
    
            #Insert budget of Week1
            days_count=0
            for day in days_list:
                if num_week==0:
                    days_count_new=days_count
                else:
                    days_count_new=days_count+7
                    
                if (day)>0:
                    day_val=last_month_total/day
                    day=(week1/day_val)*week1_per/100
                                        
                    date_of_line=datetime.datetime.strptime(self.from_date, "%Y-%m-%d")+datetime.timedelta(days=days_count_new)
                    self._update_budget(self.id,date_of_line,day)
                    overall_budget+=day
                else:
                    date_of_line=datetime.datetime.strptime(self.from_date, "%Y-%m-%d")+datetime.timedelta(days=days_count_new)
                    self._update_budget(self.id,date_of_line,0)
                         
                days_count+=1
        print vals_week1,vals_week2
        self.week1_per=(vals_week1+vals_week2)/2
        self.week2_per=(vals_week1+vals_week2)/2
        self.budget=overall_budget
   
class LaborBudgetList(models.Model):
    _name = 'labor.budget.list'

    sheet_id = fields.Many2one("staff.planning")
    date = fields.Date("Date")
    week = fields.Integer("Week")
    year = fields.Integer("Year")
    
    amount = fields.Float("Labor Budget Amount")
    forcast_amount = fields.Float("Labor Forecast Amount")
    bud_revenue_amount = fields.Float("Budget Revenue Amount")
    support_forecast_amount = fields.Float("Support Labor Forecast Amount")
    
    a_actual_rev = fields.Float("Revenue Actual Amount")
    a_labor_actual_amount = fields.Float("Labor Actual Amount")
    a_labor_percent_actual = fields.Float("Labor Percentage Actual")
    a_support_actual=fields.Float("Revenue to Support Actual")

class LaborWeekList(models.Model):
    _name = 'staff.planning.display.week'
#     _rec='employee_id'
    
    display_id = fields.Many2one("staff.planning.display",ondelete="cascade")
    employee_id = fields.Many2one("hr.employee",string="Employee", required=True)
    job_id = fields.Many2one("hr.job",string="Job", required=True)
        
    day1 = fields.Char("Day1")
    day2 = fields.Char("Day2")
    day3 = fields.Char("Day3")
    day4 = fields.Char("Day4")
    day5 = fields.Char("Day5")
    day6 = fields.Char("Day6")
    day7 = fields.Char("Day7") 
          
    in_time1 = fields.Char("Day1",default="00:00")
    in_time2 = fields.Char("Day2",default="00:00")
    in_time3 = fields.Char("Day3",default="00:00")
    in_time4 = fields.Char("Day4",default="00:00")
    in_time5 = fields.Char("Day5",default="00:00")
    in_time6 = fields.Char("Day6",default="00:00")
    in_time7 = fields.Char("Day7",default="00:00")   
          
    break_start1 = fields.Char("Day1",default="00:00")
    break_start2 = fields.Char("Day2",default="00:00")
    break_start3 = fields.Char("Day3",default="00:00")
    break_start4 = fields.Char("Day4",default="00:00")
    break_start5 = fields.Char("Day5",default="00:00")
    break_start6 = fields.Char("Day6",default="00:00")
    break_start7 = fields.Char("Day7",default="00:00")   
          
    break_end1 = fields.Char("Day1",default="00:00")
    break_end2 = fields.Char("Day2",default="00:00")
    break_end3 = fields.Char("Day3",default="00:00")
    break_end4 = fields.Char("Day4",default="00:00")
    break_end5 = fields.Char("Day5",default="00:00")
    break_end6 = fields.Char("Day6",default="00:00")
    break_end7 = fields.Char("Day7",default="00:00")   
    
    out_time1 = fields.Char("Out Time1",default="00:00", compute='compute_hours_out_time')
    out_time2 = fields.Char("Out Time2",default="00:00", compute='compute_hours_out_time')
    out_time3 = fields.Char("Out Time3",default="00:00", compute='compute_hours_out_time')
    out_time4 = fields.Char("Out Time4",default="00:00", compute='compute_hours_out_time')
    out_time5 = fields.Char("Out Time5",default="00:00", compute='compute_hours_out_time')
    out_time6 = fields.Char("Out Time6",default="00:00", compute='compute_hours_out_time')
    out_time7 = fields.Char("Out Time7",default="00:00", compute='compute_hours_out_time')

    scheduled_in_time1 = fields.Char("Scheduled In Time1",default="00:00", compute='compute_hours_in_time')
    scheduled_in_time2 = fields.Char("Scheduled In Time2",default="00:00", compute='compute_hours_in_time')
    scheduled_in_time3 = fields.Char("Scheduled In Time3",default="00:00", compute='compute_hours_in_time')
    scheduled_in_time4 = fields.Char("Scheduled In Time4",default="00:00", compute='compute_hours_in_time')
    scheduled_in_time5 = fields.Char("Scheduled In Time5",default="00:00", compute='compute_hours_in_time')
    scheduled_in_time6 = fields.Char("Scheduled In Time6",default="00:00", compute='compute_hours_in_time')
    scheduled_in_time7 = fields.Char("Scheduled In Time7",default="00:00", compute='compute_hours_in_time')

    scheduled_break_start1 = fields.Char("Scheduled Break Start1",default="00:00", compute='compute_hours_break_start')
    scheduled_break_start2 = fields.Char("Scheduled Break Start2",default="00:00", compute='compute_hours_break_start')
    scheduled_break_start3 = fields.Char("Scheduled Break Start3",default="00:00", compute='compute_hours_break_start')
    scheduled_break_start4 = fields.Char("Scheduled Break Start4",default="00:00", compute='compute_hours_break_start')
    scheduled_break_start5 = fields.Char("Scheduled Break Start5",default="00:00", compute='compute_hours_break_start')
    scheduled_break_start6 = fields.Char("Scheduled Break Start6",default="00:00", compute='compute_hours_break_start')
    scheduled_break_start7 = fields.Char("Scheduled Break Start7",default="00:00", compute='compute_hours_break_start')


    scheduled_break_end1 = fields.Char("Scheduled Break End1",default="00:00", compute='compute_hours_break_end')
    scheduled_break_end2 = fields.Char("Scheduled Break End2",default="00:00", compute='compute_hours_break_end')
    scheduled_break_end3 = fields.Char("Scheduled Break End3",default="00:00", compute='compute_hours_break_end')
    scheduled_break_end4 = fields.Char("Scheduled Break End4",default="00:00", compute='compute_hours_break_end')
    scheduled_break_end5 = fields.Char("Scheduled Break End5",default="00:00", compute='compute_hours_break_end')
    scheduled_break_end6 = fields.Char("Scheduled Break End6",default="00:00", compute='compute_hours_break_end')
    scheduled_break_end7 = fields.Char("Scheduled Break End7",default="00:00", compute='compute_hours_break_end')

    ot_total = fields.Char("OT Total", compute='compute_hours_ot_total')
    hours_total = fields.Char("Hours Total",  compute='compute_hours_ot_total')
        
    from_date = fields.Date(" From Date")
    to_date = fields.Date("To Date")        
    week_type = fields.Selection([('week1','week1'), ('week2','week2')])
    
    salary_type = fields.Char('Salary Type')
    hourly_rate = fields.Float('Hourly Rate')
    wage = fields.Float('Wage')
    week2_id = fields.Many2one("staff.planning.display.week",string="Week 2 Ref", compute='_compute_week_two')

    _sql_constraints = [('staff_week_uniq', 'unique (employee_id,week_type,to_date,job_id)', 'Employee already entered in scheduler')]
    

    @api.depends('day1','day2','day3','day4','day5','day6','day7')
    def compute_hours_in_time(self):
        for row in self:
            
            row.scheduled_in_time1=row.scheduled_in_time2=row.scheduled_in_time3=row.scheduled_in_time4=row.scheduled_in_time5=row.scheduled_in_time6=row.scheduled_in_time7=''
            
            
            if row.day1 != False and row.day1 != '00:00':
                if row.in_time1:
                    if row.in_time1 != '00:00':
                        in_time_temp = datetime.datetime.strptime(str(row.in_time1).replace('am','').strip(), "%H:%M")
                        in_time_result = in_time_temp.strftime("%I:%M %p")
                        row.scheduled_in_time1 = in_time_result
                    elif row.employee_id.in_time != '00:00':
                        in_time_temp = datetime.datetime.strptime(str(row.employee_id.in_time).replace('am','').strip(), "%H:%M")
                        in_time_result = in_time_temp.strftime("%I:%M %p")
                        row.scheduled_in_time1 = in_time_result

            if row.day2 != False and row.day2 != '00:00':
                if row.in_time2:
                    if row.in_time2 != '00:00':
                        in_time_temp = datetime.datetime.strptime(str(row.in_time2).replace('am','').strip(), "%H:%M")
                        in_time_result = in_time_temp.strftime("%I:%M %p")
                        row.scheduled_in_time2 = in_time_result
                    elif row.employee_id.in_time != '00:00':
                        print row.employee_id.name,'==',row.employee_id.in_time
                        in_time_temp = datetime.datetime.strptime(str(row.employee_id.in_time).replace('am','').strip(), "%H:%M")
                        in_time_result = in_time_temp.strftime("%I:%M %p")
                        row.scheduled_in_time2 = in_time_result
            
            if row.day3 != False and row.day3 != '00:00':
                if row.in_time3:
                    if row.in_time3 != '00:00':
                        print str(row.in_time3)
                        in_time_temp = datetime.datetime.strptime(str(row.in_time3).replace('am','').strip(), "%H:%M")
                        in_time_result = in_time_temp.strftime("%I:%M %p")
                        row.scheduled_in_time3 = in_time_result
                    elif row.employee_id.in_time != '00:00':
                        in_time_temp = datetime.datetime.strptime(str(row.employee_id.in_time).replace('am','').strip(), "%H:%M")
                        in_time_result = in_time_temp.strftime("%I:%M %p")
                        row.scheduled_in_time3 = in_time_result

            if row.day4 != False and row.day4 != '00:00':
                if row.in_time4:
                    if row.in_time4 != '00:00':
                        in_time_temp = datetime.datetime.strptime(str(row.in_time4).replace('am','').strip(), "%H:%M")
                        in_time_result = in_time_temp.strftime("%I:%M %p")
                        row.scheduled_in_time4 = in_time_result
                    elif row.employee_id.in_time != '00:00':
                        in_time_temp = datetime.datetime.strptime(str(row.employee_id.in_time).replace('am','').strip(), "%H:%M")
                        in_time_result = in_time_temp.strftime("%I:%M %p")
                        row.scheduled_in_time4 = in_time_result

            if row.day5 != False and row.day5 != '00:00':
                if row.in_time5:
                    if row.in_time5 != '00:00':
                        in_time_temp = datetime.datetime.strptime(str(row.in_time5).replace('am','').strip(), "%H:%M")
                        in_time_result = in_time_temp.strftime("%I:%M %p")
                        row.scheduled_in_time5 = in_time_result
                    elif row.employee_id.in_time != '00:00':
                        in_time_temp = datetime.datetime.strptime(str(row.employee_id.in_time).replace('am','').strip(), "%H:%M")
                        in_time_result = in_time_temp.strftime("%I:%M %p")
                        row.scheduled_in_time5 = in_time_result

            if row.day6 != False and row.day6 != '00:00':
                if row.in_time6:
                    if row.in_time6 != '00:00':
                        in_time_temp = datetime.datetime.strptime(str(row.in_time6).replace('am','').strip(), "%H:%M")
                        in_time_result = in_time_temp.strftime("%I:%M %p")
                        row.scheduled_in_time6 = in_time_result
                    elif row.employee_id.in_time != '00:00':
                        in_time_temp = datetime.datetime.strptime(str(row.employee_id.in_time).replace('am','').strip(), "%H:%M")
                        in_time_result = in_time_temp.strftime("%I:%M %p")
                        row.scheduled_in_time6 = in_time_result

            if row.day7 != False and row.day7 != '00:00':
                if row.in_time7:
                    if row.in_time7 != '00:00':
                        in_time_temp = datetime.datetime.strptime(str(row.in_time7).replace('am','').strip(), "%H:%M")
                        in_time_result = in_time_temp.strftime("%I:%M %p")
                        row.scheduled_in_time7 = in_time_result
                    elif row.employee_id.in_time != '00:00':
                        in_time_temp = datetime.datetime.strptime(str(row.employee_id.in_time).replace('am','').strip(), "%H:%M")
                        in_time_result = in_time_temp.strftime("%I:%M %p")
                        row.scheduled_in_time7 = in_time_result


    @api.depends('day1','day2','day3','day4','day5','day6','day7')
    def compute_hours_break_start(self):
        for row in self:
            row.scheduled_break_start1=row.scheduled_break_start2=row.scheduled_break_start3=row.scheduled_break_start4=row.scheduled_break_start5=row.scheduled_break_start6=row.scheduled_break_start7=''
            
            if row.day1 != False and row.day1 != '00:00':
                if row.break_start1:
                    if row.break_start1 != '00:00':
                        break_start_temp = datetime.datetime.strptime(str(row.break_start1).replace('am','').strip(), "%H:%M")
                        break_start_result = break_start_temp.strftime("%I:%M %p")
                        row.scheduled_break_start1 = break_start_result
                    elif row.employee_id.break_start != '00:00':
                        break_start_temp = datetime.datetime.strptime(str(row.employee_id.break_start).replace('am','').strip(), "%H:%M")
                        break_start_result = break_start_temp.strftime("%I:%M %p")
                        row.scheduled_break_start1 = break_start_result

            if row.day2 != False and row.day2 != '00:00':
                if row.break_start2:
                    if row.break_start2 != '00:00':
                        break_start_temp = datetime.datetime.strptime(str(row.break_start2).replace('am','').strip(), "%H:%M")
                        break_start_result = break_start_temp.strftime("%I:%M %p")
                        row.scheduled_break_start2 = break_start_result
                    elif row.employee_id.break_start != '00:00':
                        break_start_temp = datetime.datetime.strptime(str(row.employee_id.break_start).replace('am','').strip(), "%H:%M")
                        break_start_result = break_start_temp.strftime("%I:%M %p")
                        row.scheduled_break_start2 = break_start_result
            
            if row.day3 != False and row.day3 != '00:00':
                if row.break_start3:
                    if row.break_start3 != '00:00':
                        break_start_temp = datetime.datetime.strptime(str(row.break_start3).replace('am','').strip(), "%H:%M")
                        break_start_result = break_start_temp.strftime("%I:%M %p")
                        row.scheduled_break_start3 = break_start_result
                    elif row.employee_id.break_start != '00:00':
                        break_start_temp = datetime.datetime.strptime(str(row.employee_id.break_start).replace('am','').strip(), "%H:%M")
                        break_start_result = break_start_temp.strftime("%I:%M %p")
                        row.scheduled_break_start3 = break_start_result

            if row.day4 != False and row.day4 != '00:00':
                if row.break_start4:
                    if row.break_start4 != '00:00':
                        break_start_temp = datetime.datetime.strptime(str(row.break_start4).replace('am','').strip(), "%H:%M")
                        break_start_result = break_start_temp.strftime("%I:%M %p")
                        row.scheduled_break_start4 = break_start_result
                    elif row.employee_id.break_start != '00:00':
                        break_start_temp = datetime.datetime.strptime(str(row.employee_id.break_start).replace('am','').strip(), "%H:%M")
                        break_start_result = break_start_temp.strftime("%I:%M %p")
                        row.scheduled_break_start4 = break_start_result

            if row.day5 != False and row.day5 != '00:00':
                if row.break_start5:
                    if row.break_start5 != '00:00':
                        break_start_temp = datetime.datetime.strptime(str(row.break_start5).replace('am','').strip(), "%H:%M")
                        break_start_result = break_start_temp.strftime("%I:%M %p")
                        row.scheduled_break_start5 = break_start_result
                    elif row.employee_id.break_start != '00:00':
                        break_start_temp = datetime.datetime.strptime(str(row.employee_id.break_start).replace('am','').strip(), "%H:%M")
                        break_start_result = break_start_temp.strftime("%I:%M %p")
                        row.scheduled_break_start5 = break_start_result

            if row.day6 != False and row.day6 != '00:00':
                if row.break_start6:
                    if row.break_start6 != '00:00':
                        break_start_temp = datetime.datetime.strptime(str(row.break_start6).replace('am','').strip(), "%H:%M")
                        break_start_result = break_start_temp.strftime("%I:%M %p")
                        row.scheduled_break_start6 = break_start_result
                    elif row.employee_id.break_start != '00:00':
                        break_start_temp = datetime.datetime.strptime(str(row.employee_id.break_start).replace('am','').strip(), "%H:%M")
                        break_start_result = break_start_temp.strftime("%I:%M %p")
                        row.scheduled_break_start6 = break_start_result or '00:00'
            
            if row.day7 != False and row.day7 != '00:00':
                if row.break_start7:
                    if row.break_start7 != '00:00':
                        break_start_temp = datetime.datetime.strptime(str(row.break_start7).replace('am','').strip(), "%H:%M")
                        break_start_result = break_start_temp.strftime("%I:%M %p")
                        row.scheduled_break_start7 = break_start_result
                    elif row.employee_id.break_start != '00:00':
                        break_start_temp = datetime.datetime.strptime(str(row.employee_id.break_start).replace('am','').strip(), "%H:%M")
                        break_start_result = break_start_temp.strftime("%I:%M %p")
                        row.scheduled_break_start7 = break_start_result


    @api.depends('day1','day2','day3','day4','day5','day6','day7')
    def compute_hours_break_end(self):
        for row in self:
            
            row.scheduled_break_end1=row.scheduled_break_end2=row.scheduled_break_end3=row.scheduled_break_end4=row.scheduled_break_end5=row.scheduled_break_end6=row.scheduled_break_end7=''
            
            if row.day1 != False and row.day1 != '00:00':
                if row.break_end1:
                    if row.break_end1 != '00:00':
                        break_end_temp = datetime.datetime.strptime(str(row.break_end1).replace('am','').strip(), "%H:%M")
                        break_end_result = break_end_temp.strftime("%I:%M %p")
                        row.scheduled_break_end1 = break_end_result
                    elif row.employee_id.break_end != '00:00':
                        break_end_temp = datetime.datetime.strptime(str(row.employee_id.break_end).replace('am','').strip(), "%H:%M")
                        break_end_result = break_end_temp.strftime("%I:%M %p")
                        row.scheduled_break_end1 = break_end_result

            if row.day2 != False and row.day2 != '00:00':
                if row.break_end2:
                    if row.break_end2 != '00:00':
                        break_end_temp = datetime.datetime.strptime(str(row.break_end2).replace('am','').strip(), "%H:%M")
                        break_end_result = break_end_temp.strftime("%I:%M %p")
                        row.scheduled_break_end2 = break_end_result
                    elif row.employee_id.break_end != '00:00':
                        break_end_temp = datetime.datetime.strptime(str(row.employee_id.break_end).replace('am','').strip(), "%H:%M")
                        break_end_result = break_end_temp.strftime("%I:%M %p")
                        row.scheduled_break_end2 = break_end_result
            
            if row.day3 != False and row.day3 != '00:00':
                if row.break_end3:
                    if row.break_end3 != '00:00':
                        break_end_temp = datetime.datetime.strptime(str(row.break_end3).replace('am','').strip(), "%H:%M")
                        break_end_result = break_end_temp.strftime("%I:%M %p")
                        row.scheduled_break_end3 = break_end_result
                    elif row.employee_id.break_end != '00:00':
                        break_end_temp = datetime.datetime.strptime(str(row.employee_id.break_end).replace('am','').strip(), "%H:%M")
                        break_end_result = break_end_temp.strftime("%I:%M %p")
                        row.scheduled_break_end3 = break_end_result

            if row.day4 != False and row.day4 != '00:00':
                if row.break_end4:
                    if row.break_end4 != '00:00':
                        break_end_temp = datetime.datetime.strptime(str(row.break_end4).replace('am','').strip(), "%H:%M")
                        break_end_result = break_end_temp.strftime("%I:%M %p")
                        row.scheduled_break_end4 = break_end_result
                    elif row.employee_id.break_end != '00:00':
                        break_end_temp = datetime.datetime.strptime(str(row.employee_id.break_end).replace('am','').strip(), "%H:%M")
                        break_end_result = break_end_temp.strftime("%I:%M %p")
                        row.scheduled_break_end4 = break_end_result

            if row.day5 != False and row.day5 != '00:00':
                if row.break_end5:
                    if row.break_end5 != '00:00':
                        break_end_temp = datetime.datetime.strptime(str(row.break_end5).replace('am','').strip(), "%H:%M")
                        break_end_result = break_end_temp.strftime("%I:%M %p")
                        row.scheduled_break_end5 = break_end_result
                    elif row.employee_id.break_end != '00:00':
                        break_end_temp = datetime.datetime.strptime(str(row.employee_id.break_end).replace('am','').strip(), "%H:%M")
                        break_end_result = break_end_temp.strftime("%I:%M %p")
                        row.scheduled_break_end5 = break_end_result

            if row.day6 != False and row.day6 != '00:00':
                if row.break_end6:
                    if row.break_end6 != '00:00':
                        break_end_temp = datetime.datetime.strptime(str(row.break_end6).replace('am','').strip(), "%H:%M")
                        break_end_result = break_end_temp.strftime("%I:%M %p")
                        row.scheduled_break_end6 = break_end_result
                    elif row.employee_id.break_end != '00:00':
                        break_end_temp = datetime.datetime.strptime(str(row.employee_id.break_end).replace('am','').strip(), "%H:%M")
                        break_end_result = break_end_temp.strftime("%I:%M %p")
                        row.scheduled_break_end6 = break_end_result

            if row.day7 != False and row.day7 != '00:00':
                if row.break_end7:
                    if row.break_end7 != '00:00':
                        break_end_temp = datetime.datetime.strptime(str(row.break_end7).replace('am','').strip(), "%H:%M")
                        break_end_result = break_end_temp.strftime("%I:%M %p")
                        row.scheduled_break_end7 = break_end_result
                    elif row.employee_id.break_end != '00:00':
                        break_end_temp = datetime.datetime.strptime(str(row.employee_id.break_end).replace('am','').strip(), "%H:%M")
                        break_end_result = break_end_temp.strftime("%I:%M %p")
                        row.scheduled_break_end7 = break_end_result


    @api.depends('day1','day2','day3','day4','day5','day6','day7')
    def compute_hours_out_time(self):
        for row in self:
            if row.in_time1 != False and row.day1 != False:
                time_without_break=break_diff_hrs=tout_with_break='00:00'
                if row.in_time1 != '00:00' and row.day1 != '00:00':
                    time_without_break = self.add_time_tout(row.in_time1,row.day1)
                elif row.employee_id.in_time != '00:00' and row.day1 != '00:00':
                    time_without_break = self.add_time_tout(row.employee_id.in_time,row.day1)
                
                if row.break_start1 != '00:00' and row.break_end1 != '00:00':

                    if (int(str(row.break_end1).split(':')[1]))-(int(str(row.break_start1).split(':')[1]))>=0:
                        break_diff_hrs = str((int(str(row.break_end1).split(':')[0]))-(int(str(row.break_start1).split(':')[0])))+':'+str((int(str(row.break_end1).split(':')[1]))-(int(str(row.break_start1).split(':')[1])))
                    else:
                        break_diff_hrs = str((int(str(row.break_end1).split(':')[0]))-(int(str(row.break_start1).split(':')[0]))-1)+':'+str(60+(int(str(row.break_end1).split(':')[1]))-(int(str(row.break_start1).split(':')[1])))
                    
                    if break_diff_hrs != '00:00':
                        tout_with_break = self.add_time_tout(time_without_break,break_diff_hrs)
                    else:
                        tout_with_break = time_without_break

                elif row.employee_id.break_start != '00:00' and row.employee_id.break_end != '00:00':

                    if (int(str(row.employee_id.break_end).split(':')[1]))-(int(str(row.employee_id.break_start).split(':')[1]))>=0:
                        break_diff_hrs = str((int(str(row.employee_id.break_end).split(':')[0]))-(int(str(row.employee_id.break_start).split(':')[0])))+':'+str((int(str(row.employee_id.break_end).split(':')[1]))-(int(str(row.employee_id.break_start).split(':')[1])))
                    else:
                        break_diff_hrs = str((int(str(row.employee_id.break_end).split(':')[0]))-(int(str(row.employee_id.break_start).split(':')[0]))-1)+':'+str(60+(int(str(row.employee_id.break_end).split(':')[1]))-(int(str(row.employee_id.break_start).split(':')[1])))

                    if break_diff_hrs != '00:00':
                        tout_with_break = self.add_time_tout(time_without_break,break_diff_hrs)
                    else:
                        tout_with_break = time_without_break
                else:
                    tout_with_break = time_without_break

                out_time_temp=out_time_result=''

                if tout_with_break != '00:00':
                    out_time_temp = datetime.datetime.strptime(str(tout_with_break), "%H:%M")
                    out_time_result = out_time_temp.strftime("%I:%M %p")

                row.out_time1 = out_time_result
                
            if row.in_time2 != False and row.day2 != False:
                time_without_break=break_diff_hrs=tout_with_break='00:00'
                if row.in_time2 != '00:00' and row.day2 != '00:00':
                    time_without_break = self.add_time_tout(row.in_time2,row.day2)
                elif row.employee_id.in_time != '00:00' and row.day2 != '00:00':
                    time_without_break = self.add_time_tout(row.employee_id.in_time,row.day2)
                
                if row.break_start2 != '00:00' and row.break_end2 != '00:00':
                    if (int(str(row.break_end2).split(':')[1]))-(int(str(row.break_start2).split(':')[1]))>=0:
                        break_diff_hrs = str((int(str(row.break_end2).split(':')[0]))-(int(str(row.break_start2).split(':')[0])))+':'+str((int(str(row.break_end2).split(':')[1]))-(int(str(row.break_start2).split(':')[1])))
                    else:
                        break_diff_hrs = str((int(str(row.break_end2).split(':')[0]))-(int(str(row.break_start2).split(':')[0]))-1)+':'+str(60+(int(str(row.break_end2).split(':')[1]))-(int(str(row.break_start2).split(':')[1])))
                    
                    if break_diff_hrs != '00:00':
                        tout_with_break = self.add_time_tout(time_without_break,break_diff_hrs)
                    else:
                        tout_with_break = time_without_break

                elif row.employee_id.break_start != '00:00' and row.employee_id.break_end != '00:00':

                    if (int(str(row.employee_id.break_end).split(':')[1]))-(int(str(row.employee_id.break_start).split(':')[1]))>=0:
                        break_diff_hrs = str((int(str(row.employee_id.break_end).split(':')[0]))-(int(str(row.employee_id.break_start).split(':')[0])))+':'+str((int(str(row.employee_id.break_end).split(':')[1]))-(int(str(row.employee_id.break_start).split(':')[1])))
                    else:
                        break_diff_hrs = str((int(str(row.employee_id.break_end).split(':')[0]))-(int(str(row.employee_id.break_start).split(':')[0]))-1)+':'+str(60+(int(str(row.employee_id.break_end).split(':')[1]))-(int(str(row.employee_id.break_start).split(':')[1])))
                        
                    if break_diff_hrs != '00:00':
                        tout_with_break = self.add_time_tout(time_without_break,break_diff_hrs)
                    else:
                        tout_with_break = time_without_break
                else:
                    tout_with_break = time_without_break

                out_time_temp=out_time_result=''

                if tout_with_break != '00:00':
                    out_time_temp = datetime.datetime.strptime(str(tout_with_break).replace("-", "").strip(), "%H:%M")
                    out_time_result = out_time_temp.strftime("%I:%M %p")

                row.out_time2 = out_time_result
                
            if row.in_time3 != False and row.day3 != False:
                time_without_break=break_diff_hrs=tout_with_break='00:00'
                if row.in_time3 != '00:00' and row.day3 != '00:00':
                    time_without_break = self.add_time_tout(row.in_time3,row.day3)
                elif row.employee_id.in_time != '00:00' and row.day3 != '00:00':
                    time_without_break = self.add_time_tout(row.employee_id.in_time,row.day3)
                
                if row.break_start3 != '00:00' and row.break_end3 != '00:00':

                    if (int(str(row.break_end3).split(':')[1]))-(int(str(row.break_start3).split(':')[1]))>=0:
                        break_diff_hrs = str((int(str(row.break_end3).split(':')[0]))-(int(str(row.break_start3).split(':')[0])))+':'+str((int(str(row.break_end3).split(':')[1]))-(int(str(row.break_start3).split(':')[1])))
                    else:
                        break_diff_hrs = str((int(str(row.break_end3).split(':')[0]))-(int(str(row.break_start3).split(':')[0]))-1)+':'+str(60+(int(str(row.break_end3).split(':')[1]))-(int(str(row.break_start3).split(':')[1])))
                    
                    if break_diff_hrs != '00:00':
                        tout_with_break = self.add_time_tout(time_without_break,break_diff_hrs)
                    else:
                        tout_with_break = time_without_break

                elif row.employee_id.break_start != '00:00' and row.employee_id.break_end != '00:00':

                    if (int(str(row.employee_id.break_end).split(':')[1]))-(int(str(row.employee_id.break_start).split(':')[1]))>=0:
                        break_diff_hrs = str((int(str(row.employee_id.break_end).split(':')[0]))-(int(str(row.employee_id.break_start).split(':')[0])))+':'+str((int(str(row.employee_id.break_end).split(':')[1]))-(int(str(row.employee_id.break_start).split(':')[1])))
                    else:
                        break_diff_hrs = str((int(str(row.employee_id.break_end).split(':')[0]))-(int(str(row.employee_id.break_start).split(':')[0]))-1)+':'+str(60+(int(str(row.employee_id.break_end).split(':')[1]))-(int(str(row.employee_id.break_start).split(':')[1])))
                        
                    if break_diff_hrs != '00:00':
                        tout_with_break = self.add_time_tout(time_without_break,break_diff_hrs)
                    else:
                        tout_with_break = time_without_break
                else:
                    tout_with_break = time_without_break

                out_time_temp=out_time_result=''

                if tout_with_break != '00:00':
                    out_time_temp = datetime.datetime.strptime(str(tout_with_break).replace("-", "").strip(), "%H:%M")
                    out_time_result = out_time_temp.strftime("%I:%M %p")

                row.out_time3 = out_time_result
                
            if row.in_time4 != False and row.day4 != False:

                time_without_break=break_diff_hrs=tout_with_break='00:00'
                if row.in_time4 != '00:00' and row.day4 != '00:00':
                    time_without_break = self.add_time_tout(row.in_time4,row.day4)
                elif row.employee_id.in_time != '00:00' and row.day4 != '00:00':
                    time_without_break = self.add_time_tout(row.employee_id.in_time,row.day4)

                if row.break_start4 != '00:00' and row.break_end4 != '00:00':

                    if (int(str(row.break_end4).split(':')[1]))-(int(str(row.break_start4).split(':')[1]))>=0:
                        break_diff_hrs = str((int(str(row.break_end4).split(':')[0]))-(int(str(row.break_start4).split(':')[0])))+':'+str((int(str(row.break_end4).split(':')[1]))-(int(str(row.break_start4).split(':')[1])))
                    else:
                        break_diff_hrs = str((int(str(row.break_end4).split(':')[0]))-(int(str(row.break_start4).split(':')[0]))-1)+':'+str(60+(int(str(row.break_end4).split(':')[1]))-(int(str(row.break_start4).split(':')[1])))
                    
                    if break_diff_hrs != '00:00':
                        tout_with_break = self.add_time_tout(time_without_break,break_diff_hrs)
                    else:
                        tout_with_break = time_without_break

                elif row.employee_id.break_start != '00:00' and row.employee_id.break_end != '00:00':

                    if (int(str(row.employee_id.break_end).split(':')[1]))-(int(str(row.employee_id.break_start).split(':')[1]))>=0:
                        break_diff_hrs = str((int(str(row.employee_id.break_end).split(':')[0]))-(int(str(row.employee_id.break_start).split(':')[0])))+':'+str((int(str(row.employee_id.break_end).split(':')[1]))-(int(str(row.employee_id.break_start).split(':')[1])))
                    else:
                        break_diff_hrs = str((int(str(row.employee_id.break_end).split(':')[0]))-(int(str(row.employee_id.break_start).split(':')[0]))-1)+':'+str(60+(int(str(row.employee_id.break_end).split(':')[1]))-(int(str(row.employee_id.break_start).split(':')[1])))


                    if break_diff_hrs != '00:00':
                        tout_with_break = self.add_time_tout(time_without_break,break_diff_hrs)
                    else:
                        tout_with_break = time_without_break
                else:
                    tout_with_break = time_without_break

                out_time_temp=out_time_result=''

                if tout_with_break != '00:00':
                    out_time_temp = datetime.datetime.strptime(str(tout_with_break).replace("-", ""), "%H:%M")
                    out_time_result = out_time_temp.strftime("%I:%M %p")

                row.out_time4 = out_time_result
                
            if row.in_time5 != False and row.day5 != False:
                time_without_break=break_diff_hrs=tout_with_break='00:00'
                if row.in_time5 != '00:00' and row.day5 != '00:00':
                    time_without_break = self.add_time_tout(row.in_time5,row.day5)
                elif row.employee_id.in_time != '00:00' and row.day5 != '00:00':
                    time_without_break = self.add_time_tout(row.employee_id.in_time,row.day5)
                
                if row.break_start5 != '00:00' and row.break_end5 != '00:00':

                    if (int(str(row.break_end5).split(':')[1]))-(int(str(row.break_start5).split(':')[1]))>=0:
                        break_diff_hrs = str((int(str(row.break_end5).split(':')[0]))-(int(str(row.break_start5).split(':')[0])))+':'+str((int(str(row.break_end5).split(':')[1]))-(int(str(row.break_start5).split(':')[1])))
                    else:
                        break_diff_hrs = str((int(str(row.break_end5).split(':')[0]))-(int(str(row.break_start5).split(':')[0]))-1)+':'+str(60+(int(str(row.break_end5).split(':')[1]))-(int(str(row.break_start5).split(':')[1])))
                    
                    if break_diff_hrs != '00:00':
                        tout_with_break = self.add_time_tout(time_without_break,break_diff_hrs)
                    else:
                        tout_with_break = time_without_break

                elif row.employee_id.break_start != '00:00' and row.employee_id.break_end != '00:00':

                    if (int(str(row.employee_id.break_end).split(':')[1]))-(int(str(row.employee_id.break_start).split(':')[1]))>=0:
                        break_diff_hrs = str((int(str(row.employee_id.break_end).split(':')[0]))-(int(str(row.employee_id.break_start).split(':')[0])))+':'+str((int(str(row.employee_id.break_end).split(':')[1]))-(int(str(row.employee_id.break_start).split(':')[1])))
                    else:
                        break_diff_hrs = str((int(str(row.employee_id.break_end).split(':')[0]))-(int(str(row.employee_id.break_start).split(':')[0]))-1)+':'+str(60+(int(str(row.employee_id.break_end).split(':')[1]))-(int(str(row.employee_id.break_start).split(':')[1])))
                        
                    
                    if break_diff_hrs != '00:00':
                        tout_with_break = self.add_time_tout(time_without_break,break_diff_hrs)                        
                    else:
                        tout_with_break = time_without_break
                else:
                    tout_with_break = time_without_break


                out_time_temp=out_time_result=''

                if tout_with_break != '00:00':
                    out_time_temp = datetime.datetime.strptime(str(tout_with_break).replace("-", "").strip(), "%H:%M")
                    out_time_result = out_time_temp.strftime("%I:%M %p")

                row.out_time5 = out_time_result
                
            if row.in_time6 != False and row.day6 != False:
                time_without_break=break_diff_hrs=tout_with_break='00:00'
                if row.in_time6 != '00:00' and row.day6 != '00:00':
                    time_without_break = self.add_time_tout(row.in_time6,row.day6)
                elif row.employee_id.in_time != '00:00' and row.day6 != '00:00':
                    time_without_break = self.add_time_tout(row.employee_id.in_time,row.day6)
                
                if row.break_start6 != '00:00' and row.break_end6 != '00:00':

                    if (int(str(row.break_end6).split(':')[1]))-(int(str(row.break_start6).split(':')[1]))>=0:
                        break_diff_hrs = str((int(str(row.break_end6).split(':')[0]))-(int(str(row.break_start6).split(':')[0])))+':'+str((int(str(row.break_end6).split(':')[1]))-(int(str(row.break_start6).split(':')[1])))
                    else:
                        break_diff_hrs = str((int(str(row.break_end6).split(':')[0]))-(int(str(row.break_start6).split(':')[0]))-1)+':'+str(60+(int(str(row.break_end6).split(':')[1]))-(int(str(row.break_start6).split(':')[1])))
                    
                    if break_diff_hrs != '00:00':
                        tout_with_break = self.add_time_tout(time_without_break,break_diff_hrs)
                    else:
                        tout_with_break = time_without_break

                elif row.employee_id.break_start != '00:00' and row.employee_id.break_end != '00:00':

                    if (int(str(row.employee_id.break_end).split(':')[1]))-(int(str(row.employee_id.break_start).split(':')[1]))>=0:
                        break_diff_hrs = str((int(str(row.break_end6).split(':')[0]))-(int(str(row.break_start6).split(':')[0])))+':'+str((int(str(row.break_end7).split(':')[1]))-(int(str(row.break_start7).split(':')[1])))
                    else:
                        break_diff_hrs = str((int(str(row.break_end6).split(':')[0]))-(int(str(row.break_start6).split(':')[0]))-1)+':'+str(60+(int(str(row.break_end7).split(':')[1]))-(int(str(row.break_start7).split(':')[1])))
                       
                    if break_diff_hrs != '00:00':
                        tout_with_break = self.add_time_tout(time_without_break,break_diff_hrs)
                    else:
                        tout_with_break = time_without_break
                else:
                    tout_with_break = time_without_break

                out_time_temp=out_time_result=''

                if tout_with_break != '00:00':
                    out_time_temp = datetime.datetime.strptime(str(tout_with_break).replace("-", "").strip(), "%H:%M")
                    out_time_result = out_time_temp.strftime("%I:%M %p")

                row.out_time6 = out_time_result
                
            if row.in_time7 != False and row.day7 != False:
                time_without_break=break_diff_hrs=tout_with_break='00:00'
                if row.in_time7 != '00:00' and row.day7 != '00:00':
                    time_without_break = self.add_time_tout(row.in_time7,row.day7)
                elif row.employee_id.in_time != '00:00' and row.day1 != '00:00':
                    time_without_break = self.add_time_tout(row.employee_id.in_time,row.day7)
                
                if row.break_start7 != '00:00' and row.break_end7 != '00:00':

                    if (int(str(row.break_end7).split(':')[1]))-(int(str(row.break_start7).split(':')[1]))>=0:
                        break_diff_hrs = str((int(str(row.break_end7).split(':')[0]))-(int(str(row.break_start7).split(':')[0])))+':'+str((int(str(row.break_end7).split(':')[1]))-(int(str(row.break_start7).split(':')[1])))
                    else:
                        break_diff_hrs = str((int(str(row.break_end7).split(':')[0]))-(int(str(row.break_start7).split(':')[0]))-1)+':'+str(60+(int(str(row.break_end7).split(':')[1]))-(int(str(row.break_start7).split(':')[1])))
                        
                    if break_diff_hrs != '00:00':
                        tout_with_break = self.add_time_tout(time_without_break,break_diff_hrs)
                    else:
                        tout_with_break = time_without_break

                elif row.employee_id.break_start != '00:00' and row.employee_id.break_end != '00:00':

                    if (int(str(row.employee_id.break_end).split(':')[1]))-(int(str(row.employee_id.break_start).split(':')[1]))>=0:
                        break_diff_hrs = str((int(str(row.employee_id.break_end).split(':')[0]))-(int(str(row.employee_id.break_start).split(':')[0])))+':'+str((int(str(row.employee_id.break_end).split(':')[1]))-(int(str(row.employee_id.break_start).split(':')[1])))
                    else:
                        break_diff_hrs = str((int(str(row.employee_id.break_end).split(':')[0]))-(int(str(row.employee_id.break_start).split(':')[0]))-1)+':'+str(60+(int(str(row.employee_id.break_end).split(':')[1]))-(int(str(row.employee_id.break_start).split(':')[1])))
                        
                    if break_diff_hrs != '00:00':
                        tout_with_break = self.add_time_tout(time_without_break,break_diff_hrs)
                    else:
                        tout_with_break = time_without_break
                else:
                    tout_with_break = time_without_break

                out_time_temp=out_time_result=''

                if tout_with_break != '00:00':
                    out_time_temp = datetime.datetime.strptime(str(tout_with_break.replace("-", "")).strip(), "%H:%M")
                    out_time_result = out_time_temp.strftime("%I:%M %p")

                row.out_time7 = out_time_result


    @api.depends('display_id', 'employee_id', 'job_id')
    def compute_hours_ot_total(self):
        if self.week_type == 'week1':
            week_obj = self.env['staff.planning.display.week'].search([('id','!=',self.id),('week_type','=','week2'),('display_id','=',self.display_id.id),('employee_id','=',self.employee_id.id),('job_id','=',self.job_id.id)])
            if week_obj:
                self.week2_id = week_obj.id 


    @api.depends('display_id', 'employee_id', 'job_id')
    def _compute_week_two(self):
        if self.week_type == 'week1':
            week_obj = self.env['staff.planning.display.week'].search([('id','!=',self.id),('week_type','=','week2'),('display_id','=',self.display_id.id),('employee_id','=',self.employee_id.id),('job_id','=',self.job_id.id)], limit=1)
            if week_obj:
                print week_obj,'--'
                if len(week_obj) > 1:
                    raise UserError(_('There is an employee with two seniority title in same job position'))
                else:
                    self.week2_id = week_obj.id 
          
    @api.multi      
    def date_calc(self, from_date, days):
        date_from = (datetime.datetime.strptime(from_date, "%Y-%m-%d") + timedelta(days=int(days))).date().strftime("%m/%d")
        
        return date_from

    @api.multi      
    def paid_hrs_calc(self, employee, from_date, days):
        paid_hours_leaves=0
        date_var = (datetime.datetime.strptime(from_date, "%Y-%m-%d") + timedelta(days=int(days))).date()
        hr_paid_holidays=self.env['hr.holidays'].sudo().search([('employee_id', '=', employee),('holiday_status_id.paid_leave', '=', True),('date_from', '<=', date_var.strftime('%Y-%m-%d')),('date_to', '>=', date_var.strftime('%Y-%m-%d'))], limit=1)
        if hr_paid_holidays:                    
            paid_days=(datetime.datetime.strptime(hr_paid_holidays.date_to, "%Y-%m-%d")-datetime.datetime.strptime(hr_paid_holidays.date_from, "%Y-%m-%d")).days
            paid_days+=1
            paid_hours_leaves=hr_paid_holidays.number_of_hours_temp/paid_days
        if paid_hours_leaves:
            return paid_hours_leaves
        else:
            return "00:00"


    def add_time_tout(self, time, time2):
        
        list = [x.strip() for x in time.split(':')]
        list2 = [x.strip() for x in time2.split(':')]
    
        hrs = int(list[0].replace('am', '')) + int(list2[0].replace('am', ''))
        mins = int(list[1].replace('am', '')) + int(list2[1].replace('am', ''))
        if mins > 59:
            hrs = hrs + 1
            mins = mins - 60
        
        if len(str(hrs)) == 1:
            hrs = "0" + str(hrs)
        if len(str(mins)) == 1:
            mins = "0" + str(mins)


        if int(hrs) >= 24 :
            fnl_hrs = int(hrs)-24
            tot = str(fnl_hrs) + ":" + str(mins)
        else:
            tot = str(hrs) + ":" + str(mins)

        return tot

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

    
    @api.depends('day1', 'day2', 'day3', 'day4', 'day5')
    def compute_hours_ot_total(self):
        for line in self:
            hours=[]
            if line.day1:                
                hours.append(line.day1)
            if line.day2:                
                hours.append(line.day2)
            if line.day3:                
                hours.append(line.day3)
            if line.day4:                
                hours.append(line.day4)
            if line.day5:                
                hours.append(line.day5)
            if line.day6:                
                hours.append(line.day6)
            if line.day7:                
                hours.append(line.day7)
            tot_hours="00:00"
            for list in hours:
                tot_hours=self.add_time(tot_hours,list)
            line.hours_total=tot_hours
            
            split_hours=tot_hours.split(':')
            if int(split_hours[0])>=40:
                if int(split_hours[0])>40:       
                    ot_hours=int(split_hours[0])-40
                    if len(str(ot_hours))==1:
                        ot_hours="0"+str(ot_hours)
                    else:
                        ot_hours=str(ot_hours)
                    line.ot_total=ot_hours+":"+split_hours[1]
                else:
                    if int(split_hours[1])>0:
                        line.ot_total="00:"+split_hours[1]
                    else:                        
                        line.ot_total="00:00"
            else:
                line.ot_total="00:00"
                    

class StaffPlanningDisplay(models.Model):
    _name = 'staff.planning.display'
    
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


    name = fields.Many2one("hr.job",string="Name")
    planning_id = fields.Many2one("staff.planning",ondelete="cascade")
    week_hours= fields.One2many("staff.planning.display.week","display_id",ondelete="cascade")
    company_id = fields.Many2one("res.company", "Company")
    from_date = fields.Date("From Date")
    to_date = fields.Date("To Date")
    period = fields.Char("Period")
    custom_hours = fields.Float("Widget hours", default=1.0)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approval', 'Waiting for Approval'),
        ('validated', 'Validated'),
        ], string='Status', copy=False, index=True,related="planning_id.state")
    weeks2_id = fields.Many2one('staff.planning.display.week',compute='hours_calculation')


        
    def update_hours(self, date, empid, job_id,work_id,day_id,value):
        if work_id and day_id:
            if day_id=='day1':
                self.env['staff.planning.display.week'].sudo().search([('id', '=', work_id)]).day1=value
            if day_id=='day2':
                self.env['staff.planning.display.week'].sudo().search([('id', '=', work_id)]).day2=value
            if day_id=='day3':
                self.env['staff.planning.display.week'].sudo().search([('id', '=', work_id)]).day3=value
            if day_id=='day4':
                self.env['staff.planning.display.week'].sudo().search([('id', '=', work_id)]).day4=value
            if day_id=='day5':
                self.env['staff.planning.display.week'].sudo().search([('id', '=', work_id)]).day5=value
            if day_id=='day6':
                self.env['staff.planning.display.week'].sudo().search([('id', '=', work_id)]).day6=value
            if day_id=='day7':
                self.env['staff.planning.display.week'].sudo().search([('id', '=', work_id)]).day7=value

    
    def update_pto_hours(self, date, empid, job_id,work_id,day_id,paid,value):
        if work_id and day_id:        
            if day_id=='day1':
                self.env['staff.planning.display.week'].sudo().search([('id', '=', work_id)]).in_time1=value
            if day_id=='day2':
                self.env['staff.planning.display.week'].sudo().search([('id', '=', work_id)]).in_time2=value
            if day_id=='day3':
                self.env['staff.planning.display.week'].sudo().search([('id', '=', work_id)]).in_time3=value
            if day_id=='day4':
                self.env['staff.planning.display.week'].sudo().search([('id', '=', work_id)]).in_time4=value
            if day_id=='day5':
                self.env['staff.planning.display.week'].sudo().search([('id', '=', work_id)]).in_time5=value
            if day_id=='day6':
                self.env['staff.planning.display.week'].sudo().search([('id', '=', work_id)]).in_time6=value
            if day_id=='day7':
                self.env['staff.planning.display.week'].sudo().search([('id', '=', work_id)]).in_time7=value
        if float(paid)==0:
            employee_id=self.env['hr.employee'].sudo().search([('id', '=', empid)])
            if employee_id:
                employee_id.in_time=value
                return 1
        return 0

    
    def update_break_start(self, date, empid, job_id,work_id,day_id,paid,value):
        print self,date,empid,job_id,work_id,day_id,paid,value
        if work_id and day_id:        
            if day_id=='day1':
                self.env['staff.planning.display.week'].sudo().search([('id', '=', work_id)]).break_start1=value
            if day_id=='day2':
                self.env['staff.planning.display.week'].sudo().search([('id', '=', work_id)]).break_start2=value
            if day_id=='day3':
                self.env['staff.planning.display.week'].sudo().search([('id', '=', work_id)]).break_start3=value
            if day_id=='day4':
                self.env['staff.planning.display.week'].sudo().search([('id', '=', work_id)]).break_start4=value
            if day_id=='day5':
                self.env['staff.planning.display.week'].sudo().search([('id', '=', work_id)]).break_start5=value
            if day_id=='day6':
                self.env['staff.planning.display.week'].sudo().search([('id', '=', work_id)]).break_start6=value
            if day_id=='day7':
                self.env['staff.planning.display.week'].sudo().search([('id', '=', work_id)]).break_start7=value
        if float(paid)==0:
            employee_id=self.env['hr.employee'].sudo().search([('id', '=', empid)])
            if employee_id:
                employee_id.break_start=value
                return 1
        return 0

    
    def update_break_end(self, date, empid, job_id,work_id,day_id,paid,value):
        if work_id and day_id:        
            if day_id=='day1':
                self.env['staff.planning.display.week'].sudo().search([('id', '=', work_id)]).break_end1=value
            if day_id=='day2':
                self.env['staff.planning.display.week'].sudo().search([('id', '=', work_id)]).break_end2=value
            if day_id=='day3':
                self.env['staff.planning.display.week'].sudo().search([('id', '=', work_id)]).break_end3=value
            if day_id=='day4':
                self.env['staff.planning.display.week'].sudo().search([('id', '=', work_id)]).break_end4=value
            if day_id=='day5':
                self.env['staff.planning.display.week'].sudo().search([('id', '=', work_id)]).break_end5=value
            if day_id=='day6':
                self.env['staff.planning.display.week'].sudo().search([('id', '=', work_id)]).break_end6=value
            if day_id=='day7':
                self.env['staff.planning.display.week'].sudo().search([('id', '=', work_id)]).break_end7=value
        if float(paid)==0:
            employee_id=self.env['hr.employee'].sudo().search([('id', '=', empid)])
            if employee_id:
                employee_id.break_end=value
                return 1
        return 0


    def copy_previous_week(self,name,planning_id):
        hours_obj = self.env['staff.planning.display'].search([('name' , '=' , name),('planning_id' , '=' , planning_id)])
        for line in hours_obj:
            if line.planning_id.state=='draft':
                for lines in line.week_hours:
                    if(lines.week_type == 'week1'):
                        
                        weeks = self.env['staff.planning.display.week'].search([('employee_id','=',lines.employee_id.id),('job_id','=',lines.job_id.id),('week_type','=','week2'),('display_id','=',lines.display_id.id)],order='id desc')
                        print weeks
                        if len(weeks) == 1:
                            if weeks:
                                weeks.day1 = lines.day1
                                weeks.day2 = lines.day2
                                weeks.day3 = lines.day3
                                weeks.day4 = lines.day4
                                weeks.day5 = lines.day5
                                weeks.day6 = lines.day6
                                weeks.day7 = lines.day7
                                
                                weeks.in_time1 = lines.in_time1
                                weeks.in_time2 = lines.in_time2
                                weeks.in_time3 = lines.in_time3
                                weeks.in_time4 = lines.in_time4
                                weeks.in_time5 = lines.in_time5
                                weeks.in_time6 = lines.in_time6
                                weeks.in_time7 = lines.in_time7
                                
                                weeks.out_time1 = lines.out_time1
                                weeks.out_time2 = lines.out_time2
                                weeks.out_time3 = lines.out_time3
                                weeks.out_time4 = lines.out_time4
                                weeks.out_time5 = lines.out_time5
                                weeks.out_time6 = lines.out_time6
                                weeks.out_time7 = lines.out_time7
                                
                                weeks.break_start1 = lines.break_start1
                                weeks.break_start2 = lines.break_start2
                                weeks.break_start3 = lines.break_start3
                                weeks.break_start4 = lines.break_start4
                                weeks.break_start5 = lines.break_start5
                                weeks.break_start6 = lines.break_start6
                                weeks.break_start7 = lines.break_start7
                                
                                weeks.break_end1 = lines.break_end1
                                weeks.break_end2 = lines.break_end2
                                weeks.break_end3 = lines.break_end3
                                weeks.break_end4 = lines.break_end4
                                weeks.break_end5 = lines.break_end5
                                weeks.break_end6 = lines.break_end6
                                weeks.break_end7 = lines.break_end7
                        else:
                            raise UserError(_('There is an employee with two seniority title in same job position'))
            else:
                raise UserError(_('Scheduler is not in draft state to copy the work hours'))
            
            
            
    def copy_previous_week_new(self,name,planning_id):
        hours_obj_new = self.env['staff.planning.display'].search([('name' , '=' , name),('planning_id' , '=' , planning_id)])
        for line in hours_obj_new:
            if line.planning_id.state=='draft':
                for lines in line.week_hours:
                    if(lines.week_type == 'week1'):
                        date_id = lines.from_date
                        date=datetime.datetime.strptime(str(date_id), "%Y-%m-%d")- datetime.timedelta(days=1)
                        print date
                        
                        hours_obj_id = self.env['staff.planning.display'].search([('to_date' , '=' , date),('company_id' , '=' , line.company_id.id),('name' , '=' , line.name.id)])
                        print hours_obj_id
                        weeks = self.env['staff.planning.display.week'].search([('employee_id','=',lines.employee_id.id),('job_id','=',lines.job_id.id),('week_type','=','week1'),('display_id','=',lines.display_id.id)],order='id desc')
                        print weeks.display_id.id,"gggggggggg"
                        for weeks_new in hours_obj_id.week_hours:
                            if weeks_new.week_type =="week2" and weeks_new.employee_id.id == weeks.employee_id.id:
                                if weeks:
                                    weeks.day1 = weeks_new.day1
                                    weeks.day2 = weeks_new.day2
                                    weeks.day3 = weeks_new.day3
                                    weeks.day4 = weeks_new.day4
                                    weeks.day5 = weeks_new.day5
                                    weeks.day6 = weeks_new.day6
                                    weeks.day7 = weeks_new.day7
                                     
                                    weeks.in_time1 = weeks_new.in_time1
                                    weeks.in_time2 = weeks_new.in_time2
                                    weeks.in_time3 = weeks_new.in_time3
                                    weeks.in_time4 = weeks_new.in_time4
                                    weeks.in_time5 = weeks_new.in_time5
                                    weeks.in_time6 = weeks_new.in_time6
                                    weeks.in_time7 = weeks_new.in_time7
                                     
                                    weeks.out_time1 = weeks_new.out_time1
                                    weeks.out_time2 = weeks_new.out_time2
                                    weeks.out_time3 = weeks_new.out_time3
                                    weeks.out_time4 = weeks_new.out_time4
                                    weeks.out_time5 = weeks_new.out_time5
                                    weeks.out_time6 = weeks_new.out_time6
                                    weeks.out_time7 = weeks_new.out_time7
                                     
                                    weeks.break_start1 = weeks_new.break_start1
                                    weeks.break_start2 = weeks_new.break_start2
                                    weeks.break_start3 = weeks_new.break_start3
                                    weeks.break_start4 = weeks_new.break_start4
                                    weeks.break_start5 = weeks_new.break_start5
                                    weeks.break_start6 = weeks_new.break_start6
                                    weeks.break_start7 = weeks_new.break_start7
                                     
                                    weeks.break_end1 = weeks_new.break_end1
                                    weeks.break_end2 = weeks_new.break_end2
                                    weeks.break_end3 = weeks_new.break_end3
                                    weeks.break_end4 = weeks_new.break_end4
                                    weeks.break_end5 = weeks_new.break_end5
                                    weeks.break_end6 = weeks_new.break_end6
                                    weeks.break_end7 = weeks_new.break_end7
            else:
                raise UserError(_('Scheduler is not in draft state to copy the work hours'))
            
        
    def hours_list(self, from_date, to_date, company_id, job_position,week_no):
        result = {}
        dates = []        
        emp_hrs = []
        
        result['week_no'] = week_no
        from_date = datetime.datetime.strptime(from_date, "%Y-%m-%d")
        to_date = datetime.datetime.strptime(to_date, "%Y-%m-%d")
        planning_hours=self.env['staff.planning.display'].search([('from_date','=',from_date),('to_date','=',to_date),('name','=',job_position),('company_id','=',company_id)])
        planning_id=planning_hours.id
        if week_no==1:
            to_date = from_date + datetime.timedelta(days=6)  
            week_hours=self.env['staff.planning.display.week'].sudo().search([('display_id','=',planning_id),('week_type','=','week1')])          
        else:
            from_date = from_date + datetime.timedelta(days=7)
            week_hours=self.env['staff.planning.display.week'].sudo().search([('display_id','=',planning_id),('week_type','=','week2')]) 
        
        date_from = from_date
        date_to = to_date

        while (date_to >= date_from):
            date_new_antr = {}
            date_new_antr['d1'] = date_from.strftime('%a <br />%b %d')
            date_new_antr['d2'] = date_from.strftime('%Y-%m-%d')
            dates.append(date_new_antr)
            date_from = date_from + datetime.timedelta(days=1)
        result['dates'] = dates
                
        date_from = from_date
        date_to = to_date
        
        if week_hours:
            for week_hour in week_hours:                                 
                job_name = {}
                job_name['name'] = week_hour.employee_id.name
                job_name['job_position'] = week_hour.job_id.name
                job_name['work_hours'] = []
                
                for i in range(1,8):
                    day_hours="week_hour.day"+str(i)
                    pto_hours="week_hour.in_time"+str(i)
                    break_start="week_hour.break_start"+str(i)
                    break_end="week_hour.break_end"+str(i)
                    work_details = {}
                    work_details['date']=(date_from + datetime.timedelta(days=(i-1))).strftime('%Y-%m-%d')
                    if eval(day_hours):
                        work_details['hours']=eval(day_hours)
                    else:
                        work_details['hours']="00:00"
                    pto_hours_intime=eval(pto_hours)
                    
                    if pto_hours_intime=="00:00":          
                        work_details['pto_hours']=week_hour.employee_id.in_time  
                    else:               
                        work_details['pto_hours']=pto_hours_intime

                    if eval(day_hours):
                        work_details['hours']=eval(day_hours)
                    else:
                        work_details['hours']="00:00"
                    break_start_hours=eval(break_start)
                    
                    if break_start_hours=="00:00":          
                        work_details['break_start']=week_hour.employee_id.break_start  
                    else:               
                        work_details['break_start']=break_start_hours

                    if eval(day_hours):
                        work_details['hours']=eval(day_hours)
                    else:
                        work_details['hours']="00:00"
                    break_end_hours=eval(break_end)
                    
                    if break_end_hours=="00:00":          
                        work_details['break_end']=week_hour.employee_id.break_end  
                    else:               
                        work_details['break_end']=break_end_hours
                        
                    work_details['job']=job_position
                    work_details['emp_id']=week_hour.employee_id.id
                    work_details['day']="day"+str(i)
                    work_details['work_hour_id']=str(week_hour.id)
                    
                    paid_hours_leaves=unpaid_hours_leaves=0
                    hr_paid_holidays=self.env['hr.holidays'].sudo().search([('employee_id', '=', week_hour.employee_id.id),('holiday_status_id.paid_leave', '=', True),('date_from', '<=', (date_from + datetime.timedelta(days=(i-1))).strftime('%Y-%m-%d')),('date_to', '>=', (date_from + datetime.timedelta(days=(i-1))).strftime('%Y-%m-%d'))], limit=1)
                    if hr_paid_holidays:                    
                        paid_days=(datetime.datetime.strptime(hr_paid_holidays.date_to, "%Y-%m-%d")-datetime.datetime.strptime(hr_paid_holidays.date_from, "%Y-%m-%d")).days
                        paid_days+=1
                        paid_hours_leaves=hr_paid_holidays.number_of_hours_temp/paid_days
                     
                    hr_unpaid_holidays=self.env['hr.holidays'].sudo().search([('employee_id', '=', week_hour.employee_id.id),('holiday_status_id.paid_leave', '=', False),('date_from', '<=', (date_from + datetime.timedelta(days=(i-1))).strftime('%Y-%m-%d')),('date_to', '>=', (date_from + datetime.timedelta(days=(i-1))).strftime('%Y-%m-%d'))], limit=1)
                    if hr_unpaid_holidays:                    
                        paid_days=(datetime.datetime.strptime(hr_unpaid_holidays.date_to, "%Y-%m-%d")-datetime.datetime.strptime(hr_unpaid_holidays.date_from, "%Y-%m-%d")).days
                        paid_days+=1
                        unpaid_hours_leaves=hr_unpaid_holidays.number_of_hours_temp/paid_days
                     
                    work_details['paid_leaves']="{:.2f}".format(paid_hours_leaves)
                    work_details['unpaid_leaves']="{:.2f}".format(unpaid_hours_leaves)

                    job_name['work_hours'].append(work_details)                            
                    job_name['tot_hours'] = week_hour.hours_total
                    job_name['ot_hours'] =  week_hour.ot_total
                emp_hrs.append(job_name)
        result['emp_hrs'] = emp_hrs
        result['state'] = planning_hours.planning_id.state
        return result

class AddEmployee(models.TransientModel):
    _name = 'add.employee'

    @api.model
    def default_get(self, fields_name):
        res = super(AddEmployee, self).default_get(fields_name)
        if self._context.get('staff_plan_id'):
            job_obj = self.env['staff.planning.display'].sudo().search([('id','=',self._context.get('staff_plan_id'))])
            res.update({'staff_plan_id': self._context.get('staff_plan_id'), 'job_id':job_obj.name.id})
           
        return res

    job_id = fields.Many2one('hr.job', 'Job Position')
    employee_id = fields.Many2one('hr.employee', 'Employee')
    staff_plan_id = fields.Many2one('staff.planning.display', 'Staff Planning')
    contract_id = fields.Many2one('hr.contract', 'Contract')

    @api.onchange('job_id')
    def onchange_job_field(self): 
        res = {'domain': {'employee_id': "[('id', '!=', False)]",}}
        if self.staff_plan_id:
            employee_list = []
            jrl_ids = []
            for employee in self.staff_plan_id.week_hours:
                employee_list.append(employee.employee_id.id)

            contract_obj = self.env['hr.contract'].sudo().search([('employee_id','not in',employee_list),('state','in',['open','pending'])])
            for contract in contract_obj:
                for job in contract.contract_job_ids:
                    if self.job_id.id == job.job_id.id:
                        jrl_ids.append(contract.employee_id.id)
            res['domain']['employee_id'] = "[('id', 'in', %s)]" % jrl_ids
       
        return res

    @api.multi
    def add_employee(self):
        contract_obj = self.env['hr.contract'].sudo().search([('employee_id','=', self.employee_id.id),('state','in',['open','pending'])], limit=1)
        print contract_obj
        if contract_obj:
            i=0
            for contract in contract_obj.contract_job_ids:
                if self.job_id.id == contract.job_id.id:
                    self.env['staff.planning.display.week'].create({
                                                                    'display_id': self.staff_plan_id.id,
                                                                    'employee_id': self.employee_id.id,
                                                                    'job_id': self.job_id.id,
                                                                    'from_date': self.staff_plan_id.from_date,
                                                                    'to_date': datetime.datetime.strptime(self.staff_plan_id.from_date, "%Y-%m-%d") + datetime.timedelta(days=6),
                                                                    'week_type': 'week1',
                                                                    'salary_type': contract_obj.salary_computation_method,
                                                                    'hourly_rate': contract.hourly_rate,
                                                                    'wage': contract_obj.wage
                                                                })
                    self.env['staff.planning.display.week'].create({
                                                                    'display_id': self.staff_plan_id.id,
                                                                    'employee_id': self.employee_id.id,
                                                                    'job_id': self.job_id.id,
                                                                    'from_date': datetime.datetime.strptime(self.staff_plan_id.from_date, "%Y-%m-%d") + datetime.timedelta(days=7),
                                                                    'to_date': self.staff_plan_id.to_date,
                                                                    'week_type': 'week2',
                                                                    'salary_type': contract_obj.salary_computation_method,
                                                                    'hourly_rate': contract.hourly_rate,
                                                                    'wage': contract_obj.wage
                                                                }) 
                    i +=1
            
            if i == 0:
                raise UserError(_('Current job is not set for the employee.'))
        else:
            raise UserError(_('Employee contract has been expired or contract has not been created.'))






              
class StaffPlanningHours(models.Model):
    _name = 'staff.planning.hours'

    planning_id = fields.Many2one("staff.planning")
    employee = fields.Many2one("hr.employee", "Employee")
    job_position = fields.Many2one("hr.job", "Job Position")
    date = fields.Date("Date")
    hours = fields.Char("Hours")
    pto_hours = fields.Char("PTO Hours")

class TimesheetEmpList(models.Model):
    _name = 'timesheet.emp.list'
    
    sheet_id=fields.Many2one("staff.planning", "Sheet id", required=True,ondelete='cascade')
    name = fields.Many2one("hr.employee", "Staff")
    period_id=fields.Many2one("hr.period", "Period id",related='sheet_id.name')
    company_id=fields.Many2one("res.company", "Company",related='sheet_id.company_id')
    week = fields.Integer("Week")
    from_date = fields.Date("From Date")
    to_date = fields.Date("To Date")
    job_id = fields.Many2one("hr.job", "Activity")
    hours = fields.Float(compute='_compute_hours', string="Schedule")
    leaves = fields.Float(compute='_compute_hours', string="Leaves")
    attendance = fields.Float(compute='_compute_hours', string="Attendance")
    work_hours = fields.Float(compute='_compute_hours', string="Work Hours")
    difference = fields.Float(compute='_compute_hours', string="Difference")
    status = fields.Selection([
        ('draft', 'Draft'),
        ('approval', 'Waiting for Approval'),
        ('validated', 'Validated'),
        ], string='Status', related='sheet_id.state')

    def _compute_hours(self):
        for record in self:
            
            
            from_date = datetime.datetime.strptime(record.from_date, "%Y-%m-%d")
            to_date = datetime.datetime.strptime(record.to_date, "%Y-%m-%d")
#             while (to_date >= from_date):  
#                 
#                 from_date = from_date + datetime.timedelta(days=1)
            staff_hrs = self.env['staff.planning.hours'].search([('employee', '=', record.name.id),('job_position', '=', record.job_id.id), ('date', '>=', from_date), ('date', '<=', to_date)])
            tot_hours="00:00"
            for hours in staff_hrs:
                tot_hours=self.env['staff.planning'].add_time(hours.hours,tot_hours)
            list = [x.strip() for x in tot_hours.split(':')]
            hours=int(list[0])
            mins=int(list[1])*100*0.01/60
            
            work_hrs = self.env['hr.work.hours'].search([('employee_id', '=', record.name.id),('job_id', '=', record.job_id.id), ('date', '>=', from_date), ('date', '<=', to_date)])
            tot_work_hours=0
            for work_hr in work_hrs:
                tot_work_hours+=work_hr.work_hours
            
            
            from_date = datetime.datetime.strptime(record.from_date+" 00:00:00", "%Y-%m-%d %H:%M:%S")
            to_date = datetime.datetime.strptime(record.to_date+" 23:59:59", "%Y-%m-%d %H:%M:%S")
            
            hr_attendances = self.env['hr.attendance'].search([('employee_id', '=', record.name.id),('activity_id.job_id', '=', record.job_id.id), ('check_in', '>=', record.from_date+" 00:00:00" ), ('check_out', '<=', record.to_date+" 23:59:59")])
            tot_attendance="00:00"
            for hr_attendance in hr_attendances:
                tot_attendance=self.env['staff.planning'].add_time(hr_attendance.time_difference,tot_attendance)
                
            list = [x.strip() for x in tot_attendance.split(':')]
            att_hours=int(list[0])
            att_mins=int(list[1])*100*0.01/60
                
#             staff.planning.hours
            
            
            record.hours=hours+mins
            record.leaves=0
            record.attendance=att_hours+att_mins
            record.work_hours=tot_work_hours
            record.difference=0

class TimesheetConfig(models.Model):
    _name = 'timesheet.config'
    _rec_name = 'company_id'

    company_id = fields.Many2one("res.company", "Company", required=True)
    hr_job_ids = fields.One2many("timesheet.job.seq", "job_list", string="Job List")

    _sql_constraints = [('company_id_uniq', 'unique (company_id)', 'Company must be unique!')]
    

class TimesheetJobSeq(models.Model):
    _name = 'timesheet.job.seq'

    name = fields.Many2one("hr.job", "Job Positions")
    sequence = fields.Integer("Sequence")
    job_list = fields.Many2one("timesheet.config", "Job List")
    public_holidays = fields.Float('Public Holidays (%)')
    salary_applicable = fields.Boolean('Allocate Salary', default=True)
    daily_rate = fields.Boolean('Daily Rate', default=True)

    _order='sequence'