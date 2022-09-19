import babel.dates
import datetime

from odoo import api, fields, models
from odoo.tools.translate import _
from odoo.exceptions import UserError, RedirectWarning, ValidationError

class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    account_fiscal_periods_id = fields.Many2one('account.fiscal.period.lines', string = "Fiscal Month", ondelete="restrict")
    account_fiscal_period_week_id = fields.Many2one('account.fiscal.period.week', string = "Fiscal Week", ondelete="restrict")
    account_fiscal_periods_quarterly = fields.Char(string = "Fiscal Quarter")
    account_fiscal_periods_year = fields.Many2one('account.fiscal.periods',string = "Fiscal Year")
    custom_calendar = fields.Boolean('Use Custom calendar', compute='_compute_calendar_id', store=False)
    
         
    @api.depends('company_id')
    @api.multi
    def _compute_calendar_id(self):
        for res in self:
            res.custom_calendar=res.company_id.custom_calendar.id
            
    @api.model
    def create(self,vals):
        if self.env.context.get('type'):
            if self.env.context['type'] == 'in_invoice':
                date_invoice = vals.get('date')
            if self.env.context['type'] == 'out_invoice':
                date_invoice = vals.get('date_invoice')
            if self.env.context['type'] == 'in_refund':
                date_invoice = vals.get('date_invoice')                  
        else:
            date_invoice = vals.get('date')
                  
       
        company = self.env['res.company'].search([('id','=',vals.get('company_id'))])
        account_fiscal_periods = self.env['account.fiscal.periods'].search([('calendar_type', '=', company.calendar_type.id)])
        if account_fiscal_periods:
            period = self.env['account.fiscal.period.lines'].search([('account_fiscal_period_id','in',[a.id for a in account_fiscal_periods]),('date_start', '<=', date_invoice),('date_end', '>=', date_invoice)])
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
            
            period_week = self.env['account.fiscal.period.week'].search([('account_fiscal_period_week_id','in',[a.id for a in account_fiscal_periods]),('date_start', '<=', date_invoice),('date_end', '>=', date_invoice)])
            if period_week:
                vals['account_fiscal_period_week_id'] = period_week.id
            else:
                vals['account_fiscal_period_week_id'] = ''
            
        res = super(AccountInvoice, self).create(vals)
        return res
    
    @api.multi
    def write(self,vals):
        for line in self:
            context = dict(self._context or {})
            if 'type' in self.env.context:
                context['type']= self.env.context['type'] #Re assigning the value
            else:
                context['type']= line.type
            if vals and not line.account_fiscal_periods_id and vals.get('date') or vals.get('date_invoice'):
                if context['type'] == 'in_invoice':
                    date_invoice = vals.get('date')
                
                if context['type'] == 'out_invoice':
                    date_invoice = vals.get('date_invoice')
                    
                if context['type'] == 'in_refund':
                    date_invoice = vals.get('date_invoice')          
               
                if date_invoice:
                    account_fiscal_periods = self.env['account.fiscal.periods'].search([('calendar_type', '=',line.company_id.calendar_type.id)])
                    if account_fiscal_periods:
                        period = self.env['account.fiscal.period.lines'].search([('account_fiscal_period_id','in',[a.id for a in account_fiscal_periods]),('date_start', '<=', date_invoice),('date_end', '>=', date_invoice)])
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
                            
                        period_week = self.env['account.fiscal.period.week'].search([('account_fiscal_period_week_id','in',[a.id for a in account_fiscal_periods]),('date_start', '<=', date_invoice),('date_end', '>=', date_invoice)])
                        if period_week:
                            vals['account_fiscal_period_week_id'] = period_week.id
                        else:
                            vals['account_fiscal_period_week_id'] = ''
        res = super(AccountInvoice, self).write(vals)
        return res

    @api.onchange('date')
    def get_account_fiscal_periods(self):
        if self.env.context['type'] == 'in_invoice':
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
                    
                period_week = self.env['account.fiscal.period.week'].search([('account_fiscal_period_week_id','in',[a.id for a in account_fiscal_periods]),('date_start', '<=', self.date),('date_end', '>=', self.date)])
                if period_week:
                    self.account_fiscal_period_week_id = period_week.id
                else:
                    self.account_fiscal_period_week_id = ''
        return {}
    
    @api.onchange('date_invoice')
    def get_account_fiscal_periods_date(self):
        
        if self.env.context['type'] == 'out_invoice':
            account_fiscal_periods = self.env['account.fiscal.periods'].search([('calendar_type', '=', self.company_id.calendar_type.id)])
            if account_fiscal_periods:
                period = self.env['account.fiscal.period.lines'].search([('account_fiscal_period_id','in',[a.id for a in account_fiscal_periods]),('date_start', '<=', self.date_invoice),('date_end', '>=', self.date_invoice)])
                if period:
                    self.account_fiscal_periods_id = period.id
                    self.account_fiscal_periods_quarterly = period.quarter
                    self.account_fiscal_periods_year = period.account_fiscal_period_id.id

                else:
                    self.account_fiscal_periods_id = ''
                    self.account_fiscal_periods_quarterly = ''
                    self.account_fiscal_periods_year = ''

                period_week = self.env['account.fiscal.period.week'].search([('account_fiscal_period_week_id','in',[a.id for a in account_fiscal_periods]),('date_start', '<=', self.date_invoice),('date_end', '>=', self.date_invoice)])
                if period_week:
                    self.account_fiscal_period_week_id = period_week.id
                else:
                    self.account_fiscal_period_week_id = ''
        return {}
    
    @api.multi
    def action_move_create(self):
        """ Creates invoice related analytics and financial move lines """
        account_move = self.env['account.move']
        for inv in self:
            if not inv.journal_id.sequence_id:
                raise UserError(_('Please define sequence on the journal related to this invoice.'))
            if not inv.invoice_line_ids:
                raise UserError(_('Please create some invoice lines.'))
            if inv.move_id:
                continue
  
            ctx = dict(self._context, lang=inv.partner_id.lang)
  
            if not inv.date_invoice:
                inv.with_context(ctx).write({'date_invoice': fields.Date.context_today(self)})
            date_invoice = inv.date_invoice
            company_currency = inv.company_id.currency_id
  
            # create move lines (one per invoice line + eventual taxes and analytic lines)
            iml = inv.invoice_line_move_line_get()
            iml += inv.tax_line_move_line_get()
  
            diff_currency = inv.currency_id != company_currency
            # create one move line for the total and possibly adjust the other lines amount
            total, total_currency, iml = inv.with_context(ctx).compute_invoice_totals(company_currency, iml)
  
            name = inv.name or '/'
            if inv.payment_term_id:
                totlines = inv.with_context(ctx).payment_term_id.with_context(currency_id=company_currency.id).compute(total, date_invoice)[0]
                res_amount_currency = total_currency
                ctx['date'] = date_invoice
                for i, t in enumerate(totlines):
                    if inv.currency_id != company_currency:
                        amount_currency = company_currency.with_context(ctx).compute(t[1], inv.currency_id)
                    else:
                        amount_currency = False
  
                    # last line: add the diff
                    res_amount_currency -= amount_currency or 0
                    if i + 1 == len(totlines):
                        amount_currency += res_amount_currency
  
                    iml.append({
                        'type': 'dest',
                        'name': name,
                        'price': t[1],
                        'account_id': inv.account_id.id,
                        'company_id':self.company_id.id,
                        'account_fiscal_periods_id':self.account_fiscal_periods_id.id,
                        'account_fiscal_periods_quarterly' : self.account_fiscal_periods_id.quarter,
                        'date_maturity': t[0],
                        'amount_currency': diff_currency and amount_currency,
                        'currency_id': diff_currency and inv.currency_id.id,
                        'invoice_id': inv.id
                    })
            else:
                iml.append({
                    'type': 'dest',
                    'name': name,
                    'price': total,
                    'account_id': inv.account_id.id,
                    'company_id':self.company_id.id,
                    'account_fiscal_periods_id':self.account_fiscal_periods_id.id,
                    'account_fiscal_periods_quarterly': self.account_fiscal_periods_id.quarter,
                    'date_maturity': inv.date_due,
                    'amount_currency': diff_currency and total_currency,
                    'currency_id': diff_currency and inv.currency_id.id,
                    'invoice_id': inv.id
                })
            part = self.env['res.partner']._find_accounting_partner(inv.partner_id)
            line = [(0, 0, self.line_get_convert(l, part.id)) for l in iml]
            line = inv.group_lines(iml, line)
  
            journal = inv.journal_id.with_context(ctx)
            line = inv.finalize_invoice_move_lines(line)
  
            date = inv.date or date_invoice
            move_vals = {
                'ref': inv.reference,
                'line_ids': line,
                'company_id': self.company_id.id,
                'journal_id': journal.id,
                'account_fiscal_periods_id':self.account_fiscal_periods_id.id,
                'account_fiscal_periods_quarterly' :  self.account_fiscal_periods_id.quarter,
                'date': date,
                'narration': inv.comment,
            }
            ctx['company_id'] = inv.company_id.id
            ctx['invoice'] = inv
            ctx['account_fiscal_periods_id'] = self.account_fiscal_periods_id.id
            ctx['account_fiscal_periods_quarterly'] = self.account_fiscal_periods_id.quarter
            ctx_nolang = ctx.copy()
            ctx_nolang.pop('lang', None)
            move = account_move.with_context(ctx_nolang).create(move_vals)
            # Pass invoice in context in method post: used if you want to get the same
            # account move reference when creating the same invoice after a cancelled one:
            move.post()
            # make the invoice point to that move
            vals = {
                'move_id': move.id,
                'date': date,
                'move_name': move.name,
            }
            inv.with_context(ctx).write(vals)
        return True
    @api.model
    def line_get_convert(self, line, part):
        return {
            'date_maturity': line.get('date_maturity', False),
            'partner_id': part,
            'name': line['name'][:64],
            'debit': line['price'] > 0 and line['price'],
            'credit': line['price'] < 0 and -line['price'],
            'account_id': line['account_id'],
            'account_fiscal_periods_id': line.get('account_fiscal_periods_id', False),
            'account_fiscal_periods_quarterly': line.get('account_fiscal_periods_quarterly', False),
            'analytic_line_ids': line.get('analytic_line_ids', []),
            'amount_currency': line['price'] > 0 and abs(line.get('amount_currency', False)) or -abs(line.get('amount_currency', False)),
            'currency_id': line.get('currency_id', False),
            'quantity': line.get('quantity', 1.00),
            'product_id': line.get('product_id', False),
            'product_uom_id': line.get('uom_id', False),
            'analytic_account_id': line.get('account_analytic_id', False),
            'invoice_id': line.get('invoice_id', False),
            'tax_ids': line.get('tax_ids', False),
            'tax_line_id': line.get('tax_line_id', False),
            'analytic_tag_ids': line.get('analytic_tag_ids', False),
        }
