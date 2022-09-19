# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from __future__ import division

from odoo import api, fields, models, tools, _
import datetime
import re
from odoo.exceptions import ValidationError, UserError


class VitalpetPayrollInputsTimesheets(models.Model):
    _name = 'vitalpet.payroll.inputs.timesheets'

    @api.model
    def update_work_hours(self,context=None):

        if context:
            if context.get('attendance_date') and context.get('attendance_value') and context.get('attendance_emp_id') and context.get('attendance_job_id'):
                rec=[('employee_id', '=', int(context.get('attendance_emp_id'))),
                                                             ('job_id', '=', int(context.get('attendance_job_id'))),
                                                             ('date', '=', context.get('attendance_date'))]

                attendance=self.env['hr.work.hours'].search(rec)
                hours=context.get('attendance_value')
                pattern = '^(?:([01]?\d|2[0-3]):)?([0-5]?\d)$'
                match = re.search(pattern, hours)
                if match:
                    print "matched"
                else:
                    raise ValidationError(_('Input value should be HH:MM.'))
#                 list = [x.strip() for x in hours.split(':')]
#                 if len(list) == 1:
#                     if (int(list[0])*100/60).is_integer():
#                         float_hours="00."+str(int(int(list[0])*100/60))
#                     else:
#                         float_hours="00."+str(int(int(list[0])*100/60)+1)
#                 else:
#                     if (int(list[0])*100/60).is_integer():
#                         float_hours=list[0]+"."+str(int(int(list[1])*100/60))
#                     else:
#                         float_hours=list[0]+"."+str(int(int(list[1])*100/60)+1)
                float_hours=self.time_to_float(hours)
                if attendance:
                    if float_hours>0:
                        attendance.work_hours=float(float_hours)
                        return "changed"
                else:
                    if float(float_hours)>0:
#                         self.env['hr.work.hours'].create({'employee_id': context.get('attendance_emp_id'),
#                                                                  'job_id': context.get('attendance_job_id'),
#                                                                  'date': context.get('attendance_date'),
#                                                                  'period_id': context.get('payroll_period'),
#                                                                  'company_id':self.env.user.company_id.id,
#                                                                  'status':'non_validate',
#                                                                  'work_hours':float(float_hours) });

                        return "changed"

    def add_times(self, a, b):
        if not a:
            a = '00:00'
        if not b:
            b = '00:00'
        a1, a2 = a.split(":")
        b1, b2 = b.split(":")
        x = int(a1) + int(b1)
        y = int(a2) + int(b2)
        if y >= 60:
            x = x + 1
            y = y - 60
        if len(str(x)) == 1:
            x = "0" + str(x)
        if len(str(y)) == 1:
            y = "0" + str(y)
        return str(x) + ":" + str(y)
        
    def time_diff(self, a, b):
        a1, a2 = a.split(":")
        b1, b2 = b.split(":")
        x = int(a1) - int(b1)
        y = int(a2) - int(b2)
        if x<0:
            x=x*-1;
        if y<0:
            x=x*-1;
        if y >= 60:
            x = x + 1
            y = y - 60
        if len(str(x)) == 1:
            x = "0" + str(x)
        if len(str(y)) == 1:
            y = "0" + str(y)
        return str(x) + ":" + str(y)
    
    def time_to_float(self, a):
        a1, a2 = a.split(":")
        x = float(a1)
        y = (float(a2)*100/60)/100
        return x+y
    
    
    
    def float_to_time(self, a):
        result = '{0:02.0f}:{1:02.0f}'.format(*divmod(a * 60, 60))
        return result
#         print a
#         a1, a2 = str(a).split(".")
#         hrs=int(a1)
#         mins=0
#         if int(a2)>0:
#             if (int(a2)*60/100).is_integer():
#                 mins=int(a2)*60/100        
#             else:
#                 mins=int(a2)*60/100+1
#         print hrs,"hours"
#         print mins,"minutes"
#             
#         if len(str(hrs)) == 1:
#             hrs = "0" + str(hrs)
#         if len(str(mins)) == 1:
#             mins = str(mins)+"0"
#         if len(str(mins)) > 2:
#             mins = str(mins)[0]+str(mins)[1]
#         print str(hrs)+":"+str(mins)    
#         return str(hrs)+":"+str(mins)

    
    def diff_times(self, a, b):
        a1=self.time_to_float(a)
        b1=self.time_to_float(b)
        difference=a1-b1
        i=0
        if difference<0:
            i=1
            difference=difference*(-1)
        return [i,self.float_to_time(difference)]
    
    @api.model
    def fetch_timesheet_data(self,context=None):
        period_id = False
        week_type = 'two_weeks';
        filter_timesheet = 'my_timesheet'
        filter_module = 'all'
        total_employee = 1
        current_employee = False
        employee_name = 'My Timesheet'
        employee_number = 1
        week_no = 1
        if context:   
            if context.get('period_id'):
                period_id = context.get('period_id')
            if context.get('week_type'):
                week_type = context.get('week_type')
            if context.get('week_no'):
                week_no = context.get('week_no')
            if context.get('filter_timesheet'):
                filter_timesheet = context.get('filter_timesheet')
            if context.get('current_employee'):
                current_employee = context.get('current_employee')
                hr_employee = self.env['hr.employee'].search([('id', '=', int(current_employee))])
                employee_name = hr_employee.name
            if context.get('employee_number') and filter_timesheet == 'team_member':
                employee_number = context.get('employee_number')
            if context.get('week_no'):
                week_no = context.get('week_no')
            if context.get('filter_module'):
                filter_module = context.get('filter_module')
        
            
        today_date = datetime.datetime.today().date()
        result = {}
        dates = []
        periods = []
        values = []
        employee_ids = []
        employees = []
        if filter_timesheet == 'team_member':
            hr_jobs = self.env['hr.contract.job'].search([('job_id.company_id.id','=',self.env.user.company_id.id), ('contract_id.state', '=', 'open')])
            if not current_employee:
                current_employee = hr_jobs[0].contract_id.employee_id.id
                employee_name = hr_jobs[0].contract_id.employee_id.name
            
            for hr_job in hr_jobs:
                employees = []
                new_employee = False
                employee = hr_job.contract_id.employee_id
                if employee.id != new_employee and employee.active == True:
                    employee_values = {}
                    employee_values['id'] = employee.id
                    new_employee = employee.id
                    employee_values['name'] = employee.name
                    employee_ids.append(employee_values)
            total_employee = len(employee_ids)
        hr_periods = self.env['hr.period'].search([('company_id','=',self.env.user.company_id.id),('state','=','open')])
        if period_id:
            select_period = self.env['hr.period'].search([('id','=', period_id)])
        else:
            select_period = self.env['hr.period'].search([('company_id','=',self.env.user.company_id.id), ('date_start','<=', today_date), ('date_stop','>=', today_date)])
        if not select_period:
            raise ValidationError(_('Payroll Periods not configured for current company.'))
        for period in hr_periods:
            values = {}
            values['id'] = period.id
            values['name'] = period.name
            values['state'] = period.state
            periods.append(values)
            
            
        result['payroll_periods'] =   periods      
        result['current_period'] =   select_period.id
        result['current_period_state'] =   select_period.state
        
        if week_type == 'week':
            if week_no == 1:
                from_date =  datetime.datetime.strptime(select_period.date_start, "%Y-%m-%d")
                to_date =  datetime.datetime.strptime(select_period.date_start, "%Y-%m-%d")
                to_date = to_date+datetime.timedelta(days=6)
            else:
                from_date =  datetime.datetime.strptime(select_period.date_start, "%Y-%m-%d")
                to_date =  datetime.datetime.strptime(select_period.date_start, "%Y-%m-%d")
                from_date = from_date+datetime.timedelta(days=7)
                to_date = to_date+datetime.timedelta(days=13)
                
        else:
            from_date =  datetime.datetime.strptime(select_period.date_start, "%Y-%m-%d")
            to_date =  datetime.datetime.strptime(select_period.date_stop, "%Y-%m-%d")
        
        
        #From date will change in every loop, so used date_from variable to stare from date
        date_from = from_date
        #TO date will change in every loop, so used date_from variable to stare to date
        date_to = to_date        
        jobs = []       
        schedules = []
