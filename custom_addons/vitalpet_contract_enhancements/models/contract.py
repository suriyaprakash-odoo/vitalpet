from odoo import fields, models, api, _
from odoo.tools.translate import _
from odoo.exceptions import UserError, RedirectWarning, ValidationError
from odoo.tools import float_compare, float_is_zero
from dateutil.relativedelta import relativedelta
import odoo.addons.decimal_precision as dp
import string
import dateutil.parser
from datetime import date,datetime,timedelta
from __builtin__ import isinstance

class HrContractDrawType(models.Model):
    _name = "hr.contract.draw.type"
    
    _rec_name = 'draw_type'
    
    code = fields.Char(string="Code")
    draw_type = fields.Char(string="Draw Type")
    description = fields.Text(string="Description")
    
    _sql_constraints = [
        ('code_uniq', 'unique (code)', 'Code must be unique')]
    
      
class HrContractHolidayPlanLines(models.Model):
    _name = "hr.contract.holiday.plan.lines"  
    
    _rec_name = 'contract_holiday_id'

      
    is_active = fields.Boolean(string="Active")
    salary_rule_id = fields.Many2one('hr.salary.rule', string="Salary Rule")
    is_paid = fields.Boolean(string="Is Paid?")
    date_start = fields.Date(string="Date Start")
    date_end = fields.Date(string="Date End")
    salary_computation_id = fields.Selection([
        ('yearly', 'Annual Wage'),
        ('monthly', 'Monthly Wage'),
        ('hourly', 'Hourly Wage'),
    ], string='Pay Type')
    holiday_id = fields.Many2one('hr.holidays', string="Holiday")
    date = fields.Date(string="Date")
    hours_pay = fields.Float(string="Hours To Pay")
    contract_holiday_id = fields.Many2one('hr.contract.leave.holiday.plan', String="Contract Holiday")
    
    
    
class HrContractLeaveHolidayPlanLines(models.Model):
    _name = "hr.contract.leave.plan.lines"
    
    name = fields.Char(string="Name")
    is_active = fields.Boolean(string="Active")
    salary_rule_id = fields.Many2one('hr.salary.rule', string="Salary Rule")
    is_paid = fields.Boolean(string="Is Paid?")
    date_start = fields.Date(string="Date Start")
    date_end = fields.Date(string="Date End")
    salary_computation_id = fields.Selection([
        ('yearly', 'Annual Wage'),
        ('monthly', 'Monthly Wage'),
        ('hourly', 'Hourly Wage'),
    ], string='Pay Type')
   
    contract_type_id = fields.Many2one('hr.contract.type', string="Contract Type")
    employee_id = fields.Many2many('hr.employee', string="Restrict To Employee")
    tenure_start = fields.Integer(string="Tenure Start Days")
    tenure_end = fields.Integer(string="Tenure End Days")
    rate_per_hour = fields.Float(string="Rate Per Work Hour", digits=dp.get_precision('Contract Enhancement'))
    max_hour_year = fields.Integer(string="Max Hours Per Year ")
    carry_over_hour = fields.Integer(string="Carry Over Hours")
    paid_terminate = fields.Boolean(string="Paid On Termination")
    contract_leave_id = fields.Many2one('hr.contract.leave.holiday.plan', string="Contract Leaves")
    company_id = fields.Many2one('res.company', string="Company")
    description = fields.Text(string="Description")
    

class HrContractLeaveHolidayPlan(models.Model):
    _name = "hr.contract.leave.holiday.plan"
    
    name = fields.Char(string="Name")
    is_active = fields.Boolean(string="Active")
    company_id = fields.Many2one('res.company', string="Company")
    contract_leave_ids = fields.One2many('hr.contract.leave.plan.lines', 'contract_leave_id', string="Contract Leave")
    contract_holiday_ids = fields.One2many('hr.contract.holiday.plan.lines', 'contract_holiday_id', string="Contract Holiday") 
  
  
class Bonus(models.Model):
    _inherit = "bonus.accrual"  
    
    code_id = fields.Char(related='production_tag_id.code',string='Code')
    type_id = fields.Many2one('hr.production.type', related='production_tag_id.production_type', string='Type')
    rate_id = fields.Float( string='Rate',digits = (12,3))
    sub_amount = fields.Boolean(related='production_tag_id.subtract_amount', string='Subtract Amount')
    payout_period = fields.Integer(related='production_tag_id.payout', string='Payout Period')
    salary_rule = fields.Many2one('hr.salary.rule', related='production_tag_id.salary_rule_id', string='Salary Rule')
    validation = fields.Boolean(related='production_tag_id.double_validation', string='Double Validation')
#     deduct_draw =fields.Boolean(related='production_tag_id.deduct_draw',string="Deduct Draw")

class HrContract(models.Model):
    _inherit = "hr.contract"
       
    contract_log_line_ids = fields.One2many('hr.contract.line.log', 'contract_log_line_id', string="Contract log line")
    job_seniority_title = fields.Many2one('hr.job.seniority.title', string="Job Seniority Title")
    leave_holiday_plan = fields.Many2one('hr.contract.leave.holiday.plan', string="Leave and Holiday Plan")
    notice = fields.Integer(string="Notice(days)", default="30")
    notice_end = fields.Integer(string="Notice End",compute="_compute_notice_day")
    draw_type_id = fields.Many2one('hr.contract.draw.type', string="Draw Type")
    production_basis = fields.Float(string="Production Basis")
    production_rate = fields.Float(string="Production Rate")
    discount_rate = fields.Float(string="Discount Rate")
    annual_draw = fields.Float(string="Est.Annual Draw")
    payout_delay = fields.Integer(string="Payout Delay", default="2")
    name = fields.Char('Contract Reference', required=False)
   
