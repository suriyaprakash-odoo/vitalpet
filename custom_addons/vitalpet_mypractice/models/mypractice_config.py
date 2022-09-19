# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
#from odoo import models
import datetime
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, tools, SUPERUSER_ID


class MypracticeDashboard(models.Model):
    _name = 'mypractice.dashboard'

    name = fields.Char('name')


    @api.model
    def retrieve_sales_dashboard(self):
        task_obj = self.env['project.task']
        project_obj = self.env['project.project']
        project_sr = project_obj.search([('name', '=', 'My Practice'),('company_id', '=', self.env.user.company_id.id)])
        result = {

                'meeting': {'today': 0,'next_7_days': 0},
                'admin': {'today': 0,'next_7_days': 0, 'overdue':0},
                'cvisit':{'today_visit': 0,'next_7_days_visit': 0, 'overdue_visit':0},
                }
        
        # For meeting Dashboard
        min_date = datetime.datetime.now()
        start_today = min_date.strftime('%Y-%m-%d 00:00:00')
        dt = datetime.datetime.strptime(start_today, "%Y-%m-%d %H:%M:%S")


        max_date = (dt + datetime.timedelta(days=0))
        end_today = max_date.strftime('%Y-%m-%d 23:59:59')
        end_today_dt = datetime.datetime.strptime(end_today, "%Y-%m-%d %H:%M:%S")

        start_2week_date = (dt + datetime.timedelta(days=1))
        start_2week = start_2week_date.strftime('%Y-%m-%d 00:00:00')
        start_2week_dt = datetime.datetime.strptime(start_2week, "%Y-%m-%d %H:%M:%S")

        next2weeks_date = (start_2week_dt + datetime.timedelta(days=14))
        end_next2weeks = next2weeks_date.strftime('%Y-%m-%d 23:59:59')
        end_next2weeks_dt = datetime.datetime.strptime(end_next2weeks, "%Y-%m-%d %H:%M:%S")



        
        meetingstday_domain = [
            ('start', '>=', str(start_2week_dt)),
            ('start', '<=', str(end_next2weeks_dt)),
            ('partner_ids', 'in', [self.env.user.partner_id.id])
        ]

        meetings_domain = [
            ('start', '>=', str(dt)),
            ('start', '<=', str(end_today_dt)),
            ('partner_ids', 'in', [self.env.user.partner_id.id])
        ]



        meetings = self.env['calendar.event'].search(meetings_domain)

        meetings_2week = self.env['calendar.event'].search(meetingstday_domain)

        for meeting in meetings:
            if meeting['start']:
                start = datetime.datetime.strptime(meeting['start'], tools.DEFAULT_SERVER_DATETIME_FORMAT).date()
                if start == datetime.date.today():
                    result['meeting']['today'] += 1

        for meeting in meetings_2week:
            if meeting['start']:
                start = datetime.datetime.strptime(meeting['start'], tools.DEFAULT_SERVER_DATETIME_FORMAT).date()
                if datetime.date.today() <= start <= datetime.date.today() + datetime.timedelta(days=14):
                    result['meeting']['next_7_days'] += 1



        # for Todo Dashboard
        task_obj = self.env['project.task']
        user = self.env.user.id
        date_today = fields.Date.today()
        lst = str(datetime.datetime.now() + datetime.timedelta(days=-14))[:10]
        fst = str(datetime.datetime.now() + datetime.timedelta(days=-1))[:10]
        yeterday = datetime.datetime.now() + datetime.timedelta(days=-1)
        yeterday_less = datetime.datetime.now() + datetime.timedelta(days=-2)
        yeterday_dt = str(yeterday)[:10]
        s = datetime.datetime.now() + datetime.timedelta(days=-14)
        less_week = str(s)[:10]
        task_todo_sr = self.env['project.task.type'].search([('name', '=', 'To Do')])
        less_week_st = self.env['project.task.type'].search([('name', '=', 'Overdue < 1 Week')])
        less2week_st = self.env['project.task.type'].search([('name', '=', 'Overdue > 1 Week')])
        nxt_st = self.env['project.task.type'].search([('name', '=', 'Next 14 Days')])
        
        task_today_sr = task_obj.search([('mypractice','=',True),('company_id','child_of',[self.env.user.company_id.id]),('stage_id', '=', task_todo_sr.id)])  
        task_sr = task_obj.search([('mypractice','=',True),('company_id','child_of',[self.env.user.company_id.id]),('stage_id', 'in', [less_week_st.id])])
        task_overdue_sr = task_obj.search([('mypractice','=',True),('company_id','child_of',[self.env.user.company_id.id]),('stage_id', 'in', [less2week_st.id])])
        
        tot_task_today = len(task_today_sr)
        next2weeks_task = len(task_sr)
        overdue_task = len(task_overdue_sr)
        print tot_task_today, next2weeks_task, overdue_task
        #task_2_weeks_sr = task_obj.search([('user_id', '=', user),('date_deadline','&gt;=', fst), ('date_deadline','&lt;=', lst),('project_id.name', '=', 'My Practice')])

        
        result['admin']['today'] = tot_task_today
        result['admin']['next_7_days'] = next2weeks_task
        result['admin']['over_due'] = overdue_task
        
        project_tag_sr = self.env['project.tags'].search([('name', '=', 'Visit')])
        
        visit_tot_task_today = self.env['project.task'].search_count([('mypractice','=',True),('company_id','child_of',[self.env.user.company_id.id]),('stage_id', 'in', [task_todo_sr.id]),('tag_ids', 'in', [project_tag_sr.id])])  
        visit_next2weeks_task = self.env['project.task'].search_count([('mypractice','=',True),('company_id','child_of',[self.env.user.company_id.id]),('stage_id', 'in', [less_week_st.id]),('tag_ids', 'in', [project_tag_sr.id])])
        visit_overdue_task = self.env['project.task'].search_count([('mypractice','=',True),('company_id','child_of',[self.env.user.company_id.id]),('stage_id', 'in', [less2week_st.id]),('tag_ids', 'in', [project_tag_sr.id])])
        
        # visit_tot_task_today = len(visit_task_today_sr)
        # visit_next2weeks_task = len(visit_task_sr)
        # visit_overdue_task = len(visit_task_overdue_sr)
        
        print visit_tot_task_today, visit_next2weeks_task, visit_overdue_task,'11111111111111111111'
        #task_2_weeks_sr = task_obj.search([('user_id', '=', user),('date_deadline','&gt;=', fst), ('date_deadline','&lt;=', lst),('project_id.name', '=', 'My Practice')])

        
        result['cvisit']['today_visit'] = visit_tot_task_today
        result['cvisit']['next_7_days_visit'] = visit_next2weeks_task
        result['cvisit']['over_due_visit'] = visit_overdue_task
  

        if self.env.user.company_id.expense:
            result['expenses'] = {'to_approve': 10,'to_submit': 15, 'refuse':10}
            expense_obj = self.env['hr.expense']
            expense_sheet_obj = self.env['hr.expense.sheet']
            approve_sr = expense_sheet_obj.search([('state', '=', 'submit')])
            result['expenses']['to_approve'] = len(approve_sr)
            submit_sr = expense_obj.search([('state', '=', 'draft')])
            result['expenses']['to_submit'] = len(submit_sr)
            expire_sr = expense_sheet_obj.search([('state', '=', 'cancel')])
            result['expenses']['refuse'] = len(expire_sr)

        if self.env.user.company_id.recruitment:
            result['recruitment'] = {'inbox': 0,'offer': 0,'recruitment':0}
            applicant_obj = self.env['hr.applicant']
            inbox_stage_id = self.env['hr.recruitment.stage'].search([('name', '=', 'Interview')])
            offer_stage_id = self.env['hr.recruitment.stage'].search([('name', '=', 'Offer Letter')])
            #recruit_stage_id = self.env['hr.recruitment.stage'].search([('name', '=', 'Interview')])

            applicant_sr_recruitment = self.env['hr.job'].search([('state', '=', 'recruit')])
            applicant_offer_stage_id = self.env['hr.applicant'].search([('stage_id', '=', offer_stage_id[0].id)])
            applicant_inbox_stage_id = self.env['hr.applicant'].search([('stage_id', '=', inbox_stage_id[0].id)])  
            inbox = len(applicant_inbox_stage_id)
            recruitment = len(applicant_sr_recruitment)
            offer = len(applicant_offer_stage_id)
            result['recruitment']['inbox'] = inbox
            result['recruitment']['offer'] = offer
            result['recruitment']['recruitment'] = recruitment

        if self.env.user.company_id.onboarding:
            result['onboarding'] = {'today': 0,'next_7_days': 0,'to_onboard':0}
            
            onboarding_today_obj = self.env['hr.employee.onboarding'].search([('start_date' , '=' , fields.Date.today())])
            onboarding_next_seven_obj = self.env['hr.employee.onboarding'].search([('start_date' , '<' , datetime.datetime.today().date()+ relativedelta(days=-1)),('start_date' , '<' , datetime.datetime.today().date()+ relativedelta(days=13)),('state_id' , '!=' , 'complete')])
            onboarding_to_onboard_obj = self.env['hr.employee.onboarding'].search([('state_id' , '!=' , 'complete')])

            result['onboarding']['today'] = len(onboarding_today_obj)
            result['onboarding']['next_7_days'] = len(onboarding_next_seven_obj)
            result['onboarding']['to_onboard'] = len(onboarding_to_onboard_obj)



        if self.env.user.company_id.leaves:
            result['leaves'] = {'today': 0,'next_7_days': 0}
            holiday_obj = self.env['hr.holidays']
            emp_obj = self.env['hr.employee']
            manager_user_id = emp_obj.search([('manager', '=', True),('user_id', '=', self.env.user.id)])
            emp_lst = emp_obj.search([('parent_id', '=', manager_user_id.id)])

            holiday_sr = holiday_obj.search([('date_from', '=', str(date_today)),('employee_id', 'in', [emp.id for emp in emp_lst])])
            #emp_lst = emp_obj.search('parent_id', '=', manager_user_id.id)
            result['leaves']['today'] = len(holiday_sr)

        if self.env.user.company_id.payroll_conf:
            result['payroll'] = {'today': 0,'next2week': 0, 'action':0}
            payroll_status = self.env['hr.payroll.inputs']
            task_obj = self.env['project.task']
            today_value = task_obj.search([('stage_id','=','To Do'),('tag_ids','=','Payroll'),('date_deadline','=',datetime.datetime.now())])
            result['payroll']['toady'] = len(today_value)
            n2w_value = payroll_status.search([('state','=','open'),('stage','=','validate')])
            result['payroll']['next2week'] = len(n2w_value)
            action_value = task_obj.search([('stage_id','=','To Do'),('tag_ids','=','Payroll'),('date_deadline','>',datetime.datetime.now())])
            result['payroll']['action'] = len(action_value)
             
        if self.env.user.company_id.performance:
            result['performance'] = {'today': 10,'next_7_days': 15}
        
        if self.env.user.company_id.contract:
            result['contract'] = {'running': 10,'renew': 15, 'expired':0}
            contract_obj = self.env['hr.contract']
            running_sr = contract_obj.search([('state', '=', 'open')])
            result['contract']['running'] = len(running_sr)
            renew_sr = contract_obj.search([('state', '=', 'pending')])
            result['contract']['renew'] = len(renew_sr)
            draft_sr = contract_obj.search([('state', '=', 'draft')])
            result['contract']['draft'] = len(draft_sr)
            
            # id_list1=[]
            # id_list2=[]
            # for line_id in self.env['hr.employee'].search([]):
            #     id_list1.append(line_id.id)
            # tid = contract_obj.search([])
            # for line in tid:
            #     id_list2.append(line.employee_id.id)
            # contract_id = list(set(id_list1)-set(id_list2))

            # result['contract']['expired'] = len(expire_sr) + len(contract_id)

            
        if self.env.user.company_id.performance:            
            result['appraisals'] = {'overdue':0}
            performance_obj = self.env['hr.appraisal']
            today_due = performance_obj.search([('date_close', '=',  (datetime.datetime.now()).strftime('%Y-%m-%d')),('state', '=', 'pending')])
            result['appraisals']['today_due'] = len(today_due)
            next_due = performance_obj.search([('date_close', '>', (datetime.datetime.now()).strftime('%Y-%m-%d')),('date_close', '<', (datetime.datetime.now() + relativedelta(days=13)).strftime('%Y-%m-%d')),('state', '=', 'pending')])
            result['appraisals']['next_due'] = len(next_due)
            over_due = performance_obj.search([('date_close', '<', (datetime.datetime.now()).strftime('%Y-%m-%d')),('state', '=', 'pending')])
            result['appraisals']['overdue'] = len(over_due)
            print len(today_due),'--',len(next_due),'--',len(over_due), datetime.datetime.today().date()+ relativedelta(days=13),datetime.datetime.today().date()
                      
            
        if self.env.user.company_id.attendance:
            result['attendance'] = {'today_chkout': 10,'next_7_days': 15}
            attendance_sr = self.env['hr.attendance'].search([('check_out', '=', False)])
            self.env.cr.execute("SELECT count(id) FROM hr_attendance WHERE check_out IS NULL and check_in BETWEEN %s AND %s", (str(datetime.datetime.now().replace(hour=0, minute=0, second=0)),str(datetime.datetime.now().replace(hour=23, minute=59, second=59))))
            planned = self.env.cr.fetchone()
            date = datetime.datetime.now()
            att_len = 0
            result['attendance']['today_chkout'] = att_len

        if self.env.user.company_id.attendance:
            result['attendance'] = {'today_chkout': 10,'next_7_days': 15}
            attendance_sr = self.env['hr.attendance'].search([('check_out', '=', False)])
            self.env.cr.execute("SELECT count(id) FROM hr_attendance WHERE check_out IS NULL and check_in BETWEEN %s AND %s", (str(datetime.datetime.now().replace(hour=0, minute=0, second=0)),str(datetime.datetime.now().replace(hour=23, minute=59, second=59))))
            planned = self.env.cr.fetchone()
            date = datetime.datetime.now()
            att_len = 0
            result['attendance']['today_chkout'] = att_len

            
        result['revenue'] = {'this_month': str(10),'target_percent': str(5),'target_amt':100,'last_yr':str(0),'last_amt':0}
        result['revenue']['this month'] = "RM001"
        result['revenue']['target'] = "RT002"
        result['revenue']['last year'] = "RL003"
        result['revenue']['target_per'] = "%RT002"
        result['revenue']['last year_per'] = "%RL003"

        result['visit'] = {'this_month': str(10),'target_percent': str(5),'target_amt':100,'last_yr':str(0),'last_amt':0}
        result['visit']['this month'] = "VM001"
        result['visit']['target'] = "VT002"
        result['visit']['last year'] = "VL003"
        result['visit']['target_per'] = "%VT002"
        result['visit']['last year_per'] = "%VL003"
        
        result['apc'] = {'this_month': str(10),'target_percent': str(5),'target_amt':100,'last_yr':str(0),'last_amt':0}
        result['apc']['this month'] = "AM001"
        result['apc']['target'] = "AT002"
        result['apc']['last year'] = "AL003"
        result['apc']['target_per'] = "%AT002"
        result['apc']['last year_per'] = "%AL003"
             
        result['new_client'] = {'this_month': str(10),'target_percent': str(5),'target_amt':100,'last_yr':str(0),'last_amt':0}
        result['new_client']['this month'] = "CM001"
        result['new_client']['target'] = "CT002"
        result['new_client']['last year'] = "CL003"
        result['new_client']['target_per'] = "%CT002"
        result['new_client']['last year_per'] = "%CL003"
        
        result['staff_labour'] = {'this_month': str(10),'target_percent': str(5),'target_amt':100,'last_yr':str(0),'last_amt':0}
        result['staff_labour']['this month'] = "LM001"
        result['staff_labour']['target'] = "LT002"
        result['staff_labour']['last year'] = "LL003"
        result['staff_labour']['target_per'] = "%LT002"
        result['staff_labour']['last year_per'] = "%LL003"
        
        result['schedule'] = {'this_month': str(10),'target_percent': str(5),'target_amt':100,'last_yr':str(0),'last_amt':0}
        result['schedule']['this month'] = "SM001"
        result['schedule']['target'] = "ST002"
        result['schedule']['last year'] = "SL003"
        result['schedule']['target_per'] = "%ST002"
        result['schedule']['last year_per'] = "%SL003"

        return result

    # def onboarding_open_request(self):

    #     onboarding_next_seven_obj = self.env['hr.employee.onboarding'].search([('start_date' , '<' , datetime.datetime.today().date()+ relativedelta(days=-1)),('start_date' , '<' , datetime.datetime.today().date()+ relativedelta(days=13)),('state_id' , '!=' , 'complete')])

    #     onboarding_open_list = []

    #     for rec in onboarding_next_seven_obj:
    #         onboarding_open_list.append(rec.id)

    #     return onboarding_open_list
    