class AccountMove(models.Model):
    _inherit = 'account.move'

#    move_month_year = fields.Char("Fiscal Date", compute = '_convert_move_month_year', store=True)
    account_fiscal_periods_id = fields.Many2one('account.fiscal.period.lines', string = "Fiscal Month", ondelete="restrict")
    account_fiscal_period_week_id = fields.Many2one('account.fiscal.period.week', string = "Fiscal Week", ondelete="restrict")
    account_fiscal_periods_quarterly = fields.Char(string = "Fiscal Quarter")
    account_fiscal_periods_year = fields.Many2one('account.fiscal.periods',string = "Fiscal Year")

    custom_calendar = fields.Boolean('Use Custom calendar', compute='_compute_calendar_id', store=False)
    
         
    @api.depends('company_id')
    @api.multi
    def _compute_calendar_id(self):
        for res in self:
            res.custom_calendar=res.company_id.custom_calendar.id

    @api.model
    def create(self,vals):
        
        if vals.get('date', False) == False:
            vals['date'] = datetime.datetime.today()
        if vals.get('company_id'):
            company = self.env['res.company'].search([('id','=',vals.get('company_id'))])
        else:
            if vals.get('journal_id'):
                account_journal = self.env['account.journal'].search([('id', '=', int(vals.get('journal_id')))])
                company = account_journal.company_id
            else:
                company = None
    
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
                
            period_week = self.env['account.fiscal.period.week'].search([('account_fiscal_period_week_id','in',[a.id for a in account_fiscal_periods]),('date_start', '<=', vals.get('date')),('date_end', '>=', vals.get('date'))])
            if period_week:
                vals['account_fiscal_period_week_id'] = period_week.id
            else:
                vals['account_fiscal_period_week_id'] = ''

        res = super(AccountMove, self).create(vals)
        res.account_fiscal_periods_year = vals['account_fiscal_periods_year']
        res.account_fiscal_periods_quarterly = vals['account_fiscal_periods_quarterly']
        res.account_fiscal_periods_id = vals['account_fiscal_periods_id'] 
        res.account_fiscal_period_week_id = vals['account_fiscal_period_week_id']
        return res
    
    
     
    @api.multi
    def write(self,vals):
        for rec in self:
            company = self.env['res.company'].search([('id','=',rec.company_id.id)])
            account_fiscal_periods = self.env['account.fiscal.periods'].search([('calendar_type', '=', company.calendar_type.id)])
            if account_fiscal_periods and vals.get('date'):
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
                    
                    
                period_week = self.env['account.fiscal.period.week'].search([('account_fiscal_period_week_id','in',[a.id for a in account_fiscal_periods]),('date_start', '<=', vals.get('date')),('date_end', '>=', vals.get('date'))])
                if period_week:
                    vals['account_fiscal_period_week_id'] = period_week.id
                else:
                    vals['account_fiscal_period_week_id'] = ''
        res = super(AccountMove, self).write(vals)
        return res
     
    @api.onchange('date','company_id')
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
            period_week = self.env['account.fiscal.period.week'].search([('account_fiscal_period_week_id','in',[a.id for a in account_fiscal_periods]),('date_start', '<=', self.date),('date_end', '>=', self.date)])
            if period_week:
                self.account_fiscal_period_week_id = period_week.id
            else:
                self.account_fiscal_period_week_id = ''
        return {}
     
