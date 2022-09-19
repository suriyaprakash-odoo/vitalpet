# -*- coding: utf-8 -*-
# © 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import time
from datetime import datetime,date
import datetime
from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError


class AccountFiscalPeriodWeek(models.Model):
    _name = "account.fiscal.period.week"
    
#     @api.model
#     def _default_company(self):
#         return self.env['res.company']._company_default_get('account.fiscal.period.week')

    name = fields.Char(required=True, translate=True)
    week_no = fields.Char('Week')
    date_start = fields.Date(string='Start date', required=True)
    date_end = fields.Date(string='End date', required=True)
    
    active = fields.Boolean(
        help="The active field allows you to hide the Account Fiscal Period without "
        "removing it.", default=True)
    account_fiscal_period_week_id = fields.Many2one('account.fiscal.periods', 'Account Fiscal Period Week')
    account_fiscal_period_id = fields.Many2one('account.fiscal.period.lines', 'Period')

class AccountFiscalPeriods(models.Model):
    _name = "account.fiscal.periods"
    

    name = fields.Char(required=True, translate=True)
    calendar_type = fields.Many2one('calendar.type')
    account_fiscal_periods_ids = fields.One2many("account.fiscal.period.lines", 'account_fiscal_period_id', string="Periods")
    account_fiscal_period_week_ids = fields.One2many("account.fiscal.period.week", 'account_fiscal_period_week_id', string="Weeks")
    
#     date_start = fields.Date(string='Start date', required=True)
#     date_end = fields.Date(string='End date', required=True)
#     type_id = fields.Many2one(
#         comodel_name='account.fiscal.periods.type', string='Type', index=1, required=True)
#     type_name = fields.Char(
#         string='Type', readonly=True, store=True)
# #     company_id = fields.Many2one(
# #         comodel_name='res.company', string='Company', index=1,
# #         default=_default_company)
#     active = fields.Boolean(
#         help="The active field allows you to hide the Account Fiscal Period without "
#         "removing it.", default=True)
#     account_fiscal_periods_id = fields.Many2one('account.fiscal.periods.type', 'Account Fiscal Period')
#     code = fields.Char()
#     closing_period = fields.Boolean(string='Closing range')
#     quarter_end = fields.Char(string='Quarter')
#     monthly = fields.Char(string='Month')
# #     
#     _sql_constraints = [
#         ('account_fiscal_periods_uniq', 'unique (name,type_id)',
#          'A Account Fiscal Period must be unique!')]
# # 
#
    def generate_weeks(self):
        self.account_fiscal_period_week_ids.unlink();
        oldyear = 1
        for periods in self.account_fiscal_periods_ids:
            date_format = "%Y-%m-%d"
            start_date = periods.date_start
            end_date = periods.date_end
            start_date = datetime.datetime.strptime(start_date, date_format)
            end_date = datetime.datetime.strptime(end_date, date_format)
            delta = end_date - start_date
            diff_days = delta.days # that's it
            weeks = (diff_days+1) / 7
            week = 1
#             print periods.year
            newyear = periods.year
            if oldyear != newyear:
                oldyear = newyear
                week_no = 1
                pmonth = 1
            
            while(week <= weeks):
                start_week_date = start_date
                end_week_date = start_date+datetime.timedelta(days=6)
                
                self.account_fiscal_period_week_ids =[(0, 0, {
                        'week_no': "%sW- %s/%s" %  (week,pmonth,end_week_date.strftime('%Y')),
                        'name': "W-%s"% (week_no),                        
                        'date_start': start_week_date,
                        'date_end': end_week_date,
                        'account_fiscal_period_id': periods.id,
                        'active': True,
                    })]
                week_no = week_no + 1
                week = week+1
                
                start_date = start_date+datetime.timedelta(days=7)
            pmonth = pmonth+1
    @api.multi
    def get_domain(self, field_name):
        self.ensure_one()
        return [(field_name, '>=', self.date_start),
                (field_name, '<=', self.date_end)]



class AccountFiscalPeriodLines(models.Model):
    _name = 'account.fiscal.period.lines'
    
    
    name = fields.Char(string="FY Month")
    code = fields.Char(string="Code")
    quarter = fields.Char(string="FY Quarter")
    year = fields.Char(string="F Year")
    date_start = fields.Date(string="Start Date")
    date_end = fields.Date(string="End Date")
    account_fiscal_period_id = fields.Many2one('account.fiscal.periods', string="Period", ondelete='cascade')    
    closing_date_range = fields.Boolean("Closing Date Range")

    
    
    
    _sql_constraints = [
        ('account_fiscal_period_lines_uniq', 'unique (date_start,date_end,account_fiscal_period_id)',
         'A Account Fiscal Period must be unique!')]
    
    
    @api.multi
    def get_domain(self, field_name):
        self.ensure_one()
        return [(field_name, '>=', self.date_start),
                (field_name, '<=', self.date_end)]
        
        
    