#     visa_expire = fields.Date(related='employee_id.visa_exp','Visa Expire Date')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('open', 'Active'),
        ('pending', 'To Renew'),
        ('close', 'Expired'),
    ], string='Status', track_visibility='onchange', help='Status of the contract', default='draft')
    
    schedule_pay = fields.Selection(
        lambda self: self.get_schedule_selection(),
        'Scheduled Pay',
        select=True,
        default='bi-weekly',
    )
   
    @api.onchange('payout_delay')
    def _onchange_contract_approved_functionality(self):
        line_ids = []
        for line_id in self.contract_log_line_ids:
            if isinstance(line_id.id, int):
                line_ids.append((4,line_id.id))
             
        if self.payout_delay:
            context = self._context
            current_uid = context.get('uid')
            user = self.env['res.users'].browse(current_uid)
             
            original_val_payout = self._origin.payout_delay
            for loop in self:
                if loop.payout_delay:
                    if loop.payout_delay != original_val_payout:
                        vals = ({
                                    'field':"Payout Delay",
                                    'user_id':user.id,
                                    'date':datetime.today(),
                                    'original_value':original_val_payout,
                                    'change_value':loop.payout_delay,
                          
                                    })
                        line_ids.append((0, 0, vals))
                        loop.update({'contract_log_line_ids': line_ids})
                    else:
                        loop.update({'contract_log_line_ids': line_ids})     
            
            
    @api.onchange('leave_holiday_plan')
    def _onchange_contract_approved_functionality_leave(self):
        line_ids = []
        for line_id in self.contract_log_line_ids:
            if isinstance(line_id.id, int):
                line_ids.append((4,line_id.id))
             
        if self.leave_holiday_plan:
            context = self._context
            current_uid = context.get('uid')
            user = self.env['res.users'].browse(current_uid)
             
            original_val_leave_plan = self._origin.leave_holiday_plan
            for loop in self:
                if loop.leave_holiday_plan:
                    if loop.leave_holiday_plan.id != original_val_leave_plan.id:
                        
                        vals = ({
                                    'field':"Leave Plan",
                                    'user_id':user.id,
                                    'date':datetime.today(),
                                    'original_value':original_val_leave_plan.name,
                                    'change_value':loop.leave_holiday_plan.name,
                          
                                    })
                        line_ids.append((0, 0, vals))
                        loop.update({'contract_log_line_ids': line_ids})
                    else:
                        loop.update({'contract_log_line_ids': line_ids})
    
    @api.onchange('salary_computation_method')
    def _onchange_contract_approved_functionality_pay_type(self):
        line_ids = []
        for line_id in self.contract_log_line_ids:
            if isinstance(line_id.id, int):
                line_ids.append((4,line_id.id))
             
        if self.salary_computation_method:
            context = self._context
            current_uid = context.get('uid')
            user = self.env['res.users'].browse(current_uid)
             
            original_val_salary_computation_method = self._origin.salary_computation_method
            for loop in self:
                if loop.salary_computation_method:
                    if loop.salary_computation_method != original_val_salary_computation_method:
                        
                        vals = ({
                                    'field':"Pay Type",
                                    'user_id':user.id,
                                    'date':datetime.today(),
                                    'original_value':original_val_salary_computation_method,
                                    'change_value':loop.salary_computation_method,
                          
                                    })
                        line_ids.append((0, 0, vals))
                        loop.update({'contract_log_line_ids': line_ids})
                    else:
                        loop.update({'contract_log_line_ids': line_ids})  
                        
                        
                        
    @api.onchange('wage')
    def _onchange_contract_approved_functionality_wage(self):
        line_ids = []
        for line_id in self.contract_log_line_ids:
            if isinstance(line_id.id, int):
                line_ids.append((4,line_id.id))
             
        if self.wage:
            context = self._context
            current_uid = context.get('uid')
            user = self.env['res.users'].browse(current_uid)
             
            original_val_wage = self._origin.wage
            for loop in self:
                if loop.wage:
                    if loop.wage != original_val_wage:
                        vals = ({
                                    'field':"Wage",
                                    'user_id':user.id,
                                    'date':datetime.today(),
                                    'original_value':original_val_wage,
                                    'change_value':loop.wage,
                          
                                    })
                        line_ids.append((0, 0, vals))
                        loop.update({'contract_log_line_ids': line_ids})
                    else:
                        loop.update({'contract_log_line_ids': line_ids})  
                        
    @api.onchange('schedule_pay')
    def _onchange_contract_approved_functionality_schedule_pay(self):
        line_ids = []
        for line_id in self.contract_log_line_ids:
            if isinstance(line_id.id, int):
                line_ids.append((4,line_id.id))
             
        if self.schedule_pay:
            context = self._context
            current_uid = context.get('uid')
            user = self.env['res.users'].browse(current_uid)
             
            original_val_schedule_pay = self._origin.schedule_pay
            for loop in self:
                if loop.schedule_pay:
                    if loop.schedule_pay != original_val_schedule_pay:
                        
                        vals = ({
                                    'field':"Schedule Pay",
                                    'user_id':user.id,
                                    'date':datetime.today(),
                                    'original_value':original_val_schedule_pay,
                                    'change_value':loop.schedule_pay,
                          
                                    })
                        line_ids.append((0, 0, vals))
                        loop.update({'contract_log_line_ids': line_ids})
                    else:
                        loop.update({'contract_log_line_ids': line_ids})  
                        
    @api.onchange('trial_date_start')
    def _onchange_contract_approved_functionality_trial_date_start(self):
        line_ids = []
        for line_id in self.contract_log_line_ids:
            if isinstance(line_id.id, int):
                line_ids.append((4,line_id.id))
             
        if self.trial_date_start:
            context = self._context
            current_uid = context.get('uid')
            user = self.env['res.users'].browse(current_uid)
             
            original_val_trial_date_start = self._origin.trial_date_start
            for loop in self:
                if loop.trial_date_start:
                    if loop.trial_date_start != original_val_trial_date_start:
                        
                        vals = ({
                                    'field':"Trial Period Start Date",
                                    'user_id':user.id,
                                    'date':datetime.today(),
                                    'original_value':original_val_trial_date_start,
                                    'change_value':loop.trial_date_start,
                          
                                    })
                        line_ids.append((0, 0, vals))
                        loop.update({'contract_log_line_ids': line_ids})
                    else:
                        loop.update({'contract_log_line_ids': line_ids})  
                        
    @api.onchange('trial_date_end')
    def _onchange_contract_approved_functionality_trial_date_end(self):
        line_ids = []
        for line_id in self.contract_log_line_ids:
            if isinstance(line_id.id, int):
                line_ids.append((4,line_id.id))
             
        if self.trial_date_end:
            context = self._context
            current_uid = context.get('uid')
            user = self.env['res.users'].browse(current_uid)
             
            original_val_trial_date_end = self._origin.trial_date_end
            for loop in self:
                if loop.trial_date_end:
                    if loop.trial_date_end != original_val_trial_date_end:
                        
                        vals = ({
                                    'field':"Trial Period End Date",
                                    'user_id':user.id,
                                    'date':datetime.today(),
                                    'original_value':original_val_trial_date_end,
                                    'change_value':loop.trial_date_end,
                          
                                    })
                        line_ids.append((0, 0, vals))
                        loop.update({'contract_log_line_ids': line_ids})
                    else:
                        loop.update({'contract_log_line_ids': line_ids}) 
                        
    @api.onchange('date_start')
    def _onchange_contract_approved_functionality_date_start(self):
        line_ids = []
        for line_id in self.contract_log_line_ids:
            if isinstance(line_id.id, int):
                line_ids.append((4,line_id.id))
             
        if self.date_start:
            context = self._context
            current_uid = context.get('uid')
            user = self.env['res.users'].browse(current_uid)
             
            original_val_date_start = self._origin.date_start
            for loop in self:
                if loop.date_start:
                    if loop.date_start != original_val_date_start:
                        
                        vals = ({
                                    'field':"Duration Start",
                                    'user_id':user.id,
                                    'date':datetime.today(),
                                    'original_value':original_val_date_start,
                                    'change_value':loop.date_start,
                          
                                    })
                        line_ids.append((0, 0, vals))
                        loop.update({'contract_log_line_ids': line_ids})
                    else:
                        loop.update({'contract_log_line_ids': line_ids})    
          
    @api.onchange('date_end')
    def _onchange_contract_approved_functionality_date_end(self):
        line_ids = []
        for line_id in self.contract_log_line_ids:
            if isinstance(line_id.id, int):
                line_ids.append((4,line_id.id))
             
        if self.date_end:
            context = self._context
            current_uid = context.get('uid')
            user = self.env['res.users'].browse(current_uid)
             
            original_val_date_end = self._origin.date_end
            for loop in self:
                if loop.date_end:
                    if loop.date_end != original_val_date_end:
                        
                        vals = ({
                                    'field':"Duration End",
                                    'user_id':user.id,
                                    'date':datetime.today(),
                                    'original_value':original_val_date_end,
                                    'change_value':loop.date_end,
                          
                                    })
                        line_ids.append((0, 0, vals))
                        loop.update({'contract_log_line_ids': line_ids})
                    else:
                        loop.update({'contract_log_line_ids': line_ids})   
                        
                        
    @api.onchange('type_id')
    def _onchange_contract_approved_functionality_type_id(self):
        line_ids = []
        for line_id in self.contract_log_line_ids:
            if isinstance(line_id.id, int):
                line_ids.append((4,line_id.id))
             
        if self.type_id:
            context = self._context
            current_uid = context.get('uid')
            user = self.env['res.users'].browse(current_uid)
             
            original_val_type_id = self._origin.type_id
            for loop in self:
                if loop.type_id:
                    if loop.type_id.id != original_val_type_id.id:
                        
                        vals = ({
                                    'field':"Contract Type",
                                    'user_id':user.id,
                                    'date':datetime.today(),
                                    'original_value':original_val_type_id.name,
                                    'change_value':loop.type_id.name,
                          
                                    })
                        line_ids.append((0, 0, vals))
                        loop.update({'contract_log_line_ids': line_ids})
                    else:
                        loop.update({'contract_log_line_ids': line_ids})   
    
    @api.onchange('draw_type_id')
    def _onchange_contract_approved_functionality_draw_type_id(self):
        line_ids = []
        for line_id in self.contract_log_line_ids:
            if isinstance(line_id.id, int):
                line_ids.append((4,line_id.id))
             
        if self.draw_type_id:
            context = self._context
            current_uid = context.get('uid')
            user = self.env['res.users'].browse(current_uid)
             
            original_val_draw_type_id = self._origin.draw_type_id
            for loop in self:
                if loop.draw_type_id:
                    if loop.draw_type_id.id != original_val_draw_type_id.id:
                        
                        vals = ({
                                    'field':"Draw Type",
                                    'user_id':user.id,
                                    'date':datetime.today(),
                                    'original_value':original_val_draw_type_id.draw_type,
                                    'change_value':loop.draw_type_id.draw_type,
                          
                                    })
                        line_ids.append((0, 0, vals))
                        loop.update({'contract_log_line_ids': line_ids})
                    else:
                        loop.update({'contract_log_line_ids': line_ids})                                                                                                                                                                                       
                        
