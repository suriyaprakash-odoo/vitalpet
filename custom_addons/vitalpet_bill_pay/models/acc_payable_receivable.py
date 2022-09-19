from odoo import fields, models, api , _
from odoo.exceptions import UserError
from odoo.addons.base.res.res_partner import Partner
from datetime import datetime
from dateutil import relativedelta as rdelta
from datetime import date

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"
    _order= 'date_maturity asc, id asc'
    
    
    day_since = fields.Char('Days Since', copy=False, compute='_calculate_since', readonly=True)
    bill_pay = fields.Boolean()
    invoice_number = fields.Char(related='invoice_id.reference',string="Invoice Number")
    
    @api.multi
    @api.depends('date')
    def _calculate_since(self):
        for bill in self:
            start = datetime.strptime(bill.date, '%Y-%m-%d')
            ends = datetime.now()
            diff_days = ends - start
            bill.day_since = diff_days.days
    
    @api.multi
    def create_bills(self):
        
        company_obj = self.env['res.company'].search([('id','=',self.env.user.company_id.id)], limit=1)
        domain = [
            ('type', '=', 'purchase'),
            ('company_id', '=', self.env.user.company_id.id),
        ]
        journal = self.env['account.journal'].search(domain, limit=1)
        if journal:
            journal_id = journal.id
        else:
            journal_id = False
        if self[0].account_id.tag_ids.name == company_obj.child_payable_tag.name:
            partner_id = self[0].partner_id.id
            invoice_amount = 0
            line_items = []
            for line in self:
                if partner_id != line.partner_id.id:
                    raise UserError(_("Partner should be same!"))
                invoice_amount+= round(line.credit, 2)
                
                items = {}
                items['account_id'] = line.account_id.id
                if line.invoice_id:
                    items['invoice_id'] = line.invoice_id.id
                items['company_id'] = line.company_id.id
                items['quantity'] = 1
                items['price_unit'] = line.credit
                items['amount'] = line.credit
                items['name'] = line.name
                items['req_analytic'] = False
                if line.product_id:
                    items['product_id'] = line.product_id.id
                    items['req_analytic'] = line.product_id.require_analytic
                items['payable_receivable_move_line_id'] = line.id
                line_items.append(items)
                date = line.date
            return {
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'billpay.bills',
                'target': 'current',
                'context': {
                    'default_bill_credit_type': 'bill',
                    'default_bill_credit_source': 'payable',
                    'default_partner_id': partner_id,
                    'default_journal_id': journal_id,
                    'default_invoice_amount': invoice_amount,
                    'default_bill_line_ids': line_items,
                    'default_bill_date':date,
                }
            }

