from odoo import models, fields, api, _
from datetime import datetime, timedelta
import calendar
import StringIO
import xlsxwriter
from odoo.http import request

class ReportAccountFinancialReport(models.Model):
    _inherit = "account.financial.html.report"
    
    
    def get_fiscal_period_start_date(self):
        company_id = self.env.user.company_id
        account_fiscal_periods = self.env['account.fiscal.periods'].search([('calendar_type', '=',company_id.calendar_type.id)])
        if account_fiscal_periods:
            period = self.env['account.fiscal.period.lines'].search([('account_fiscal_period_id','in',[a.id for a in account_fiscal_periods]),('date_start', '<=', self.id),('date_end', '>=', self.id)])
            if period:
                return datetime.strptime(period.date_start, '%Y-%m-%d').strftime('%m/%d/%Y')

        return "No Period"
    
    def get_fiscal_period_end_date(self):
        company_id = self.env.user.company_id
        account_fiscal_periods = self.env['account.fiscal.periods'].search([('calendar_type', '=',company_id.calendar_type.id)])
        if account_fiscal_periods:
            period = self.env['account.fiscal.period.lines'].search([('account_fiscal_period_id','in',[a.id for a in account_fiscal_periods]),('date_start', '<=', self.id),('date_end', '>=', self.id)])
            if period:
                return datetime.strptime(period.date_end, '%Y-%m-%d').strftime('%m/%d/%Y')

        return "No Period"  
    
    def get_default_company(self):
        # user_obj = self.env['res.users'].browse(self.uid)
        # print user_obj.company_id.id, 'llll', user_obj.company_id.name
        return self.env.user.company_id.id


    def get_parent_company(self):
        result = {}
        allowed_lst = []
        lst = []
        lst.append(self.id)
        for loop in self.env.user.company_ids:
            allowed_lst.append(loop.id)

        company_obj = self.env['res.company']
        company_sr = company_obj.search([('parent_id', '=', self.id)])
        for loop_comp in company_sr:
            if loop_comp.id in allowed_lst:
                company_br = company_obj.search([('parent_id', '=', loop_comp.id)])
                lst.append(loop_comp.id)
                if company_br:
                    for loop_gp in company_br:
                        lst.append(loop_gp.id)         
        return lst

    def get_parent_name(self, context):
        lst = []
        parent_lst = []
        child_lst = []
        if context:
            for loop in context:
                if not loop.parent_id.id:
                    return set(loop)
                else:
                    parent_lst.append(loop.parent_id.id)
                    child_lst.append(loop.id)
        if parent_lst and child_lst:
            for loop in context:
                if parent_lst and loop.id in parent_lst:
                    lst.append(loop)
            if lst:
                if len(lst) > 1:
                    new_lst = []
                    for parent_line in lst:
                        if parent_line.parent_id in lst:
                            new_lst.append(parent_line.parent_id)
                        if not parent_line.parent_id and parent_line in lst:
                            new_lst.append(parent_line)
                    if new_lst:
                        lst = new_lst
                else:
                    lst


        if child_lst:
            for loop in context:
                if parent_lst not in child_lst and loop.id in child_lst and not loop.parent_id in lst:
                    lst.append(loop)
        return set(lst)
        
    def get_fiscal_period_quarter(self):
        result = {}
        company_id = self.env.user.company_id
        account_fiscal_periods = self.env['account.fiscal.periods'].search([('calendar_type', '=',company_id.calendar_type.id)])
        if account_fiscal_periods:
            period = self.env['account.fiscal.period.lines'].search([('account_fiscal_period_id','in',[a.id for a in account_fiscal_periods]),('date_start', '<=', self.id),('date_end', '>=', self.id)])
            if period:
                start_quarter = self.env['account.fiscal.period.lines'].search([('account_fiscal_period_id','in',[a.id for a in account_fiscal_periods]),('quarter', '=', period.quarter)],limit=1,  order="date_start asc")
                end_quarter = self.env['account.fiscal.period.lines'].search([('account_fiscal_period_id','in',[a.id for a in account_fiscal_periods]),('quarter', '=', period.quarter)],limit=1,  order="date_start desc")
                result['from_date'] =  datetime.strptime(start_quarter.date_start, '%Y-%m-%d').strftime('%m/%d/%Y')
                result['to_date'] =  datetime.strptime(end_quarter.date_end, '%Y-%m-%d').strftime('%m/%d/%Y')
                return result
            
            
        result['from_date'] = "No Period"
        return result
    
    
    
    def get_fiscal_period_year(self):
        result = {}
        company_id = self.env.user.company_id
        account_fiscal_periods = self.env['account.fiscal.periods'].search([('calendar_type', '=',company_id.calendar_type.id)])
        if account_fiscal_periods:
            period = self.env['account.fiscal.period.lines'].search([('account_fiscal_period_id','in',[a.id for a in account_fiscal_periods]),('date_start', '<=', self.id),('date_end', '>=', self.id)])
            if period:
                start_quarter = self.env['account.fiscal.period.lines'].search([('account_fiscal_period_id','in',[a.id for a in account_fiscal_periods]),('year', '=', period.year)],limit=1,  order="date_start asc")
                end_quarter = self.env['account.fiscal.period.lines'].search([('account_fiscal_period_id','in',[a.id for a in account_fiscal_periods]),('year', '=', period.year)],limit=1,  order="date_start desc")
                result['from_date'] =  datetime.strptime(start_quarter.date_start, '%Y-%m-%d').strftime('%m/%d/%Y')
                result['to_date'] =  datetime.strptime(end_quarter.date_end, '%Y-%m-%d').strftime('%m/%d/%Y')
                return result
            
            
        result['from_date'] = "No Period"
        return result
    
    def get_last_month_fiscal_period(self):
        result = {}
        company_id = self.env.user.company_id
        account_fiscal_periods = self.env['account.fiscal.periods'].search([('calendar_type', '=',company_id.calendar_type.id)])
        if account_fiscal_periods:
            current_period = self.env['account.fiscal.period.lines'].search([('account_fiscal_period_id','in',[a.id for a in account_fiscal_periods]),('date_start', '<=', self.id),('date_end', '>=', self.id)])
            if current_period:
                previous_day = datetime.strptime(current_period.date_start, '%Y-%m-%d') -  timedelta(1)
                previous_period = self.env['account.fiscal.period.lines'].search([('account_fiscal_period_id','in',[a.id for a in account_fiscal_periods]),('date_start', '<=', previous_day),('date_end', '>=', previous_day)])
                if previous_period:
                    result['from_date'] =  datetime.strptime(previous_period.date_start, '%Y-%m-%d').strftime('%m/%d/%Y')
                    result['to_date'] =  datetime.strptime(previous_period.date_end, '%Y-%m-%d').strftime('%m/%d/%Y')
                    return result
        result['from_date'] = "No Period"
        return result
    
    def get_last_quarter_fiscal_period(self):
        result = {}
        company_id = self.env.user.company_id
        account_fiscal_periods = self.env['account.fiscal.periods'].search([('calendar_type', '=',company_id.calendar_type.id)])
        if account_fiscal_periods:
            current_period = self.env['account.fiscal.period.lines'].search([('account_fiscal_period_id','in',[a.id for a in account_fiscal_periods]),('date_start', '<=', self.id),('date_end', '>=', self.id)])
            if current_period:
                current_quarter = self.env['account.fiscal.period.lines'].search([('account_fiscal_period_id','in',[a.id for a in account_fiscal_periods]),('quarter', '=', current_period.quarter)],limit=1,  order="date_start asc")
                previous_day = datetime.strptime(current_quarter.date_start, '%Y-%m-%d') -  timedelta(1)
                previous_period = self.env['account.fiscal.period.lines'].search([('account_fiscal_period_id','in',[a.id for a in account_fiscal_periods]),('date_start', '<=', previous_day),('date_end', '>=', previous_day)])
                if previous_period:
                    start_quarter = self.env['account.fiscal.period.lines'].search([('account_fiscal_period_id','in',[a.id for a in account_fiscal_periods]),('quarter', '=', previous_period.quarter)],limit=1,  order="date_start asc")
                    end_quarter = self.env['account.fiscal.period.lines'].search([('account_fiscal_period_id','in',[a.id for a in account_fiscal_periods]),('quarter', '=', previous_period.quarter)],limit=1,  order="date_start desc")
                    result['from_date'] =  datetime.strptime(start_quarter.date_start, '%Y-%m-%d').strftime('%m/%d/%Y')
                    result['to_date'] =  datetime.strptime(end_quarter.date_end, '%Y-%m-%d').strftime('%m/%d/%Y')
                    return result