#-------------------------------------Start Leave values---------------------------------------------------------------------
#-------------------------------------Start Leave values by type-------------------------------------------------------------
        leaves = []
        total_leaves = []
        holiday_statuses = self.env['hr.holidays.status'].search([])
        if filter_timesheet == 'all_timesheet':
            hr_contract_jobs = self.env['hr.contract.job'].search([('job_id.company_id.id','=',self.env.user.company_id.id), ('contract_id.state', '=', 'open')])
            employees = []
            new_employee = False
            for hr_contract_job in hr_contract_jobs:
                employee = hr_contract_job.contract_id.employee_id
                if employee.id != new_employee:
                    employee_values = {}
                    employee_values['id'] = employee.id
                    employee_values['name'] = employee.name
                    employees.append(employee_values)
        if filter_timesheet == 'my_timesheet':
            hr_contract_jobs = self.env['hr.contract.job'].search([('contract_id.employee_id.user_id','=',self.env.user.id), ('contract_id.state', '=', 'open')])
            employees = []
            new_employee = False
            for hr_contract_job in hr_contract_jobs:
                employee = hr_contract_job.contract_id.employee_id
                if employee.id != new_employee:
                    employee_values = {}
                    employee_values['id'] = employee.id
                    new_employee = employee.id
                    employee_values['name'] = employee.name
                    employees.append(employee_values)
        if filter_timesheet == 'team_member':
            employees = []
            new_employee = False
            hr_contract_jobs = self.env['hr.contract.job'].search([('contract_id.employee_id.company_id.id','=',self.env.user.company_id.id),('contract_id.employee_id.id','=',int(current_employee))])
            for hr_contract_job in hr_contract_jobs:
                employee = hr_contract_job.contract_id.employee_id
                if employee.id != new_employee:
                    employee_values = {}
                    new_employee = employee.id
                    employee_values['id'] = employee.id
                    employee_values['name'] = employee.name
                    employees.append(employee_values)
        for employee in employees:
            for holiday_status in holiday_statuses:
                holidays = self.env['hr.holidays'].search([('holiday_status_id', '=', holiday_status.id),
                                                           ('state', '=', 'validate'),
                                                           ('employee_id', '=', employee['id']),
                                                           ('company_id', '=', self.env.user.company_id.id),
                                                            ('date_to', '<=', date_to),
                                                           ('date_from', '>=', date_from)])
                if holidays:
                    values = {}
                    values['leave_type_name'] = employee['name']+'/'+holiday_status.name
                    leave_type_values = []
                    from_date = date_from
                    to_date = date_to
                    total_value = 0.0
                    
                    while(to_date >= from_date):
                        time_value = 0.0
                        hr_holidays = self.env['hr.holidays'].search([('holiday_status_id', '=', holiday_status.id),
                                                                   ('state', '=', 'validate'),
                                                                   ('employee_id', '=', employee['id']),
                                                                   ('company_id', '=', self.env.user.company_id.id),
                                                                    ('date_to', '>=', from_date),
                                                                   ('date_from', '<=', from_date)])
                        if hr_holidays and hr_holidays.leave_days > 0:
                            if hr_holidays.leave_days == 1:
                                time_value = hr_holidays.number_of_hours_temp
                                total_value+=time_value
                            else:
                                time_value =hr_holidays.number_of_hours_temp / hr_holidays.leave_days
                                total_value+=time_value
                            
                           
                        leave_type_values.append(str(datetime.timedelta(hours=time_value)).rsplit(':', 1)[0])
                        from_date = from_date+datetime.timedelta(days=1)
                    values['leave_type_total'] = self.float_time(total_value)    
                    values['leave_type_values'] = leave_type_values
                    leaves.append(values)
        result['leaves'] = leaves
        
        
        
#-------------------------------------End Leave values by type-------------------------------------------------------------