#  
    @api.multi
    @api.depends('date_end')
    def _compute_notice_day(self):
        for line in self:
            if line.date_end:
                current_date = date.today()
                end_date = datetime.strptime(line.date_end, "%Y-%m-%d")
                end_date = end_date.date()
                if end_date >= current_date:
                    day = end_date - current_date
                    line.notice_end = day.days
                else:
                    line.notice_end = 0

    @api.multi
    def set_draft(self):       
        self.state='draft'
               
    @api.model
    def create(self, vals):
        current_date = date.today()
        notice_days=False
        if vals.get('date_end'):            
            date_end = datetime.strptime(vals.get('date_end'), "%Y-%m-%d").date()
            if vals.get('notice'):
                notice_days = date_end - timedelta(days=vals.get('notice'))
            
             
        if vals.get('date_end'):
            if vals.get('date_end') >= str(current_date) :
                vals['state'] = 'open'   
                
                if notice_days:
                    if current_date >= notice_days:               
                        vals['state'] = 'pending'   
                        
            elif vals.get('date_end') < str(current_date):
                vals['state'] = 'close'
        else:
            if vals.get('date_start') <= str(current_date) :
                vals['state'] = 'open' 
            elif vals.get('date_start') > str(current_date):
                vals['state'] = 'draft' 

            if notice_days:
                if current_date >= notice_days:               
                    vals['state'] = 'pending' 
     
        prefix_contract = self.env['hr.contract.type'].search([('id', '=', vals.get('type_id'))]).prefix      
        contracts_count = self.env['hr.contract'].search_count([('employee_id', '=', vals.get('employee_id'))])
                
        if prefix_contract:
            name = self.env['hr.employee'].search([('id', '=', vals.get('employee_id'))]).name
            if name:
                vals["name"] = prefix_contract + ":" + name 
        else:
            raise ValidationError(_('Please update prefix in contract types'))
        
              
        if contracts_count>=1 :
            previous_contracts = self.env['hr.contract'].search([('employee_id', '=', vals.get('employee_id'))])
            date_start = datetime.strptime(vals.get('date_start'), '%Y-%m-%d').date()
            
            if vals.get('date_end') or vals.get('date_start'):  
                date_end =''
                if vals.get('date_end'):
                    date_end = datetime.strptime(vals.get('date_end'), '%Y-%m-%d').date()
        
                for contract in previous_contracts:
                    if contract.date_end:
                        contract_end = datetime.strptime(contract.date_end, '%Y-%m-%d').date()
                    else:
                        contract_end = False

                    if contract.date_start:
                        contract_start = datetime.strptime(contract.date_start, '%Y-%m-%d').date()
                    else:
                        contract_start = False
                    if date_end:
                        if contract_start:
                            if contract_start >= date_start and contract_start <= date_end :
                                raise UserError(_('Active Contract already exists for this employee for the contract period'))
                        if contract_end:
                            if contract_end >= date_start and contract_end <= date_end :
                                raise UserError(_('Active Contract already exists for this employee for the contract period'))
                            
                    if vals.get('date_start'): 
                        if vals.get('date_start') <= str(current_date):
                                raise UserError(_('Active Contract already exists for this employee for the contract period'))
                                                 
                                        
        if 'contract_job_ids' in vals:
            for c_vals in vals['contract_job_ids']:
                if c_vals[2]['is_main_job']:
                    vals['job_seniority_title'] = c_vals[2]['seniority_id']
                    
                
                    
        terminate_employee = self.env['hr.employee'].search([('id', '=', vals.get('employee_id'))])
        for temp in terminate_employee:
            if temp.termination_date < str(current_date):
                temp.state='close' 
            if temp.termination_date:
                raise ValidationError(_('This employee is terminated.you cannot create contract for this employee'))  
              
        res = super(HrContract, self).create(vals)
        
        
        if vals.get('type_id'):
            res.employee_id.employment_status = vals['type_id']     
            
        if vals.get('date_start'):
            res.employee_id.start_date = vals['date_start']        
            
        if vals.get('type'): 
            res.employee_id.termination_type=vals.get('type')
            
        if vals.get('reason'): 
            res.employee_id.termination_reason=vals.get('reason')
        
        
        res.employee_id.job_id = res.job_id.id
        res.employee_id.job_seniority_title = res.job_seniority_title
        res.employee_id.pay_type = res.salary_computation_method
        
        
                
        template_sr = self.env['ir.values'].search([('name', '=', 'contract_create')])        
        if not template_sr:            
            raise ValidationError(_('Please Select Contract Create Email Template in Configuration'))  
        else:        
            temp_id = template_sr.value_unpickle           
            template_id = self.env['mail.template'].search([('id', '=', int(temp_id))])
            
            if template_id:
                template_id.send_mail(res.id, force_send=True)  
                
        return res
    
   
    
    @api.multi
    def write(self, vals):
        print vals
        print self.contract_job_ids.user_approved_id.name
        state=''
        if vals.get('state'):
            if vals.get('state')=='draft':
                state='draft'
                
        if vals.get('type_id'):  
            prefix_contract = self.env['hr.contract.type'].search([('id', '=', vals.get('type_id'))]).prefix  
            if prefix_contract:
                name = self.employee_id.name
                if name:
                    vals["name"] = prefix_contract + ":" + name 
            else:
                raise ValidationError(_('Please update prefix in contract types'))
        
        current_date = date.today()
        contracts_count = self.env['hr.contract'].search_count([('employee_id', '=', self.employee_id.id),('id', '!=', self.id)])

           
        if vals.get('date_start'):
            date_start = datetime.strptime(vals.get('date_start'), '%Y-%m-%d').date()
        else:
            date_start = datetime.strptime(self.date_start, '%Y-%m-%d').date()
        if vals.get('date_end'):
            date_end = datetime.strptime(vals.get('date_end'), '%Y-%m-%d').date()
        elif self.date_end:
            date_end = datetime.strptime(self.date_end, '%Y-%m-%d').date()  
        else:
            date_end=False
            
        if contracts_count>=1:
            previous_contracts = self.env['hr.contract'].search([('employee_id', '=', self.employee_id.id)])
            
            for contract in previous_contracts:
                
                if contract.date_end:
                    contract_end = datetime.strptime(contract.date_end, '%Y-%m-%d').date()
                else:
                    contract_end = False
                if contract.date_start:
                    contract_start = datetime.strptime(contract.date_start, '%Y-%m-%d').date()
                else:
                    contract_start = False

                if date_end:
                    if contract_start:
                        if contract_start >= date_start and contract_start <= date_end:
                            raise UserError(_('Active Contract already exists for this employee for the contract period'))
                    if contract_end:
                        if contract_end >= date_start and contract_end <= date_end:
                            raise UserError(_('Active Contract already exists for this employee for the contract period'))
                         
                if vals.get('date_start'): 
                    if vals.get('date_start') <= str(current_date):
                        raise UserError(_('Active Contract already exists for this employee for the contract period'))
               
               
        if vals.get('type_id'):
            if vals.get('employee_id'):
                prefix_contract = self.env['hr.contract.type'].search([('id', '=', vals.get('type_id'))]).prefix
                emp = self.env['hr.employee'].search([('id', '=', vals.get('employee_id'))])
                contracts_count = self.env['hr.contract'].search_count([('employee_id', '=', vals.get('employee_id'))])
                if emp:
                    vals["name"] = prefix_contract + ":" + emp.name
                

        logs = {}
        logs['contract_log_line_id'] = self.id
        logs['user_id'] = self.env.user.id
        logs['employee_id'] = self.employee_id.id
        logs['date'] = datetime.today()
        