#             
            
        result['from_date'] = "No Period"
        return result
    
    
    def get_last_year_fiscal_period(self):
        result = {}
        company_id = self.env.user.company_id
        account_fiscal_periods = self.env['account.fiscal.periods'].search([('calendar_type', '=',company_id.calendar_type.id)])
        if account_fiscal_periods:
            current_period = self.env['account.fiscal.period.lines'].search([('account_fiscal_period_id','in',[a.id for a in account_fiscal_periods]),('date_start', '<=', self.id),('date_end', '>=', self.id)])
            if current_period:
                current_quarter = self.env['account.fiscal.period.lines'].search([('account_fiscal_period_id','in',[a.id for a in account_fiscal_periods]),('year', '=', current_period.year)],limit=1,  order="date_start asc")
                previous_day = datetime.strptime(current_quarter.date_start, '%Y-%m-%d') -  timedelta(1)
                previous_period = self.env['account.fiscal.period.lines'].search([('account_fiscal_period_id','in',[a.id for a in account_fiscal_periods]),('date_start', '<=', previous_day),('date_end', '>=', previous_day)])
                if previous_period:
                    start_year = self.env['account.fiscal.period.lines'].search([('account_fiscal_period_id','in',[a.id for a in account_fiscal_periods]),('year', '=', previous_period.year)],limit=1,  order="date_start asc")
                    end_year = self.env['account.fiscal.period.lines'].search([('account_fiscal_period_id','in',[a.id for a in account_fiscal_periods]),('year', '=', previous_period.year)],limit=1,  order="date_start desc")
                    result['from_date'] =  datetime.strptime(start_year.date_start, '%Y-%m-%d').strftime('%m/%d/%Y')
                    result['to_date'] =  datetime.strptime(end_year.date_end, '%Y-%m-%d').strftime('%m/%d/%Y')
                    return result
            
            
        result['from_date'] = "No Period"
        return result
    @api.multi 
    def unlink(self):
        for i in self:
            action_client = self.env['ir.actions.client'].search([('name','=',i.get_title())])
            action_client.unlink()
            menu = self.env['ir.ui.menu'].search([('name','=',i.get_title())])
            menu.unlink()
        return super(ReportAccountFinancialReport, self).unlink()
        
    def get_fiscal_period_lines(self):
        current_period = self.env['account.fiscal.period.lines'].search([('account_fiscal_period_id','=', int(self.id))])
        return [[a.id,a.name] for a in current_period]
    
    def start_end_date_for_months(self):
        current_period = self.env['account.fiscal.period.lines'].search([('id','=', int(self.id))])
        return [current_period.date_start,current_period.date_end]

class AccountFinancialReportLine(models.Model):
    _inherit = "account.financial.html.report.line"
    
    def _get_with_statement(self, financial_report):
        """ This function allow to define a WITH statement as prologue to the usual queries returned by query_get().
            It is useful if you need to shadow a table entirely and let the query_get work normally although you're
            fetching rows from your temporary table (built in the WITH statement) instead of the regular tables.

            @returns: the WITH statement to prepend to the sql query and the parameters used in that WITH statement
            @rtype: tuple(char, list)
        """
        sql = ''
        params = []

        #Cash basis option
        #-----------------
        #In cash basis, we need to show amount on income/expense accounts, but only when they're paid AND under the payment date in the reporting, so
        #we have to make a complex query to join aml from the invoice (for the account), aml from the payments (for the date) and partial reconciliation
        #(for the reconciled amount). This is True also for the cash flow statement except for lines 'CASHSTART' and 'CASHEND' because those have to be
        #computed on the normal account_move_line table).
        
        if self.code not in ('CASHSTART', 'CASHEND') \
          and (financial_report == self.env['account.financial.html.report'] or self.env.context.get('cash_basis')):
            #we use query_get() to filter out unrelevant journal items to have a shadowed table as small as possible
            tables, where_clause, where_params = self.env['account.move.line']._query_get()
            sql = """WITH account_move_line AS (
              SELECT \"account_move_line\".id, \"account_move_line\".date, \"account_move_line\".name, \"account_move_line\".debit_cash_basis, \"account_move_line\".credit_cash_basis, \"account_move_line\".move_id, \"account_move_line\".account_id, \"account_move_line\".journal_id, \"account_move_line\".balance_cash_basis, \"account_move_line\".amount_residual, \"account_move_line\".partner_id, \"account_move_line\".reconciled, \"account_move_line\".company_id, \"account_move_line\".company_currency_id
               FROM """ + tables + """
               WHERE \"account_move_line\".journal_id IN (SELECT id FROM account_journal WHERE type in ('cash', 'bank'))
                 AND """ + where_clause + """
              UNION ALL
              (
               WITH payment_table AS (
                 SELECT aml.move_id, \"account_move_line\".date, CASE WHEN aml.balance = 0 THEN 0 ELSE part.amount / ABS(aml.balance) END as matched_percentage
                   FROM account_partial_reconcile part LEFT JOIN account_move_line aml ON aml.id = part.debit_move_id, """ + tables + """
                   WHERE part.credit_move_id = "account_move_line".id
                    AND """ + where_clause + """
                 UNION ALL
                 SELECT aml.move_id, \"account_move_line\".date, CASE WHEN aml.balance = 0 THEN 0 ELSE part.amount / ABS(aml.balance) END as matched_percentage
                   FROM account_partial_reconcile part LEFT JOIN account_move_line aml ON aml.id = part.credit_move_id, """ + tables + """
                   WHERE part.debit_move_id = "account_move_line".id
                    AND """ + where_clause + """
               )
               SELECT aml.id, ref.date, aml.name,
                 CASE WHEN aml.debit > 0 THEN ref.matched_percentage * aml.debit ELSE 0 END AS debit_cash_basis,
                 CASE WHEN aml.credit > 0 THEN ref.matched_percentage * aml.credit ELSE 0 END AS credit_cash_basis,
                 aml.move_id, aml.account_id, aml.journal_id,
                 ref.matched_percentage * aml.balance AS balance_cash_basis,
                 aml.amount_residual, aml.partner_id, aml.reconciled, aml.company_id, aml.company_currency_id
                FROM account_move_line aml
                RIGHT JOIN payment_table ref ON aml.move_id = ref.move_id
                WHERE journal_id NOT IN (SELECT id FROM account_journal WHERE type in ('cash', 'bank'))
              )
            ) """
            
            params = where_params + where_params + where_params
        return sql, params
    
    