#-------------------------------------Start T0tal Leave values-------------------------------------------------------------
        total_values = {}
        total_leave_values = []
        total_value = 0.0
        from_date = date_from
        to_date = date_to
        while(to_date >= from_date):
            if filter_timesheet == 'all_timesheet':
                hr_holidays = self.env['hr.holidays'].search([('state', '=', 'validate'),
                                                           ('company_id.id', '=', self.env.user.company_id.id),
                                                            ('date_to', '>=', from_date),
                                                           ('date_from', '<=', from_date)])
            if filter_timesheet == 'my_timesheet':
                hr_holidays = self.env['hr.holidays'].search([('state', '=', 'validate'),
                                                           ('employee_id.user_id.id', '=', self.env.user.id),
                                                           ('company_id.id', '=', self.env.user.company_id.id),
                                                            ('date_to', '>=', from_date),
                                                           ('date_from', '<=', from_date)])
            if filter_timesheet == 'team_member':
                hr_holidays = self.env['hr.holidays'].search([('state', '=', 'validate'),
                                                           ('employee_id', '=', int(current_employee)),
                                                           ('company_id.id', '=', self.env.user.company_id.id),
                                                            ('date_to', '>=', from_date),
                                                           ('date_from', '<=', from_date)])
            
            
            time_value = 0.0
            for hr_holiday in hr_holidays:
                if hr_holiday and hr_holiday.leave_days > 0:
                    if hr_holiday.leave_days == 1:
                        time_value = time_value+hr_holiday.number_of_hours_temp
                        
                        total_value+=hr_holiday.number_of_hours_temp
                    else:
                        time_value =time_value+(hr_holiday.number_of_hours_temp / hr_holiday.leave_days)
                        total_value+=hr_holiday.number_of_hours_temp / hr_holiday.leave_days 
            total_leave_values.append(str(datetime.timedelta(hours=time_value)).rsplit(':', 1)[0])
            from_date = from_date+datetime.timedelta(days=1)
        total_values['total_leave_total'] = self.float_time(total_value)   
        total_values['total_leave_values'] = total_leave_values
        total_leaves.append(total_values)                
        result['total_leaves'] = total_leaves
        
        
        
#-------------------------------------End Total Leave values-------------------------------------------------------------
#-------------------------------------End Leave values------------------------------------------------------------------------


#-------------------------------------Attendance-------------------------------------------------------------
#-------------------------------------Start Attendance values------------------------------------------------------------------------
#                 remove_work_hours = self.env['hr.work.hours'].search([('work_hours', '=', '0'), ('employee_id', '=', employee.id)])
#                 remove_work_hours.unlink()
        result['schedules']={}
        result['schedules_tot']={}
        result['schedules_tot_all']={}
        if filter_timesheet == 'all_timesheet':
            jobs_total = []
            employees = []
            new_employee = False
            hr_contract_jobs = self.env['hr.contract.job'].search([('job_id.company_id.id','=',self.env.user.company_id.id), ('contract_id.state', '=', 'open')])
            for hr_contract_job in hr_contract_jobs:
                employee = hr_contract_job.contract_id.employee_id
                if employee.id != new_employee:
                    employee_values = {}
                    employee_values['id'] = employee.id
                    new_employee = employee.id
                    employee_values['name'] = employee.name
                    employees.append(employee_values)
            hr_jobs = self.env['hr.job'].search([('company_id','=',self.env.user.company_id.id)])

            date1 = date_from + datetime.timedelta(hours=00, minutes=00, seconds=00)
            date2 = date_to + datetime.timedelta(hours=23, minutes=59, seconds=59)
            
            for employee in employees:
                for hr_job in hr_jobs:
                    values = {}
                    attendance = self.env['hr.attendance'].search_count([
                        ('check_in','>=',str(date1)),('check_out','<=',str(date2)),
                        ('activity_id.job_id', '=', hr_job.id),('activity_id.job_id.company_id', '=', self.env.user.company_id.id),('employee_id', '=', employee['id'])])
                    work_hours = self.env['hr.work.hours'].search_count([
                        ('date', '>=', str(date1)), ('date', '<=', str(date1)),
                        ('job_id', '=', hr_job.id),('job_id.company_id', '=', self.env.user.company_id.id),('employee_id', '=', employee['id'])])
                    if attendance>0:
                    
#                         if work_hours == 0:          
#                             
#                             self.env['hr.work.hours'].create({
#                                 'date':date1,
#                                 'job_id':hr_job.id,
#                                 'employee_id':employee['id'],
#                                 'work_hours':0,
#                                 'name':'/'                           
#                                 })
                        values['job_name'] = employee['name'] + "/" + hr_job.name
                        job_values = []
                        job_work = []
                        job_id = []
                        from_date = date_from
                        to_date = date_to
                        sum_tot = "00:00"
                        work_hours_total="00:00"
                        while (to_date >= from_date):
                            time1 = from_date + datetime.timedelta(hours=00, minutes=00, seconds=00)
                            time2 = from_date + datetime.timedelta(hours=23, minutes=59, seconds=59)
                            timesheets = self.env['hr.attendance'].search(
                                [('check_in', '>=', str(time1)), ('check_out', '<=', str(time2)),
                                 ('activity_id.job_id', '=', hr_job.id),('activity_id.job_id.company_id', '=', self.env.user.company_id.id),('employee_id', '=', employee['id'])])
                            diff = "00:00"
                            sum = "00:00"
                            id = 0
                            work_hours = "00:00"
                            for timesheet in timesheets:
                                id = timesheet.id
                                diff = str(timesheet.time_difference)
                                sum = self.add_times(sum, diff)
                                sum_tot = self.add_times(sum_tot, diff)
                                work_hours = self.add_times(work_hours, timesheet.time_difference)
                                work_hours_total = self.add_times(work_hours_total, timesheet.time_difference)
                            job_id.append(id)
                            job_values.append(sum)
                            job_work.append(work_hours)
                            from_date = from_date + datetime.timedelta(days=1)
