from odoo import api, fields, models, tools, _


# from odoo.exceptions import UserError, ValidationError
class EmployeeProductionLines(models.Model):
    _name = 'hr.bonus.accrual'    
    _rec_name = 'employee_id'
    _order = 'employee_id asc,production_type asc,company_id asc,date asc,payroll_period asc'
    
    payroll_period = fields.Many2one('hr.period', string='Payroll Period', domain="[('company_id','=',company_id)]")
    salary_rule = fields.Many2one('hr.salary.rule', string='Salary Rule')
    production_type = fields.Many2one('hr.production.type', string='Type')
    source = fields.Selection([('manual_entry', 'Manual Entry'), ('calculated', 'Calculated')])
    accured = fields.Float('Accured')
    paid = fields.Float('Paid')
    balance = fields.Float('Balance', compute='_compute_balance_amount', store=True)
    hr_payslip_id = fields.Many2one('hr.payslip')
    employee_id = fields.Many2one('hr.employee', "Employee")
    company_id = fields.Many2one("res.company", "Company")
    account_fiscal_periods_id = fields.Many2one('account.fiscal.period.lines', string="Fiscal Month", readonly=True)
    account_fiscal_period_week_id = fields.Many2one('account.fiscal.period.week', string="Fiscal Week", readonly=True)
    account_fiscal_periods_quarterly = fields.Char(string="Fiscal Quarter", readonly=True)
    account_fiscal_periods_year = fields.Many2one('account.fiscal.periods', string="Fiscal Year", readonly=True)
    date = fields.Date("Date")
    earned = fields.Float('Earned')
    payout = fields.Integer("Payout")
    production_line_id = fields.Many2one('hr.production.line', string="Production Line")
    payroll_period_num = fields.Integer('Payroll Period', related='payroll_period.number')
    contract_id = fields.Many2one('hr.contract', string="Contract")
    date_create = fields.Date('Date create', default=fields.Datetime.now)

    
    @api.onchange('employee_id')
    def onchange_employee(self):
        contract_obj = self.env['hr.contract'].search([('employee_id', '=', self.employee_id.id)], limit=1)
        if contract_obj:
            self.contract_id = contract_obj.id

    @api.model
    def create(self, vals):
        if vals.get('company_id') and vals.get('date'):
            company = vals.get('company_id')
            date_period = vals.get('date')
            company_id = self.env['res.company'].search([('id', '=', company)])
            account_fiscal_periods = self.env['account.fiscal.periods'].search([('calendar_type', '=', company_id.calendar_type.id)])
            tid_id = self.env['account.fiscal.period.week'].search([('account_fiscal_period_week_id', 'in', [a.id for a in account_fiscal_periods]), ('date_start', '<=', date_period), ('date_end', '>=', date_period)])
             
            vals.update({'account_fiscal_period_week_id':tid_id.id,
                         'account_fiscal_periods_id':tid_id.account_fiscal_period_id.id,
                         'account_fiscal_periods_year':tid_id.account_fiscal_period_week_id.id,
                         'account_fiscal_periods_quarterly':tid_id.account_fiscal_period_id.quarter
                         })
            print company_id
        
        res = super(EmployeeProductionLines, self).create(vals)

#         template_id = self.env.ref('vitalpet_bonus_accrual.bonus_creation_notification')
#         if template_id:
#             template_id.send_mail(res.id, force_send=True)

        return res
    
    @api.onchange('date')
    def onchange_periods(self):
        company = self.company_id
        date_period = self.date
        company_id = self.env['res.company'].search([('id', '=', company.id)])
        
        account_fiscal_periods = self.env['account.fiscal.periods'].search([('calendar_type', '=', company_id.calendar_type.id)])
        tid_id = self.env['account.fiscal.period.week'].search([('account_fiscal_period_week_id', 'in', [a.id for a in account_fiscal_periods]), ('date_start', '<=', date_period), ('date_end', '>=', date_period)])
         
        self.update({'account_fiscal_period_week_id':tid_id.id,
                     'account_fiscal_periods_id':tid_id.account_fiscal_period_id.id,
                     'account_fiscal_periods_year':tid_id.account_fiscal_period_week_id.id,
                     'account_fiscal_periods_quarterly':tid_id.account_fiscal_period_id.quarter
                     })
        
    @api.multi
    @api.depends('accured', 'paid')
    def _compute_balance_amount(self):
        for line in self:
            if line.id:
                pre_bonus_obj = self.env['hr.bonus.accrual'].search([('id','<',line.id),('employee_id','=',line.employee_id.id)])
                balance=0
                for row in pre_bonus_obj:      
                    balance+= row.earned - row.paid
                line.balance=balance+line.earned - line.paid
                
class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    
    bonus_accrual_line_ids = fields.One2many('hr.bonus.accrual', 'employee_id', string="Production")
    
    @api.multi
    def import_production(self):
        return self
    
    bonus_count = fields.Integer(compute='_compute_bonus_count', string='Bonus')
    
    def _compute_bonus_id(self):
        """ get the lastest Bonuses """
        production = self.env['hr.bonus.accrual']
        for employee in self:
            employee.contract_id = production.search([('employee_id', '=', employee.id)], order='date_start asc', limit=1)

    def _compute_bonus_count(self):
        production_data = self.env['hr.bonus.accrual'].sudo().read_group([('employee_id', 'in', self.ids)], ['employee_id'], ['employee_id'])
        result = dict((data['employee_id'][0], data['employee_id_count']) for data in production_data)
        for employee in self:
            employee.bonus_count = result.get(employee.id, 0)
    
