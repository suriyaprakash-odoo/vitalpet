from odoo import api, fields, models, _
from odoo.exceptions import UserError 
import odoo.addons.decimal_precision as dp
from datetime import datetime
from dateutil import relativedelta as rdelta
from datetime import date
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError, UserError


# inherit res.partner.bank to change rec_name
class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'
    
    @api.multi
    @api.depends('acc_number', 'company_id')
    def name_get(self):
        result = []
        for item in self:
            if item.company_id:
                name = item.company_id.code+"-"+item.acc_number
            else:
                name = item.acc_number
                
            result.append((item.id, name))
        return result
    
class BillPayBills(models.Model):
    _name = 'billpay.bills'
    _inherit = ['mail.thread']
    _rec_name = 'bill_credit_id'
    _order = 'due_date asc'
    _description = "BillPay Bill"  

    @api.multi
    def cron_fetch_mails_call(self):
        self.env["fetchmail.server"]._fetch_mails()
        return True
    
    
    @api.multi
    def action_get_attachment_view(self):      
        res = self.env['ir.actions.act_window'].for_xml_id('base', 'action_attachment')       
        res['domain'] = [('res_model', '=', 'billpay.bills'), ('res_id', 'in', self.ids), '|', ('res_field', '=', 'attachment'), ('res_field', '=', False)]
        res['context'] = {'default_res_model': 'billpay.bills', 'default_res_id': self.id}
        return res


    @api.multi
    def action_get_accounting_entries(self):        
        ctx = dict()         
        return {
            'name': _('Journal Entry'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'view_id': False,
            'res_id':self.id ,
            'domain': [('billpay_id', '=', self.id or False)],
            'target': 'current',
            'context': ctx,
            }     
        

    @api.multi
    def _compute_attachment_number(self):
        attachment_data = self.env['ir.attachment'].read_group([('res_model', '=', 'billpay.bills'), ('res_id', 'in', self.ids)], ['res_id'], ['res_id'])
        attachment = dict((data['res_id'], data['res_id_count']) for data in attachment_data)
        for billapproval in self:
            billapproval.attachment_number = attachment.get(billapproval.id, 0)
        
    @api.multi
    @api.onchange('bill_date', 'partner_id')
    def _date_compute(self):
        for loop in self:
            bill_date = loop.bill_date
            
            payment_term_id = loop.partner_id.property_supplier_payment_term_id
            if not bill_date:
                loop.bill_date = fields.Date.context_today(bill_date)
            
            if not loop.partner_id.property_supplier_payment_term_id:
                # When no payment term defined
                loop.due_date = loop.due_date or loop.bill_date
                loop.original_due_date = loop.original_due_date or loop.bill_date
            else:
                pterm = payment_term_id
                pterm_list = pterm.with_context(currency_id=loop.company_id.currency_id.id).compute(value=1, date_ref=loop.bill_date)[0]
                loop.due_date = max(line[0] for line in pterm_list)
                loop.original_due_date = max(line[0] for line in pterm_list)


    
    def _compute_parent_company(self):
        billpay_settings = self.env['res.company'].search([('id', '=', self.env.user.company_id.id)])
        return billpay_settings.id    

    bill_credit_id = fields.Char('Bill Credit ID', readonly=True, copy=False, default='/')
    bill_credit_type = fields.Selection([('bill', 'Bill'), ('credit', 'Credit')], default='bill', string='Bill Credit Type', track_visibility='onchange')
    state = fields.Selection([
         ('open', 'Open'),
        ('hold', 'Hold'),
        ('toapprove', 'Awaiting Approval'),
        ('refuse', 'Refused'),
        ('approved', 'Approved'),
        ('posted', 'Posted'),
        ('cancel', 'Cancelled'),
        ('paid', 'Paid'),
        ], string='Status', readonly=True, copy=False, index=True, default='open', track_visibility='onchange')
    account_fiscal_periods_id = fields.Many2one('account.fiscal.period.lines', string="Fiscal Month",
                                                ondelete="restrict")
    account_fiscal_period_week_id = fields.Many2one('account.fiscal.period.week', string="Fiscal Week",
                                                    ondelete="restrict")
    account_fiscal_periods_quarterly = fields.Char(string="Fiscal Quarter")
    account_fiscal_periods_year = fields.Many2one('account.fiscal.periods',string = "Fiscal Year")
    submit_date = fields.Datetime(string='Submit Date', store=True, readonly=True, default=lambda self: fields.datetime.now(), track_visibility='onchange')
    bill_date = fields.Date(string='Bill Date', default=lambda self: fields.datetime.now(), copy=False, track_visibility='onchange')
    due_date = fields.Date(string='Due Date', copy=False,store=True)
    process_date = fields.Datetime(string='Process Date', track_visibility='onchange')
    purchase_id = fields.Many2one('purchase.order', string='Purchase Order', track_visibility='onchange')
    user_id = fields.Many2one('res.users', string='User', store=True, readonly=True, default=lambda self: self.env.user.id)
    partner_id = fields.Many2one('res.partner', string='Vendor', index=True, track_visibility='onchange')
    bill_credit_source = fields.Selection([('inbox', 'Inbox'), ('payable', 'Payable'),
                                           ('receivable', 'Receivable')], string='Source ', default='inbox', track_visibility='onchange')
    invoice_amount = fields.Float('Invoice Amount', default="0.00", required=True, digits=dp.get_precision('Amount'), track_visibility='onchange')
    invoice_number = fields.Char('Invoice Number', track_visibility='onchange', size=30)
    bill_line_ids = fields.One2many('billpay.lines', 'billpay_bill_id', 'BILL', required=True, ondelete='cascade', index=True, track_visibility='onchange')
    amount = fields.Monetary('Total', compute='_amount_compute', store=True, currency_field='currency_id', digits=dp.get_precision('Amount'))
    company_id = fields.Many2one('res.company', string='Company', store=True, readonly=True, track_visibility='onchange', default=_compute_parent_company)
    currency_id = fields.Many2one('res.currency', compute='_compute_currency_id', store=False)
    fiscal_position_id = fields.Many2one('account.fiscal.position', string='Fiscal Position', oldname='fiscal_position')
    split_difference_amount = fields.Float('Amount Difference', compute='_amount_compute', help="Display difference while doing split amount", default="0.00")
    attachment = fields.Binary('Attachment', attachment=True, track_visibility='onchange')
    attachment_text = fields.Text('Attachment', compute='_attachment_text')
    attachment_type = fields.Char('Attachment')
    day_since = fields.Char('Days Since Entered', copy=False, compute='_calculate_since', readonly=True)
    notes = fields.Text('Hold Reason', track_visibility='onchange')
    refuse_reason = fields.Text('Refuse Reason', track_visibility='onchange')
    attachment_number = fields.Integer(compute='_compute_attachment_number', string='Number of Attachments', track_visibility='onchange')
    invoice_id = fields.Many2one('account.invoice', 'Supplier Invoice')
    invoice_state = fields.Char('Invoice State', copy=False)
    vendor_ref = fields.Char('Vendor Reference', track_visibility='onchange')
    inbox_id = fields.Many2one('billpay.inbox')
    account_move_id = fields.Many2one('account.move', string='Journal Entry', copy=False)
    description = fields.Text("Description")
    note = fields.Char("Notes")
    vendor_payment_terms_id = fields.Many2one("account.payment.term", related='partner_id.property_supplier_payment_term_id', string="Vendor Payment Terms", store=True)
    account_receivable_id = fields.Many2one("account.account", related='partner_id.property_account_receivable_id', string="Account Receivable", store=True)
    account_payable_id = fields.Many2one("account.account", related='partner_id.property_account_payable_id', string="Account Payable", store=True)
    reversal_reason = fields.Text("Reversal Reason", track_visibility='onchange')
    journal_id = fields.Many2one('account.journal', 'Journal', domain="[('type','=','purchase'),('company_id', '=', company_id)]")
    acc_number_id = fields.Many2one('account.number', 'Account Number', domain="[('vendor_id','=',partner_id)]")
    payment_mode_id = fields.Many2one('account.payment.mode', string="Payment Mode",ondelete='restrict',readonly=True, states={'open': [('readonly', False)]})
    partner_bank_id = fields.Many2one('res.partner.bank', string='Bank Account',
                                      help='Bank Account Number to which the invoice will be paid. A Company bank account if this is a Customer Invoice or Vendor Refund, otherwise a Partner bank account number.',
                                      readonly=True, states={'open': [('readonly', False)]})
    bank_account_required = fields.Boolean(
        related='payment_mode_id.payment_method_id.bank_account_required',
        readonly=True)
    over_write_duedate = fields.Boolean('Over Write DueDate',track_visibility='onchange')
    original_due_date = fields.Date(string='Original Due Date')
    _sql_constraints = [
        ('inv_vendor_uniq', 'unique (vendor_ref,partner_id)', 'Vendor reference must be unique per Vendor !'),
    ]
     
    
    @api.depends('company_id')
    @api.multi
    def _compute_currency_id(self):
        for res in self:
            res.currency_id=res.company_id.currency_id.id
            
    @api.multi
    def action_set_vendor_account(self):
        receivable_acc = self.env['account.account'].search([('company_id','=',self.env.user.company_id.id),('internal_type', '=', 'receivable')])
        payable_acc = self.env['account.account'].search([('company_id','=',self.env.user.company_id.id),('internal_type', '=', 'payable')])
        vendor_obj = self.env['res.partner'].search([('id','=',self.partner_id.id)])
        if vendor_obj:
            vendor_obj.property_account_receivable_id = receivable_acc.id
            vendor_obj.property_account_payable_id = payable_acc.id
        
    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id:
            pay_mode = self.partner_id.supplier_payment_mode_id
            self.payment_mode_id = pay_mode
            
            bank_account = self.env['res.partner.bank'].search([('partner_id', '=', self.partner_id.id)])
            if bank_account and self.payment_mode_id.name == 'ACH':
                self.partner_bank_id = bank_account[0].id
                
            
        if self.acc_number_id:
            self.acc_number_id = False
            
    
    # onchange invoice number and account number
    @api.onchange('invoice_number', 'acc_number_id')
    def _onchange_vendor_ref(self):
        for line in self:
            if line.invoice_number and line.acc_number_id:
                if line.acc_number_id.company_id:
                    line.vendor_ref = "INV[" + line.invoice_number + "]ACCT[" + line.acc_number_id.company_id.code +"-" + line.acc_number_id.account_number  + "]"
                else:
                    line.vendor_ref = "INV[" + line.invoice_number + "]ACCT["+line.acc_number_id.account_number  + "]"
            elif line.invoice_number:
                line.vendor_ref = "INV[" + line.invoice_number + "]"
            elif line.acc_number_id:
                if line.acc_number_id.company_id:
                    line.vendor_ref = "ACC[" + line.acc_number_id.company_id.code  +"-" +  line.acc_number_id.account_number + "]"
                else:
                    line.vendor_ref = "ACC[" + line.acc_number_id.account_number + "]"
            
            
    @api.onchange('bill_date')
    def get_account_fiscal_periods(self):
        if self.company_id.calendar_type:
            account_fiscal_periods = self.env['account.fiscal.periods'].search([('calendar_type', '=', self.company_id.calendar_type.id)])
            if account_fiscal_periods :
                period = self.env['account.fiscal.period.lines'].search(
                    [('account_fiscal_period_id', 'in', [a.id for a in account_fiscal_periods]),
                     ('date_start', '<=', self.bill_date), ('date_end', '>=', self.bill_date)])
                if period :
                    self.account_fiscal_periods_id = period.id
                    self.account_fiscal_periods_quarterly = period.quarter
                    self.account_fiscal_periods_year = period.account_fiscal_period_id
                period_week = self.env['account.fiscal.period.week'].search(
                    [('account_fiscal_period_id', 'in', [a.id for a in account_fiscal_periods]),
                     ('date_start', '<=', self.bill_date), ('date_end', '>=', self.bill_date)])
                if period_week:
                    self.account_fiscal_period_week_id = period_week.id
                    

# Hold multiple bills from tree view and the state should be open
    @api.multi
    def submit_on_hold(self):
        active_ids = []
        context = dict(self._context)
        for bill in self:
            active_ids.append(bill.id)
            if bill.state not in ['open','toapprove']:
                raise UserError(_('Bills can only hold in Open and Awaiting Approval state'))
        context['active_ids'] = active_ids
        return {
            'name': _('Hold Reason'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'hold.reason.wizard',
            'view_id': self.env.ref('vitalpet_bill_pay.hold_reason_wizard_view_form').id,
            'type': 'ir.actions.act_window',
            'context': context,
            'target': 'new'
        }
        
# Hold multiple bills from tree view and the state should be open
    @api.multi
    def submit_on_refuse(self):
        active_ids = []
        context = dict(self._context)
        for bill in self:
            active_ids.append(bill.id)
            if bill.state in ['posted']:
                raise UserError(_('Posted bills can not be refuse'))
        context['active_ids'] = active_ids
        return {
            'name': _('Refuse Reason'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'refuse.reason.wizard',
            'view_id': self.env.ref('vitalpet_bill_pay.refuse_reason_wizard_view_form').id,
            'type': 'ir.actions.act_window',
            'context': context,
            'target': 'new'
        }
        
    @api.multi
    def action_popup_image(self):
        active_ids = []
        context = dict(self._context)
        for bill in self:
            active_ids.append(bill.id)
            
#         context['attachment'] = bill.attachment
        context['default_attachment'] = bill.attachment
        return {
            'name': _('Image'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'popup.image.wizard',
            'view_id': self.env.ref('vitalpet_bill_pay.popup_image_wizard_view_form').id,
            'type': 'ir.actions.act_window',
            'context': context,
            'target': 'new'
        }

    @api.multi
    @api.depends('bill_line_ids.price_subtotal')
    def _amount_compute(self):
        for bill in self:
            total = 0.0
            for line in bill.bill_line_ids:
                total += line.price_subtotal
            bill.amount = total
            diff = float(bill.invoice_amount) - float(bill.amount)
            bill.split_difference_amount = diff

    @api.multi
    @api.depends('bill_line_ids.price_subtotal')
    def _attachment_text(self):
        for attachment in self:         
            attachment.attachment_text = '/web/image?model=billpay.bills&id=' + str(attachment.id) + '&field=attachment'
#             self._cr.execute("""SELECT attachment from billpay_bills where id = %s""" % (attachment.id))
#             tot_qty = self._cr.fetchall()
#             attachment.attachment_text=tot_qty[0][0]

    @api.multi
    @api.depends('submit_date')
    def _calculate_since(self):
        for bill in self:
            start = datetime.strptime(bill.submit_date, '%Y-%m-%d %H:%M:%S')
            ends = datetime.now()
            diff_days = ends - start
            bill.day_since = diff_days.days

    @api.multi
    def action_bill_validate(self):
        # lots of duplicate calls to action_invoice_open, so we remove those already open
        commpany_obj = self.env['res.company'].search([('id', '=', self.env.user.company_id.id)], limit=1)
        for bills in self:
            if not bills.bill_credit_type:
                raise UserError(_('Please choose bill type.'))
            if not bills.partner_id:
                raise UserError(_('Please select vendor.'))
#             if not bills.invoice_number:
#                 raise UserError(_('Please enter invoice number.'))
            if not bills.bill_line_ids:
                raise UserError(_('Please create some bill lines.'))
            
            if commpany_obj.po_required_amount != 0 and commpany_obj.po_required_amount <= bills.invoice_amount and not bills.purchase_id:
                raise UserError(_('Please attach purchase order.'))
            for line in bills.bill_line_ids:
                if not line.account_id:
                    raise UserError(_('Please Select Account.'))
                if line.price_subtotal == 0.0:
                    raise UserError(_('Amount should be more than 0.0.'))
            invoice_amount = bills.invoice_amount
            total_amount = 0.00
            for line_ids in bills.bill_line_ids:
                total_amount += line_ids.price_subtotal
            
            if round(invoice_amount,2) != round(total_amount,2):
                raise UserError(_('Invoice amount and Total amount should be equal.'))

            if self.invoice_amount > 0:
                vals = {}
                sequence = self.env['ir.sequence'].next_by_code('billpay.bills') or '/'
                prefix = commpany_obj.intercompany_id_prefix
        # Fixme: Values need to be taken from readonly field
                bill_date = datetime.today().strftime('%d%m%y')
                submit_date = datetime.today().strftime('%H%M')
                billpay_settings = self.env['res.company'].search([('id', '=', self.env.user.company_id.id)]).ensure_one()
                company_code = billpay_settings.id
                bill_credit_id = str(prefix) + str(company_code) + str(bill_date) + str(submit_date) + str(self.env.user.id) + str(sequence)
                bills.bill_credit_id = bill_credit_id
# If auto post enable follow approve process
                if commpany_obj.bill_approval_amount <= self.invoice_amount:
                    bills.state = 'toapprove'
# IF auto post not enabled  and approve amout is greater
                else:
                    bills.state = 'approved'
            if bills.state == 'approved' and commpany_obj.auto_post_bills:
                self.action_bill_post()
            
        self.process_date= str(date.today())

    @api.multi
    def action_set_to_open(self):
        # lots of duplicate calls to action_invoice_open, so we remove those already open
        for bills in self:
            bills.state = 'open'

    @api.multi
    def action_bill_split_amount(self):
        # lots of duplicate calls to action_invoice_open, so we remove those already open
        for bills in self:
            invoice_amount = bills.invoice_amount
            total_amount = 0.00
            if len(bills.bill_line_ids) > 0:
                no_of_items = len(bills.bill_line_ids)
                amount = invoice_amount / no_of_items
                for line in bills.bill_line_ids:
                    split_amount = str(amount).split('.')
                    split_amount = split_amount[0] + '.' + split_amount[1][:2]
                    split_amount = float(split_amount)
                    total_amount += split_amount
                    line.quantity = 1
                    line.price_unit = split_amount
                    line.price_subtotal = split_amount                
                balance_amount = invoice_amount - total_amount
                bills.split_difference_amount = balance_amount

            else:
                raise UserError(_('Please create some bill lines.'))
            
            if balance_amount != 0.0:
                line.price_unit = split_amount + balance_amount
    
    @api.multi
    def action_bill_apply_product(self):
        # lots of duplicate calls to action_invoice_open, so we remove those already open
        product_id = ''
        for bills in self:
            for line_ids in bills.bill_line_ids:
                if product_id == '':
                    if line_ids.product_id:
                        product_id = line_ids.product_id
                    else:
                        raise UserError(_('Please select product for bill lines.'))
                else:
                    if not line_ids.product_id:
                        line_ids.product_id = product_id
                        line_ids._onchange_product_id()
                        
    @api.multi
    def action_all_company(self):
        # List all companies in items
        temp = []
        for company in self.company_id.allowed_companies:
            vals = []
            temp.append([0, 0, {'company_id':company.id, 'allowed_companies':self.company_id.allowed_companies}])
        self.bill_line_ids = temp
            
    @api.model
    def create(self, vals):
        if not vals.get('due_date'):
            bill_date = vals.get('bill_date')
            partner_id = self.env['res.partner'].browse(vals.get('partner_id'))
            payment_term_id = partner_id.property_supplier_payment_term_id
            company_id = self.env['res.company'].browse(vals.get('company_id'))
            if not bill_date:
                bill_date = fields.Date.context_today(bill_date)
            
            if not partner_id.property_supplier_payment_term_id:
                # When no payment term defined
                vals['due_date'] = bill_date
            else:
                pterm = payment_term_id
                pterm_list = pterm.with_context(currency_id=company_id.currency_id.id).compute(value=1, date_ref=bill_date)[0]
                vals['due_date'] = max(line[0] for line in pterm_list)
        vals['state'] = 'open'
# Get bill config settings
        commpany_obj = self.env['res.company'].search([('id', '=', self.env.user.company_id.id)], limit=1)
        company = self.env['res.company'].search([('id', '=', commpany_obj.id)])
        account_fiscal_periods = self.env['account.fiscal.periods'].search([('calendar_type', '=', company.calendar_type.id)])
        
    
        if vals.get('invoice_number') and vals.get('acc_number_id'):
            acc=self.env['account.number'].search([('id','=',vals.get('acc_number_id'))])
            if acc.company_id:
                vals['vendor_ref'] = "INV[" + vals.get('invoice_number') + "]ACCT[" + acc.company_id.code +"-" + acc.account_number  + "]"
            else:
                vals['vendor_ref'] = "INV[" + vals.get('invoice_number') + "]ACCT["+acc.account_number  + "]"
        elif vals.get('invoice_number'):
            vals['vendor_ref'] = "INV[" + vals.get('invoice_number') + "]"
        elif vals.get('acc_number_id'):
            acc=self.env['account.number'].search([('id','=',vals.get('acc_number_id'))])
            if acc.company_id:
                vals['vendor_ref'] = "ACC[" + acc.company_id.code  +"-" +  acc.account_number + "]"
            else:
                vals['vendor_ref'] = "ACC[" + acc.account_number + "]"
        
     
        if (vals.get('invoice_amount')) == 0.0:
            raise ValidationError(_('Please enter a valid invoice amount'))   
            
        if account_fiscal_periods:
            period = self.env['account.fiscal.period.lines'].search([('account_fiscal_period_id', 'in', [a.id for a in account_fiscal_periods]), ('date_start', '<=', vals.get('bill_date')), ('date_end', '>=', vals.get('bill_date'))])
            if period:
                vals['account_fiscal_periods_id'] = period.id
                vals['account_fiscal_periods_quarterly'] = period.quarter
                vals['account_fiscal_periods_year'] = period.account_fiscal_period_id.id
            else:
                vals['account_fiscal_periods_id'] = ''
                vals['account_fiscal_periods_quarterly'] = ''
                vals['account_fiscal_periods_year'] = ''
                
            period_week = self.env['account.fiscal.period.week'].search([('account_fiscal_period_week_id', 'in', [a.id for a in account_fiscal_periods]), ('date_start', '<=', vals.get('bill_date')), ('date_end', '>=', vals.get('bill_date'))])
            if period_week:
                vals['account_fiscal_period_week_id'] = period_week.id
            else:
                vals['account_fiscal_period_week_id'] = ''
        if 'vendor_ref' in vals:
            vendor_ref_count = self.env['billpay.bills'].search_count([('vendor_ref', '=', vals['vendor_ref'])])
            if vendor_ref_count>0:
                raise ValidationError(_('Vendor reference already used'))
            
        bill_obj = super(BillPayBills, self).create(vals)
        if vals.get('bill_line_ids', False):
            i = 0
            for line in vals.get('bill_line_ids', False):
                if line[2]:
                    bill_obj._post_messages_line_items(line[2], i, line[1])
                i += 1
        if bill_obj:
            bill_obj.inbox_id.write({'state': 'processed'})
        for line in bill_obj.bill_line_ids:
            line.billpay_bill_id = bill_obj.id
        
        
        if bill_obj.due_date != bill_obj.original_due_date:
            message_id = bill_obj.message_post(body=_('Due date updated'))
            bill_obj._add_post_message_values(message_id, 'due_date', 'Due Date', "Original due date "+bill_obj.original_due_date, "Updated due date"+bill_obj.due_date)
        return bill_obj
    
    def get_id_name(self, model_name, id):
        value = self.env[model_name].search([('id', '=', id)])
        return value.name
        
    def _post_messages_line_items(self, line, i, line_id):
        
        if line_id:           
            message_id = self.message_post(body=_('Default message'))
            if message_id:
                if line.has_key('company_id'): 
                    self._add_post_message_values(message_id, 'company_id', 'Company', self.bill_line_ids[i].company_id.name, self.get_id_name('res.company', line['company_id']))
                if line.has_key('product_id'): 
                    self._add_post_message_values(message_id, 'product_id', 'Product', self.bill_line_ids[i].product_id.name, self.get_id_name('product.product', line['product_id']))
                if line.has_key('name'): 
                    self._add_post_message_values(message_id, 'name', 'Product Description', self.bill_line_ids[i].name, line['name'])
                if line.has_key('account_id'): 
                    self._add_post_message_values(message_id, 'account_id', 'Account', self.bill_line_ids[i].account_id.name, self.get_id_name('account.account', line['account_id']))
                if line.has_key('asset_category'): 
                    self._add_post_message_values(message_id, 'asset_category', 'Asset Category', self.bill_line_ids[i].asset_category.name, self.get_id_name('account.asset.category', line['asset_category']))
                if line.has_key('account_analytic_id'): 
                    self._add_post_message_values(message_id, 'account_analytic_id', 'Analytic Account', self.bill_line_ids[i].account_analytic_id.name, self.get_id_name('account.analytic.account', line['account_analytic_id']))
                if line.has_key('description'): 
                    self._add_post_message_values(message_id, 'description', 'Description', self.bill_line_ids[i].description, line['description'])
                if line.has_key('quantity'): 
                    self._add_post_message_values(message_id, 'quantity', 'Quantity', self.bill_line_ids[i].quantity, line['quantity'])
                if line.has_key('price_unit'): 
                    self._add_post_message_values(message_id, 'price_unit', 'Unit Price', self.bill_line_ids[i].price_unit, line['price_unit'])
                if line.has_key('price_subtotal'): 
                    self._add_post_message_values(message_id, 'price_subtotal', 'Amount', self.bill_line_ids[i].price_subtotal, line['price_subtotal'])
                    self.message_post(body=_('Line item  %s updated .') % (i + 1))
        else:
            message_new_id = self.message_post(body=_('Line item  %s created .') % (i + 1))
            if line.has_key('company_id'): 
                self._add_post_message_values(message_new_id, 'company_id', 'Company', '', self.get_id_name('res.company', line['company_id']))
            if line.has_key('product_id'): 
                self._add_post_message_values(message_new_id, 'product_id', 'Product', '', self.get_id_name('product.product', line['product_id']))
            if line.has_key('name'): 
                self._add_post_message_values(message_new_id, 'name', 'Product Description', '', line['name'])
            if line.has_key('account_id'): 
                self._add_post_message_values(message_new_id, 'account_id', 'Account', '', self.get_id_name('account.account', line['account_id']))
            if line.has_key('asset_category'): 
                self._add_post_message_values(message_new_id, 'asset_category', 'Asset Category', '', self.get_id_name('account.asset.category', line['asset_category']))
            if line.has_key('account_analytic_id'): 
                self._add_post_message_values(message_new_id, 'account_analytic_id', 'Analytic Account', '', self.get_id_name('account.analytic.account', line['account_analytic_id']))
            if line.has_key('description'): 
                self._add_post_message_values(message_new_id, 'description', 'Description', '', line['description'])
            if line.has_key('quantity'): 
                self._add_post_message_values(message_new_id, 'quantity', 'Quantity', '', line['quantity'])
            if line.has_key('price_unit'): 
                self._add_post_message_values(message_new_id, 'price_unit', 'Unit Price', '', line['price_unit'])
            if line.has_key('price_subtotal'): 
                self._add_post_message_values(message_new_id, 'price_subtotal', 'Amount', '', line['price_subtotal'])
        
            self.message_post(body=_('Line item  %s created .') % (i + 1))
                
    def _add_post_message_values(self, message_id, field, field_desc, old_value_char, new_value_char):
        vals = {}
        vals['field'] = field
        vals['field_desc'] = field_desc
        vals['mail_message_id'] = message_id.id
        vals['new_value_char'] = new_value_char
        vals['old_value_char'] = old_value_char
        self.env['mail.tracking.value'].create(vals)
    
    @api.multi
    def write(self, vals):
       
        if vals.get('invoice_number') and vals.get('acc_number_id'):
            acc=self.env['account.number'].search([('id','=',vals.get('acc_number_id'))])
            if acc.company_id:
                vals['vendor_ref'] = "INV[" + vals.get('invoice_number') + "]ACCT[" + acc.company_id.code +"-" + acc.account_number  + "]"
            else:
                vals['vendor_ref'] = "INV[" + vals.get('invoice_number') + "]ACCT["+acc.account_number  + "]"
        elif vals.get('invoice_number'):
            vals['vendor_ref'] = "INV[" + vals.get('invoice_number') + "]"
        elif vals.get('acc_number_id'):
            acc=self.env['account.number'].search([('id','=',vals.get('acc_number_id'))])
            if acc.company_id:
                vals['vendor_ref'] = "ACC[" + acc.company_id.code  +"-" +  acc.account_number + "]"
            else:
                vals['vendor_ref'] = "ACC[" + acc.account_number + "]"
                
        if (vals.get('invoice_amount')) == 0.0:
            raise ValidationError(_('Please enter a valid invoice amount'))
        
        bill_credit_id = self.bill_credit_id
        
        if vals.get('bill_line_ids', False):
            i = 0
            for line in vals.get('bill_line_ids', False):
                if line[2]:
                    line[2].update({'billpay_bill_id':self.id})
                    line[2].update({'bill_id' : self.bill_credit_id})
                    self._post_messages_line_items(line[2], i, line[1])
                i += 1
        for line in self.bill_line_ids:
            line.billpay_bill_id = self.id
            line.bill_id = bill_credit_id
            
        if vals.get('due_date'):
            if vals.get('original_due_date'):
                original_due_date = vals.get('original_due_date')
            else:
                original_due_date = self.original_due_date


            if vals.get('due_date'):
                due_date = vals.get('due_date')

            if original_due_date != due_date:
                message_id = self.message_post(body=_('Default message'))
                self._add_post_message_values(message_id, 'original_due_date', 'Due date', 'Original Due Date '+original_due_date, "Updated Due Date "+due_date)
        return super(BillPayBills, self).write(vals)
    
    
# Approve bills at a time
    @api.multi
    def approve_bills(self):
        user_sc_admin = self.env.ref('vitalpet_bill_pay.group_billpay_approver').users
        user_sc_admin_ids = [user.id for user in user_sc_admin]
        if self.env.uid in user_sc_admin_ids:
            for bill in self:
                if bill.state != 'toapprove':
                    raise UserError(_('You can only approve bills in Awaiting Approval State')) 
                bill.state = 'approved'
        else:
            raise ValidationError("You don't have access to approve bills")
            
    @api.multi
    def approve_bills_rev(self):
        
        for bill in self:   
            if bill.state != 'reversal':
                raise UserError(_('You can only approve bills in Reversal Approval State'))  
            
            if bill:
                account_move = self.env['account.move'].search([('billpay_id', '=', bill.id)])
                for i in account_move:
                    res = i.reverse_moves(self.bill_date)
                    res_move = self.env['account.move'].search([('id', '=', res[0])])
                    res_move.write({'state':'draft'})                 
           
            if res:
                bill.write({'state':'reverse','reversal_reason':self.reversal_reason})
                account_move = self.env['account.move'].search([('billpay_id', '=', bill.id)])
                return {
                    'name': _('Reverse Moves'),
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'res_model': 'account.move',
                    'domain': [('id', 'in', [i.id for i in account_move])],
                }
            return {'type': 'ir.actions.act_window_close'}

                 
            bill.state = 'reverse'
        
# Post bills to pay
    @api.multi
    def action_bill_post(self):
        # Parent Level Intercompany Flow
        for bill in self:
            if bill.bill_credit_type == 'bill':
                    account_debit = 'debit'
                    account_credit = 'credit'
                    invoice_type = 'in_invoice'
                
            if bill.bill_credit_type == 'credit':
                account_debit = 'credit'
                account_credit = 'debit'
                invoice_type = 'in_refund'
            invoice_vals = {}
            # Get bill config settings
            company_obj = self.env['res.company'].search([('id', '=', self.env.user.company_id.id)], limit=1)
            if not company_obj:
                raise UserError(_('Billpay parent company configuration not found'))
            if not company_obj.billpay_processing_company:
                raise UserError(_('Could not find bill payment parent company in settings'))
            if not company_obj.billpayment_journal:
                raise UserError(_('Could not find bill payment journal company in settings'))
            
            
            if bill.note:
                bill_description = bill.note
            else:
                bill_description = "/"

            invoice_vals = {}
            val = {}
            line_ids = []
            val.update({
                'name': bill_description,
                'company_id': company_obj.id,
                'account_id': company_obj.intercompany_expense_account.id,
                'uom_id' : bill.bill_line_ids[0].uom_id.id,
                'quantity' : 1,
                'description': bill_description,
#                 'asset_category' : bill.bill_line_ids[0].asset_category.id,
                'price_unit' : bill.invoice_amount,
                'account_analytic_id' : bill.bill_line_ids[0].account_analytic_id.id,
                'analytic_tag_ids' : [(6, 0, [a.id for a in bill.bill_line_ids[0].analytic_tag_ids])],
                'billpay_id' : bill.id

                
            })
            line_ids.append((0, 0, val))
            if bill.acc_number_id:
                account_number_id = bill.acc_number_id.id
            else:
                account_number_id = False

            invoice_vals.update({
                'name': '',
                'partner_id': bill.partner_id.id,
                'date_invoice': bill.bill_date,
                'date_due': bill.due_date,
                'invoice_number':bill.invoice_number,
                'acc_number_id':account_number_id,
                'date': bill.bill_date,
                'journal_id':bill.journal_id.id,
                'purchase_id': bill.purchase_id.id,
                'company_id': bill.company_id.id,
                'reference':bill.vendor_ref,
                'amount_total':bill.invoice_amount,
                'invoice_line_ids': line_ids,
                'billpay_id' : bill.id,
                'notes' : bill.note,
                'payment_mode_id':bill.payment_mode_id.id,
                'partner_bank_id':bill.partner_bank_id.id

            })
            invoice = self.env['account.invoice'].with_context({'type': invoice_type}).create(invoice_vals)
            invoice.action_invoice_open()
            if bill.due_date:
                invoice.date_due = bill.due_date
            invoice.move_id.write({'billpay_id':bill.id, 'description':bill.note})
# Child level intercompany
            for line in bill.bill_line_ids:                
                    
                account_move = self.env['account.move']
                billpay_account = self.env['account.account'].search([('company_id', '=', line.company_id.id), ('tag_ids', '=', company_obj.child_intercompany_account.id)])
                if not billpay_account:
                    raise UserError('Could not find account with ' + company_obj.child_intercompany_account.name + ' for ' + line.company_id.name)
                if not line.company_id.child_billpay_journal:
                    raise UserError('Could not find billpay journal for ' + line.company_id.name + '. Please configure in company settings ')
                if len(billpay_account) > 1:
                    raise UserError('More than one acount mapped with ' + company_obj.child_intercompany_account.name + ' for ' + line.company_id.name)
                move_sequence = line.company_id.child_billpay_journal.sequence_id
                new_name = move_sequence.with_context(ir_sequence_date=bill.bill_date).next_by_id()
                move_vals = {}
                opposite_move_vals = {}
                move_line_ids = []
                if line.price_subtotal < 0:
                    if bill.bill_credit_type == 'bill':
                        price_subtotal = line.price_subtotal * (-1)
                        account_debit = 'credit'
                        account_credit = 'debit'
                    if bill.bill_credit_type == 'credit':
                        price_subtotal = line.price_subtotal * (-1)
                        account_debit = 'debit'
                        account_credit = 'credit'
                else:
                    if bill.bill_credit_type == 'bill':
                        account_debit = 'debit'
                        account_credit = 'credit'
                    if bill.bill_credit_type == 'credit':
                        account_debit = 'credit'
                        account_credit = 'debit'
                        
                    price_subtotal = line.price_subtotal

                move_vals.update({
                    'name': new_name,
#                     'company_id': line.company_id.id,
                    'account_id': line.account_id.id,
                    'product_id': line.product_id.id,
                    'partner_id': bill.partner_id.id,
                    'product_id': line.product_id.id,
                    account_debit : round(price_subtotal,2),
                    'analytic_account_id' : line.account_analytic_id.id,
                    'billpay_id' : bill.id,
                    'date':bill.bill_date,
                    'date_maturity':bill.due_date
                })
                opposite_move_vals.update({
                    'name': new_name,
#                     'company_id': line.company_id.id,
                    'account_id': billpay_account.id,
                    'partner_id': bill.partner_id.id,
                    account_credit : round(price_subtotal, 2),
                    'analytic_account_id' : line.account_analytic_id.id,
                    'billpay_id' : bill.id,
                    'date':bill.bill_date,
                    'date_maturity':bill.due_date
                })
                move_line_ids.append((0, 0, move_vals))
                move_line_ids.append((0, 0, opposite_move_vals))
                
                description = bill.note
                move_vals.update({
                    'ref':bill.vendor_ref,
                    'journal_id': line.company_id.child_billpay_journal.id,
                    'date': bill.bill_date,
#                     'company_id': line.company_id.id,
                    'amount_total':line.price_unit,
                    'line_ids': move_line_ids,
                    'billpay_id' : bill.id,
                    'description' : description
                })
                move_ids = account_move.create(move_vals)

                if line.payable_receivable_move_line_id:
                    line.payable_receivable_move_line_id.write({'billpay_id':bill.id})
        bill.state = 'posted'
        
        for line in self.bill_line_ids:
            if line.asset_category:
                vals = {
                        'name': line.name,
                        'code': line.name,
                        'category_id': line.asset_category.id,
                        'value': line.price_subtotal,
                        'partner_id': self.partner_id.id,
                        'company_id': line.company_id.id,
                        #'currency_id': line.invoice_id.company_currency_id.id,
                        'date': self.bill_date,
                        
                        'method_number':line.asset_category.method_number,
                        'method_period':line.asset_category.method_period,
                        'method':line.asset_category.method,
                        'method_time':line.asset_category.method_time,
                        'prorata':line.asset_category.prorata,
                        'bill_id' : self.bill_credit_id,
                        }
                if line.asset_category.method_time == 'end' and not line.asset_category.method_end:
                    raise UserError(_('Please update ending date in asset category - %s.') % line.asset_category.name)

                if line.asset_category.method_end:
                    vals['method_end'] = line.asset_category.method_end
                asset = self.env['account.asset.asset'].create(vals)
    
    @api.multi
    def action_bill_cancel(self):
        moves = self.env['account.move']
        invoices = self.env['account.invoice'].search([('billpay_id', '=', self.id), ('state','!=', 'cancel')])
        for inv in invoices:
            if inv.move_id:
                moves += inv.move_id
            if inv.payment_move_line_ids:
                raise UserError(_('You cannot cancel an invoice which is partially paid. You need to unreconcile related payment entries first.'))

        # First, set the invoices as cancelled and detach the move ids
        invoices.write({'state': 'cancel', 'move_id': False})
        if moves:
            # second, invalidate the move(s)
            moves.button_cancel()
            # delete the move this invoice was pointing to
            # Note that the corresponding move_lines and move_reconciles
            # will be automatically deleted too
            moves.unlink()
            
        moves = self.env['account.move'].search([('billpay_id', '=', self.id)])
        for move in moves:
            move.button_cancel()
            # delete the move this invoice was pointing to
            # Note that the corresponding move_lines and move_reconciles
            # will be automatically deleted too
            move.unlink()
        self.state = 'cancel'
    
        assets= self.env['account.asset.asset'].search([('bill_id', '=', self.bill_credit_id)])
        for line in assets:
            if line.state == 'draft':
                line.unlink()
            else:
                raise UserError(_('The state has been already moved from draft to running in assets.'))
        return True

class BillPayLines(models.Model):
    _name = 'billpay.lines'
    
    @api.one
    @api.depends('price_unit', 'quantity')
    def _compute_price(self):
        self.price_subtotal = self.quantity * self.price_unit
    
    
    @api.model
    def default_get(self, fields):
        res = super(BillPayLines, self).default_get(fields)
        if self.env.context.get('company_id', False):
            company_obj = self.env['res.company']
            if company_obj.browse(self.env.context['company_id']).allowed_companies:
                allowed_companies = [i.id for i in company_obj.browse(self.env.context['company_id']).allowed_companies]
                res.update({'allowed_companies': [(6, 0, allowed_companies)]})
            else:
                raise UserError('Please configure allowed companies, Contact administrator')

        return res
    
    name = fields.Text('Description', track_visibility='onchange', default=' ')
    bill_id = fields.Char('Bill Ref ID', readonly=True, store=True)
    billpay_bill_id = fields.Many2one('billpay.bills', 'Bill Approval Ref ID')
    allowed_companies = fields.Many2many("res.company", string="Allowed Companies")
    company_id = fields.Many2one('res.company', 'Company', track_visibility='onchange')
    product_id = fields.Many2one('product.product', string='Product', ondelete='restrict', index=True, track_visibility='onchange')
    asset_category = fields.Many2one('account.asset.category', string='Asset Category', ondelete='restrict', index=True, track_visibility='onchange')
    account_id = fields.Many2one('account.account', string='Account',
                                 help="The income or expense account related to the selected product.", company_dependent=True, track_visibility='onchange')
    account_analytic_id = fields.Many2one('account.analytic.account', string='Analytic Account', track_visibility='onchange')
    analytic_tag_ids = fields.Many2many(related="account_analytic_id.tag_ids" , string='Analytic Tags', track_visibility='onchange')
    quantity = fields.Float(string='Quantity', digits=dp.get_precision('Quantity'), required=True, default=1, track_visibility='onchange')
    price_unit = fields.Float(string='Unit Price', required=True, digits=dp.get_precision('Product Price'), track_visibility='onchange')
    bill_line_tax_ids = fields.Many2many('account.tax', string='Taxes', domain=[('type_tax_use', '!=', 'none'), '|', ('active', '=', False), ('active', '=', True)], track_visibility='onchange')
    price_subtotal = fields.Monetary(string='Amount', currency_field='currency_id',
        store=True, readonly=True, compute='_compute_price', track_visibility='onchange')
    currency_id = fields.Many2one('res.currency', compute='_compute_currency_id', store=False)
    uom_id = fields.Many2one('product.uom', string='Unit of Measure', ondelete='set null', index=True, oldname='uos_id', track_visibility='onchange')
    payable_receivable_move_line_id = fields.Many2one('account.move.line')
    invoice_id = fields.Many2one('account.invoice', 'Invoice Id')

    @api.depends('company_id')
    @api.multi
    def _compute_currency_id(self):
        for res in self:
            res.currency_id=res.company_id.currency_id.id
            
    def _set_taxes(self):
        """ Used in on_change to set taxes and price."""
        taxes = self.product_id.supplier_taxes_id or self.account_id.tax_ids
        # Keep only taxes of the company
        company_id = self.company_id
        taxes = taxes.filtered(lambda r: r.company_id == company_id)
        fix_price = self.env['account.tax']._fix_tax_included_price

    @api.onchange('company_id')
    def _onchange_company_id(self):
        self.account_id = ''
        self.name = ''
        self.asset_category = ''
        self.account_analytic_id = ''   
        self.price_unit = ''
        self.product_id=''
        
    @api.onchange('product_id')
    def _onchange_product_id(self):
        self.account_id = ''
        self.name = ''
        self.asset_category = ''
        self.account_analytic_id = ''   
        self.price_unit = ''
        if self.product_id:
            product = self.product_id
            company = self.company_id
            currency = self.company_id.currency_id
            if product.partner_ref and product.partner_ref != 'False':
                self.name = product.partner_ref
            if product.description_purchase:
                self.name += '\n' + product.description_purchase
            if product.description_sale:
                self.name += '\n' + product.description_sale
                                    
                
            if product.categ_id:
                ir_parameter_asset = self.env['ir.property'].search([('company_id', '=', self.company_id.id),
                                                            ('name', '=', 'asset_category_pro_id'),
                                                           ('res_id', '=', 'product.category,' + str(product.categ_id.id))])
                if ir_parameter_asset.value_reference:
                    ref_asset_id = (ir_parameter_asset.value_reference).split(',')[1]
                    asset = self.env['account.asset.category'].search([('id', '=', ref_asset_id)])
                    if asset:
                        self.asset_category = asset.id
                        if asset.account_analytic_id:
                            self.account_analytic_id = asset.account_analytic_id.id
                        
                ir_parameter = self.env['ir.property'].search([('company_id', '=', self.company_id.id),
                                                                ('name', '=', 'property_account_expense_categ_id'),
                                                               ('res_id', '=', 'product.category,' + str(product.categ_id.id))])
                if ir_parameter.value_reference:
                    ref_account_id = (ir_parameter.value_reference).split(',')[1]
                    account = self.env['account.account'].search([('id', '=', ref_account_id)])
                    if account:
                        self.account_id = account.id
                elif self.asset_category:
                    self.account_id  = self.asset_category.account_asset_id.id
    
                self._set_taxes()
                if company and currency:
                    if self.uom_id and self.uom_id.id != product.uom_id.id:
                        self.price_unit = product.uom_id._compute_price(self.price_unit, self.uom_id)


BillPayLines()