#                         job_values.append(sum_tot)
                        job_work.append(work_hours_total)
                        values['job_ids'] = job_id
                        values['job_works'] = job_work
                        values['job_values'] = job_values
                        values['total_job_values'] = sum_tot
                        jobs.append(values)
                        
                                    
            for employee in employees:
                for hr_job in hr_jobs:
                    values = {}
                    job_values = []
                    job_values_float = []
                    job_work = []
                    job_id = []
                    from_date = date_from
                    to_date = date_to
                    sum_tot = "00:00"
                    sch_hours = self.env['staff.planning.display.week'].search(['|',
                        ('from_date', '=', str(from_date)),('to_date', '=', str(to_date)),
                        ('job_id', '=', hr_job.id),
                        ('employee_id', '=', employee['id'])])
                    if len(sch_hours) > 0:
                        for sch_hour in sch_hours:
                            sum = "00:00"
                            if sch_hour.day1:
                                day1_value = sch_hour.day1
                                sum_tot = self.add_times(sum_tot,day1_value)
                                sum = self.add_times(sum,day1_value)
                            else:
                                day1_value = "00.00"
                            job_values.append(day1_value)
                            job_post={}
                            job_post[str(from_date)]=float(self.time_to_float(sum))
                            job_values_float.append(job_post)
                            from_date = from_date + datetime.timedelta(days=1)
                            sum = "00:00"
                            if sch_hour.day2:
                                day2_value = sch_hour.day2
                                sum_tot = self.add_times(sum_tot,day2_value)
                                sum = self.add_times(sum,day2_value)
                            else:
                                day2_value = "00.00"
                            job_values.append(day2_value)
                            job_post={}
                            job_post[str(from_date)]=float(self.time_to_float(sum))
                            job_values_float.append(job_post)
                            from_date = from_date + datetime.timedelta(days=1)
                            sum = "00:00"
                            if sch_hour.day3:
                                day3_value = sch_hour.day3
                                sum_tot = self.add_times(sum_tot,day3_value)
                                sum = self.add_times(sum,day3_value)
                            else:
                                day3_value = "00.00"
                            job_values.append(day3_value)
                            job_post={}
                            job_post[str(from_date)]=float(self.time_to_float(sum))
                            job_values_float.append(job_post)
                            from_date = from_date + datetime.timedelta(days=1)
                            sum = "00:00"
                            if sch_hour.day4:
                                day4_value = sch_hour.day4
                                sum_tot = self.add_times(sum_tot,day4_value)
                                sum = self.add_times(sum,day4_value)
                            else:
                                day4_value = "00.00"
                            job_values.append(day4_value)
                            job_post={}
                            job_post[str(from_date)]=float(self.time_to_float(sum))
                            job_values_float.append(job_post)
                            from_date = from_date + datetime.timedelta(days=1)
                            sum = "00:00"
                            if sch_hour.day5:
                                day5_value = sch_hour.day5
                                sum_tot = self.add_times(sum_tot,day5_value)
                                sum = self.add_times(sum,day5_value)
                            else:
                                day5_value = "00.00"
                            job_values.append(day5_value)
                            job_post={}
                            job_post[str(from_date)]=float(self.time_to_float(sum))
                            job_values_float.append(job_post)
                            from_date = from_date + datetime.timedelta(days=1)
                            sum = "00:00"
                            if sch_hour.day6:
                                day6_value = sch_hour.day6
                                sum_tot = self.add_times(sum_tot,day6_value)
                                sum = self.add_times(sum,day6_value)
                            else:
                                day6_value = "00.00"
                            job_values.append(day6_value)
                            job_post={}
                            job_post[str(from_date)]=float(self.time_to_float(sum))
                            job_values_float.append(job_post)
                            from_date = from_date + datetime.timedelta(days=1)
                            sum = "00:00"
                            if sch_hour.day7:
                                day7_value = sch_hour.day7
                                sum_tot = self.add_times(sum_tot,day7_value)
                                sum = self.add_times(sum,day7_value)
                            else:
                                day7_value = "00.00"
                            job_values.append(day7_value)
                            job_post={}
                            job_post[str(from_date)]=float(self.time_to_float(sum))
                            job_values_float.append(job_post)
                            from_date = from_date + datetime.timedelta(days=1)
                                
                                   
                            
                        values['sch_emp'] = employee['name']+"/"+hr_job.name
                        values['sch_works'] = job_work
                        values['sch_values'] = job_values
                        values['sch_values_float'] = job_values_float
                        values['total_sch_values'] = sum_tot
                        schedules.append(values)                    
            result['schedules']=schedules
            from_date = date_from
            to_date = date_to
            overall_tot=0.0
            job_post=[]
            while (to_date >= from_date): 
                tot=0.0
                for schedule in schedules: 
                    for key in schedule['sch_values_float']:  
                        if str(from_date) in key:             
                            tot+= key[str(from_date)]
                            overall_tot+=key[str(from_date)]
                job_post.append(self.float_to_time(tot))
                from_date = from_date + datetime.timedelta(days=1)
            result['schedules_tot']=job_post
            result['schedules_tot_all']=self.float_to_time(overall_tot)
            
            
            
            from_date = date_from
            to_date = date_to
            values = {}
            job_values = []
            job_work=[]
            values['job_name'] = 'Attendance'
            sum_tot = "00:00"
            work_hours_total = "00:00"
            while (to_date >= from_date):
                time1=from_date+datetime.timedelta(hours=00,minutes=00,seconds=00)
                time2=from_date+datetime.timedelta(hours=23,minutes=59,seconds=59)
                timesheets=self.env['hr.attendance'].search([('check_in','>=',str(time1)),('check_out','<=',str(time2)),('activity_id.job_id.company_id.id','=',self.env.user.company_id.id)])
                diff="0:00:00"
                sum = "00:00"
                work_hours = "00:00"
                for timesheet in timesheets:
                    diff=str(timesheet.time_difference)
                    sum = self.add_times(sum,diff)
                    sum_tot= self.add_times(sum_tot,diff)
                    work_hours = self.add_times(work_hours, timesheet.time_difference)
                    work_hours_total = self.add_times(work_hours_total, timesheet.time_difference)
                job_values.append(sum)
                job_work.append(work_hours)
                from_date = from_date + datetime.timedelta(days=1)
            job_values.append(str(sum_tot))
            job_work.append(work_hours_total)
            values['job_values'] = job_values
            values['job_works'] = job_work
            jobs_total.append(values)
            
            from_date = date_from
            to_date = date_to
            
            work_hours = []
            hr_jobs = self.env['hr.job'].search([('company_id', '=', self.env.user.company_id.id)])
            date1 = date_from + datetime.timedelta(hours=00, minutes=00, seconds=00)
            date2 = date_to + datetime.timedelta(hours=23, minutes=59, seconds=59)
            hr_contract_jobs = self.env['hr.contract.job'].search([('job_id.company_id.id','=',self.env.user.company_id.id), ('contract_id.state', '=', 'open')])
            new_employee = False
            employees = []
            for hr_contract_job in hr_contract_jobs:
                employee = hr_contract_job.contract_id.employee_id
                if employee.id != new_employee:
                    employee_values = {}
                    employee_values['id'] = employee.id
                    new_employee = employee.id
                    employee_values['name'] = employee.name
                    employees.append(employee_values)
            for employee in employees:
                for hr_job in hr_jobs:
                    values = {}
                    work_data = False
                    hr_work_hours = self.env['hr.work.hours'].search_count([
                        ('job_id', '=', hr_job.id),('job_id.company_id.id', '=', self.env.user.company_id.id),('employee_id.id', '=', employee['id'])])
                    if hr_work_hours > 0:
                        values['job_name'] = employee['name'] + "/" + hr_job.name
                        values['emp_id'] = employee['id']
                        values['job_id'] = hr_job.id
                        work_values = []
                        work_values_details = []
    #                     work_work = []
    #                     work_id = []
                        from_date = date_from
                        to_date = date_to
                        sum_tot = "00:00"
                        work_hours_total="00:00"
                        while (to_date >= from_date):
                            time1 = from_date + datetime.timedelta(hours=00, minutes=00, seconds=00)
                            time2 = from_date + datetime.timedelta(hours=23, minutes=59, seconds=59)
                            timesheets = self.env['hr.work.hours'].search(
                                [('date', '>=', str(time1)), ('date', '<=', str(time2)),
                                 ('job_id', '=', hr_job.id),('job_id.company_id.id', '=', self.env.user.company_id.id), ('employee_id.id', '=', employee['id'])])
                            diff = "00:00"
                            sum = "00:00"
                            id = 0
                            work_hour = 0.0
                            for timesheet in timesheets:
                                work_data = True
                                id = timesheet.id
                                work_hour+=timesheet.work_hours
                            work_hour = self.float_to_time(work_hour)
                            work_values.append(work_hour)
                            work_values_detail={}
                            work_values_detail[str(from_date)]=float(self.time_to_float(work_hour))
                            work_values_details.append(work_values_detail)
                            sum_tot = self.add_times(sum_tot, work_hour)
                            from_date = from_date + datetime.timedelta(days=1)
                        values['work_values'] = work_values
                        values['work_values_details'] = work_values_details
                        values['total_work_values'] = sum_tot
                        if work_data:
                            work_hours.append(values)
            
            result['work_hours'] = work_hours
            
            
            from_date = date_from
            to_date = date_to
            overall_tot=0.0
            job_post=[]
            while (to_date >= from_date): 
                tot=0.0
                for work_hour in work_hours: 
                    for key in work_hour['work_values_details']:  
                            if str(from_date) in key:             
                                tot+= key[str(from_date)]
                                overall_tot+=key[str(from_date)]
                job_post.append(self.float_to_time(tot))
                from_date = from_date + datetime.timedelta(days=1)
            result['total_work_hours']=job_post
            result['total_work_hours_all']=self.float_to_time(overall_tot)
            
                           
            sch_diff=[]
            for x in range(0, len(result['schedules_tot'])):
                values = {}
                diff_hours=self.diff_times(result['schedules_tot'][x],result['total_work_hours'][x])
                values['diff_hours'] = diff_hours[1]
                values['diff_type'] = diff_hours[0]
                sch_diff.append(values)
            result['total_work_hours_diff']=sch_diff
            result['tot_diff_hours']=self.diff_times(result['schedules_tot_all'],result['total_work_hours_all'])[1]
                                
                                
            date1 = date_from + datetime.timedelta(hours=00, minutes=00, seconds=00)
            date2 = date_to + datetime.timedelta(hours=23, minutes=59, seconds=59)
            values = {}
            hr_work_hours = self.env['hr.work.hours'].search_count([
                ('date', '>=', str(date1)), ('date', '<=', str(date1)),
                ('employee_id', '=', employee['id']), ('job_id.company_id.id', '=', self.env.user.company_id.id)])
                       
            total_work_values = [] 
            from_date = date_from
            to_date = date_to
            sum_tot = "00:00"
            work_hours_total="00:00"
            while (to_date >= from_date):
                time1 = from_date + datetime.timedelta(hours=00, minutes=00, seconds=00)
                time2 = from_date + datetime.timedelta(hours=23, minutes=59, seconds=59)
                timesheets = self.env['hr.work.hours'].search(
                    [('date', '>=', str(time1)), ('date', '<=', str(time2)),
                    ('employee_id.id', '=',  employee['id']), ('job_id.company_id.id', '=', self.env.user.company_id.id)])
                sum = "00:00"
                work_hour = 0.0
                for timesheet in timesheets:
                    work_hour+=timesheet.work_hours
                work_hour = self.float_to_time(work_hour)
                sum = self.add_times(sum, work_hour)
                sum_tot = self.add_times(sum_tot, work_hour)
                
                from_date = from_date + datetime.timedelta(days=1)
                total_work_values.append(sum)
                
            total_work_values.append(sum_tot)
            