#         if vals.get('wage'):
#             if float(self.wage)!=float(vals['wage']):
#                 logs['field'] = 'Wage'
#                 logs['original_value'] = self.wage
#                 logs['change_value'] = float(vals['wage'])
#                 if logs['original_value'] != logs['change_value']:
#                     self.env['hr.contract.line.log'].create(logs)
            
        if vals.get('contract_job_ids'):
            logs['field'] = 'Job seniority title'
            logs['original_value'] = self.job_seniority_title.name
            
            if 'user_approved_id' in vals['contract_job_ids'][0][2]:
                logs['approved_by'] = vals['contract_job_ids'][0][2]['user_approved_id']
            else:
                logs['approved_by'] = self.contract_job_ids.user_approved_id.id 
                
            if 'reason_approved' in vals['contract_job_ids'][0][2]: 
                logs['reason'] = vals['contract_job_ids'][0][2]['reason_approved']
            else:
                logs['reason'] = self.contract_job_ids.reason_approved    
           
            vals_job = {}
            vals_job['job_seniority_title'] = 0      
            con_id = 0
            for c_vals in vals['contract_job_ids']:
                if c_vals[2] != False:
                    if 'is_main_job' in c_vals[2]:
                        if c_vals[2]['is_main_job'] == True:
                            con_id = c_vals[1]
                            if 'seniority_id' in c_vals[2]:
                                vals_job['job_seniority_title'] = c_vals[2]['seniority_id']
                            else:
                                job_list = self.env['hr.contract.job'].search([('id', '=', c_vals[1])]) 
                                vals_job['job_seniority_title'] = job_list.seniority_id.id
                    elif 'seniority_id' in c_vals[2]:
                        job_list = self.env['hr.contract.job'].search([('id', '=', c_vals[1])])
                        if job_list.is_main_job == True:
                            vals_job['job_seniority_title'] = c_vals[2]['seniority_id']
                
            if vals_job['job_seniority_title'] != 0:
                vals['job_seniority_title'] = vals_job['job_seniority_title']
                if self.job_seniority_title.id != vals['job_seniority_title']:
                    if con_id != 0:
                        logs['change_value'] = self.env['hr.contract.job'].search([('id', '=', con_id)]).seniority_id.name
                    else:
                        logs['change_value'] = self.env['hr.job.seniority.title'].search([('id', '=', vals['job_seniority_title'])]).name
                        
                    if logs['original_value'] != logs['change_value']:
                        
                        self.env['hr.contract.line.log'].create(logs)
                    
        if vals.get('contract_job_ids'):
            if 'user_approved_id' in vals['contract_job_ids'][0][2]: 
                logs['approved_by'] = vals['contract_job_ids'][0][2]['user_approved_id']
            else:
                logs['approved_by'] = self.contract_job_ids.user_approved_id.id 
                
            if 'reason_approved' in vals['contract_job_ids'][0][2]: 
                logs['reason'] = vals['contract_job_ids'][0][2]['reason_approved']
            else:
                logs['reason'] = self.contract_job_ids.reason_approved    
            logs['field'] = 'Job'
            logs['original_value'] = self.job_id.name
            for c_vals in vals['contract_job_ids']:
                if c_vals[2] != False:
                    if 'is_main_job' in c_vals[2]:
                        if c_vals[2]['is_main_job'] == True:
                            if 'job_id' in c_vals[2]:
                                logs['change_value'] = c_vals[2]['job_id']
                            else:
                                logs['change_value'] = self.env['hr.contract.job'].search([('id', '=', c_vals[1])]).job_id.name
                                                        
                            if logs['original_value'] != logs['change_value']:
                                self.env['hr.contract.line.log'].create(logs)
                    elif 'job_id' in c_vals[2]:
                        row_list = self.env['hr.contract.job'].search([('id', '=', c_vals[1])])
                        if row_list.is_main_job == True:
                            logs['change_value'] = self.env['hr.job'].search([('id', '=', c_vals[2]['job_id'])]).name
                            if logs['original_value'] != logs['change_value']:
                                self.env['hr.contract.line.log'].create(logs)
                            
            
        if vals.get('contract_job_ids'):
            if 'user_approved_id' in vals['contract_job_ids'][0][2]: 
                logs['approved_by'] = vals['contract_job_ids'][0][2]['user_approved_id']
            else:
                logs['approved_by'] = self.contract_job_ids.user_approved_id.id 
                
            if 'reason_approved' in vals['contract_job_ids'][0][2]: 
                logs['reason'] = vals['contract_job_ids'][0][2]['reason_approved']
            else:
                logs['reason'] = self.contract_job_ids.reason_approved    
            today = fields.Date.today()
            logs['field'] = 'Hourly Rate'
            for contract in self.contract_job_ids:
                logs['original_value'] = contract.hourly_rate
                for c_vals in vals['contract_job_ids']:
                    if c_vals[2]!=False:
                        if 'hourly_rate_class_id' in c_vals[2]:
                            hourly_rate_class_id = c_vals[2].get('hourly_rate_class_id')
                            if hourly_rate_class_id and \
                                self.salary_computation_method == 'hourly': 
                                    rate_class = self.env['hr.hourly.rate.class'].browse(hourly_rate_class_id)
                                    rates = [
                                        r for r in rate_class.line_ids
                                        if(r.date_start <= today and (not r.date_end or
                                                                      today <= r.date_end))]
                                    hourly_rate = rates and rates[0].rate or 0
                            else:
                                hourly_rate = False
                                 
                            logs['change_value'] = hourly_rate
                            if float(contract.hourly_rate)!=float(hourly_rate):
                                self.env['hr.contract.line.log'].create(logs)
    
                                