#     
class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
      
    account_fiscal_periods_id = fields.Many2one('account.fiscal.period.lines', string = "Fiscal Month", ondelete="restrict", related='move_id.account_fiscal_periods_id', store=True)
    account_fiscal_period_week_id = fields.Many2one('account.fiscal.period.week', string = "Fiscal Week", ondelete="restrict", related='move_id.account_fiscal_period_week_id', store=True)
    account_fiscal_periods_quarterly = fields.Char(string = "Fiscal Quarter", related='move_id.account_fiscal_periods_quarterly', store=True)
    account_fiscal_periods_year = fields.Many2one('account.fiscal.periods',string = "Fiscal Year", related='move_id.account_fiscal_periods_year', store=True)

    custom_calendar = fields.Boolean('Use Custom Calendar',related='company_id.custom_calendar',store=True)
    
    @api.model
    def create(self,vals):
        if vals.get('credit'):
            vals['credit']=float("%.2f" % vals['credit'])
        if vals.get('debit'):
            vals['debit']=float("%.2f" % vals['debit'])
        if vals.get('credit_cash_basis'):
            vals['credit_cash_basis']=float("%.2f" % vals['credit_cash_basis'])
        if vals.get('debit_cash_basis'):
            vals['debit_cash_basis']=float("%.2f" % vals['debit_cash_basis'])
        if vals.get('balance_cash_basis'):
            vals['balance_cash_basis']=float("%.2f" % vals['balance_cash_basis'])
        if vals.get('balance'):
            vals['balance']=float("%.2f" % vals['balance'] )     
        
        res = super(AccountMoveLine, self).create(vals)
        return res
    
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
      
