from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import datetime
from dateutil.relativedelta import relativedelta

class HrproductionType(models.Model):
    _name = "hr.production.type"
    _order = 'sequence asc'
    
    
    name = fields.Char("Name")
    sequence = fields.Integer("Sequence")
    color = fields.Integer("Color Index")
    payout = fields.Integer(string="Payout")

    
class HrproductionTag(models.Model):
    _name = "hr.production.tag"
    
    name = fields.Char("Production Tag")
    active = fields.Boolean("Active")
    code = fields.Char("Code")
    sequence = fields.Integer("Sequence")
    production_type = fields.Many2one('hr.production.type', "Type")
    color = fields.Integer("Color Index")
    double_validation = fields.Boolean("Apply Double Validation")
    rate = fields.Float("Rate",digits = (12,3))
    salary_rule_id = fields.Many2one('hr.salary.rule', "Salary Rule")
    subtract_amount = fields.Boolean("Subtract Amount")
    payout = fields.Integer(string="Payout")
    deduct_draw = fields.Boolean('Deduct Draw')


class VitalpetHrProductions(models.Model):
    _name = 'hr.production'
    _inherit = ['mail.thread']
    _rec_name = "employee_id"
    
    @api.multi
    def _compute_amount(self):
        for production in self:
            if production.production_line_ids:
                tot_amt = 0.0
                for line in production.production_line_ids:
                    tot_amt += line.amount                     
                production.tot_amt = tot_amt
    
    @api.multi
    def _compute_production(self):
        for production in self:
            if production.days_worked != 0.0:
                if production.production_line_ids:
                    tot_amt = 0.0
                    for line in production.production_line_ids:
                        tot_amt += line.amount                     
                    production.production_per_day = tot_amt/production.days_worked

                
    @api.multi
    @api.depends('production_line_ids')
    def _record_count(self):
        if self.production_line_ids:
            tid = []
            for product in self:
                for product_id in product.production_line_ids:
                    tid.append(product_id.id)
            self.record_count = len(tid)
    
        
    @api.multi
    @api.depends('employee_id')
    def _active_contract(self):
        if self.employee_id:
            contract = self.env['hr.contract'].search([('employee_id','=',self.employee_id.id),('state','=','open')]).id
            self.contract_id = contract
        
    @api.multi
    @api.constrains("production_line_ids","start_date","end_date") 
    def _check_date(self):
        for rec in self:
            if rec.start_date and rec.end_date:
                for line_date in self.production_line_ids:
                    date = line_date.date 
                    if  date < self.start_date or date > self.end_date:
                        raise UserError(_('Please enter the proper date within start Date and End Date'))
    
    employee_id = fields.Many2one('hr.employee', 'Employee', required=True)
    company_id = fields.Many2one('res.company', string='Company', related="employee_id.company_id", readonly=True)
    period_id = fields.Many2one('hr.period', string='Period')
    tot_amt = fields.Float("Total Amount", compute="_compute_amount")
    start_date = fields.Date('Start Date', related="period_id.date_start")
    end_date = fields.Date('End Date', related="period_id.date_stop")
    production_line_ids = fields.One2many('hr.production.line', 'production_line_id', string="Production Details")
    contract_id = fields.Many2one('hr.contract',string="Contract",compute="_active_contract")
    state = fields.Selection([('draft', 'Draft'), ('validated', 'Validated'), ('history', 'History')], default='draft') 
    payslip_id = fields.Many2one('hr.payslip',string="Payslip")
    record_count = fields.Integer("Records", compute="_record_count")
    
    period_history=fields.Char("Period History")
    is_history=fields.Boolean("Is History")
    extra_shift=fields.Integer("Extra Shift")
    end_date_import=fields.Date("End Date")
    company_import=fields.Many2one("res.company", "Company Import")
    status = fields.Selection([('draft', 'Draft'), ('validated', 'Validated'), ('history', 'History')], default='draft')            
    days_worked = fields.Float('Days Worked')
    production_per_day = fields.Float('Production per day',compute="_compute_production")

    @api.multi        
    def validate(self):
        self.status = 'validated' 
    
        

                
class VitalpetHrProductionLine(models.Model):
    _name = 'hr.production.line'
    _inherit = ['mail.thread']
    
    _rec_name = 'job_id'
    
    job_id = fields.Many2one('hr.job', 'Job Position', required=True)
    company_id = fields.Many2one('res.company', string='Company')
    date = fields.Date('Date', required=True)
    amount = fields.Float('Amount', required=True)
    bonus_id = fields.Many2one('hr.production.tag', 'Bonus')
    production_line_id = fields.Many2one('hr.production')
    job_ids = fields.Many2many('hr.job', string="Job Position")
    bonus_ids = fields.Many2many('hr.production.tag', string="Bonus")
    employee_id = fields.Many2one('hr.employee', 'Employee', related="production_line_id.employee_id", store=True)
    payroll_period = fields.Many2one('hr.period', 'Payroll Period', related="production_line_id.period_id", store=True)
    production_type = fields.Many2one('hr.production.type', string="Production Type", related="bonus_id.production_type")
    status = fields.Selection([('validate', 'Validated'), ('non_validate', 'Draft'), ('history', 'History')], string='Status', default='non_validate')
    status_production = fields.Selection([('draft', 'Draft'), ('validated', 'Validated'), ('history', 'History')], related='production_line_id.status', string='Status Production')
    quarter = fields.Char("Fiscal Quarter")
    fin_week = fields.Many2one('account.fiscal.period.week', 'Fiscal Week')  
    fin_month = fields.Many2one('account.fiscal.period.lines', 'Fiscal Month') 
    fin_year = fields.Many2one('account.fiscal.periods', 'Fiscal Year')
    date_create = fields.Date('Date create', default=fields.Datetime.now)
    contract_id = fields.Many2one('hr.contract', string="Contract")
    pre_amount = fields.Float('Previous Amount', compute="_compute_pre_amount")