#         if vals.get('salary_computation_method'):
#             logs['field'] = 'Pay Type'
#             logs['original_value'] = self.salary_computation_method   
#             logs['change_value'] = vals['salary_computation_method']
#             if logs['original_value'] != logs['change_value']:
#                 self.env['hr.contract.line.log'].create(logs)
        
#         if vals.get('type_id'):
#             logs['field'] = 'Contract Type'
#             logs['original_value'] = self.type_id.name                 
#             logs['change_value'] = self.env['hr.contract.type'].search([('id', '=', vals.get('type_id'))]).name
#             if logs['original_value'] != logs['change_value']:
#                 self.env['hr.contract.line.log'].create(logs)
            
#         if vals.get('leave_holiday_plan'):
#             logs['field'] = 'Leave Plan'
#             logs['original_value'] = self.leave_holiday_plan.name                 
#             logs['change_value'] = self.env['hr.contract.leave.holiday.plan'].search([('id', '=', vals.get('leave_holiday_plan'))]).name
#             if logs['original_value'] != logs['change_value']:
#                 self.env['hr.contract.line.log'].create(logs)
            
#         if vals.get('schedule_pay'):
#             logs['field'] = 'Schedule Pay'
#             logs['original_value'] = self.schedule_pay                 
#             logs['change_value'] = vals.get('schedule_pay')
#             if logs['original_value'] != logs['change_value']:
#                 self.env['hr.contract.line.log'].create(logs)
            
            
#         if vals.get('trial_date_start'):
#             logs['field'] = 'Trial Period Start Date'
#             logs['original_value'] = self.trial_date_start                 
#             logs['change_value'] = vals.get('trial_date_start')
#             if logs['original_value'] != logs['change_value']:
#                 self.env['hr.contract.line.log'].create(logs)
            