MypracticeDashboard()

# Empty class but required since it's overridden by sale & crm
class MypracticeConfigSettings(models.TransientModel):

    _name = 'mypractice.config.settings'
    _inherit = 'res.config.settings'

    #settings_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    company_id = fields.Many2one('res.company', string='Company',
        default=lambda self: self.env.user.company_id, required=True)
    manager_user_id = fields.Many2one('res.users', related='company_id.manager_user_id', string='Manager', required=True)
    designee_user_id = fields.Many2one('res.users', related='company_id.designee_user_id' ,string='Designee')
    vat = fields.Char( related='company_id.vat' ,string='Federal Tax ID',  required=True)
    vat_state  = fields.Char(related='company_id.vat_state' ,string='State Tax ID')
    vat_city  = fields.Char(related='company_id.vat_city' ,string='City Tax ID')
    # Operations Days Open
    Sunday = fields.Boolean(string='Sunday' ,related='company_id.Sunday')
    Monday = fields.Boolean(string='Monday', related='company_id.Monday')
    Tuesday = fields.Boolean(string='Tuesday', related='company_id.Tuesday')
    Wednesday = fields.Boolean(string='Wednesday', related='company_id.Wednesday')
    Thursday = fields.Boolean(string='Thursday', related='company_id.Thursday')
    Friday = fields.Boolean(string='Friday', related='company_id.Friday')
    Saturday = fields.Boolean(string='Saturday', related='company_id.Saturday')
    # Operations Shifts
    sunday_shift = fields.Selection([('0', 'Day'),('1', 'Night'),('2', 'Day &amp;Night')],'Sunday Shift',related='company_id.sunday_shift')
    monday_shift = fields.Selection([('0', 'Day'),('1', 'Night'),('2', 'Day &amp;Night')],'Monday Shift',related='company_id.monday_shift')
    tuesday_shift = fields.Selection([('0', 'Day'),('1', 'Night'),('2', 'Day &amp;Night')],'Tuesday Shift',related='company_id.tuesday_shift')
    wednesday_shift = fields.Selection([('0', 'Day'),('1', 'Night'),('2', 'Day &amp;Night')],'Wednesday Shift',related='company_id.wednesday_shift')
    thursday_shift = fields.Selection([('0', 'Day'),('1', 'Night'),('2', 'Day &amp;Night')],'Thursday Shift',related='company_id.thursday_shift')
    friday_shift = fields.Selection([('0', 'Day'),('1', 'Night'),('2', 'Day &amp;Night')],'Friday Shift',related='company_id.friday_shift')
    saturday_shift = fields.Selection([('0', 'Day'),('1', 'Night'),('2', 'Day &amp;Night')],'Saturday Shift',related='company_id.saturday_shift')
    # for Dashboard To Dos
    #front_desk = fields.Boolean(string='Front Desk', help='Tip: Stay alerted when a inbound calls needs attention.', related='company_id.front_desk')
    expense = fields.Boolean(string='Expenses', help='Tip: Stay alerted when a inbound calls needs attention.', related='company_id.expense')
    recruitment = fields.Boolean(string='Recruitment', help='Tip: Stay alerted regarding requisitions and new applicants.', related='company_id.recruitment')
    onboarding = fields.Boolean(string='Onboarding', help='Tip: Stay alerted regarding onboarding activities.', related='company_id.onboarding')
    leaves = fields.Boolean(string='Leaves', help='Tip: Stay alerted regarding time off requests.', related='company_id.leaves')
    attendance = fields.Boolean(string='Attendance', help='Tip: Stay alerted regarding time punches.', related='company_id.attendance')
    payroll_conf = fields.Boolean(string='Payroll', related='company_id.payroll_conf', help='Tip: Stay alerted regarding payroll approval.')
    performance = fields.Boolean(string='Appraisal', help='Tip: Stay alerted regarding performance reviews.', related='company_id.performance')
    contract = fields.Boolean(string='Contract', help='Tip: Stay alerted regarding performance reviews.', related='company_id.contract')
    company_logo = fields.Binary(related="company_id.logo", string='Company Logo')
    total_capacity = fields.Integer(related="company_id.total_capacity", string="Total Capacity")
    total_day_camp_capacity = fields.Integer(related="company_id.total_day_camp_capacity", string="Total Capacity")


    