#     @api.model
#     def create(self,vals):
# #         if vals.get('invoice_id'):
# #             inv = self.env['account.invoice'].search([('id','=',vals.get('invoice_id'))])        
# #             if inv:
# #                 vals['account_fiscal_periods_id'] = inv.account_fiscal_periods_id.id
# #                 vals['account_fiscal_periods_quarterly'] = inv.account_fiscal_periods_id.quarter        
# #         else:
# #             company = self.env['res.company'].search([('id','=',vals.get('company_id'))])
# #             account_fiscal_periods = self.env['account.fiscal.periods'].search([('calendar_type', '=', company.calendar_type.id)])
# #             if account_fiscal_periods:
# #                 period = self.env['account.fiscal.period.lines'].search([('account_fiscal_period_id','in',[a.id for a in account_fiscal_periods]),('date_start', '<=', vals.get('date')),('date_end', '>=', vals.get('date'))])
# #                 if period.closing_date_range == True:
# #                     raise UserError(_('Account Period date is expired so you cannot create a record.'))
# #                 if period:
# #                     vals['account_fiscal_periods_id'] = period.id
# #                     vals['account_fiscal_periods_quarterly'] = period.quarter
# #                     vals['account_fiscal_periods_year'] = period.account_fiscal_period_id.id
# #                 
# #                 period_week = self.env['account.fiscal.period.week'].search([('account_fiscal_period_week_id','in',[a.id for a in account_fiscal_periods]),('date_start', '<=', vals.get('date')),('date_end', '>=', vals.get('date'))])
# #                 if period_week:
# #                     vals['account_fiscal_period_week_id'] = period_week.id
# #                 else:
# #                     vals['account_fiscal_period_week_id'] = ''
#                
#         res = super(AccountMoveLine, self).create(vals)
#         res.date=res.date       # to update fiscalperiod 
#         return res
#       
#     @api.multi
#     def write(self,vals):
#         if vals.get('date'):  
#             account_fiscal_periods = self.env['account.fiscal.periods'].search([('calendar_type', '=', self.company_id.calendar_type.id)])
#             if account_fiscal_periods:
#                 period = self.env['account.fiscal.period.lines'].search([('account_fiscal_period_id','in',[a.id for a in account_fiscal_periods]),('date_start', '<=', vals.get('date')),('date_end', '>=', vals.get('date'))])
#                 if period.closing_date_range == True:
#                     raise UserError(_('Account Period date is expired so you cannot create a record.'))
#                 if period:
#                     vals['account_fiscal_periods_id'] = period.id
#                     vals['account_fiscal_periods_quarterly'] = period.quarter
#                     vals['account_fiscal_periods_year'] = period.account_fiscal_period_id.id
# 
#                 
#                 period_week = self.env['account.fiscal.period.week'].search([('account_fiscal_period_week_id','in',[a.id for a in account_fiscal_periods]),('date_start', '<=', vals.get('date')),('date_end', '>=', vals.get('date'))])
#                 if period_week:
#                     vals['account_fiscal_period_week_id'] = period_week.id
#                 else:
#                     vals['account_fiscal_period_week_id'] = ''
#         res = super(AccountMoveLine, self).write(vals)
#         return res
#      
class AccountPayment(models.Model):
    _inherit = 'account.payment'
      
    account_fiscal_periods_id = fields.Many2one('account.fiscal.period.lines', string = "Fiscal Month", ondelete="restrict")
    account_fiscal_period_week_id = fields.Many2one('account.fiscal.period.week', string = "Fiscal Week", ondelete="restrict")
    account_fiscal_periods_quarterly = fields.Char(string = "Fiscal Quarter")
    account_fiscal_periods_year = fields.Many2one('account.fiscal.periods',string = "Fiscal Year")

    custom_calendar = fields.Boolean('Use Custom calendar', compute='_compute_calendar_id', store=False)
    
         
    @api.depends('company_id')
    @api.multi
    def _compute_calendar_id(self):
        for res in self:
            res.custom_calendar=res.company_id.custom_calendar.id
            