#         if vals.get('trial_date_end'):
#             logs['field'] = 'Trial Period End Date'
#             logs['original_value'] = self.trial_date_end                 
#             logs['change_value'] = vals.get('trial_date_end')
#             if logs['original_value'] != logs['change_value']:
#                 self.env['hr.contract.line.log'].create(logs)
#             
#         if vals.get('date_start'):
#             logs['field'] = 'Duration Start'
#             logs['original_value'] = self.date_start                 
#             logs['change_value'] = vals.get('date_start')
#             if logs['original_value'] != logs['change_value']:
#                 self.env['hr.contract.line.log'].create(logs)
            
#         if vals.get('date_end'):
#             logs['field'] = 'Duration End'
#             logs['original_value'] = self.date_end                 
#             logs['change_value'] = vals.get('date_end')
#             if logs['original_value'] != logs['change_value']:
#                 self.env['hr.contract.line.log'].create(logs)
            
#         if vals.get('payout_delay'):
#             logs['field'] = 'Payout Delay'
#             logs['original_value'] = self.payout_delay                 
#             logs['change_value'] = vals.get('payout_delay')
#             if logs['original_value'] != logs['change_value']:
#                 self.env['hr.contract.line.log'].create(logs)
#             
#         if vals.get('draw_type_id'):
#             logs['field'] = 'Draw type'
#             logs['original_value'] = self.draw_type_id.code                 
#             logs['change_value'] = self.env['hr.contract.draw.type'].search([('id', '=', vals.get('draw_type_id'))]).code
#             if logs['original_value'] != logs['change_value']:
#                 self.env['hr.contract.line.log'].create(logs)         
                                                    
            
#         if vals.get('staff_bonus_ids'):
#             logs['field'] = 'Rate' 
#             logs['original_value'] = self.staff_bonus_ids.rate_id
#             for s_vals in vals['staff_bonus_ids']:
#                 if s_vals[2]!=False:
#                     if 'rate_id' in s_vals[2]:
#                         logs['change_value'] = float(s_vals[2].get('rate_id'))
#                         self.env['hr.contract.line.log'].create(logs)
            
        
        start_date=end_date=notice_days=notice_days_date=False
       
        if vals.get('notice'):
            notice_days = vals.get('notice')
        elif self.notice:
            notice_days = self.notice    
        
        if vals.get('date_end'):            
            if vals.get('date_end')==False:
                end_date=None
            else:
                end_date=vals.get('date_end')    
        elif self.date_end:
            end_date=self.date_end
            
        if vals.get('date_start'):
            start_date=vals.get('date_start')
        elif self.date_start:
            start_date=self.date_start
                        
        if end_date: 
            notice_days_date = date_end - timedelta(days=notice_days) 
            if start_date > str(current_date):
                vals['state'] = 'draft' 
            elif end_date < str(current_date):
                vals['state'] = 'close'
            elif end_date >= str(current_date) :
                vals['state'] = 'open'  
                if notice_days_date:
                    if current_date >= notice_days_date:               
                        vals['state'] = 'pending'   
        else:
            if start_date <= str(current_date) :
                vals['state'] = 'open' 
            elif start_date > str(current_date):
                vals['state'] = 'draft' 