#     def _compute_line(self, currency_table, financial_report, group_by=None, domain=[]):
#         """ Computes the sum that appeas on report lines when they aren't unfolded. It is using _query_get() function
#             of account.move.line which is based on the context, and an additional domain (the field domain on the report
#             line) to build the query that will be used.
# 
#             @param currency_table: dictionary containing the foreign currencies (key) and their factor (value)
#                 compared to the current user's company currency
#             @param financial_report: browse_record of the financial report we are willing to compute the lines for
#             @param group_by: used in case of conditionnal sums on the report line
#             @param domain: domain on the report line to consider in the query_get() call
# 
#             @returns : a dictionnary that has for each aml in the domain a dictionnary of the values of the fields
#         """
#         tables, where_clause, where_params = self.env['account.move.line']._query_get(domain=domain)
#         if financial_report.tax_report:
#             where_clause += ''' AND "account_move_line".tax_exigible = 't' '''
# 
#         line = self
#         financial_report = False
# 
#         while(not financial_report):
#             financial_report = line.financial_report_id
#             if not line.parent_id:
#                 break
#             line = line.parent_id
# 
#         sql, params = self._get_with_statement(financial_report)
# 
#         select, select_params = self._query_get_select_sum(currency_table)
#         where_params = params + select_params + where_params
# 
#         if (self.env.context.get('sum_if_pos') or self.env.context.get('sum_if_neg')) and group_by:
#             sql = sql + "SELECT account_move_line." + group_by + " as " + group_by + "," + select + " FROM " + tables + " WHERE " + where_clause + " GROUP BY account_move_line." + group_by
#             self.env.cr.execute(sql, where_params)
#             res = {'balance': 0, 'debit': 0, 'credit': 0, 'amount_residual': 0}
#             for row in self.env.cr.dictfetchall():
#                 if (row['balance'] > 0 and self.env.context.get('sum_if_pos')) or (row['balance'] < 0 and self.env.context.get('sum_if_neg')):
#                     for field in ['debit', 'credit', 'balance', 'amount_residual']:
#                         res[field] += row[field]
#             res['currency_id'] = self.env.user.company_id.currency_id.id
#             return res
# 
#         sql = sql + "SELECT " + select + " FROM " + tables + " WHERE " + where_clause
#         self.env.cr.execute(sql, where_params)
#         results = self.env.cr.dictfetchall()[0]
#         results['currency_id'] = self.env.user.company_id.currency_id.id
#         return results
    
    