#     move_month_year = fields.Char("Fiscal Date", compute = '_convert_move_month_year', store=True)
#     week_of_year = fields.Char("Fiscal Week", compute = '_convert_week_of_year', store=True)
   
    # Get month year from account move for group by filter
# It works based on company configuration 445 or fiscal date
#     @api.one
#     @api.depends('payment_date', 'company_id')
#     def _convert_move_month_year(self):
#         locale = self._context.get('lang', 'en_US')
#         for line in self:
#             if line.payment_date:
#                 company_id = ''
#                 if not line.company_id:
#     #Note: do not assign yourself journal company as journal
#                     if not line.partner_id.company_id:
#                         raise UserError(_('Please assign company for the Vendor.'))
#     # Check is 445 enabled for the company
#                 if line.company_id and line.company_id.custom_calendar == False:
#     # if not 445 used for the company conver the move date to sting month_year
#                     value = datetime.datetime.strptime(line.payment_date, '%Y-%m-%d')
#                     string_date_year = babel.dates.format_date(value, format = 'MMMM yyyy', locale = locale)                   
#                     line.move_month_year = string_date_year
#                 else:
#     # if 445 enabled for the company get fiscal year month and save it
#                     account_fiscal_periods = self.env['account.fiscal.periods'].search(['&', ('name', 'ilike', line.payment_date[:4]), ('calendar_type', '=', line.company_id.calendar_type.id)])
#                     if account_fiscal_periods :
#                         # Get period based on account move line
#                         period = self.env['account.fiscal.period.lines'].search([('account_fiscal_period_id', '=', account_fiscal_periods.id), ('date_start', '<=', line.payment_date),('date_end', '>=', line.payment_date)])
#                         line.move_month_year = period.name
#     @api.one
#     @api.depends('payment_date', 'company_id')
#     def _convert_week_of_year(self):
#         locale = self._context.get('lang', 'en_US')
#         for line in self:
#             if line.payment_date:
#                 company_id = ''
#                 if not line.company_id:
#     #Note: do not assign yourself company 
#                     if not line.category_id.company_id:
#                         raise UserError(_('Please assign company for the Asset.'))
#     # Check is 445 enabled for the company
#                 if line.company_id and line.company_id.custom_calendar == False:
#     # if not 445 used for the company convert the move date to sting month_year
#                     value = datetime.datetime.strptime(line.payment_date, '%Y-%m-%d')                   
#                     string_date_week = babel.dates.format_date(value, format = '-ww ', locale = locale)
#                     week_string = 'Week'+string_date_week 
#                     line.week_of_year = week_string
#                 else:
#     # if 445 enabled for the company get fiscal year month and save it
#                     account_fiscal_periods = self.env['account.fiscal.periods'].search(['&', ('name', 'ilike', line.payment_date[:4]), ('calendar_type', '=', line.company_id.calendar_type.id)])
#                     if account_fiscal_periods :
#                         # Get period based on account move line                        
#                         week = self.env['account.fiscal.period.week'].search([('account_fiscal_period_week_id', '=', account_fiscal_periods.id), ('date_start', '<=', line.payment_date),('date_end', '>=', line.payment_date)])
#                         if week:
#                             line.week_of_year = week.name

    # Get month year from account move for group by filter