#             if notice_days_date:
#                 if current_date >= notice_days_date:               
#                     vals['state'] = 'pending'   
          
        if self.employee_id.termination_date:  
            if self.employee_id.termination_date <= str(current_date):
                vals['state']='close' 
              
         
        if state!='':
            vals['state']=state
            
            
    
        res = super(HrContract, self).write(vals)
        
        for rec in self:
            if vals.get('date_start'):
                rec.employee_id.start_date = vals['date_start'] 
                 
            if vals.get('type_id'):
                rec.employee_id.employment_status = vals['type_id']         
              
            if vals.get('type'): 
                rec.employee_id.termination_type=vals.get('type')
                 
            if vals.get('reason'): 
                rec.employee_id.termination_reason=vals.get('reason') 
                       
        
        emp_id = self.env['hr.contract'].search([('id', '=', self.id)])
        employee_id = self.env['hr.employee'].search([('id', '=', self.employee_id.id)])
        
        if employee_id:
            employee_id[0].pay_type = emp_id[0].salary_computation_method
            employee_id[0].job_seniority_title = emp_id[0].job_seniority_title

        for vals_list in emp_id.contract_job_ids:            
            if vals_list.is_main_job:                
                emp_id.employee_id.job_id = vals_list.job_id.id

        return res     

    @api.multi
    def update_employee(self):
        contract_log_obj = self.env['hr.contract.line.log'].search([])
        for rec in contract_log_obj:
            if rec.contract_log_line_id:
                rec.employee_id = rec.contract_log_line_id.employee_id
  

    @api.constrains('date_start', 'date_end')
    def _check_dates(self):
        if self.date_end:
            if self.filtered(lambda c: c.date_end and c.date_start > c.date_end):
                raise ValidationError(_('Contract start date must be less than contract end date.')) 

    @api.constrains('trial_date_start', 'trial_date_end')
    def _check_dates_trial(self):
        if self.filtered(lambda c: c.trial_date_end and c.trial_date_start > c.trial_date_end):
            raise ValidationError(_('Please check trial period date'))
        
        
    @api.constrains('date_start', 'trial_date_end', 'trial_date_start')
    def _check_dates_duration_start(self):
        date_today = datetime.strptime(fields.Date.context_today(self), '%Y-%m-%d')
               
#         if self.trial_date_start:       
#             if self.filtered(lambda c: c.date_start and c.trial_date_start > c.date_start)  :
#                 raise ValidationError(_('Please check duration date.'))
            
        if self.trial_date_end:        
            if self.filtered(lambda c: c.date_start and c.date_start >= c.trial_date_end)  :
                raise ValidationError(_('Please check duration date.'))
                        
#         if self.trial_date_start:
#             if self.filtered(lambda c: c.date_start and c.trial_date_start > c.date_start):
#                 raise ValidationError(_('Please check duration date.'))       
           
         
    @api.multi
    def cron_contract_daily(self):
        current_date = datetime.today().date()
        contract_daily = self.env['hr.contract'].search([('state', 'in', ['draft', 'open', 'pending', 'close'])])

        template_id = self.env.ref('vitalpet_contract_enhancements.gurantee_to_production').id
        mail_template = self.env['mail.template'].browse(template_id)


        for daily in contract_daily:
            if daily.date_end and daily.notice:
                date_start = datetime.strptime(daily.date_start, "%Y-%m-%d").date()
                date_end = datetime.strptime(daily.date_end, "%Y-%m-%d").date()
                notice_days = date_end - timedelta(days=daily.notice)
            else:
                notice_days = False

                if date_end:
                    if date_start <= current_date and date_end >= current_date:
                        daily.write({"state":"open"})
                    if date_end < current_date: 
                        daily.write({"state":"close"})
                else:
                    if date_start <= current_date:
                        daily.write({"state":"open"})
                    else:
                        daily.write({"state":"draft"})
                
                if notice_days: 
                    if current_date > notice_days:
                        daily.write({"state":"pending"})
                else:
                    if date_start <= current_date:
                        daily.write({"state":"open"})
                    else:
                        daily.write({"state":"draft"})  
                                      
                if daily.employee_id.termination_date <= str(current_date):
                    daily.write({"state":"close"}) 

        contract_obj = self.env['hr.contract'].search([('state','!=','close')])
        for value in contract_obj:
            if value.trial_date_end:
                trial_end_date = datetime.strptime(value.trial_date_end, "%Y-%m-%d").date()
                if trial_end_date > current_date:
                    difference = trial_end_date - current_date
                    if mail_template:
                        if difference.days == 30:
                            mail_template.with_context(notice_days=difference.days).send_mail(value.id, force_send=True)
                        if difference.days == 60:
                            mail_template.with_context(notice_days=difference.days).send_mail(value.id, force_send=True)
                        if difference.days == 90:
                            mail_template.with_context(notice_days=difference.days).send_mail(value.id, force_send=True)
                        
                
        return True 
                
    @api.multi
    def cron_contract_weekly(self):
        current_date = datetime.today().date()
        contract_daily = self.env['hr.contract'].search([('state', 'in', ['pending'])])
      
        for daily in contract_daily:
            if daily.state == "pending":
                if daily.notice_end in [30,60,90]:
                    template_sr = self.env['ir.values'].search([('name', '=', 'notice_email_manager')])
                    if template_sr:      
                        temp_id = template_sr.value_unpickle   
                        template_id = self.env['mail.template'].search([('id', '=', int(temp_id))])
                    if template_id:
                        template_id.send_mail(daily.id, force_send=True)
                     
                    template_sr_2 = self.env['ir.values'].search([('name', '=', 'notice_email_hr')])   
                    if template_sr_2:      
                        temp_id_2 = template_sr.value_unpickle           
                        template_id_2 = self.env['mail.template'].search([('id', '=', int(temp_id_2))])
                    if template_id_2:
                        template_id_2.send_mail(daily.id, force_send=True) 
                    
        return True 
     
    @api.onchange('production_basis')
    def _onchange_production_basis(self): 
        if self.production_basis:
            self.annual_draw = self.production_basis * self.production_rate * self.discount_rate
            
    @api.onchange('production_rate')
    def _onchange_production_rate(self): 
        if self.production_rate:
            self.annual_draw = self.production_basis * self.production_rate * self.discount_rate
            
    @api.onchange('discount_rate')
    def _onchange_discount_rate(self): 
        if self.discount_rate:
            self.annual_draw = self.production_basis * self.production_rate * self.discount_rate
                
                
    @api.multi
    def update_wage(self):
        for emp in self:
            annual_draw = emp.production_basis * emp.production_rate * emp.discount_rate
            emp.annual_draw=annual_draw
            if emp.salary_computation_method=="yearly":
                emp.wage=emp.annual_draw
#         self.write({'annual_draw':annual_draw})   
        

class HrContractType(models.Model):
    _inherit = "hr.contract.type"  
        
    prefix = fields.Char(string="Prefix")
       