class AccountReportContextCommon(models.TransientModel):
    _inherit = "account.report.context.common"
    @api.model
    def create(self,vals):
        print self,'create'
        res = super(AccountReportContextCommon, self).create(vals)
        return res
    
    @api.multi
    def write(self,vals):
        print self
        company_id = self.env.user.company_id
        account_fiscal_periods = self.env['account.fiscal.periods'].search([('calendar_type', '=',company_id.calendar_type.id)])
        if account_fiscal_periods:
            period_line = self.env['account.fiscal.period.lines'].search([('account_fiscal_period_id','in',[a.id for a in account_fiscal_periods]),('date_end', '=', self.date_to)])
            if period_line:
                if self.date_filter_cmp == 'same_last_year':
                    if 'month' in self.date_filter:
                        period_prefix = (period_line.name).split("-")[0]
                        period_year = int((period_line.name).split("-")[1])
                        previous_year = period_year-1
                        where_condition = "%s-%s" %(period_prefix, previous_year)
                        previous_line = self.env['account.fiscal.period.lines'].search([('account_fiscal_period_id','in',[a.id for a in account_fiscal_periods]),('name', '=', where_condition)])
                        if previous_line:
                            vals['date_from_cmp'] = previous_line.date_start
                            vals['date_to_cmp'] = previous_line.date_end
                            res = super(AccountReportContextCommon, self).write(vals)
                            return res
                    if 'quarter' in self.date_filter:
                        period_prefix = (period_line.quarter).split("-")[0]
                        period_year = int((period_line.quarter).split("-")[1])
                        previous_year = period_year-1
                        where_condition = "%s-%s" %(period_prefix, previous_year)
                        previous_line_start = self.env['account.fiscal.period.lines'].search([('account_fiscal_period_id','in',[a.id for a in account_fiscal_periods]),('quarter', '=', where_condition)],limit=1,  order="date_start desc")
                        previous_line_end = self.env['account.fiscal.period.lines'].search([('account_fiscal_period_id','in',[a.id for a in account_fiscal_periods]),('quarter', '=', where_condition)],limit=1,  order="date_start asc")
                        if previous_line_start and previous_line_end:
                            vals['date_from_cmp'] = previous_line_start.date_start
                            vals['date_to_cmp'] = previous_line_end.date_end
                            res = super(AccountReportContextCommon, self).write(vals)
                            return res
                    if 'year' in self.date_filter:
                        period_prefix = (period_line.quarter).split("-")[0]
                        period_year = int((period_line.quarter).split("-")[1])
                        previous_year = period_year-1
                        where_condition = "%s-%s" %(period_prefix, previous_year)
                        previous_line_start = self.env['account.fiscal.period.lines'].search([('account_fiscal_period_id','in',[a.id for a in account_fiscal_periods]),('year', '=', where_condition)],limit=1,  order="date_start desc")
                        previous_line_end = self.env['account.fiscal.period.lines'].search([('account_fiscal_period_id','in',[a.id for a in account_fiscal_periods]),('year', '=', where_condition)],limit=1,  order="date_start asc")
                        if previous_line_start and previous_line_end:
                            vals['date_from_cmp'] = previous_line.date_start
                            vals['date_to_cmp'] = previous_line.date_end
                            res = super(AccountReportContextCommon, self).write(vals)
                            return res
                if 'month' in self.date_filter:
                    previous_day = datetime.strptime(period_line.date_start, '%Y-%m-%d') -  timedelta(1)
                    previous_period = self.env['account.fiscal.period.lines'].search([('account_fiscal_period_id','in',[a.id for a in account_fiscal_periods]),('date_start', '<=', previous_day),('date_end', '>=', previous_day)])
                    if previous_period:
                        vals['date_from_cmp'] = previous_period.date_start
                        vals['date_to_cmp'] = previous_period.date_end          
                        res = super(AccountReportContextCommon, self).write(vals)
                        return res
                    
                if 'quarter' in self.date_filter:
                        current_line_start = self.env['account.fiscal.period.lines'].search([('account_fiscal_period_id','in',[a.id for a in account_fiscal_periods]),('quarter', '=', period_line.quarter)],limit=1,  order="date_start asc")
                        current_line_end = self.env['account.fiscal.period.lines'].search([('account_fiscal_period_id','in',[a.id for a in account_fiscal_periods]),('quarter', '=', period_line.quarter)],limit=1,  order="date_start desc")
                        if current_line_start and current_line_end:
                            previous_day = datetime.strptime(current_line_start.date_start, '%Y-%m-%d') -  timedelta(1)
                            previous_period = self.env['account.fiscal.period.lines'].search([('account_fiscal_period_id','in',[a.id for a in account_fiscal_periods]),('date_start', '<=', previous_day),('date_end', '>=', previous_day)])
                            if previous_period:
                                previous_line_start = self.env['account.fiscal.period.lines'].search([('account_fiscal_period_id','in',[a.id for a in account_fiscal_periods]),('quarter', '=', previous_period.quarter)],limit=1,  order="date_start asc")
                                previous_line_end = self.env['account.fiscal.period.lines'].search([('account_fiscal_period_id','in',[a.id for a in account_fiscal_periods]),('quarter', '=', previous_period.quarter)],limit=1,  order="date_start desc")
                                vals['date_from_cmp'] = previous_line_start.date_start
                                vals['date_to_cmp'] = previous_line_end.date_end          
                                res = super(AccountReportContextCommon, self).write(vals)
                                return res
                            
                if 'year' in self.date_filter:
                        current_line_start = self.env['account.fiscal.period.lines'].search([('account_fiscal_period_id','in',[a.id for a in account_fiscal_periods]),('year', '=', period_line.year)],limit=1,  order="date_start asc")
                        current_line_end = self.env['account.fiscal.period.lines'].search([('account_fiscal_period_id','in',[a.id for a in account_fiscal_periods]),('year', '=', period_line.year)],limit=1,  order="date_start desc")
                        if current_line_start and current_line_end:
                            previous_day = datetime.strptime(current_line_start.date_start, '%Y-%m-%d') -  timedelta(1)
                            previous_period = self.env['account.fiscal.period.lines'].search([('account_fiscal_period_id','in',[a.id for a in account_fiscal_periods]),('date_start', '<=', previous_day),('date_end', '>=', previous_day)])
                            if previous_period:
                                previous_line_start = self.env['account.fiscal.period.lines'].search([('account_fiscal_period_id','in',[a.id for a in account_fiscal_periods]),('year', '=', previous_period.year)],limit=1,  order="date_start asc")
                                previous_line_end = self.env['account.fiscal.period.lines'].search([('account_fiscal_period_id','in',[a.id for a in account_fiscal_periods]),('year', '=', previous_period.year)],limit=1,  order="date_start desc")
                                vals['date_from_cmp'] = previous_line_start.date_start
                                vals['date_to_cmp'] = previous_line_end.date_end          
                                res = super(AccountReportContextCommon, self).write(vals)
                                return res
                        
        res = super(AccountReportContextCommon, self).write(vals)
        return res
    @api.multi
    def get_html_and_data(self, given_context=None):
        if given_context is None:
            given_context = {}
        result = {}
        if given_context:
            if 'force_account' in given_context and (not self.date_from or self.date_from == self.date_to):
                self.date_from = self.env.user.company_id.compute_fiscalyear_dates(datetime.strptime(self.date_to, "%Y-%m-%d"))['date_from']
                self.date_filter = 'custom'
        lines = self.get_report_obj().get_lines(self)
        rcontext = {
            'res_company': self.env['res.users'].browse(self.env.uid).company_id,
            'context': self,
            'report': self.get_report_obj(),
            'lines': lines,
            'footnotes': self.get_footnotes_from_lines(lines),
            'mode': 'display',
        }
        self.multicompany_manager_id.update_companies()
        result['html'] = self.env['ir.model.data'].xmlid_to_object(self.get_report_obj().get_template()).render(rcontext)
        result['report_type'] = self.get_report_obj().get_report_type().read(['date_range', 'comparison', 'cash_basis', 'analytic', 'extra_options'])[0]
        select = ['id', 'date_filter', 'date_filter_cmp', 'date_from', 'date_to', 'periods_number', 'date_from_cmp', 'date_to_cmp', 'cash_basis', 'all_entries', 'company_ids', 'multi_company', 'hierarchy_3', 'analytic']
        if self.get_report_obj().get_name() == 'general_ledger':
            select += ['journal_ids']
            result['available_journals'] = self.get_available_journal_ids_names_and_codes()
        if self.get_report_obj().get_name() == 'partner_ledger':
            select += ['account_type']
        result['report_context'] = self.read(select)[0]
        result['report_context'].update(self._context_add())
        if result['report_type']['analytic']:
            result['report_context']['analytic_account_ids'] = [(t.id, t.name) for t in self.analytic_account_ids]
            result['report_context']['analytic_tag_ids'] = [(t.id, t.name) for t in self.analytic_tag_ids]
            result['report_context']['available_analytic_account_ids'] = self.analytic_manager_id.get_available_analytic_account_ids_and_names()
            result['report_context']['available_analytic_tag_ids'] = self.analytic_manager_id.get_available_analytic_tag_ids_and_names()
        result['xml_export'] = self.env['account.financial.html.report.xml.export'].is_xml_export_available(self.get_report_obj())
        result['fy'] = {
            'fiscalyear_last_day': self.env.user.company_id.fiscalyear_last_day,
            'fiscalyear_last_month': self.env.user.company_id.fiscalyear_last_month,
        }
        company_id = self.env.user.company_id
        account_fiscal_periods = self.env['account.fiscal.periods'].search([('calendar_type', '=',company_id.calendar_type.id)])
        if account_fiscal_periods:
            result['fiscal_periods'] = [[a.id,a.name] for a in account_fiscal_periods]
        else:
            result['fiscal_periods'] = []
        result['available_companies'] = self.multicompany_manager_id.get_available_company_ids_and_names()
        return result
    
    def get_cmp_date(self):
        if not self.get_report_obj().get_report_type().date_range:
            return self.get_full_date_names(self.date_to_cmp)
        return self.get_full_date_names(self.date_to_cmp, self.date_from_cmp)
    
    def get_cmp_periods(self, display=False):
        if not self.comparison:
            return []
        dt_to = datetime.strptime(self.date_to, "%Y-%m-%d")
        if self.get_report_obj().get_report_type().date_range:
            dt_from = self.date_from and datetime.strptime(self.date_from, "%Y-%m-%d") or self.env.user.company_id.compute_fiscalyear_dates(dt_to)['date_from']
        columns = []
        if self.date_filter_cmp == 'custom':
            if display:
                return [_('Comparison<br />') + self.get_cmp_date(), '%']
            else:
                if not self.get_report_obj().get_report_type().date_range:
                    return [[False, self.date_to_cmp]]
                return [[self.date_from_cmp, self.date_to_cmp]]
        if self.date_filter_cmp == 'same_last_year':
            columns = []
            for k in xrange(0, self.periods_number):
                i = 0
                company_id = self.env.user.company_id
                account_fiscal_periods = self.env['account.fiscal.periods'].search([('calendar_type', '=',company_id.calendar_type.id)])
                if account_fiscal_periods:
                    period_line = self.env['account.fiscal.period.lines'].search([('account_fiscal_period_id','in',[a.id for a in account_fiscal_periods]),('date_end', '=', dt_to)])
                    if period_line:
                        i = 1
                        if 'month' in self.date_filter:
                            period_prefix = (period_line.name).split("-")[0]
                            period_year = int((period_line.name).split("-")[1])
                            previous_year = period_year-1
                            where_condition = "%s-%s" %(period_prefix, previous_year)
                            previous_line = self.env['account.fiscal.period.lines'].search([('account_fiscal_period_id','in',[a.id for a in account_fiscal_periods]),('name', '=', where_condition)])
                            if previous_line:
                                dt_to = datetime.strptime(previous_line.date_end, "%Y-%m-%d")
                            else:
                                dt_to = dt_to.replace(year=dt_to.year - 1)
                            if display:
                                if not self.get_report_obj().get_report_type().date_range:
                                    columns += [self.get_full_date_names(dt_to.strftime("%Y-%m-%d"))]
                                else:
                                    if previous_line:
                                        dt_from = datetime.strptime(previous_line.date_start, "%Y-%m-%d")
                                    else:
                                        dt_from = dt_from.replace(year=dt_from.year - 1)
                                    columns += [self.get_full_date_names(dt_to.strftime("%Y-%m-%d"), dt_from.strftime("%Y-%m-%d"))]
                            else:
                                if not self.get_report_obj().get_report_type().date_range:
                                    columns += [[False, dt_to.strftime("%Y-%m-%d")]]
                                else:
                                    if previous_line:
                                        dt_from = datetime.strptime(previous_line.date_start, "%Y-%m-%d")
                                    else:
                                        dt_from = dt_from.replace(year=dt_from.year - 1)
                                    columns += [[dt_from.strftime("%Y-%m-%d"), dt_to.strftime("%Y-%m-%d")]]
                        elif 'quarter' in self.date_filter:
                            period_prefix = (period_line.quarter).split("-")[0]
                            period_year = int((period_line.quarter).split("-")[1])
                            previous_year = period_year-1
                            where_condition = "%s-%s" %(period_prefix, previous_year)
                            previous_line_start = self.env['account.fiscal.period.lines'].search([('account_fiscal_period_id','in',[a.id for a in account_fiscal_periods]),('quarter', '=', where_condition)],limit=1,  order="date_start desc")
                            previous_line_end = self.env['account.fiscal.period.lines'].search([('account_fiscal_period_id','in',[a.id for a in account_fiscal_periods]),('quarter', '=', where_condition)],limit=1,  order="date_start asc")
                            if previous_line_start:
                                dt_to = datetime.strptime(previous_line_start.date_end, "%Y-%m-%d")
                            else:
                                dt_to = dt_to.replace(year=dt_to.year - 1)
                            if display:
                                if not self.get_report_obj().get_report_type().date_range:
                                    columns += [self.get_full_date_names(dt_to.strftime("%Y-%m-%d"))]
                                else:
                                    if previous_line_end:
                                        dt_from = datetime.strptime(previous_line_end.date_start, "%Y-%m-%d")
                                    else:
                                        dt_from = dt_from.replace(year=dt_from.year - 1)
                                    columns += [self.get_full_date_names(dt_to.strftime("%Y-%m-%d"), dt_from.strftime("%Y-%m-%d"))]
                            
                            else:
                                if not self.get_report_obj().get_report_type().date_range:
                                    columns += [[False, dt_to.strftime("%Y-%m-%d")]]
                                else:
                                    if previous_line_end:
                                        dt_from = datetime.strptime(previous_line_end.date_start, "%Y-%m-%d")
                                    else:
                                        dt_from = dt_from.replace(year=dt_from.year - 1)
                                    columns += [[dt_from.strftime("%Y-%m-%d"), dt_to.strftime("%Y-%m-%d")]]
                        elif 'year' in self.date_filter:
                            previous_year = int(period_line.year)-1
                            previous_line_end = self.env['account.fiscal.period.lines'].search([('account_fiscal_period_id','in',[a.id for a in account_fiscal_periods]),('year', '=', previous_year)],limit=1,  order="date_start desc")
                            previous_line_start = self.env['account.fiscal.period.lines'].search([('account_fiscal_period_id','in',[a.id for a in account_fiscal_periods]),('year', '=', previous_year)],limit=1,  order="date_start asc")
                            if previous_line_end:
                                dt_to = datetime.strptime(previous_line_end.date_end, "%Y-%m-%d")
                            else:
                                dt_to = dt_to.replace(year=dt_to.year - 1)
                                 
                            if display:
                                if not self.get_report_obj().get_report_type().date_range:
                                    columns += [self.get_full_date_names(dt_to.strftime("%Y-%m-%d"))]
                                else:
                                    if previous_line_start:
                                        dt_from = datetime.strptime(previous_line_start.date_start, "%Y-%m-%d")
                                    else:
                                        dt_from = dt_from.replace(year=dt_from.year - 1)
                                    columns += [self.get_full_date_names(dt_to.strftime("%Y-%m-%d"), dt_from.strftime("%Y-%m-%d"))]
                            else:
                                if not self.get_report_obj().get_report_type().date_range:
                                    columns += [[False, dt_to.strftime("%Y-%m-%d")]]
                                else:
                                    if previous_line_start:
                                        dt_from = datetime.strptime(previous_line_start.date_start, "%Y-%m-%d")
                                    else:
                                        dt_from = dt_from.replace(year=dt_from.year - 1)
                                    columns += [[dt_from.strftime("%Y-%m-%d"), dt_to.strftime("%Y-%m-%d")]]
                if i == 0:
                    dt_to = dt_to.replace(year=dt_to.year - 1)
                    if display:
                        if not self.get_report_obj().get_report_type().date_range:
                            columns += [self.get_full_date_names(dt_to.strftime("%Y-%m-%d"))]
                        else:
                            dt_from = dt_from.replace(year=dt_from.year - 1)
                            columns += [self.get_full_date_names(dt_to.strftime("%Y-%m-%d"), dt_from.strftime("%Y-%m-%d"))]
                    else:
                        if not self.get_report_obj().get_report_type().date_range:
                            columns += [[False, dt_to.strftime("%Y-%m-%d")]]
                        else:
                            dt_from = dt_from.replace(year=dt_from.year - 1)
                            columns += [[dt_from.strftime("%Y-%m-%d"), dt_to.strftime("%Y-%m-%d")]]
            return columns
        if 'month' in self.date_filter:
            for k in xrange(0, self.periods_number):
                i = 0
                company_id = self.env.user.company_id
                account_fiscal_periods = self.env['account.fiscal.periods'].search([('calendar_type', '=',company_id.calendar_type.id)])
                if account_fiscal_periods:
                    current_period = self.env['account.fiscal.period.lines'].search([('account_fiscal_period_id','in',[a.id for a in account_fiscal_periods]),('date_start', '<=', dt_to),('date_end', '>=', dt_to)])
                    if current_period:
                        previous_day = datetime.strptime(current_period.date_start, '%Y-%m-%d') -  timedelta(1)
                        previous_period = self.env['account.fiscal.period.lines'].search([('account_fiscal_period_id','in',[a.id for a in account_fiscal_periods]),('date_start', '<=', previous_day),('date_end', '>=', previous_day)])
                        if previous_period:
                            i = 1
                            dt_to = datetime.strptime(previous_period.date_end, "%Y-%m-%d")
                            if display:
                                columns += [previous_period.name]
                            else:
                                if not self.get_report_obj().get_report_type().date_range:
                                    columns += [[False, dt_to.strftime("%Y-%m-%d")]]
                                else:
                                    dt_from = datetime.strptime(previous_period.date_start, "%Y-%m-%d")
                                    columns += [[dt_from.strftime("%Y-%m-%d"), dt_to.strftime("%Y-%m-%d")]]
                if i == 0:
                    dt_to = dt_to.replace(day=1)
                    dt_to -= timedelta(days=1)
                    if display:
                        columns += [dt_to.strftime('%b %Y')]
                    else:
                        if not self.get_report_obj().get_report_type().date_range:
                            columns += [[False, dt_to.strftime("%Y-%m-%d")]]
                        else:
                            dt_from -= timedelta(days=1)
                            dt_from = dt_from.replace(day=1)
                            columns += [[dt_from.strftime("%Y-%m-%d"), dt_to.strftime("%Y-%m-%d")]]
        elif 'quarter' in self.date_filter:
            quarter = (dt_to.month - 1) / 3 + 1
            year = dt_to.year
            for k in xrange(0, self.periods_number):
                i = 0
                company_id = self.env.user.company_id
                account_fiscal_periods = self.env['account.fiscal.periods'].search([('calendar_type', '=',company_id.calendar_type.id)])
                if account_fiscal_periods:
                    current_period = self.env['account.fiscal.period.lines'].search([('account_fiscal_period_id','in',[a.id for a in account_fiscal_periods]),('date_start', '<=', dt_to),('date_end', '>=', dt_to)])
                    if current_period:
                        current_quarter = self.env['account.fiscal.period.lines'].search([('account_fiscal_period_id','in',[a.id for a in account_fiscal_periods]),('quarter', '=', current_period.quarter)],limit=1,  order="date_start asc")
                        previous_day = datetime.strptime(current_quarter.date_start, '%Y-%m-%d') -  timedelta(1)
                        previous_period = self.env['account.fiscal.period.lines'].search([('account_fiscal_period_id','in',[a.id for a in account_fiscal_periods]),('date_start', '<=', previous_day),('date_end', '>=', previous_day)])
                        if previous_period:
                            i = 1
                            start_quarter = self.env['account.fiscal.period.lines'].search([('account_fiscal_period_id','in',[a.id for a in account_fiscal_periods]),('quarter', '=', previous_period.quarter)],limit=1,  order="date_start asc")
                            end_quarter = self.env['account.fiscal.period.lines'].search([('account_fiscal_period_id','in',[a.id for a in account_fiscal_periods]),('quarter', '=', previous_period.quarter)],limit=1,  order="date_start desc")
                            dt_to = datetime.strptime(end_quarter.date_end, "%Y-%m-%d")
                            if display:
                                columns += [previous_period.quarter]
                            else:
                                if not self.get_report_obj().get_report_type().date_range:
                                    columns += [[False, dt_to.strftime("%Y-%m-%d")]]
                                else:
                                    dt_from = datetime.strptime(start_quarter.date_start, "%Y-%m-%d")
                                    columns += [[dt_from.strftime("%Y-%m-%d"), dt_to.strftime("%Y-%m-%d")]]
                if i == 0:
                    if display:
                        if quarter == 1:
                            quarter = 4
                            year -= 1
                        else:
                            quarter -= 1
                        columns += [_('Quarter #') + str(quarter) + ' ' + str(year)]
                    else:
                        if dt_to.month == 12:
                            dt_to = dt_to.replace(month=9, day=30)
                        elif dt_to.month == 9:
                            dt_to = dt_to.replace(month=6, day=30)
                        elif dt_to.month == 6:
                            dt_to = dt_to.replace(month=3, day=31)
                        else:
                            dt_to = dt_to.replace(month=12, day=31, year=dt_to.year - 1)
                        if not self.get_report_obj().get_report_type().date_range:
                            columns += [[False, dt_to.strftime("%Y-%m-%d")]]
                        else:
                            if dt_from.month == 10:
                                dt_from = dt_from.replace(month=7)
                            elif dt_from.month == 7:
                                dt_from = dt_from.replace(month=4)
                            elif dt_from.month == 4:
                                dt_from = dt_from.replace(month=1)
                            else:
                                dt_from = dt_from.replace(month=10, year=dt_from.year - 1)
                            columns += [[dt_from.strftime("%Y-%m-%d"), dt_to.strftime("%Y-%m-%d")]]
        elif 'year' in self.date_filter:
            dt_to = datetime.strptime(self.date_to, "%Y-%m-%d")
            for k in xrange(0, self.periods_number):
                i = 0
                company_id = self.env.user.company_id
                account_fiscal_periods = self.env['account.fiscal.periods'].search([('calendar_type', '=',company_id.calendar_type.id)])
                if account_fiscal_periods:
                    current_period = self.env['account.fiscal.period.lines'].search([('account_fiscal_period_id','in',[a.id for a in account_fiscal_periods]),('date_start', '<=', dt_to),('date_end', '>=', dt_to)])
                    if current_period:
                        current_year = self.env['account.fiscal.period.lines'].search([('account_fiscal_period_id','in',[a.id for a in account_fiscal_periods]),('year', '=', current_period.year)],limit=1,  order="date_start asc")
                        previous_day = datetime.strptime(current_year.date_start, '%Y-%m-%d') -  timedelta(1)
                        previous_period = self.env['account.fiscal.period.lines'].search([('account_fiscal_period_id','in',[a.id for a in account_fiscal_periods]),('date_start', '<=', previous_day),('date_end', '>=', previous_day)])
                        if previous_period:
                            i = 1
                            start_year = self.env['account.fiscal.period.lines'].search([('account_fiscal_period_id','in',[a.id for a in account_fiscal_periods]),('year', '=', previous_period.year)],limit=1,  order="date_start asc")
                            end_year = self.env['account.fiscal.period.lines'].search([('account_fiscal_period_id','in',[a.id for a in account_fiscal_periods]),('year', '=', previous_period.year)],limit=1,  order="date_start desc")
                            dt_to = datetime.strptime(end_year.date_end, "%Y-%m-%d")
                            if display:
                                columns += [previous_period.year]
                            else:
                                if not self.get_report_obj().get_report_type().date_range:
                                    columns += [[False, dt_to.strftime("%Y-%m-%d")]]
                                else:
                                    dt_from = datetime.strptime(start_year.date_start, "%Y-%m-%d")
                                    columns += [[dt_from.strftime("%Y-%m-%d"), dt_to.strftime("%Y-%m-%d")]]
                if i == 0:                    
                    dt_to = dt_to.replace(year=dt_to.year - 1)
                    if display:
                        if dt_to.strftime("%m-%d") == '12-31':
                            columns += [dt_to.year]
                        else:
                            columns += [str(dt_to.year - 1) + ' - ' + str(dt_to.year)]
                    else:
                        if not self.get_report_obj().get_report_type().date_range:
                            columns += [[False, dt_to.strftime("%Y-%m-%d")]]
                        else:
                            dt_from = dt_to.replace(year=dt_to.year - 1) + timedelta(days=1)
                            columns += [[dt_from.strftime("%Y-%m-%d"), dt_to.strftime("%Y-%m-%d")]]
        else:
            if self.get_report_obj().get_report_type().date_range:
                dt_from = datetime.strptime(self.date_from, "%Y-%m-%d")
                delta = dt_to - dt_from
                delta = timedelta(days=delta.days + 1)
                delta_days = delta.days
                for k in xrange(0, self.periods_number):
                    dt_from -= delta
                    dt_to -= delta
                    if display:
                        columns += [_('%s - %s days ago') % ((k + 1) * delta_days, (k + 2) * delta_days)]
                    else:
                        columns += [[dt_from.strftime("%Y-%m-%d"), dt_to.strftime("%Y-%m-%d")]]
            else:
                for k in xrange(0, self.periods_number):
                    dt_to -= timedelta(days=calendar.monthrange(dt_to.year, dt_to.month)[1])
                    if display:
                        columns += [_('(as of %s)') % dt_to.strftime('%d %b %Y').decode("utf-8")]
                    else:
                        columns += [[False, dt_to.strftime("%Y-%m-%d")]]
        return columns
    
    def get_xlsx(self, response):
        output = StringIO.StringIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        report_id = self.get_report_obj()
        name_length = len(report_id.get_title())
        if name_length > 31:
            remove_length = name_length - 31
            sheet_name = report_id.get_title()[:remove_length]
            sheet = workbook.add_worksheet(sheet_name)
        else:
            sheet = workbook.add_worksheet(report_id.get_title())

        def_style = workbook.add_format({'font_name': 'Arial'})
        title_style = workbook.add_format({'font_name': 'Arial', 'bold': True, 'bottom': 2})
        level_0_style = workbook.add_format({'font_name': 'Arial', 'bold': True, 'bottom': 2, 'top': 2, 'pattern': 1, 'font_color': '#FFFFFF'})
        level_0_style_left = workbook.add_format({'font_name': 'Arial', 'bold': True, 'bottom': 2, 'top': 2, 'left': 2, 'pattern': 1, 'font_color': '#FFFFFF'})
        level_0_style_right = workbook.add_format({'font_name': 'Arial', 'bold': True, 'bottom': 2, 'top': 2, 'right': 2, 'pattern': 1, 'font_color': '#FFFFFF'})
        level_1_style = workbook.add_format({'font_name': 'Arial', 'bold': True, 'bottom': 2, 'top': 2})
        level_1_style_left = workbook.add_format({'font_name': 'Arial', 'bold': True, 'bottom': 2, 'top': 2, 'left': 2})
        level_1_style_right = workbook.add_format({'font_name': 'Arial', 'bold': True, 'bottom': 2, 'top': 2, 'right': 2})
        level_2_style = workbook.add_format({'font_name': 'Arial', 'bold': True, 'top': 2})
        level_2_style_left = workbook.add_format({'font_name': 'Arial', 'bold': True, 'top': 2, 'left': 2})
        level_2_style_right = workbook.add_format({'font_name': 'Arial', 'bold': True, 'top': 2, 'right': 2})
        level_3_style = def_style
        level_3_style_left = workbook.add_format({'font_name': 'Arial', 'left': 2})
        level_3_style_right = workbook.add_format({'font_name': 'Arial', 'right': 2})
        domain_style = workbook.add_format({'font_name': 'Arial', 'italic': True})
        domain_style_left = workbook.add_format({'font_name': 'Arial', 'italic': True, 'left': 2})
        domain_style_right = workbook.add_format({'font_name': 'Arial', 'italic': True, 'right': 2})
        upper_line_style = workbook.add_format({'font_name': 'Arial', 'top': 2})

        sheet.set_column(0, 0, 100) #  Set the first column width to 1000

        sheet.write(0, 0, '', title_style)

        y_offset = 0
        if self.get_report_obj().get_name() == 'coa' and self.get_special_date_line_names():
            sheet.write(y_offset, 0, '', title_style)
            sheet.write(y_offset, 1, '', title_style)
            x = 2
            for column in self.with_context(is_xls=True).get_special_date_line_names():
                sheet.write(y_offset, x, column, title_style)
                sheet.write(y_offset, x+1, '', title_style)
                x += 2
            sheet.write(y_offset, x, '', title_style)
            y_offset += 1

        x = 1
        for column in self.with_context(is_xls=True).get_columns_names():
            sheet.write(y_offset, x, column.replace('<br/>', ' '), title_style)
            x += 1
        y_offset += 1

        lines = report_id.with_context(no_format=True, print_mode=True).get_lines(self)

        if lines:
            max_width = max([len(l['columns']) for l in lines])
        print max_width
        for y in range(0, len(lines)):
            if lines[y].get('level') == 0 and lines[y].get('type') == 'line':
                for x in range(0, len(lines[y]['columns']) + 1):
                    sheet.write(y + y_offset, x, None, upper_line_style)
                y_offset += 1
                style_left = level_0_style_left
                style_right = level_0_style_right
                style = level_0_style
            elif lines[y].get('level') == 1 and lines[y].get('type') == 'line':
                for x in range(0, len(lines[y]['columns']) + 1):
                    sheet.write(y + y_offset, x, None, upper_line_style)
                y_offset += 1
                style_left = level_1_style_left
                style_right = level_1_style_right
                style = level_1_style
            elif lines[y].get('level') == 2:
                style_left = level_2_style_left
                style_right = level_2_style_right
                style = level_2_style
            elif lines[y].get('level') == 3:
                style_left = level_3_style_left
                style_right = level_3_style_right
                style = level_3_style
            elif lines[y].get('type') != 'line':
                style_left = domain_style_left
                style_right = domain_style_right
                style = domain_style
            else:
                style = def_style
                style_left = def_style
                style_right = def_style
            sheet.write(y + y_offset, 0, lines[y]['name'], style_left)
            for x in xrange(1, max_width - len(lines[y]['columns']) + 1):
                sheet.write(y + y_offset, x, None, style)
            for x in xrange(1, len(lines[y]['columns']) + 1):
                if isinstance(lines[y]['columns'][x - 1], tuple):
                    lines[y]['columns'][x - 1] = lines[y]['columns'][x - 1][0]
                if x < len(lines[y]['columns']):
                    sheet.write(y + y_offset, x+lines[y].get('colspan', 1)-1, lines[y]['columns'][x - 1], style)
                else:
                    sheet.write(y + y_offset, x+lines[y].get('colspan', 1)-1, lines[y]['columns'][x - 1], style_right)
            if lines[y]['type'] == 'total' or lines[y].get('level') == 0:
                for x in xrange(0, len(lines[0]['columns']) + 1):
                    sheet.write(y + 1 + y_offset, x, None, upper_line_style)
                y_offset += 1
        if lines:
            for x in xrange(0, max_width+1):
                sheet.write(len(lines) + y_offset, x, None, upper_line_style)

        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