#             result['total_work_hours'] = total_work_values
            
            while (date_to >= date_from):
                date_new_antr={}
                date_new_antr['d1']=date_from.strftime('%a <br />%b %d')
                date_new_antr['d2']=date_from.strftime('%Y-%m-%d')
                dates.append(date_new_antr)
                date_from = date_from + datetime.timedelta(days=1)
    
            sch_work_total = []
            values = {}
            job_work_n=[]
            n=0
            for x in total_work_values:
                job_work_n.append(self.time_diff(total_work_values[n], job_values[n]))
                n+=1
            values['job_work_diff'] = job_work_n
            sch_work_total.append(values)
        
        
        else:
            jobs_total = []
            hr_jobs = self.env['hr.job'].search([('company_id','=', self.env.user.company_id.id)])
            date1 = date_from + datetime.timedelta(hours=00, minutes=00, seconds=00)
            date2 = date_to + datetime.timedelta(hours=23, minutes=59, seconds=59)
            
            if filter_timesheet == 'my_timesheet':
                employees = []
                hr_contract_jobs = self.env['hr.contract.job'].search([('contract_id.employee_id.user_id','=',self.env.user.id), ('contract_id.state', '=', 'open')])
                new_employee = False
                for hr_contract_job in hr_contract_jobs:
                    employee = hr_contract_job.contract_id.employee_id
                    if employee.id != new_employee:
                        employee_values = {}
                        employee_values['id'] = employee.id
                        new_employee = employee.id
                        employee_values['name'] = employee.name
                        employees.append(employee_values)
            if filter_timesheet == 'team_member':
                hr_contract_jobs = self.env['hr.contract.job'].search([('contract_id.employee_id.id','=',int(current_employee)), ('contract_id.state', '=', 'open')])
                employees = []
                new_employee = False
                for hr_contract_job in hr_contract_jobs:
                    employee = hr_contract_job.contract_id.employee_id
                    if employee.id != new_employee:
                        employee_values = {}
                        employee_values['id'] = employee.id
                        new_employee = employee.id
                        employee_values['name'] = employee.name
                        employees.append(employee_values)
            for employee in employees:
                for hr_job in hr_jobs:
                    values = {}
                    attendance = self.env['hr.attendance'].search_count([
                        ('check_in','>=',str(date1)),('check_out','<=',str(date2)),
                        ('activity_id.job_id', '=', hr_job.id),('activity_id.job_id.company_id.id', '=', self.env.user.company_id.id),('employee_id.id', '=', employee['id'])])
                    work_hours = self.env['hr.work.hours'].search_count([
                        ('date', '>=', str(date1)), ('date', '<=', str(date1)),
                        ('job_id', '=', hr_job.id),('job_id.company_id.id', '=', self.env.user.company_id.id),('employee_id.id', '=', employee['id'])])
                    if attendance>0:
                    