# It works based on company configuration 445 or fiscal date
    @api.one
    @api.depends('payment_date', 'company_id')
    def _convert_week_of_month(self):
        locale = self._context.get('lang', 'en_US')
        for line in self:
            if line.payment_date:
                company_id = ''
                if not line.company_id:
    #Note: do not assign yourself journal company as journal
                    if not line.partner_id.company_id:
                        raise UserError(_('Please assign company for the Vendor.'))
    # Check is 445 enabled for the company
                if line.company_id and line.company_id.custom_calendar == False:
    # if not 445 used for the company conver the move date to sting month_year
                    value = datetime.datetime.strptime(line.payment_date, '%Y-%m-%d')
                    string_date_year = babel.dates.format_date(value, format = 'MMMM yyyy', locale = locale)
                    line.move_month_year = string_date_year
                else:
    # if 445 enabled for the company get fiscal year month and save it
                    account_fiscal_periods = self.env['account.fiscal.periods'].search(['&', ('name', 'ilike', line.payment_date[:4]), ('calendar_type', '=', line.company_id.calendar_type.id)])
                    if account_fiscal_periods :
                        # Get period based on account move line
                        period = self.env['account.fiscal.period.lines'].search([('account_fiscal_period_id', '=', account_fiscal_periods.id), ('date_start', '<=', line.payment_date),('date_end', '>=', line.payment_date)])
                        line.move_month_year = period.name

    @api.onchange('payment_date')
    def get_account_fiscal_periods(self):
        account_fiscal_periods = self.env['account.fiscal.periods'].search([('calendar_type', '=', self.company_id.calendar_type.id)])
        if account_fiscal_periods:
            period = self.env['account.fiscal.period.lines'].search([('account_fiscal_period_id','in',[a.id for a in account_fiscal_periods]),('date_start', '<=', self.payment_date),('date_end', '>=', self.payment_date)])
            if period:
                self.account_fiscal_periods_id = period.id
                self.account_fiscal_periods_quarterly = period.quarter
                self.account_fiscal_periods_year = period.account_fiscal_period_id.id
            else:
                self.account_fiscal_periods_id = ''
                self.account_fiscal_periods_quarterly = ''
                self.account_fiscal_periods_year = ''
                
            period_week = self.env['account.fiscal.period.week'].search([('account_fiscal_period_week_id','in',[a.id for a in account_fiscal_periods]),('date_start', '<=', self.payment_date),('date_end', '>=', self.payment_date)])
            if period_week:
                self.account_fiscal_period_week_id = period_week.id
            else:
                self.account_fiscal_period_week_id = ''
        return {}
      
    @api.model
    def create(self,vals):
        
        journal = self.env['account.journal'].search([('id','=',vals.get('journal_id'))])     
        company = journal.company_id
        account_fiscal_periods = self.env['account.fiscal.periods'].search([('calendar_type', '=', company.calendar_type.id)])
        if account_fiscal_periods:
            period = self.env['account.fiscal.period.lines'].search([('account_fiscal_period_id','in',[a.id for a in account_fiscal_periods]),('date_start', '<=', vals.get('payment_date')),('date_end', '>=', vals.get('payment_date'))])
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
                
            period_week = self.env['account.fiscal.period.week'].search([('account_fiscal_period_week_id','in',[a.id for a in account_fiscal_periods]),('date_start', '<=', vals.get('payment_date')),('date_end', '>=', vals.get('payment_date'))])
            if period_week:
                vals['account_fiscal_period_week_id'] = period_week.id
            else:
                vals['account_fiscal_period_week_id'] = ''    
            
        res = super(AccountPayment, self).create(vals)
        return res
      
    @api.multi
    def write(self,vals): 
        account_fiscal_periods = self.env['account.fiscal.periods'].search([('calendar_type', '=', self.company_id.calendar_type.id)])
        if account_fiscal_periods:
            period = self.env['account.fiscal.period.lines'].search([('account_fiscal_period_id','in',[a.id for a in account_fiscal_periods]),('date_start', '<=', self.payment_date),('date_end', '>=', self.payment_date)])
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
            
            period_week = self.env['account.fiscal.period.week'].search([('account_fiscal_period_week_id','in',[a.id for a in account_fiscal_periods]),('date_start', '<=', self.payment_date),('date_end', '>=', self.payment_date)])
            if period_week:
                vals['account_fiscal_period_week_id'] = period_week.id
            else:
                vals['account_fiscal_period_week_id'] = ''
        res = super(AccountPayment, self).write(vals)
        return res