#     
#     
    def get_full_date_names(self, dt_to, dt_from=None):
        convert_date = self.env['ir.qweb.field.date'].value_to_html
        date_to = convert_date(dt_to, None)
        dt_to = datetime.strptime(dt_to, "%Y-%m-%d")
        company_id = self.env.user.company_id
        account_fiscal_periods = self.env['account.fiscal.periods'].search([('calendar_type', '=',company_id.calendar_type.id)])
        if account_fiscal_periods:
            period_line = self.env['account.fiscal.period.lines'].search([('account_fiscal_period_id','in',[a.id for a in account_fiscal_periods]),('date_end', '=', dt_to)])
            if period_line:
                if 'month' in self.date_filter:
                    return period_line.name
                elif 'quarter' in self.date_filter:
                    return period_line.quarter
                elif 'year' in self.date_filter:
                    return period_line.year
                else:
                    return period_line.name
                
                if not dt_from:
                    return _('As of %s') % (date_to,)
        if dt_from:
            date_from = convert_date(dt_from, None)
        if 'month' in self.date_filter:
            return '%s %s' % (self._get_month(dt_to.month - 1), dt_to.year)
        if 'quarter' in self.date_filter:
            quarter = (dt_to.month - 1) / 3 + 1
            return dt_to.strftime(_('Quarter #') + str(quarter) + ' %Y')
        if 'year' in self.date_filter:
            if self.env.user.company_id.fiscalyear_last_day == 31 and self.env.user.company_id.fiscalyear_last_month == 12:
                return dt_to.strftime('%Y')
            else:
                return str(dt_to.year - 1) + ' - ' + str(dt_to.year)
        if not dt_from:
            return _('As of %s') % (date_to,)
        return _('From %s <br/> to  %s') % (date_from, date_to)
    
    