#         
#             
        if self[0].account_id.tag_ids.name == company_obj.child_receivable_tag.name:
            partner_id = self[0].partner_id.id
            invoice_amount = 0
            line_items = []
            for line in self:
                if partner_id != line.partner_id.id:
                    raise UserError(_("Partner should be same!"))
                invoice_amount+=line.debit
                items = {}
                items['account_id'] = line.account_id.id
                if line.invoice_id:
                    items['invoice_id'] = line.invoice_id.id
                items['company_id'] = line.company_id.id
                items['quantity'] = 1
                items['price_unit'] = line.debit
                items['amount'] = line.debit
                items['name'] = line.name
                items['req_analytic'] = False
                if line.product_id:
                    items['product_id'] = line.product_id.id
                    items['req_analytic'] = line.product_id.require_analytic
                items['payable_receivable_move_line_id'] = line.id
                line_items.append(items)
                date = line.date
            return {
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'billpay.bills',
                'target': 'current',
                'context': {
                    'default_bill_credit_type': 'bill',
                    'default_bill_credit_source': 'receivable',
                    'default_partner_id': partner_id,
                    'default_journal_id': journal_id,
                    'default_invoice_amount': invoice_amount,
                    'default_bill_line_ids': line_items,
                    'default_bill_date':date,
                }
            }
            
        raise UserError(_("Please check Billpay configuration"))
    
    @api.multi
    def create_vendor_credit(self):
        company_obj = self.env['res.company'].search([('id','=',self.env.user.company_id.id)], limit=1)
        domain = [
            ('type', '=', 'purchase'),
            ('company_id', '=', self.env.user.company_id.id),
        ]
        journal = self.env['account.journal'].search(domain, limit=1)
        if journal:
            journal_id = journal.id
        else:
            journal_id = False
        if self[0].account_id.tag_ids.name == company_obj.child_payable_tag.name:
            partner_id = self[0].partner_id.id
            invoice_amount = 0
            line_items = []
            for line in self:
                if partner_id != line.partner_id.id:
                    raise UserError(_("Partner should be same!"))
                invoice_amount+=line.credit
                items = {}
                items['account_id'] = line.account_id.id
                if line.invoice_id:
                    items['invoice_id'] = line.invoice_id.id
                items['company_id'] = line.company_id.id
                items['quantity'] = 1
                items['price_unit'] = line.credit
                items['amount'] = line.credit
                items['name'] = line.name
                items['payable_receivable_move_line_id'] = line.id
                items['req_analytic'] = False
                if line.product_id:
                    items['product_id'] = line.product_id.id
                    items['req_analytic'] = line.product_id.require_analytic
                line_items.append(items)
            return {
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'billpay.bills',
                'target': 'current',
                'context': {
                    'default_bill_credit_type': 'credit',
                    'default_bill_credit_source': 'payable',
                    'default_partner_id': partner_id,
                    'default_journal_id': journal_id,
                    'default_invoice_amount': invoice_amount,
                    'default_bill_line_ids': line_items,
                }
            }

#         
#             
        if self[0].account_id.tag_ids.name == company_obj.child_receivable_tag.name:
            partner_id = self[0].partner_id.id
            invoice_amount = 0
            line_items = []
            for line in self:
                if partner_id != line.partner_id.id:
                    raise UserError(_("Partner should be same!"))
                invoice_amount+=line.debit
                items = {}
                items['account_id'] = line.account_id.id
                if line.invoice_id:
                    items['invoice_id'] = line.invoice_id.id
                items['company_id'] = line.company_id.id
                items['quantity'] = 1
                items['price_unit'] = line.debit
                items['amount'] = line.debit
                items['name'] = line.name
                items['payable_receivable_move_line_id'] = line.id
                items['req_analytic'] = False
                if line.product_id:
                    items['product_id'] = line.product_id.id
                    items['req_analytic'] = line.product_id.require_analytic
                line_items.append(items)
                date = line.date
            return {
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'billpay.bills',
                'target': 'current',
                'context': {
                    'default_bill_credit_type': 'credit',
                    'default_bill_credit_source': 'receivable',
                    'default_partner_id': partner_id,
                    'default_journal_id': journal_id,
                    'default_invoice_amount': invoice_amount,
                    'default_bill_line_ids': line_items,
                    'default_bill_date':date,
                }
            }
            
        raise UserError(_("Please check Billpay configuration"))
    
class AccountMoveLineReconcile(models.TransientModel):
    _inherit = 'account.move.line.reconcile'
        
        
    @api.model
    def default_get(self, fields):
        notallowed_gr = []
        user_groups = set([i.id for i in self.env.user.groups_id])
        bill_pay_manager = self.env.ref('vitalpet_bill_pay.group_billpay_manager').id
        adviser = self.env.ref('account.group_account_manager').id
        if not bill_pay_manager in user_groups and not  adviser in user_groups:
            raise UserError(_("You do not have rights to access Reconcile Entries"))
        return super(AccountMoveLineReconcile, self).default_get(fields)
     
    
class AccountUnreconcile(models.TransientModel):
    _inherit = "account.unreconcile"
    
    @api.model
    def default_get(self, fields):
        notallowed_gr = []
        user_groups = set([i.id for i in self.env.user.groups_id])
        bill_pay_manager = self.env.ref('vitalpet_bill_pay.group_billpay_manager').id
        adviser = self.env.ref('account.group_account_manager').id
        if not bill_pay_manager in user_groups and not  adviser in user_groups:
            raise UserError(_("You do not have rights to access Unreconcile Entries"))
        return super(AccountUnreconcile, self).default_get(fields)
             