class HrContractLinesLog(models.Model):
    _name = "hr.contract.line.log"
    
    _rec_name = 'contract_log_line_id'
     
    user_id = fields.Many2one('res.users', string='User')
    change_value = fields.Char(string="Changed Value")
    reason = fields.Char( string="Reason")
    type = fields.Many2one('termination.type', string="Termination Type")
    approved_by = fields.Many2one('res.users', string='Approved By')
    date = fields.Datetime(string="Date") 
    original_value = fields.Char(string="Original Value") 
    field = fields.Char(string="Field")
    contract_log_line_id = fields.Many2one('hr.contract', string="Contract log line")
    employee_id = fields.Many2one('hr.employee', realated='contract_log_line_id.employee_id', string="Employee")
    date_create = fields.Date('Date create', default=fields.Datetime.now)


    @api.model
    def create(self, vals):
        res = super(HrContractLinesLog, self).create(vals)

        template_sr = self.env['ir.values'].search([('name', '=', 'contract_change')])
        if not template_sr:            
            raise ValidationError(_('Please Select Contract Create Email Template in Configuration'))  
        else:
            temp_id = template_sr.value_unpickle           
            template_id = self.env['mail.template'].search([('id', '=', int(temp_id))])

            if template_id and res.change_value != False:
                template_id.send_mail(res.id, force_send=True)

        return res

class HrContractJob(models.Model):
    _inherit = 'hr.contract.job'
    
    user_approved_id= fields.Many2one("res.users",string='Approved By')
    reason_approved= fields.Char("Reason")
    

    def create(self,vals):
        res = super(HrContractJob, self).create(vals)

        if vals.get('job_id') and vals.get('seniority_id'):
            if vals.get('is_main_job') == False:

                log_obj = self.env['hr.contract.line.log'].search([('employee_id','=',res.contract_id.employee_id.id)],limit=1)

                template_sr = self.env['ir.values'].search([('name', '=', 'contract_change')])
                if not template_sr:            
                    raise ValidationError(_('Please Select Contract Create Email Template in Configuration'))  
                else:
                    temp_id = template_sr.value_unpickle           
                    template_id = self.env['mail.template'].search([('id', '=', int(temp_id))])

                    job_obj = self.env['hr.job'].search([('id','=',int(vals.get('job_id')))])
                    seniority_obj = self.env['hr.job.seniority.title'].search([('id','=',int(vals.get('seniority_id')))])

                    if template_id:
                        template_id.with_context({'job':job_obj.name,'seniority':seniority_obj.name}).send_mail(log_obj.id, force_send=True)

        return res
    

    def write(self,vals):
        res = super(HrContractJob, self).write(vals)

        if vals.get('job_id') or vals.get('seniority_id'):
            if self.is_main_job == False:

                log_obj = self.env['hr.contract.line.log'].search([('employee_id','=',self.contract_id.employee_id.id)],limit=1)

                template_sr = self.env['ir.values'].search([('name', '=', 'contract_change')])
                if not template_sr:            
                    raise ValidationError(_('Please Select Contract Create Email Template in Configuration'))  
                else:
                    temp_id = template_sr.value_unpickle           
                    template_id = self.env['mail.template'].search([('id', '=', int(temp_id))])

                    job_obj = self.env['hr.job'].search([('id','=',self.job_id.id)])
                    seniority_obj = self.env['hr.job.seniority.title'].search([('id','=',self.seniority_id.id)])

                    if template_id:
                        template_id.with_context({'job':job_obj.name,'seniority':seniority_obj.name}).send_mail(log_obj.id, force_send=True)

        return res

    
class Company(models.Model):
    _inherit = 'res.company'  

    company_id = fields.Many2one('res.company', "Contract Company", default=lambda self: self.env.user.company_id.id, readonly=True)
    payroll_company = fields.Boolean(string="Is a Payroll Company?")
    manager_user_id = fields.Many2one('res.users', string="HR Manager")
    designee_user_id = fields.Many2one('res.users', string="HR Manager Designee")
    
       
    
class HrContractEmployeeConfiguration(models.TransientModel):
    _name = "hr.contract.employee.configuration"
    _inherit = 'res.config.settings'

    _rec_name = 'company_id'

    
    contract_create = fields.Many2one('mail.template', string="Contract Create Email Template", store=True)
    contract_change = fields.Many2one('mail.template', string="Contract Change Email Template", store=True)
    notice_email_manager = fields.Many2one('mail.template', string="Notice Email Template - Manager", store=True)
    notice_email_hr = fields.Many2one('mail.template', string="Notice Email Template - HR Manager", store=True)
    company_id = fields.Many2one('res.company', "Company", default=lambda self: self.env.user.company_id.id, readonly=True, store=True)
    payroll_company = fields.Boolean(string="Is a Payroll Company?", related='company_id.payroll_company', store=True)
    manager_user_id = fields.Many2one('res.users', string="HR Manager", related='company_id.manager_user_id', store=True)
    designee_user_id = fields.Many2one('res.users', string="HR Manager Designee", related='company_id.designee_user_id', store=True)


    @api.model
    def get_default_contract_create(self, fields):
        res = {'contract_create': self.env['ir.values'].get_default('hr.contract', 'contract_create'),
               'contract_change': self.env['ir.values'].get_default('hr.contract', 'contract_change'),
               'notice_email_manager': self.env['ir.values'].get_default('hr.contract', 'notice_email_manager'),
               'notice_email_hr': self.env['ir.values'].get_default('hr.contract', 'notice_email_hr'),
            
             }
        return res
 
    @api.multi
    def set_default_contract_create(self):
         
        ir_values_obj = self.env['ir.values']
        if self.contract_create:
            ir_values_obj.sudo().set_default('hr.contract', "contract_create", self.contract_create.id, for_all_users=True)
        if self.contract_change:
            ir_values_obj.sudo().set_default('hr.contract', "contract_change", self.contract_change.id, for_all_users=True)
        if self.notice_email_manager:
            ir_values_obj.sudo().set_default('hr.contract', "notice_email_manager", self.notice_email_manager.id, for_all_users=True)
        if self.notice_email_hr:
            ir_values_obj.sudo().set_default('hr.contract', "notice_email_hr", self.notice_email_hr.id, for_all_users=True)
         
  