#                         if work_hours == 0:          
#                             
#                             self.env['hr.work.hours'].create({
#                                 'date':date1,
#                                 'job_id':hr_job.id,
#                                 'employee_id':employee['id'],
#                                 'work_hours':0,
#                                 'name':'/'
#                                                         
#                                 })
                        values['job_name'] = employee['name'] + "/" + hr_job.name
                        job_values = []
                        job_work = []
                        job_id = []
                        from_date = date_from
                        to_date = date_to
                        sum_tot = "00:00"
                        work_hours_total="00:00"
                        while (to_date >= from_date):
                            time1 = from_date + datetime.timedelta(hours=00, minutes=00, seconds=00)
                            time2 = from_date + datetime.timedelta(hours=23, minutes=59, seconds=59)
                            timesheets = self.env['hr.attendance'].search(
                                [('check_in', '>=', str(time1)), ('check_out', '<=', str(time2)),
                                 ('activity_id.job_id', '=', hr_job.id),('activity_id.job_id.company_id.id', '=', self.env.user.company_id.id),('employee_id.id', '=', employee['id'])])
                            diff = "00:00"
                            sum = "00:00"
                            id = 0
                            work_hours = "00:00"
                            for timesheet in timesheets:
                                id = timesheet.id
                                diff = str(timesheet.time_difference)
                                sum = self.add_times(sum, diff)
                                sum_tot = self.add_times(sum_tot, diff)
                                work_hours = self.add_times(work_hours, timesheet.time_difference)
                                work_hours_total = self.add_times(work_hours_total, timesheet.time_difference)
                            job_id.append(id)
                            job_values.append(sum)
                            job_work.append(work_hours)
                            from_date = from_date + datetime.timedelta(days=1)
