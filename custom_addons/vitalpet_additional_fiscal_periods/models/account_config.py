# -*- coding: utf-8 -*-

from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import ValidationError
import time
from datetime import datetime,date
import datetime
from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta

class ResCompany(models.Model):
    _inherit = "res.company"
    
    calendar_type = fields.Many2one('calendar.type')
    custom_calendar = fields.Boolean()
    
    @api.multi
    def write(self,vals):
        if vals.get('custom_calendar') == False:
            vals['calendar_type'] = False
        
        res = super(ResCompany, self).write(vals)
        return res
    
    
class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    custom_calendar = fields.Boolean('Use Custom calendar',related='company_id.custom_calendar')
    calendar_type = fields.Many2one('calendar.type',related='company_id.calendar_type')
    
    


#     @api.model
#     def get_default_calender_type(self, fields):
#         IrConfigParam = self.env['ir.config_parameter']
# 
#         # we use safe_eval on the result, since the value of the parameter is a nonempty string
#         return {
#             'calender_type': safe_eval(IrConfigParam.get_param('calender_type', 'False')),
#             'from_year': safe_eval(IrConfigParam.get_param('from_year', 'False')),
#             'to_year': safe_eval(IrConfigParam.get_param('to_year', 'False')),
#         }
#  
#     @api.multi
#     def set_calender_type(self):
#         if self.calender_type == '445':
#             to_year = self.to_year+1
#             for year in range(self.from_year, to_year):
#                 account_fiscal_periods = self.env['account.fiscal.periods.type'].search([('year_selection', '=', year)])
#                 if not account_fiscal_periods:
#                     if year < 1990 or year > 9999:
#                         raise ValidationError(("Enter the correct year format (Example –2017)"))
#                     diff_days = date(year, 1, 1).weekday()
#                     # print date(year, 1, 1).weekday()
#                     # print diff_days
#                     code = ''
#                     
#                     print date(year, 1, 1).weekday()
#                     print diff_days
#                     if diff_days == 4:
#                         weeks = 53
#                     else:
#                         weeks = 52
#                     week = 1
#                     cmonth = 0
#                     # firstday = 
#                     if diff_days == 6:
#                         cday = datetime.datetime(year, 1, 1)
#                         start_date = cday
#                     else:               
#                         cday = datetime.datetime(year, 1, 1) - datetime.timedelta(days=diff_days+1)
#                         start_date = cday
#                         
#                     while(week <= weeks):
#                         if week in [1,5,9,14,18,22,27,31,35,40,44,48]:
#                             cmonth = cmonth+1
#                         else:
#                             if weeks == 53:
#                                 if week in [4,8,13,17,21,26,30,34,39,43,47,53]:
#                                     clday = cday+datetime.timedelta(days=6)  
#                             else:
#                                 if week in [4,8,13,17,21,26,30,34,39,43,47,52]:
#                                     clday = cday+datetime.timedelta(days=6)
#                         
#                         cday = cday+datetime.timedelta(days=7)
#                         week = week+1
#                     day_start = start_date.strftime('%A')
#                     day_stop = clday.strftime('%A')
#                     
#                     account_fiscal_periods_vals = {
#                         'name' : year,
#                         'active' : True,
#                         'calender_type' : True,
#                         'year_selection' : year,
#                         'date_start' : start_date,
#                         'day_start' : day_start,
#                         'date_stop' : clday,
#                         'day_stop' : day_stop,                    
#                         } 
#                     account_fical_period_new = self.env['account.fiscal.periods.type'].create(account_fiscal_periods_vals)
#                         
#         #             print self.company_id.code, company_code
#                     if diff_days == 4:
#                         weeks = 53
#                     else:
#                         weeks = 52
#                         
#                     pmonth = 0
#                     quarter_end = 1
#                     
#                     # firstday = 
#                     if diff_days == 6:
#                         cday = datetime.datetime(year, 1, 1)
#                     else:               
#                         cday = datetime.datetime(year, 1, 1) - datetime.timedelta(days=diff_days+1)
#                     week = 1
#                     period = 00
#                     ds = datetime.datetime.strptime(account_fical_period_new.date_start, '%Y-%m-%d')
#                    
#                     account_fical_period_new.account_fiscal_periods_ids = [(0, 0, {
#                             'name':  "%s %s" %  (_('Opening Period'), year),
#                             'monthly': "M1-%s" %  (year),
#                             'quarter_end': "Q1-%s" %  (year),
#                             'date_start': ds,
#                             'date_end': ds,
#                             'type_id': account_fical_period_new.id,
#                             'code' : "00/%s" % (str(year)),
#                             'closing_period': True,
#                             'active': True
#                         })]
#                     while(week <= weeks):
#                         if week in [1,5,9,14,18,22,27,31,35,40,44,48]:
#                             sday = cday.date()
#                             sweek = 1
#                             pmonth = pmonth+1
#                             clday = cday+datetime.timedelta(days=6)
#                             
#         #                     print range_id
#                             
#                         else:
#                             clday = cday+datetime.timedelta(days=6)
#                             sweek = sweek+1
#                             
#         #                     print range_id
#                             if weeks == 53:
#                                 if week in [4,8,13,17,21,26,30,34,39,43,47,53]:
#                                     clday = cday+datetime.timedelta(days=6) 
#                                     period = period + 1 
#                                    
#                                     
#                                     account_fical_period_new.account_fiscal_periods_ids =[(0, 0, {
#                                         'name': "%s/%s" %  (period,clday.strftime('%Y')),
#                                         'monthly': "M%s-%s" %  (period,clday.strftime('%Y')),
#                                         'quarter_end': "Q%s-%s" % (quarter_end,year),
#                                         'date_start': sday,
#                                         'date_end': clday,
#                                         'type_id': account_fical_period_new.id,
#                                         'code' : "%s" % (cday.strftime('%m/%Y')),
#                                         'active': True,
#                                     })]
#                                     if period % 3 == 0:
#                                         quarter_end = quarter_end+1
#                             else:
#                                 if week in [4,8,13,17,21,26,30,34,39,43,47,52]:
#                                     clday = cday+datetime.timedelta(days=6)
#                                     period = period + 1 
#                                    
#                                     account_fical_period_new.account_fiscal_periods_ids =[(0, 0, {
#                                         'name': "%s/%s" %  (period,clday.strftime('%Y')),
#                                         'monthly': "M%s-%s" %  (period,clday.strftime('%Y')),
#                                         'quarter_end': "Q%s-%s" % (quarter_end,year),
#                                         'date_start': sday,
#                                         'date_end': clday,
#                                         'type_id': account_fical_period_new.id,
#                                         'code' : "%s" % (cday.strftime('%m/%Y')),
#                                         'active': True,
#                                     })]
#                                     if period % 3 == 0:
#                                         quarter_end = quarter_end+1
#                         
#                         
#                         
#             
#                         
#                         cday = cday+datetime.timedelta(days=7)
#                         week = week+1
#                     
#                     # firstday = 
#                     if diff_days == 6:
#                         cday = datetime.datetime(year, 1, 1)
#                     else:               
#                         cday = datetime.datetime(year, 1, 1) - datetime.timedelta(days=diff_days+1)    
#                     week = 1
#                     pmonth = 0    
#                     while(week <= weeks):
#                         if week in [1,5,9,14,18,22,27,31,35,40,44,48]:
#                             sday = cday.date()
#                             sweek = 1
#                             pmonth = pmonth+1
#                             clday = cday+datetime.timedelta(days=6)
#                             range_date = self.env['account.fiscal.periods'].search([('date_start', '=', sday),('name','not ilike','opening'),('type_id','=',account_fical_period_new.id)])
#                             print range_date
#                             account_fical_period_new.account_fiscal_periods_week_ids =[(0, 0, {
#                                 'name': "%sW- %s/%s" %  (sweek,pmonth,clday.strftime('%Y')),
#                                 'date_start': cday,
#                                 'date_end': clday,
#                                 'account_fiscal_periods_id': range_date.id,
#                                 'week_no': "W-%s" % (week),
#                                 'type_id': account_fical_period_new.id,
#                                 'code' : "%sW-%s/%s%s" % (sweek,pmonth,clday.strftime('%Y'),code),
#                                 'active': True,
#                             })]
#                             
#                             
#                         else:
#                             clday = cday+datetime.timedelta(days=6)
#                             sweek = sweek+1
#                             range_date = self.env['account.fiscal.periods'].search([('date_start', '=', sday),('name','not ilike','opening'),('type_id','=',account_fical_period_new.id)])
#                             print range_date
#                             account_fical_period_new.account_fiscal_periods_week_ids =[(0, 0, {
#                                 'name': "%sW- %s/%s" %  (sweek,pmonth,clday.strftime('%Y')),
#                                 'date_start': cday,
#                                 'date_end': clday,
#                                 'week_no': "W-%s" % (week),
#                                 'account_fiscal_periods_id': range_date.id,
#                                 'type_id': account_fical_period_new.id,
#                                 'code' : "%sW-%s/%s%s" % (sweek,pmonth,clday.strftime('%Y'),code),
#                                 'active': True,
#                             })]
#                         
#                         
#             
#                         
#                         cday = cday+datetime.timedelta(days=7)
#                         week = week+1
#                 
#                 
#         self.ensure_one()
#         IrConfigParam = self.env['ir.config_parameter']
#         # we store the repr of the values, since the value of the parameter is a required string
#         IrConfigParam.set_param('calender_type', repr(self.calender_type))
#         IrConfigParam.set_param('from_year', repr(self.from_year))
#         IrConfigParam.set_param('to_year', repr(self.to_year))
        
        
        
#         while(self.from_year < self.to_year)