from odoo import api, fields, models, tools, _
import datetime
from datetime import timedelta, date
from odoo.exceptions import UserError, ValidationError


class ProductionLines(models.Model):
    _name = 'payslip.production.lines'
    
    name = fields.Many2one('hr.production.tag','Production')
    date = fields.Date('Date')
    job_position = fields.Many2one('hr.job', string='Job Position')
    production_type = fields.Many2one('hr.production.type', string='Production Type')
    amount = fields.Float('Amount')
    hr_payslip_id = fields.Many2one('hr.payslip')

class VitalpetHrProductionLine(models.Model):
    _inherit = 'hr.production.line'

    hr_payslip_id = fields.Many2one('hr.payslip')


class HrPayslipWorkedDays(models.Model):

    _inherit = 'hr.payslip.worked_days'
    
    job_id = fields.Many2one('hr.job', string='Job Position')
    
class HrPayslip(models.Model):
    _inherit = 'hr.payslip'
    
    production_line_ids = fields.One2many('payslip.production.lines','hr_payslip_id', string="Production")
    timesheet_value = fields.Float( compute='_compute_timesheet_value',string="Timesheet Value", )


    worked_days_line_ids = fields.One2many(
        domain=[('activity_type', 'in', ('job', None))],
    )
    
    @api.multi
    def hr_rule_new(self):
        payslip=self
        contract=self.contract_id
        employee=self.employee_id
    # Computation
        print 23132
        # inputs
        
        pp_start = payslip.date_from
        pp_end = payslip.date_to
        tp_start = contract.trial_date_start
        tp_end = contract.trial_date_end
        c_start = contract.date_start
        c_end = contract.date_end
        
        allocation = 0.0
        prod_allocation = 0.0
        balance = 0.0
        bonus1 = 0.0
        total_bonus = 0.0
        bal = 0.0
        # Check Contract
        if c_start > pp_start and c_start < pp_end:
            if c_end < pp_end:
                allocation = (c_end - c_start).days / (pp_end - pp_start).days
            else:
                allocation = (pp_end - c_start).days / (pp_end - pp_start).days
        else:
            if c_end > pp_start and c_end < pp_end:
                if c_start > pp_start:
                    allocation = (c_end - c_start).days / (pp_end - pp_start).days
                else:
                    allocation = (pp_end - c_start).days / (pp_end - pp_start).days
            else:
                allocation = 1.0
        
        # Check Trial Period
        
        if tp_start > pp_start and tp_start < pp_end:
            if tp_end < pp_end:
                prod_allocation = (tp_end - c_start).days / (pp_end - pp_start).days
            else:
                prod_allocation = (pp_end - tp_start).days / (pp_end - pp_start).days
        else:
            if tp_end > pp_start and tp_end < pp_end:
                if tp_start > pp_start:
                    prod_allocation = (tp_end - c_start).days / (pp_end - pp_start).days
                else:
                    prod_allocation = (pp_end - tp_start).days / (pp_end - pp_start).days
            else:
                prod_allocation = 1.0
        
        if prod_allocation != 1.0:
            if allocation < 1.0 and prod_allocation < 1.0:
                prod_allocation = prod_allocation * allocation
        
        bonus = 0.0
        
        # Calculate total leave hours
        unpaid = 0.0
        for leave in payslip.leave_days_line_ids:
            if leave.activity_id.leave_id.name == 'Unpaid':
                unpaid += leave.number_of_hours
        
        pays_per_year = payslip.pays_per_year
        
        period_hours = 2080 / pays_per_year - unpaid
        
        wage_pool = ((contract.wage / pays_per_year) * (period_hours / 2080) * pays_per_year)
        pp = 0
        
        total_work_hours = 0.0
        for rec in payslip.worked_days_line_ids:
            total_work_hours += rec.number_of_hours
        all_locations = {}
        for job in contract.staff_bonus_ids.sorted(lambda x: x.job_id):
            if job.job_id.company_id.id not in all_locations:
                worked_job_days = payslip.worked_days_line_ids.filtered(lambda x: x.activity_id.job_id.id == job.job_id.id)
                if worked_job_days:
                    total_job_work_hours = 0.0
                    for rec in worked_job_days:
                        if rec.activity_id.job_id.id == job.job_id.id:
                            total_job_work_hours += rec.number_of_hours
                    if total_job_work_hours > 0:
                        job_base_comp = ((total_job_work_hours / total_work_hours) * allocation * wage_pool)
                        all_locations[job.job_id.company_id.id] = {'job_base_comp': job_base_comp, 'bonus': 0.0,
                                                                   'job_type': job.type_id.id}
            if total_work_hours == 0.0:
                continue
            if job.type_id.name == 'Doctor' and job.rate_id > 0.0 and job.is_bonus == True:
                tags_worked_total = payslip.production_line_ids.filtered(lambda x: x.name.id == job.production_tag_id.id)
                if tags_worked_total:
                    bonus = 0.0
                    for tags_worked in tags_worked_total:
                        p_total = 0.0
                        if tags_worked.job_position.id == job.job_id.id:
                            for rec in tags_worked:
                                p_total += rec.amount
                            if job.sub_amount:
                                bonus = bonus - job.rate_id * p_total
                            else:
                                bonus = bonus + job.rate_id * p_total
                                pp = job.payout_period
                            all_locations[job.job_id.company_id.id]['bonus'] += bonus
                    total_bonus += bonus
        total_job_base_comp = 0.0
        for key, value in all_locations.items():
            total_job_base_comp += value['job_base_comp']
            print (payslip.hr_period_id.number) / pp, '--'
            print isinstance(((payslip.hr_period_id.number) / pp), (int, long))
            print payslip.hr_period_id.number,'--', pp
            
            if not ((payslip.hr_period_id.number) / pp) % 1 == 0:                
                # PERFORM WRITE
                payslip.hr_create_bonus(employee.id, value['job_type'], key, payslip.hr_period_id.id, value['bonus'],
                                        value['job_base_comp'], payslip.date_payment)
            else:
                # PERFORM READ
                balance = payslip.hr_read_bonus(key, employee.id, payslip.hr_period_id.number - contract.payout_delay,
                                                 value['job_type'], 'b')
                print key, '--',employee.id, '--',payslip.hr_period_id.number - contract.payout_delay,'--',value['job_type'], 'b'
                # PERFORM WRITE
                payslip.hr_create_bonus(employee.id, value['job_type'], key, payslip.hr_period_id.id, value['bonus'], value['job_base_comp'] + balance, payslip.date_payment)
        
        result = (total_bonus) - (total_job_base_comp)
        raise ValidationError(_(str(balance)+'---'+str(result)))
        result = balance 
        #result = job_base_comp

    @api.multi
    def hr_create_bonus(self, employee, production_type, company, payroll_period, earned, paid,date):
        print earned,'--', paid
        if company:
            bonus_obj = self.env['hr.bonus.accrual'].search([('employee_id','=',employee),('company_id','=',company),('payroll_period','=',payroll_period)])
            if bonus_obj:
                bonus_obj.update({'date': date,
                                  'earned': earned,
                                  'paid': paid,
                                  'production_type': production_type,
                                    })
            else:
                bonus_id = self.env['hr.bonus.accrual'].create({
                                                    'employee_id': employee,
                                                    'production_type': production_type,
                                                    'company_id': company,
                                                    'date': date,
                                                    'payroll_period': payroll_period,
                                                    'source': 'calculated',
                                                    'paid': paid,
                                                    'earned': earned,
                                                    })      
                
    @api.multi
    def hr_read_bonus(self, company, employee, payroll_period_num, production_type, action):
        bonus_obj = self.env['hr.bonus.accrual'].search([('company_id','=', company),('employee_id','=', employee),('payroll_period_num','=',payroll_period_num),('production_type','=',production_type)])
        if action == 'e':
            amount = bonus_obj.earned
        elif action == 'p':
            amount = bonus_obj.paid
        else:
            amount = bonus_obj.balance
        
        print amount
        return amount
    