#                         job_values.append(sum_tot)
                        job_id.append(0)
                        job_work.append(work_hours_total)
                        values['total_job_values'] = sum_tot
                        values['job_ids'] = job_id
                        values['job_works'] = job_work
                        values['job_values'] = job_values
                        jobs.append(values)

            
            
                               
            for employee in employees:
                for hr_job in hr_jobs:
                    values = {}
                    job_values = []
                    job_values_float = []
                    job_work = []
                    job_id = []
                    from_date = date_from
                    to_date = date_to
                    sum_tot = "00:00"                       
                    sch_hours = self.env['staff.planning.display.week'].search(['|',
                        ('from_date', '=', str(from_date)),('to_date', '=', str(to_date)),
                        ('job_id', '=', hr_job.id),
                        ('employee_id', '=', employee['id'])])
                    if len(sch_hours) > 0:
                        for sch_hour in sch_hours:
                            sum = "00:00"
                            if sch_hour.day1:
                                day1_value = sch_hour.day1
                                sum_tot = self.add_times(sum_tot,day1_value)
                                sum = self.add_times(sum,day1_value)
                            else:
                                day1_value = "00.00"
                            job_values.append(day1_value)
                            job_post={}
                            job_post[str(from_date)]=float(self.time_to_float(sum))
                            job_values_float.append(job_post)
                            from_date = from_date + datetime.timedelta(days=1)
                            sum = "00:00"
                            if sch_hour.day2:
                                day2_value = sch_hour.day2
                                sum_tot = self.add_times(sum_tot,day2_value)
                                sum = self.add_times(sum,day2_value)
                            else:
                                day2_value = "00.00"
                            job_values.append(day2_value)
                            job_post={}
                            job_post[str(from_date)]=float(self.time_to_float(sum))
                            job_values_float.append(job_post)
                            from_date = from_date + datetime.timedelta(days=1)
                            sum = "00:00"
                            if sch_hour.day3:
                                day3_value = sch_hour.day3
                                sum_tot = self.add_times(sum_tot,day3_value)
                                sum = self.add_times(sum,day3_value)
                            else:
                                day3_value = "00.00"
                            job_values.append(day3_value)
                            job_post={}
                            job_post[str(from_date)]=float(self.time_to_float(sum))
                            job_values_float.append(job_post)
                            from_date = from_date + datetime.timedelta(days=1)
                            sum = "00:00"
                            if sch_hour.day4:
                                day4_value = sch_hour.day4
                                sum_tot = self.add_times(sum_tot,day4_value)
                                sum = self.add_times(sum,day4_value)
                            else:
                                day4_value = "00.00"
                            job_values.append(day4_value)
                            job_post={}
                            job_post[str(from_date)]=float(self.time_to_float(sum))
                            job_values_float.append(job_post)
                            from_date = from_date + datetime.timedelta(days=1)
                            sum = "00:00"
                            if sch_hour.day5:
                                day5_value = sch_hour.day5
                                sum_tot = self.add_times(sum_tot,day5_value)
                                sum = self.add_times(sum,day5_value)
                            else:
                                day5_value = "00.00"
                            job_values.append(day5_value)
                            job_post={}
                            job_post[str(from_date)]=float(self.time_to_float(sum))
                            job_values_float.append(job_post)
                            from_date = from_date + datetime.timedelta(days=1)
                            sum = "00:00"
                            if sch_hour.day6:
                                day6_value = sch_hour.day6
                                sum_tot = self.add_times(sum_tot,day6_value)
                                sum = self.add_times(sum,day6_value)
                            else:
                                day6_value = "00.00"
                            job_values.append(day6_value)
                            job_post={}
                            job_post[str(from_date)]=float(self.time_to_float(sum))
                            job_values_float.append(job_post)
                            from_date = from_date + datetime.timedelta(days=1)
                            sum = "00:00"
                            if sch_hour.day7:
                                day7_value = sch_hour.day7
                                sum_tot = self.add_times(sum_tot,day7_value)
                                sum = self.add_times(sum,day7_value)
                            else:
                                day7_value = "00.00"
                            job_values.append(day7_value)
                            job_post={}
                            job_post[str(from_date)]=float(self.time_to_float(sum))
                            job_values_float.append(job_post)
                            from_date = from_date + datetime.timedelta(days=1)
                        values['sch_emp'] = employee['name']+"/"+hr_job.name
                        values['sch_works'] = job_work
                        values['sch_values'] = job_values
                        values['sch_values_float'] = job_values_float
                        values['total_sch_values'] = sum_tot
                        schedules.append(values)                    
            result['schedules']=schedules
              
            from_date = date_from
            to_date = date_to
            overall_tot=0.0
            job_post=[]
            while (to_date >= from_date): 
                tot=0.0
                for schedule in schedules: 
                    for key in schedule['sch_values_float']:  
                        if str(from_date) in key:             
                            tot+= key[str(from_date)]
                            overall_tot+=key[str(from_date)]
                job_post.append(self.float_to_time(tot))
                from_date = from_date + datetime.timedelta(days=1)
            result['schedules_tot']=job_post
            result['schedules_tot_all']=self.float_to_time(overall_tot)
            
            
            from_date = date_from
            to_date = date_to

            values = {}
            job_values = []
            job_work=[]
            values['job_name'] = 'Attendance'
            sum_tot = "00:00"
            work_hours_total = "00:00"
            while (to_date >= from_date):
                time1=from_date+datetime.timedelta(hours=00,minutes=00,seconds=00)
                time2=from_date+datetime.timedelta(hours=23,minutes=59,seconds=59)
                if filter_timesheet == 'my_timesheet':
                    timesheets=self.env['hr.attendance'].search([('check_in','>=',str(time1)),('check_out','<=',str(time2)),('activity_id.job_id.company_id.id', '=', self.env.user.company_id.id), ('employee_id.user_id.id', '=', self.env.user.id)])
                if filter_timesheet == 'team_member':
                    timesheets = self.env['hr.attendance'].search(
                        [('check_in', '>=', str(time1)), ('check_out', '<=', str(time2)),
                         ('activity_id.job_id.company_id.id', '=', self.env.user.company_id.id),
                         ('employee_id.id', '=', int(current_employee))])
    
                diff="0:00:00"
                sum = "00:00"
                work_hours = "00:00"
                for timesheet in timesheets:
                    diff=str(timesheet.time_difference)
                    sum = self.add_times(sum,diff)
                    sum_tot= self.add_times(sum_tot,diff)
                    work_hours = self.add_times(work_hours, timesheet.time_difference)
                    work_hours_total = self.add_times(work_hours_total, timesheet.time_difference)
                job_values.append(sum)
                job_work.append(work_hours)
                from_date = from_date + datetime.timedelta(days=1)
            job_values.append(str(sum_tot))
            job_work.append(work_hours_total)
            values['job_values'] = job_values
            values['job_works'] = job_work
            jobs_total.append(values)
            
            from_date = date_from
            to_date = date_to
            
            work_hours = []
            hr_jobs = self.env['hr.job'].search([])
            date1 = date_from + datetime.timedelta(hours=00, minutes=00, seconds=00)
            date2 = date_to + datetime.timedelta(hours=23, minutes=59, seconds=59)
            if filter_timesheet == 'my_timesheet':
                hr_contract_jobs = self.env['hr.contract.job'].search([('contract_id.employee_id.user_id.id','=',self.env.user.id), ('contract_id.state', '=', 'open')])
                employees = []
                new_employee = False
                for hr_contract_job in hr_contract_jobs:
                    employee = hr_contract_job.contract_id.employee_id
                    if employee.id != new_employee:
                        employee_values = {}
                        employee_values['id'] = employee.id
                        new_employee = employee.id
                        employee_values['name'] = employee.name
                        employees.append(employee_values)
            if filter_timesheet == 'team_member':
                hr_contract_jobs = self.env['hr.contract.job'].search([('job_id.company_id.id','=',self.env.user.company_id.id),('contract_id.employee_id.id', '=', int(current_employee)), ('contract_id.state', '=', 'open')])
                employees = []
                new_employee = False
                for hr_contract_job in hr_contract_jobs:
                    employee = hr_contract_job.contract_id.employee_id
                    if employee.id != new_employee:
                        employee_values = {}
                        employee_values['id'] = employee.id
                        new_employee = employee.id
                        employee_values['name'] = employee.name
                        employees.append(employee_values)
            for employee in employees:
                for hr_job in hr_jobs:
                    values = {}
                    work_data = False
                    if filter_timesheet == 'all_timesheet':
                        hr_work_hours = self.env['hr.work.hours'].search_count([
                            ('job_id', '=', hr_job.id),('job_id.company_id.id', '=', self.env.user.company_id.id),('employee_id.id', '=', employee['id'])])
                    else:
                        hr_work_hours = self.env['hr.work.hours'].search_count([
                            ('job_id.company_id.id', '=', self.env.user.company_id.id),
                            ('job_id', '=', hr_job.id),('employee_id.id', '=', employee['id'])])
                        
                    if hr_work_hours > 0:
                        values['job_name'] = employee['name'] + "/" + hr_job.name
                        values['emp_id'] = employee['id']
                        values['job_id'] = hr_job.id
                        work_values = []
    #                     work_work = []
    #                     work_id = []
                        from_date = date_from
                        to_date = date_to
                        sum_tot = "00:00"
                        work_hours_total="00:00"
                        work_values_details=[]
                        while (to_date >= from_date):
                            time1 = from_date + datetime.timedelta(hours=00, minutes=00, seconds=00)
                            time2 = from_date + datetime.timedelta(hours=23, minutes=59, seconds=59)
                            timesheets = self.env['hr.work.hours'].search(
                                [('date', '>=', str(time1)), ('date', '<=', str(time2)),
                                 ('job_id', '=', hr_job.id), ('job_id.company_id.id', '=', self.env.user.company_id.id), ('employee_id', '=', employee['id'])])
                            diff = "00:00"
                            sum = "00:00"
                            id = 0
                            work_hour = 0.0
    
                            for timesheet in timesheets:
                                work_data = True
                                id = timesheet.id
                                work_hour+=timesheet.work_hours
                            work_hour = self.float_to_time(work_hour)
                            work_values.append(work_hour)
                            work_values_detail={}
                            work_values_detail[str(from_date)]=float(self.time_to_float(work_hour))
                            work_values_details.append(work_values_detail)
                            sum_tot = self.add_times(sum_tot, work_hour)
                            from_date = from_date + datetime.timedelta(days=1)
                        values['work_values'] = work_values
                        values['work_values_details'] = work_values_details
                        values['total_work_values'] = sum_tot
                        if work_data:
                            work_hours.append(values)               
            
            result['work_hours'] = work_hours
            
            
            from_date = date_from
            to_date = date_to
            overall_tot=0.0
            job_post=[]
            while (to_date >= from_date): 
                tot=0.0
                for work_hour in work_hours: 
                    for key in work_hour['work_values_details']:
                        if str(from_date) in key:             
                            tot+= key[str(from_date)]
                            overall_tot+=key[str(from_date)]
                job_post.append(self.float_to_time(tot))
                from_date = from_date + datetime.timedelta(days=1)
            result['total_work_hours']=job_post
            result['total_work_hours_all']=self.float_to_time(overall_tot)
               
            sch_diff=[]
            for x in range(0, len(result['schedules_tot'])):
                values = {}
                diff_hours=self.diff_times(result['schedules_tot'][x],result['total_work_hours'][x])
                values['diff_hours'] = diff_hours[1]
                values['diff_type'] = diff_hours[0]
                sch_diff.append(values)
            result['total_work_hours_diff']=sch_diff
            result['tot_diff_hours']=self.diff_times(result['schedules_tot_all'],result['total_work_hours_all'])[1]
                                
            hr_jobs = self.env['hr.job'].search([('company_id', '=', self.env.user.company_id.id)])
            date1 = date_from + datetime.timedelta(hours=00, minutes=00, seconds=00)
            date2 = date_to + datetime.timedelta(hours=23, minutes=59, seconds=59)

            values = {}
            total_work_values = [] 
            from_date = date_from
            to_date = date_to
            sum_tot = "00:00"
            work_hours_total="00:00"
            while (to_date >= from_date):
                time1 = from_date + datetime.timedelta(hours=00, minutes=00, seconds=00)
                time2 = from_date + datetime.timedelta(hours=23, minutes=59, seconds=59)
                if filter_timesheet == 'my_timesheet':
                    timesheets = self.env['hr.work.hours'].search(
                        [('date', '>=', str(time1)), ('date', '<=', str(time2)),
                        ('employee_id.user_id','=',self.env.user.id)])
                if filter_timesheet == 'team_member':
                    timesheets = self.env['hr.work.hours'].search(
                        [('date', '>=', str(time1)), ('date', '<=', str(time2)),
                        ('employee_id','=',int(current_employee))])
                sum = "00:00"
                work_hour = 0.0
                for timesheet in timesheets:
                    work_hour+=timesheet.work_hours
                work_hour = self.float_to_time(work_hour)
                sum = self.add_times(sum, work_hour)
                sum_tot = self.add_times(sum_tot, work_hour)
                
                from_date = from_date + datetime.timedelta(days=1)
                total_work_values.append(sum)
                    
            result['total_work_hours'] = total_work_values
            while (date_to >= date_from):
                date_new_antr={}
                date_new_antr['d1']=date_from.strftime('%a <br />%b %d')
                date_new_antr['d2']=date_from.strftime('%Y-%m-%d')
                dates.append(date_new_antr)
                date_from = date_from + datetime.timedelta(days=1)
    
            sch_work_total = []
            values = {}
            job_work_n=[]
            n=0

            for x in total_work_values:
                job_work_n.append(self.time_diff(total_work_values[n], job_values[n]))
                n+=1
            values['job_work_diff'] = job_work_n
            sch_work_total.append(values)

        result['filter_timesheet'] = filter_timesheet
        result['filter_module'] = filter_module
        
        
        result['employee_ids'] = employee_ids
        result['total_employee'] = total_employee
        result['current_employee'] = current_employee
        result['employee_name'] = employee_name
        result['employee_number'] = employee_number
        result['jobs_total'] = jobs_total
        result['sch_work_total'] = sch_work_total
        result['jobs'] = jobs
        result['dates'] = dates
        result['week_no'] = week_no
        result['week_type'] = week_type
        
        
        return result


    def float_time(self,time_value):  

        hours, minutes = ([int(x)]  for x in str(time_value).split(".",1))
        if minutes[0] > 60:
            minutes = minutes[0] % 60
            hours=int(hours[0])+1
        else:
            minutes = minutes[0]
            hours = hours[0]
        if len(str(hours)) == 1:
            hours = "0" + str(hours)
        if len(str(minutes)) == 1:
            minutes = "0" + str(minutes)
#         convert_int_to_time =  datetime.datetime.strptime((str(hours)+":"+str('%02d'%minutes)),"%H:%M")  
        formated_time = str(hours)+":"+str(minutes)
        return formated_time