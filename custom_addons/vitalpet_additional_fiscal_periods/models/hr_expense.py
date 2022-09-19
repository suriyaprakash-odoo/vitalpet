import babel.dates
import datetime

from odoo import api, fields, models
from odoo.tools.translate import _
from odoo.exceptions import UserError, RedirectWarning, ValidationError


class HrExpense(models.Model):
    _inherit = 'hr.expense'
    
    account_fiscal_periods_id = fields.Many2one('account.fiscal.period.lines', string = "Fiscal Month", ondelete="restrict",track_visibility='onchange')
    account_fiscal_period_week_id = fields.Many2one('account.fiscal.period.week', string = "Fiscal Week", ondelete="restrict")
    account_fiscal_periods_quarterly = fields.Char(string = "Fiscal Quarter")
    account_fiscal_periods_year = fields.Many2one('account.fiscal.periods',string = "Fiscal Year")
    custom_calendar = fields.Boolean('Use Custom calendar',related='company_id.custom_calendar',store=True)
#     move_month_year = fields.Char("Fiscal Date", compute = '_convert_move_month_year', store=True)
#     week_of_year = fields.Char("Fiscal Week", compute = '_convert_week_of_year', store=True)

     # Get month year from account move for group by filter
# It works based on company configuration 445 or fiscal date
#     @api.one
#     @api.depends('date', 'company_id')
#     def _convert_move_month_year(self):
#         print 'to month'
#         locale = self._context.get('lang', 'en_US')
#         for line in self:
#             if line.date:
#                 company_id = ''
#                 if not line.company_id:
#     #Note: do not assign yourself product company as product
#                     if not line.product_id.company_id:
#                         raise UserError(_('Please assign company for the Product.'))
#     # Check is 445 enabled for the company
#                 if line.company_id and line.company_id.custom_calendar == False:
#     # if not 445 used for the company conver the move date to sting month_year
#                     value = datetime.datetime.strptime(line.date, '%Y-%m-%d')
#                     string_date_year = babel.dates.format_date(value, format = 'MMMM yyyy', locale = locale)
#                     line.move_month_year = string_date_year
#                 else:
#     # if 445 enabled for the company get fiscal year month and save it
#                     account_fiscal_periods = self.env['account.fiscal.periods'].search(['&', ('name', 'ilike', line.date[:4]), ('calendar_type', '=', line.company_id.calendar_type.id)])
#                     if account_fiscal_periods :
#                         # Get period based on account move line
#                         period = self.env['account.fiscal.period.lines'].search([('account_fiscal_period_id', '=', account_fiscal_periods.id), ('date_start', '<=', line.date),('date_end', '>=', line.date)])
#                         line.move_month_year = period.name
#     @api.one
#     @api.depends('date', 'company_id')
#     def _convert_week_of_year(self):
#         print 'ccccmg'
#         locale = self._context.get('lang', 'en_US')
#         for line in self:
#             if line.date:
#                 company_id = ''
#                 if not line.company_id:
#     #Note: do not assign yourself company 
#                     if not line.category_id.company_id:
#                         raise UserError(_('Please assign company for the Asset.'))
#     # Check is 445 enabled for the company
#                 if line.company_id and line.company_id.custom_calendar == False:
#     # if not 445 used for the company convert the move date to sting month_year
#                     value = datetime.datetime.strptime(line.date, '%Y-%m-%d')                   
#                     string_date_week = babel.dates.format_date(value, format = '-ww ', locale = locale)
#                     week_string = 'Week'+string_date_week 
#                     line.week_of_year = week_string
#                 else:
#     # if 445 enabled for the company get fiscal year month and save it
#                     account_fiscal_periods = self.env['account.fiscal.periods'].search(['&', ('name', 'ilike', line.date[:4]), ('calendar_type', '=', line.company_id.calendar_type.id)])
#                     if account_fiscal_periods :
#                         # Get period based on account move line                        
#                         week = self.env['account.fiscal.period.week'].search([('account_fiscal_period_week_id', '=', account_fiscal_periods.id), ('date_start', '<=', line.date),('date_end', '>=', line.date)])
#                         if week:
#                             line.week_of_year = week.name


    @api.onchange('date')
    def get_account_fiscal_periods(self):
        account_fiscal_periods = self.env['account.fiscal.periods'].search([('calendar_type', '=', self.company_id.calendar_type.id)])
        if account_fiscal_periods:
            period = self.env['account.fiscal.period.lines'].search([('account_fiscal_period_id','in',[a.id for a in account_fiscal_periods]),('date_start', '<=', self.date),('date_end', '>=', self.date)])
            if period:
                self.account_fiscal_periods_id = period.id
                self.account_fiscal_periods_quarterly = period.quarter
                self.account_fiscal_periods_year = period.account_fiscal_period_id.id
            else:
                self.account_fiscal_periods_id = ''
                self.account_fiscal_periods_quarterly = ''
                self.account_fiscal_periods_year = ''
                
            period_week = self.env['account.fiscal.period.week'].search([('account_fiscal_period_id','in',[a.id for a in account_fiscal_periods]),('date_start', '<=', self.date),('date_end', '>=', self.date)])
            if period_week:
                self.account_fiscal_period_week_id = period_week.id
            else:
                self.account_fiscal_period_week_id = ''
        return {}
    
    @api.model
    def create(self,vals):
        company = self.env['res.company'].search([('id','=',vals.get('company_id'))])
        account_fiscal_periods = self.env['account.fiscal.periods'].search([('calendar_type', '=', company.calendar_type.id)])
        if account_fiscal_periods:
            period = self.env['account.fiscal.period.lines'].search([('account_fiscal_period_id','in',[a.id for a in account_fiscal_periods]),('date_start', '<=', vals.get('date')),('date_end', '>=', vals.get('date'))])
            if period.closing_date_range == True:
                raise UserError(_('Account Period date is expired so you cannot create a record.'))
            if period:
                vals['account_fiscal_periods_id'] = period.id
                vals['account_fiscal_periods_quarterly'] = period.quarter
                vals['account_fiscal_periods_year'] = period.account_fiscal_period_id.id
            else:
                vals['account_fiscal_periods_id'] = ''
                vals['account_fiscal_periods_quarterly'] = ''
                vals['account_fiscal_periods_year'] = ''
                
            period_week = self.env['account.fiscal.period.week'].search([('account_fiscal_period_id','in',[a.id for a in account_fiscal_periods]),('date_start', '<=', vals.get('date')),('date_end', '>=', vals.get('date'))])
            if period_week:
                vals['account_fiscal_period_week_id'] = period_week.id
            else:
                vals['account_fiscal_period_week_id'] = ''
                
                
        res = super(HrExpense, self).create(vals)
        return res
    
    @api.multi
    def write(self,vals):
        for rec in self:
            account_fiscal_periods = self.env['account.fiscal.periods'].search([('calendar_type', '=', rec.company_id.calendar_type.id)])
            if account_fiscal_periods:
                period = self.env['account.fiscal.period.lines'].search([('account_fiscal_period_id','in',[a.id for a in account_fiscal_periods]),('date_start', '<=', rec.date),('date_end', '>=', rec.date)])
                if period.closing_date_range == True:
                    raise UserError(_('Account Period date is expired so you cannot create a record.'))
                if period:
                    vals['account_fiscal_periods_id'] = period.id
                    vals['account_fiscal_periods_quarterly'] = period.quarter
                    vals['account_fiscal_periods_year'] = period.account_fiscal_period_id.id
                else:
                    vals['account_fiscal_periods_id'] = ''
                    vals['account_fiscal_periods_quarterly'] = ''
                    vals['account_fiscal_periods_year'] = ''
                period_week = self.env['account.fiscal.period.week'].search([('account_fiscal_period_id','in',[a.id for a in account_fiscal_periods]),('date_start', '<=', rec.date),('date_end', '>=', rec.date)])
                if period_week:
                    vals['account_fiscal_period_week_id'] = period_week.id
                else:
                    vals['account_fiscal_period_week_id'] = ''
        res = super(HrExpense, self).write(vals)
        return res