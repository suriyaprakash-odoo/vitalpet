from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import UserError, RedirectWarning, ValidationError
from datetime import datetime

class BillPayReversal(models.TransientModel):
    """
    Account move reversal wizard, it cancel an account move by reversing it.
    """
    _name = 'billpay.reversal'
    _description = 'Account move reversal'

    date = fields.Date(string='Reversal date', default=fields.Date.context_today, required=True)
    account_fiscal_periods_id = fields.Many2one('account.fiscal.period.lines', string="Account Fiscal Period",
                                                ondelete="restrict")
    account_fiscal_period_week_id = fields.Many2one('account.fiscal.period.week', string="Account Fiscal Period Week",
                                                    ondelete="restrict")
    account_fiscal_periods_quarterly = fields.Char(string="Account Fiscal Period Quarterly")
    reversal_reason = fields.Text("Reversal Reason")

    
#     journal_id = fields.Many2one('account.journal', string='Use Specific Journal', help='If empty, uses the journal of the journal entry to be reversed.')
    
    @api.onchange('date')
    def get_account_fiscal_periods(self):
        company_obj = self.env['res.company'].search([('id', '=', self.env.user.company_id.id)], limit=1)
#         
        company = self.env['res.company'].search([('id', '=', company_obj.id)])
        account_fiscal_periods = self.env['account.fiscal.periods'].search([('calendar_type', '=', company.calendar_type.id)])
        if account_fiscal_periods:
            period = self.env['account.fiscal.period.lines'].search([('account_fiscal_period_id','in',[a.id for a in account_fiscal_periods]),('date_start', '<=', self.date),('date_end', '>=', self.date)])
            if period.closing_date_range == True:
                raise UserError(_('Account Period date is expired so you cannot create a record.'))
            if period:
                self.account_fiscal_periods_id = period.id
                self.account_fiscal_periods_quarterly = period.quarter
            else:
                self.account_fiscal_periods_id = ''
                self.account_fiscal_periods_quarterly = ''
                
            period_week = self.env['account.fiscal.period.week'].search([('account_fiscal_period_week_id','in',[a.id for a in account_fiscal_periods]),('date_start', '<=', self.date),('date_end', '>=', self.date)])
            if period_week:
                self.account_fiscal_period_week_id = period_week.id
            else:
                self.account_fiscal_period_week_id = ''
        return {}
    
    
    
    @api.multi
    def reverse_moves(self):
        ac_move_ids = self._context.get('active_ids', False)
        billpay_bills = self.env['billpay.bills'].search([('id', '=', ac_move_ids[0])])
        billpay=self.env['account.invoice'].search([('billpay_id','=', ac_move_ids[0]),('state','!=','cancel')])
        if not billpay:
           raise UserError("This bill is already Reversed")
        billpay.state='cancel'     
        bill_date = datetime.strptime(billpay_bills.bill_date, "%Y-%m-%d").date()
        reverse_date = datetime.strptime(self.date, "%Y-%m-%d").date()
        if reverse_date < bill_date:
            raise UserError(_("Reverse date %s is lesser than Bill date %s. Reverse date cannot be lesser than bill date!") %(reverse_date,bill_date))
        
        if billpay_bills.invoice_amount>=billpay_bills.company_id.reverse_app_amt:
            billpay_bills.state = 'open'
        else:     
            if billpay_bills:
                account_move = self.env['account.move'].search([('billpay_id', '=', billpay_bills.id)])
                for i in account_move:
                    res = i.reverse_moves(self.date)
                    res_move = self.env['account.move'].search([('id', '=', res[0])])
                    res_move.write({'state':'draft'})
        
        assets= self.env['account.asset.asset'].search([('bill_id', '=', billpay_bills.bill_credit_id)])
        for line in assets:
            if line.state == 'draft':
                line.unlink()
            else:
                raise UserError(_('The state has been already moved from draft to running in assets.')) 
            
         
    #               
    #                 print res_move = self
    #                 i.write({'state':'draft'})
    #         res = self.env['account.move'].browse(ac_move_ids).reverse_moves(self.date, self.journal_id or False)
            if res:
                billpay_bills.write({'state':'open','reversal_reason':self.reversal_reason})
                account_move = self.env['account.move'].search([('billpay_id', '=', billpay_bills.id)])
                return {
                    'name': _('Reverse Moves'),
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'res_model': 'account.move',
                    'domain': [('id', 'in', [i.id for i in account_move])],
                }
            return {'type': 'ir.actions.act_window_close'}