#     mail_template_id = fields.Many2one('mail.template', string="Email Template for Production", default=lambda self: self.env.ref('vitalpet_production_model.production_validation_notification'))

    @api.multi
    def _compute_pre_amount(self):
        current_date = datetime.now().date()
        i=0
        for line in self.fin_year.account_fiscal_periods_ids:
            if line.name == "M01-" + str(datetime.strptime(self.date, '%Y-%m-%d').year):
                i=1
                date_calc =  datetime.strptime(line.date_start, '%Y-%m-%d')
        if i==1:
            if date_calc:
                start_date = date_calc
                yesterday = current_date

                production_obj = self.env['hr.production.line'].search([('employee_id','=',self.employee_id.id),('company_id','=',self.company_id.id),('production_type','=',self.production_type.id),('date','>=',start_date),('date','<=',yesterday)])
                if production_obj:
                    amount = 0.00
                    for production in production_obj:
                        amount+=production.amount
                        
                    self.pre_amount = amount
    
    @api.onchange('employee_id')
    def onchange_employee(self):
        contract_obj = self.env['hr.contract'].search([('employee_id', '=', self.employee_id.id)], limit=1)
        if contract_obj:
            self.contract_id = contract_obj.id

    @api.onchange('date')
    def onchange_date(self):
        date = self.date
        company = self.env['res.company'].search([('id','=',self.company_id.id)])
        account_fiscal_periods = self.env['account.fiscal.periods'].search([('calendar_type', '=', company.calendar_type.id)])
        tid_week = self.env['account.fiscal.period.week'].search([('account_fiscal_period_week_id','in',[a.id for a in account_fiscal_periods]),('date_start', '<=', date),('date_end', '>=', date)])
        tid_period = self.env['account.fiscal.period.lines'].search([('account_fiscal_period_id','in',[a.id for a in account_fiscal_periods]),('date_start', '<=', date),('date_end', '>=', date)])
        
        self.quarter = tid_period.quarter
        self.fin_week = tid_week.id 
        self.fin_month = tid_period.id 
        self.fin_year = tid_period.account_fiscal_period_id.id
    
    @api.model
    def create(self, vals):
        if vals.get('date') and vals.get('company_id'):
            date = vals.get('date')
            company = self.env['res.company'].search([('id','=',vals.get('company_id'))])
            account_fiscal_periods = self.env['account.fiscal.periods'].search([('calendar_type', '=', company.calendar_type.id)])
            tid_week = self.env['account.fiscal.period.week'].search([('account_fiscal_period_week_id','in',[a.id for a in account_fiscal_periods]),('date_start', '<=', date),('date_end', '>=', date)])
            tid_period = self.env['account.fiscal.period.lines'].search([('account_fiscal_period_id','in',[a.id for a in account_fiscal_periods]),('date_start', '<=', date),('date_end', '>=', date)])
            
            vals.update({
                        'quarter':tid_period.quarter,
                        'fin_week':tid_week.id ,
                        'fin_month':tid_period.id ,
                        'fin_year':tid_period.account_fiscal_period_id.id , 
                        })
        res = super(VitalpetHrProductionLine, self).create(vals)
        res.status =  res.status
        return res
    
    @api.model
    def write(self, vals):
        if vals.get('date'):
            date = vals.get('date')
        else:
            date = self.date
        company = self.env['res.company'].search([('id','=',self.company_id.id)])
        account_fiscal_periods = self.env['account.fiscal.periods'].search([('calendar_type', '=', company.calendar_type.id)])
        tid_week = self.env['account.fiscal.period.week'].search([('account_fiscal_period_week_id','in',[a.id for a in account_fiscal_periods]),('date_start', '<=', date),('date_end', '>=', date)])
        tid_period = self.env['account.fiscal.period.lines'].search([('account_fiscal_period_id','in',[a.id for a in account_fiscal_periods]),('date_start', '<=', date),('date_end', '>=', date)])
        
        vals.update({
                    'quarter':tid_period.quarter,
                    'fin_week':tid_week.id ,
                    'fin_month':tid_period.id ,
                    'fin_year':tid_period.account_fiscal_period_id.id , 
                    })
                
#                 
#         if vals.get('status') == 'validate':
#             print "res called to mail"
#             template_id = self.env.ref('vitalpet_production_model.production_validation_notification')
#             if template_id: 
#                 template_id.with_context(vals_cont).send_mail(self.id, force_send=True)
        return super(VitalpetHrProductionLine, self).write(vals)
            
            
            