#     @api.multi
#     def hr_verify_sheet(self):
#         contract_obj = self.env['hr.contract'].search([('employee_id','=',self.employee_id.id)])
#         production_types = []
#         production_tags = []
#         if contract_obj:
#             for types in contract_obj.staff_bonus_ids:
#                 production_types.append(types.type_id.id)
#                 production_tags.append(types.production_tag_id.id)
#             production_types = list(set(production_types))
#             production_tags = list(set(production_tags))
#             for production_type in production_types:
#                 amount = 0.00
#                 production_objs = self.env['hr.production.line'].search([('date','>=',self.date_from),('date','<=',self.date_to),('company_id','=',self.employee_id.company_id.id),('employee_id','=',self.employee_id.id),('production_type','=',production_type)])
#                 for production_obj in production_objs:
#                     for production_tag in production_tags:
#                         if production_obj.bonus_id.id == production_tag:
#                             for rates in contract_obj.staff_bonus_ids:
#                                 if rates.production_tag_id.id == production_tag:
#                                     bonus = rates.rate_id * production_obj.amount
#                             amount += bonus 
#                 if amount > 0:
#                     bonus_id = self.env['hr.bonus.accrual'].create({
#                                                                     'employee_id': self.employee_id.id,
#                                                                     'production_type': production_type,
#                                                                     'company_id': self.employee_id.company_id.id,
#                                                                     'date': self.date_to,
#                                                                     'payroll_period': self.hr_period_id.id,
#                                                                     'source': 'calculated',
#                                                                     'paid': amount,
#                                                                     })
#         return super(HrPayslip, self).hr_verify_sheet()
    
    @api.multi
    def getweek(self,day,weekstart): 
        week_days=["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
        week_day=datetime.datetime.strptime(weekstart, "%Y-%m-%d").weekday()
        if week_days[week_day]=="Sunday":
            day_start=1
        elif week_days[week_day]=="Monday":
            day_start=2
        elif week_days[week_day]=="Tuesday":
            day_start=3
        elif week_days[week_day]=="Wednesday":
            day_start=4
        elif week_days[week_day]=="Thursday":
            day_start=5
        elif week_days[week_day]=="Friday":
            day_start=6
        elif week_days[week_day]=="Saturday":
            day_start=0
        
        date=datetime.datetime.strptime(day, "%Y-%m-%d")+ datetime.timedelta(days=day_start)
        weekNumber = date.isocalendar()[1]    
        return weekNumber
    
    
    
#     @api.multi
#     def compute_sheet(self):
#         for payslip in self:
#             if payslip.contract_id:
#                 if payslip.contract_id.draw_type_id:
#                     if payslip.contract_id.draw_type_id.code=='DVMPROD':
#                         total_pay=payslip.contract_id.annual_draw/2
#                         amount=0
#                         for production in payslip.production_line_ids:
#                             amount+=production.amount
#                         prodcution_amount=amount*payslip.contract_id.production_rate
# #                         print prodcution_amount
#                         bonus={}
#                         bonus['accured'] = prodcution_amount
#                         bonus['paid'] = total_pay
#                         bonus['balance'] = prodcution_amount-total_pay
#                         bonus['hr_payslip_id'] = payslip.id
#                         bonus['source'] = 'calculated'
#                         bonus['payroll_period'] = payslip.hr_period_id.id
#                         bonus['employee_id'] = payslip.employee_id.id
#                                                 
#                         self.env['hr.bonus.accrual'].create(bonus)
# #             DVMPROD
# 
#         return super(HrPayslip, self).compute_sheet()
    
    @api.depends('worked_days_line_ids')
    def _compute_timesheet_value(self):
        for record in self:
            tot=0
            for rec in record.worked_days_line_ids:
                tot+=rec.total
            record.timesheet_value=tot
     
    @api.multi
    def import_production(self):
        if self.state == 'done':
            raise ValidationError(_('Done payslips can not be edited'))

        if self.production_line_ids:
            self.production_line_ids.unlink()

        production_recs = self.env["hr.production.line"].search([('employee_id','=',self.employee_id.id),('date', '>=', self.date_from),('date','<=',self.date_to),('status' ,'=','validate'),'|',('hr_payslip_id','=', False),('hr_payslip_id','=', self.id)])
        print production_recs
              
        for production in production_recs:
            production.hr_payslip_id = self.id
            product_import = self.env["payslip.production.lines"].search([('job_position','=',production.job_id.id),('name','=',production.bonus_id.id),('production_type','=',production.production_type.id), ('hr_payslip_id', '=', self.id)])            
            if product_import:               
                product_import.amount=product_import.amount+production.amount
            else:
                if production.amount != 0.00:
                    line_vals = []
                    vals = {
                    'date': production.date,
                    'job_position':production.job_id.id,
                    'amount':production.amount, 
                    'name':production.bonus_id.id,    
                    'production_type':production.bonus_id.production_type.id,          
                        }
                    line_vals.append((0, 0, vals)) 
                    self.production_line_ids = line_vals
                
                   
     
    @api.multi
    def import_worked_days(self):  
        work_days_rec = self.env["hr.work.hours"].search([('employee_id','=',self.employee_id.id),('date', '>=', self.date_from),('date','<=',self.date_to)])
        if work_days_rec:
            line_vals = []
            if self.worked_days_line_ids:
                self.worked_days_line_ids.unlink()
            for work in work_days_rec:
                if work.work_hours != 0.00:
                    for positions in work.employee_id.contract_id.contract_job_ids:
                        if positions.job_id.id==work.job_id.id:
                            activity_obj = self.env['hr.activity'].search([('job_id','=',work.job_id.id)])
                            vals = {
                                'date': work.date,
                                'job_id': work.job_id.id,
                                'activity_id': activity_obj.id,  
                                'number_of_hours':work.work_hours,
                                'hourly_rate': positions.hourly_rate,
                                'activity_type':'job',                
                                }
                            line_vals.append((0, 0, vals))
            self.worked_days_line_ids = line_vals
        else:
            raise ValidationError(_('No records found'))
            
         


          


    
