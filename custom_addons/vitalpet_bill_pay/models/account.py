from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, RedirectWarning, ValidationError
from odoo.http import request
import odoo

class AccountInvoice(models.Model):
    _inherit = "account.invoice"
    
    
    invoice_number = fields.Char('Invoice Number', size=30)
    acc_number_id = fields.Many2one('account.number', 'Account Number', domain="[('vendor_id','=',partner_id)]")
    partner_bank_id = fields.Many2one('res.partner.bank', string='Bank Account',
        help='Bank Account Number to which the invoice will be paid. A Company bank account if this is a Customer Invoice or Vendor Refund, otherwise a Partner bank account number.',
        readonly=True, states={'draft': [('readonly', False)], 'open': [('readonly', False)]})

    @api.model
    def create(self,vals):
        if vals.get('invoice_line_ids'):
            for order in vals.get('invoice_line_ids'):
                if order[2]['price_unit'] == 0:
                    raise UserError(_("Amount should be more than 0.0."))
        return super(AccountInvoice, self).create(vals)

    @api.multi
    def invoice_validate(self):
        for invoice in self:
            # refuse to validate a vendor bill/refund if there already exists one with the same reference for the same partner,
            # because it's probably a double encoding of the same bill/refund
            if invoice.type in ('in_invoice', 'in_refund') and invoice.reference:
                if self.search([('type', '=', invoice.type), ('reference', '=', invoice.reference), ('company_id', '=', invoice.company_id.id), ('commercial_partner_id', '=', invoice.commercial_partner_id.id), ('id', '!=', invoice.id),('state','!=','cancel')]):
                    raise UserError(_("Duplicated vendor reference detected. You probably encoded twice the same vendor bill/refund."))
        return self.write({'state': 'open'})


    @api.multi
    def _compute_attachment_number(self):
        for line in self:       
            attachment_data = self.env['ir.attachment'].search([('res_model', '=', 'billpay.bills'), ('res_id', '=', line.billpay_id.id), '|', ('res_field', '=', 'attachment'), ('res_field', '=', False)])       
            line.attachment_number = len(attachment_data)
        
    @api.multi
    def action_get_attachment_view(self):    
        res = self.env['ir.actions.act_window'].for_xml_id('base', 'action_attachment')         
        res['domain'] = [('res_model', '=', 'billpay.bills'), ('res_id', '=', self.billpay_id.id), '|', ('res_field', '=', 'attachment'), ('res_field', '=', False)]
        res['context'] = {'default_res_model': 'billpay.bills', 'default_res_id': self.billpay_id.id}
        return res
    
    
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
                    if inv.billpay_id and inv.billpay_id.due_date:
                        date_due = inv.billpay_id.due_date
                    else:
                        date_due = t[0]


                    iml.append({
                        'type': 'dest',
                        'name': name,
                        'price': t[1],
                        'account_id': inv.account_id.id,
                        'date_maturity': date_due,
                        'amount_currency': diff_currency and amount_currency,
#                         'currency_id': diff_currency and inv.currency_id.id,
                        'invoice_id': inv.id
                    })
            else:
                if inv.billpay_id and inv.billpay_id.due_date:
                    date_due = inv.billpay_id.due_date
                else:
                    date_due = inv.date_due

                iml.append({
                    'type': 'dest',
                    'name': name,
                    'price': total,
                    'account_id': inv.account_id.id,
                    'date_maturity': date_due,
                    'amount_currency': diff_currency and total_currency,
#                     'currency_id': diff_currency and inv.currency_id.id,
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
                'journal_id': journal.id,
                'date': date,
                'narration': inv.comment,
            }
            ctx['company_id'] = inv.company_id.id
            ctx['invoice'] = inv
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
            
        result = super(AccountInvoice, self).action_move_create()    
        for inv in self:
            context = dict(self.env.context)
            
            context.pop('default_type', None)
            inv.invoice_line_ids.with_context(context).asset_create()    
        return result   
    
    billpay_id = fields.Many2one('billpay.bills', string="Bill Pay Id", ondelete="restrict")
    billpay_ref = fields.Char(string="Bill Pay Ref")
    # invoice_number = fields.Char("Invoice Number")
    description = fields.Text("Description")
    attachment_number = fields.Integer(compute='_compute_attachment_number', string='Number of Attachments')
    notes = fields.Char("Notes")

    @api.multi
    def write(self, vals):
        if vals.get('invoice_line_ids'):
            for order in vals.get('invoice_line_ids'):
                if not order[2] == False:
                    if order[2].get('price_unit') == 0:
                        raise UserError(_("Amount should be more than 0.0."))
        res = super(AccountInvoice, self).write(vals)
        for item in self:
            state = item.state
            if state == 'paid' and vals.get('state') == 'paid':
                tid = self.env['account.payment.mode'].search([('name','=','ACH')])
                if tid:
                    if item.partner_id.supplier_payment_mode_id.name != 'ACH':
                        pay_line_obj = self.env['account.payment.line'].search([('invoice_id','=',item.id),('order_id.state','!=','cancel')])
                        if pay_line_obj.ach_sent == False:
                            item.partner_id.send_ach_signup_link(payment_send=1)
                            for payment_lines in item.payment_id.payment_line_ids:
                                if payment_lines.partner_id.id == pay_line_obj.partner_id.id:
                                    payment_lines.ach_sent = True
                                
                if item.billpay_id:
                    item.billpay_id.state="paid"
                    for line_id in item.billpay_id:
                        for line in line_id.bill_line_ids:
                            if line.invoice_id:
                                query = "UPDATE account_invoice set state='paid', residual=0.00, residual_signed=0.00 where id= %d" % line.invoice_id.id
                                self._cr.execute(query)
        return res
    
class AccountMove(models.Model):
    _inherit = "account.move"
    
    @api.multi
    def action_get_attachment_view(self):    
        res = self.env['ir.actions.act_window'].for_xml_id('base', 'action_attachment')         
        res['domain'] = [('res_model', '=', 'billpay.bills'), ('res_id', '=', self.billpay_id.id), '|', ('res_field', '=', 'attachment'), ('res_field', '=', False)]
        res['context'] = {'default_res_model': 'billpay.bills', 'default_res_id': self.billpay_id.id}
        return res
    


    @api.multi
    def post(self):
        invoice = self._context.get('invoice', False)
        self._post_validate()
        for move in self:
            move.line_ids.create_analytic_lines()
            print move
            if move.name == '/':
                new_name = False
                journal = move.journal_id

                if invoice and invoice.move_name and invoice.move_name != '/':
                    new_name = invoice.move_name
                else:
                    if journal.sequence_id:
                        # If invoice is actually refund and journal has a refund_sequence then use that one or use the regular one
                        sequence = journal.sequence_id
                        if invoice and invoice.type in ['out_refund', 'in_refund'] and journal.refund_sequence:
                            if not journal.refund_sequence_id:
                                raise UserError(_('Please define a sequence for the refunds'))
                            sequence = journal.refund_sequence_id

                        new_name = sequence.with_context(ir_sequence_date=move.date).next_by_id()

                        name_obj = self.env['account.move'].search_count([('name' , '=' , new_name)])

                        if name_obj > 0:
                            raise UserError('The journal entry reference is already created.So Please contact IT Support team')

                    else:
                        raise UserError(_('Please define a sequence on the journal.'))

                if new_name:
                    move.name = new_name
        return self.write({'state': 'posted'})
#   
    @api.multi
    def _compute_attachment_number(self):
        for line in self:  
            attachment_data = self.env['ir.attachment'].search([('res_model', '=', 'billpay.bills'), ('res_id', '=', line.billpay_id.id), '|', ('res_field', '=', 'attachment'), ('res_field', '=', False)])
            line.attachment_number = len(attachment_data)
        
    @api.multi
    def _reverse_move(self, date=None, journal_id=None):
        self.ensure_one()
        reversed_move = self.copy(default={
            'date': date,
            'journal_id': journal_id.id if journal_id else self.journal_id.id,
            'ref': _('reversal of: ') + self.name})
        for acm_line in reversed_move.line_ids:
            acm_line.with_context(check_move_validity=False).write({
                'debit': acm_line.credit,
                'credit': acm_line.debit,
                'amount_currency': -acm_line.amount_currency
            })
        self.write({'reverse_move_id':reversed_move.id})
        return reversed_move
      

    attachment_number = fields.Integer(compute='_compute_attachment_number', string='Number of Attachments')
    billpay_id = fields.Many2one('billpay.bills', string="Bill Pay Id", ondelete="restrict")
    description = fields.Text("Description")
    reverse_move_id = fields.Many2one('account.move', readonly=True, string="Reverse Journal Entry")
    dublicate_move_id = fields.Many2one('account.move')
    
    
class AccountJournal(models.Model):
    _inherit = "account.journal"

    bill_pay_journal = fields.Boolean( string="Bill Pay Journal")
    
class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    billpay_id = fields.Many2one('billpay.bills', string="Bill Pay", ondelete="restrict")
    
    
class account_payment(models.Model):
    _inherit = "account.payment"
    
     
    @api.multi
    def post(self):
        if self.env.context.get('active_id'):
            invoice=self.env['account.invoice'].search([('id','=',self.env.context['active_id'])])
            if invoice.billpay_id:
                invoice.billpay_id.state="paid"
        super(account_payment, self).post()