#      
#      
#      
class AccountAssetAsset(models.Model):
    _inherit = 'account.asset.asset'
      
    account_fiscal_periods_id = fields.Many2one('account.fiscal.period.lines', string = "Fiscal Month", ondelete="restrict")
    account_fiscal_period_week_id = fields.Many2one('account.fiscal.period.week', string = "Fiscal Week", ondelete="restrict")
    account_fiscal_periods_quarterly = fields.Char(string = "Fiscal Quarter")
    account_fiscal_periods_year = fields.Many2one('account.fiscal.periods',string = "Fiscal Year")

    custom_calendar = fields.Boolean('Use Custom calendar', compute='_compute_calendar_id', store=False)
    
         
    @api.depends('company_id')
    @api.multi
    def _compute_calendar_id(self):
        for res in self:
            res.custom_calendar=res.company_id.custom_calendar.id
#     move_month_year = fields.Char("Fiscal Date", compute = '_convert_move_month_year', store=True)
#     week_of_year = fields.Char("Fiscal Week", compute = '_convert_week_of_year', store=True)

    # Get month year from account asset for group by filter
# It works based on company configuration 445 or fiscal date
#     @api.one
#     @api.depends('date', 'company_id')
#     def _convert_move_month_year(self):
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
#                     string_date_year = babel.dates.format_date(value, format = 'MMMM yyyy', locale = locale)
#                     line.move_month_year = string_date_year
#                 else:
#     # if 445 enabled for the company get fiscal year month and save it
#                     account_fiscal_periods = self.env['account.fiscal.periods'].search(['&', ('name', 'ilike', line.date[:4]), ('calendar_type', '=', line.company_id.calendar_type.id)])
#                     if account_fiscal_periods :
#                         # Get period based on account move line
#                         period = self.env['account.fiscal.period.lines'].search([('account_fiscal_period_id', '=', account_fiscal_periods.id), ('date_start', '<=', line.date),('date_end', '>=', line.date)])                        
#                         line.move_month_year = period.name
#     
#     @api.one
#     @api.depends('date', 'company_id')
#     def _convert_week_of_year(self):
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
                
            period_week = self.env['account.fiscal.period.week'].search([('account_fiscal_period_week_id','in',[a.id for a in account_fiscal_periods]),('date_start', '<=', self.date),('date_end', '>=', self.date)])
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
            if period:
                vals['account_fiscal_periods_id'] = period.id
                vals['account_fiscal_periods_quarterly'] = period.quarter
                vals['account_fiscal_periods_year'] = period.account_fiscal_period_id.id
            else:
                vals['account_fiscal_periods_id'] = ''
                vals['account_fiscal_periods_quarterly'] = ''
                vals['account_fiscal_periods_year'] = ''
                
            period_week = self.env['account.fiscal.period.week'].search([('account_fiscal_period_week_id','in',[a.id for a in account_fiscal_periods]),('date_start', '<=', vals.get('date')),('date_end', '>=', vals.get('date'))])
            if period_week:
                vals['account_fiscal_period_week_id'] = period_week.id
            else:
                vals['account_fiscal_period_week_id'] = ''    
                
                
        res = super(AccountAssetAsset, self).create(vals)
        return res
      
    @api.multi
    def write(self,vals):
        
        account_fiscal_periods = self.env['account.fiscal.periods'].search([('calendar_type', '=', self.company_id.calendar_type.id)])
        if account_fiscal_periods:
            period = self.env['account.fiscal.period.lines'].search([('account_fiscal_period_id','in',[a.id for a in account_fiscal_periods]),('date_start', '<=', self.date),('date_end', '>=', self.date)])
            if period:
                vals['account_fiscal_periods_id'] = period.id
                vals['account_fiscal_periods_quarterly'] = period.quarter
                vals['account_fiscal_periods_year'] = period.account_fiscal_period_id.id
            else:
                vals['account_fiscal_periods_id'] = ''
                vals['account_fiscal_periods_quarterly'] = ''
                vals['account_fiscal_periods_year'] = ''
                
            period_week = self.env['account.fiscal.period.week'].search([('account_fiscal_period_week_id','in',[a.id for a in account_fiscal_periods]),('date_start', '<=', self.date),('date_end', '>=', self.date)])
            if period_week:
                vals['account_fiscal_period_week_id'] = period_week.id
            else:
                vals['account_fiscal_period_week_id'] = ''
        res = super(AccountAssetAsset, self).write(vals)
        return res
    
    