class AccountReportMulticompanyManager(models.TransientModel):
    _inherit = 'account.report.multicompany.manager'
    
    def update_companies(self):
        if self.available_company_ids != self.env.user.company_ids:
            self.write({'available_company_ids' : [(6, 0, self.env.user.company_ids.ids)]})
    

class account_bank_reconciliation_report(models.AbstractModel):
    _inherit = 'account.bank.reconciliation.report'
    
    
    @api.model
    def _lines(self):
        lines = []
        #Start amount
        
        new_jounal_id=False
        print self.env.context['journal_id']
        if self.env.context['journal_id'].id:
            new_jounal_id=self.env.context['journal_id']            
            request.session['new_jounal_id']=self.env.context['journal_id'].id
        else:
            print 2,'--'
            new_jounal_id=self.env['account.journal'].search([('id', '=', request.session['new_jounal_id'])])
        
        use_foreign_currency = bool(self.env.context['journal_id'].currency_id)
        account_ids = list(set([self.env.context['journal_id'].default_debit_account_id.id, new_jounal_id.default_credit_account_id.id]))
        lines_already_accounted = self.env['account.move.line'].search([('account_id', 'in', account_ids),
                                                                        ('date', '<=', self.env.context['date_to']),
                                                                        ('company_id', 'in', self.env.context['company_ids'])])
        start_amount = sum([line.amount_currency if use_foreign_currency else line.balance for line in lines_already_accounted])
        lines.append(self.add_title_line(_("Current Balance in GL"), start_amount))

        # Un-reconcilied bank statement lines
        move_lines = self.env['account.move.line'].sudo().search([('move_id.journal_id', '=', new_jounal_id.id),
                                                           '|', ('move_id.statement_line_id', '=', False), ('move_id.statement_line_id.date', '>', self.env.context['date_to']),
                                                           ('user_type_id.type', '!=', 'liquidity'),
                                                           ('date', '<=', self.env.context['date_to']),
                                                           ('company_id', 'in', self.env.context['company_ids'])])
        print len(self.env['account.move.line'].sudo().search([('move_id.journal_id', '=', new_jounal_id.id), 
                                                               '|', ('move_id.statement_line_id', '=', False), ('move_id.statement_line_id.date', '>', self.env.context['date_to']), 
                                                               ('user_type_id.type', '!=', 'liquidity'),
                                                           ('date', '<=', self.env.context['date_to']),
                                                           ('company_id', 'in', self.env.context['company_ids'])]))
        print move_lines
        print self.env.context
        
        print [('move_id.journal_id', '=', new_jounal_id.id),
                                                           '|', ('move_id.statement_line_id', '=', False), ('move_id.statement_line_id.date', '>', self.env.context['date_to']),
                                                           ('user_type_id.type', '!=', 'liquidity'),
                                                           ('date', '<=', self.env.context['date_to']),
                                                           ('company_id', 'in', self.env.context['company_ids'])]
        print '--'
        print '--'
        print '--'
        print '--'
        unrec_tot = 0
        if move_lines:
            tmp_lines = []
            for line in move_lines:
                self.line_number += 1
                tmp_lines.append({
                    'id': self.line_number,
                    'move_id': line.move_id.id,
                    'type': 'move_line_id',
                    'action': line.get_model_id_and_name(),
                    'name': line.name,
                    'footnotes': self.env.context['context_id']._get_footnotes('move_line_id', self.line_number),
                    'columns': [line.date, line.ref, self._format(line.amount_currency if use_foreign_currency else line.balance)],
                    'level': 1,
                })
                unrec_tot += line.amount_currency if use_foreign_currency else line.balance
            if unrec_tot > 0:
                title = _("Plus Unreconciled Payments")
            else:
                title = _("Minus Unreconciled Payments")
            lines.append(self.add_subtitle_line(title))
            lines += tmp_lines
            lines.append(self.add_total_line(unrec_tot))

        # Outstanding plus
        not_reconcile_plus = self.env['account.bank.statement.line'].search([('statement_id.journal_id', '=', new_jounal_id.id),
                                                                             ('date', '<=', self.env.context['date_to']),
                                                                             ('journal_entry_ids', '=', False),
                                                                             ('amount', '>', 0),
                                                                             ('company_id', 'in', self.env.context['company_ids'])])
        outstanding_plus_tot = 0
        if not_reconcile_plus:
            lines.append(self.add_subtitle_line(_("Plus Unreconciled Statement Lines")))
            for line in not_reconcile_plus:
                lines.append(self.add_bank_statement_line(line, line.amount))
                outstanding_plus_tot += line.amount
            lines.append(self.add_total_line(outstanding_plus_tot))

        # Outstanding less
        not_reconcile_less = self.env['account.bank.statement.line'].search([('statement_id.journal_id', '=', new_jounal_id.id),
                                                                             ('date', '<=', self.env.context['date_to']),
                                                                             ('journal_entry_ids', '=', False),
                                                                             ('amount', '<', 0),
                                                                             ('company_id', 'in', self.env.context['company_ids'])])
        outstanding_less_tot = 0
        if not_reconcile_less:
            lines.append(self.add_subtitle_line(_("Minus Unreconciled Statement Lines")))
            for line in not_reconcile_less:
                lines.append(self.add_bank_statement_line(line, line.amount))
                outstanding_less_tot += line.amount
            lines.append(self.add_total_line(outstanding_less_tot))

        # Final
        computed_stmt_balance = start_amount + outstanding_plus_tot + outstanding_less_tot + unrec_tot
        last_statement = self.env['account.bank.statement'].search([('journal_id', '=', new_jounal_id.id),
                                       ('date', '<=', self.env.context['date_to']), ('company_id', 'in', self.env.context['company_ids'])], order="date desc, id desc", limit=1)
        real_last_stmt_balance = last_statement.balance_end
        if computed_stmt_balance != real_last_stmt_balance:
            if real_last_stmt_balance - computed_stmt_balance > 0:
                title = _("Plus Missing Statements")
            else:
                title = _("Minus Missing Statements")
            lines.append(self.add_subtitle_line(title, real_last_stmt_balance - computed_stmt_balance))
        lines.append(self.add_title_line(_("Equal Last Statement Balance"), real_last_stmt_balance))
        
        return lines
    
    
    
    