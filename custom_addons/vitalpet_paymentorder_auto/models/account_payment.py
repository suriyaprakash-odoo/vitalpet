from odoo import api, fields, models, _
from lxml import etree
import base64
import time
import datetime
import re
import pprint
import logging
from pychart.arrow import default
from odoo.exceptions import ValidationError, UserError
from odoo.exceptions import Warning


class ResCompany(models.Model):
    _inherit = 'res.company'

    immediate_origin = fields.Char(string="IMMEDIATE ORIGIN", size=10)



class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    immediate_origin = fields.Char(related='company_id.immediate_origin', string="IMMEDIATE ORIGIN", size=10)



class AccountPaymentMethod(models.Model):
    _inherit = 'account.payment.method'

    
    address_required = fields.Boolean(string='Address Required')
    courier_code = fields.Char('Courier Code')
    special_handling_code = fields.Selection([('special mail', 'Special mail'),
                                              ('regular Mail', 'Regular Mail')], string ='Special Handling Code')
    # immediate_origin = fields.Char(string="IMMEDIATE ORIGIN", size=10)
    # originating_dfi = fields.Char(string="ORIGINATING DFI", size=10)
    # company_identity = fields.Char(string ='COMPANY IDENTIFICATION', size=10)
    

class Partner(models.Model):
    _inherit = "res.partner"

    @api.multi
    def get_ref_id(self):
        for line in self:
            line.ref = line.id

    ref = fields.Char(string='Internal Reference', index=True, compute='get_ref_id')

    echeck_add = fields.Boolean(related="supplier_payment_mode_id.payment_method_id.address_required",string='Address req')


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    status_line = fields.Selection([
                                    ('draft', 'Draft'),
                                    ('open', 'Confirmed'),
                                    ('generated', 'Processing'),
                                    ('rejected', 'Rejected'),
                                    ('partial rejection', 'Partial Rejection'),
                                    ('processed', 'Processed'),
                                    ('cancel', 'Cancel'),
                                    ], string='Transaction Status', compute='_compute_status')
    rejection_reson = fields.Char('Reason', track_visibility='onchange' )
    payment_id = fields.Many2one('account.payment.order', string='Payment Order')
    payment_mode_id = fields.Many2one(
        comodel_name='account.payment.mode', string="Payment Mode",
        ondelete='restrict',
        readonly=False, states={'paid': [('readonly', True)]}, track_visibility='onchange')
    

    @api.multi
    def create_account_payment_line(self):
        apoo = self.env['account.payment.order']
        aplo = self.env['account.payment.line']
        result_payorder_ids = []
        action_payment_type = 'debit'
        for inv in self:
            if inv.state != 'open':
                raise UserError(_(
                    "The invoice %s is not in Open state") % inv.number)
            pattern = re.compile(r',')
            if pattern.findall(inv.partner_id.name):
                raise UserError(_(
                    "Remove comma from %s") % inv.partner_id.name)
            if inv.partner_id.street and pattern.findall(inv.partner_id.street):
                raise UserError(_(
                    "Remove comma from %s street") % inv.partner_id.name)
            if inv.partner_id.street2 and pattern.findall(inv.partner_id.street2):
                raise UserError(_(
                    "Remove comma from %s street2") % inv.partner_id.name)
            if inv.partner_id.zip and len(inv.partner_id.zip) > 10:
                raise UserError(_(
                    "Enter a valid Zip code for %s") % inv.partner_id.name)
            pay_mode_obj = self.env['account.payment.mode'].search([('name','=','ACH')])
            if inv.payment_mode_id.id == pay_mode_obj.id:
                if len(inv.partner_id.name)>22:
                    raise UserError(_(
                        "For ACH payment, Vendor name should be 22 characters. %s has more than 22 characters") % inv.partner_id.name)    
            if not inv.payment_mode_id:
                raise UserError(_(
                    "No Payment Mode on invoice %s") % inv.number)
            else:
                mode_obj = self.env['account.payment.mode'].search([('name','=','E-Check')])
                if inv.payment_mode_id.id == mode_obj.id:
                    if not inv.partner_id.street or not inv.partner_id.city or not inv.partner_id.state_id or not inv.partner_id.country_id:
                        raise UserError(_(
                            "Please enter address for Vendor %s") % inv.partner_id.name)    
            if not inv.move_id:
                raise UserError(_(
                    "No Journal Entry on invoice %s") % inv.number)
            if not inv.payment_order_ok:
                raise UserError(_(
                    "The invoice %s has a payment mode '%s' "
                    "which is not selectable in payment orders."))
            if not inv.billpay_id:
                raise UserError(_("This Vendor bill is not from billpay bills so you can not process it."))
            payorders = apoo.search([
                ('payment_mode_id', '=', inv.payment_mode_id.id),
                ('state', '=', 'draft')])
            if payorders:
                payorder = payorders[0]
                new_payorder = False
            else:
                payorder = apoo.create(inv._prepare_new_payment_order())
                new_payorder = True
            result_payorder_ids.append(payorder.id)
            action_payment_type = payorder.payment_type
            count = 0
            for line in inv.move_id.line_ids:
                if line.account_id == inv.account_id and not line.reconciled:
                    paylines = aplo.search([
                        ('move_line_id', '=', line.id),
                        ('state', '!=', 'cancel')])
                    if not paylines:
                        line.create_payment_line_from_move_line(payorder)
                        count += 1
            if count:
                if new_payorder:
                    inv.message_post(_(
                        '%d payment lines added to the new draft payment '
                        'order %s which has been automatically created.')
                        % (count, payorder.name))
                else:
                    inv.message_post(_(
                        '%d payment lines added to the existing draft '
                        'payment order %s.')
                        % (count, payorder.name))
            else:
                raise UserError(_(
                    'No Payment Line created for invoice %s because '
                    'it already exists or because this invoice is '
                    'already paid.') % inv.number)
        action = self.env['ir.actions.act_window'].for_xml_id(
            'account_payment_order',
            'account_payment_order_%s_action' % action_payment_type)
        if len(result_payorder_ids) == 1:
            action.update({
                'view_mode': 'form,tree,pivot,graph',
                'res_id': payorder.id,
                'views': False,
                })
        else:
            action.update({
                'view_mode': 'tree,form,pivot,graph',
                'domain': "[('id', 'in', %s)]" % result_payorder_ids,
                'views': False,
                })
        return action
    
    @api.multi
    def _compute_status(self):
        for line in self:
            if line.reference:
                tids = self.env['account.payment.line'].search([('communication','=',line.reference),('partner_id','=',line.partner_id.id)])
                if tids:
                    for tid in tids:
                        line.status_line = tid.status_line
            elif line.number:
                tids = self.env['account.payment.line'].search([('communication','=',line.number),('partner_id','=',line.partner_id.id)])
                if tids:
                    for tid in tids:
                        line.status_line = tid.status_line
    
    @api.model
    def create(self,vals):
        if vals.get('partner_id'):
            partner_obj = self.env['res.partner'].search([('id', '=', vals.get('partner_id'))])
            tid = self.env['account.payment.mode'].search([('id','=',vals.get('payment_mode_id'))])
            if tid:
                if tid.name == 'E-Check':
                    if partner_obj.street == False or partner_obj.state_id == False or partner_obj.city == False or partner_obj.zip == False or partner_obj.country_id == False:
                        raise UserError(_("No Address Found"))
        return super(AccountInvoice, self).create(vals)
  
#     @api.multi
#     def write(self,vals):
#         if vals.get('partner_id'):
#             partner_obj = self.env['res.partner'].search([('id', '=', vals.get('partner_id'))])
#             if partner_obj.supplier_payment_mode_id:
#                 vals['payment_mode_id'] = partner_obj.supplier_payment_mode_id.id
#             else:
#                 vals['payment_mode_id'] = False
#         res = super(AccountInvoice, self).write(vals)
#         return res

    @api.multi
    def write(self,vals):
        res = super(AccountInvoice, self).write(vals)
        
        for line in self:
            if line.state:
                if self and line.state == 'paid' and self.state != 'paid' and  self.payment_mode_id.name == 'ACH':
                    template_id = self.env.ref('vitalpet_paymentorder_auto.vendor_bill_payments')
                    if template_id:
                        print "something" 
                        template_id.send_mail(self.id, force_send=True)
                    
        return res



class AccountPaymentOrder(models.Model):
    _inherit = "account.payment.order"

    transaction_line_count = fields.Integer(
        compute='_transaction_line_count', string='Number of Transaction Lines',
        readonly=True)
    order_seq = fields.Char(string='Payment Sequence')
    is_manual = fields.Boolean('Is Manual', compute='_compute_is_manual')
    payment_line_ids = fields.One2many(
        'account.payment.line', 'order_id', string='Transaction Lines',
        readonly=False)
    is_cron = fields.Boolean()
    
    # @api.onchange('payment_mode_id')
    # def payment_mode_id_change(self):
    #     res = super(AccountPaymentOrder, self).payment_mode_id_change()
    #     if self.payment_mode_id.name == 'ACH': 
    #         if self.payment_mode_id.default_date_prefered == 'fixed':
    #             return {
    #     'warning': {'title': _('Warning'), 'message': _('Please change date'),},
    #     }
#         return res

    @api.multi
    def write(self, vals):
        if vals.get('payment_mode_id'):
            for payment_line in self.payment_line_ids:
                payment_line.invoice_id.write({'payment_mode_id':vals.get('payment_mode_id')})
                print "updated"
        return super(AccountPaymentOrder, self).write(vals)

    
    @api.depends('payment_mode_id')
    def _compute_is_manual(self):
        if self.payment_mode_id.name not in ('ACH','E-Check'):
            self.is_manual = False
        else:
            self.is_manual=True

    @api.multi
    @api.constrains('date_scheduled')
    def check_date_scheduled(self):
        today = fields.Date.context_today(self)
        for order in self:
            if order.date_scheduled:
                if not order.payment_mode_id.allow_back_date and order.date_scheduled < today:
                    raise ValidationError(_(
                        "On payment order %s, the Payment Execution Date "
                        "is in the past (%s).")
                        % (order.name, order.date_scheduled))

    @api.onchange('date_scheduled')
    def onchange_date_scheduled_warning(self):
        warning = {}
        title = False
        message = False
        today = fields.Date.context_today(self)
        if self.payment_mode_id.allow_back_date and self.date_scheduled < today:
            message = "The Payment Execution Date is in the past (%s)." % (self.date_scheduled)
            warning = {
                    'title': "Odoo Warning",
                    'message': message,
            }
        

        if warning:
            return {'warning': warning}

    @api.multi
    @api.depends('payment_line_ids')
    def _transaction_line_count(self):
        for order in self:
            order.transaction_line_count = len(order.payment_line_ids)
            
    state = fields.Selection([
        ('draft', 'Draft'),
        ('open', 'Confirmed'),
        ('generated', 'Processing'),
        ('rejected', 'Rejected'),
        ('partial rejection', 'Partial Rejection'),
        ('processed', 'Processed'),
        ('cancel', 'Cancel'),
        ], string='Status', readonly=True, copy=False, default='draft',
        track_visibility='onchange')
    
    payment_acknowledgement = fields.Selection([('yes', 'Yes'),
                                              ('no', 'No')], string ='Payment Acknowledgement')
    payment_final_status = fields.Selection([('processed', 'Processed'),
                                             ('partial rejection', 'Partial Rejection'),
                                             ('rejected', 'Rejected')], string ='Payment Final Status')
    Payment_return_message = fields.Char('Payment Return Message')
    
    @api.multi
    def generated2uploaded(self):
        for order in self:
            if order.payment_mode_id.generate_move:
                order.generate_move()
        self.write({
            'state': 'processed',
            'date_uploaded': fields.Date.context_today(self),
            })
        return True

    @api.multi
    def action_reject(self):
        for line in self.payment_line_ids:
            if line.status_line == 'rejected':
                tid = self.env['account.invoice'].search([('number','=',line.communication)])
                tid.write({'rejection_reson':'Rejected'})
                line.unlink()

    @api.multi
    def action_cancel(self):
        for order in self:
            order.write({'state': 'cancel'})
            order.bank_line_ids.unlink()
            for move in order.move_ids:
                move.button_cancel()
                for move_line in move.line_ids:
                    move_line.remove_move_reconcile()
                move.unlink()
        return True
                
    @api.multi           
    def manual_confrom(self):
        self.draft2open()
        self.state='generated'

    @api.multi
    def draft2open(self):
        """
        Called when you click on the 'Confirm' button
        Set the 'date' on payment line depending on the 'date_prefered'
        setting of the payment.order
        Re-generate the bank payment lines
        """
        bplo = self.env['bank.payment.line']
        today = fields.Date.context_today(self)
        for order in self:
            if not order.journal_id:
                raise UserError(_(
                    'Missing Bank Journal on payment order %s.') % order.name)
            if (
                    order.payment_method_id.bank_account_required and
                    not order.journal_id.bank_account_id):
                raise UserError(_(
                    "Missing bank account on bank journal '%s'.")
                    % order.journal_id.display_name)
            if not order.payment_line_ids:
                raise UserError(_(
                    'There are no transactions on payment order %s.')
                    % order.name)
            # Delete existing bank payment lines
            order.bank_line_ids.unlink()
            # Create the bank payment lines from the payment lines
            group_paylines = {}  # key = hashcode
            for payline in order.payment_line_ids:
                payline.draft2open_payment_line_check()
                # Compute requested payment date
                if order.date_prefered == 'due':
                    requested_date = payline.ml_maturity_date or today
                elif order.date_prefered == 'fixed':
                    requested_date = order.date_scheduled or today
                else:
                    requested_date = today
                # No payment date in the past
                if not order.payment_mode_id.allow_back_date and requested_date < today:
                    requested_date = today
                # inbound: check option no_debit_before_maturity
                if (
                        order.payment_type == 'inbound' and
                        order.payment_mode_id.no_debit_before_maturity and
                        payline.ml_maturity_date and
                        requested_date < payline.ml_maturity_date):
                    raise UserError(_(
                        "The payment mode '%s' has the option "
                        "'Disallow Debit Before Maturity Date'. The "
                        "payment line %s has a maturity date %s "
                        "which is after the computed payment date %s.") % (
                            order.payment_mode_id.name,
                            payline.name,
                            payline.ml_maturity_date,
                            requested_date))
                # Write requested_date on 'date' field of payment line
                payline.date = requested_date
                # Group options
                if order.payment_mode_id.group_lines:
                    hashcode = payline.payment_line_hashcode()
                elif order.payment_mode_id.group_vendor_account:
                    hashcode = payline.account_id_payment_line_hashcode()
                else:
                    # Use line ID as hascode, which actually means no grouping
                    hashcode = payline.id
                if hashcode in group_paylines:
                    group_paylines[hashcode]['paylines'] += payline
                    group_paylines[hashcode]['total'] +=\
                        payline.amount_currency
                else:
                    group_paylines[hashcode] = {
                        'paylines': payline,
                        'total': payline.amount_currency,
                    }
            # Create bank payment lines
            for paydict in group_paylines.values():
                # Block if a bank payment line is <= 0
                if paydict['total'] <= 0:
                    raise UserError(_(
                        "The amount for Partner '%s' is negative "
                        "or null (%.2f) !")
                        % (paydict['paylines'][0].partner_id.name,
                           paydict['total']))
                vals = self._prepare_bank_payment_line(paydict['paylines'])
                bplo.create(vals)
        self.write({'state': 'open'})
        return True

    
    @api.multi           
    def payment_processed(self):
        for line in self.bank_line_ids:
            if not line.partner_id and not line.date and line.amount_currency==0:
                line.unlink()
        self.generated2uploaded()
        self.state='processed'
    
    @api.multi
    def action_payment_order(self):
        date_yesterday = datetime.datetime.now() + datetime.timedelta(days=-1)
        payment_id = self.env['account.payment.order'].search([('date_generated','<=',date_yesterday),('payment_mode_id.name','in',['ACH','E-Check']),('state','=','generated')])
        for payment in payment_id:
            payment.payment_processed()
            
    @api.multi
    def action_account_payment_order_status(self):
        payment_obj = self.env['account.payment.order'].search([('state','=','processed')])
        if payment_obj:
            for payment in payment_obj:
                reason = []
                for payment_line in payment.payment_line_ids:
                    reason.append(payment_line.return_message)
                count = list(set(reason))
                if len(count) == 1:
                    if count[0] == 'rejected':
                        payment.state = 'rejected'
                else:
                    payment.state = 'partial rejection'
                    
    @api.multi
    def unlink(self):
        for line in self:
            for payment in line.payment_line_ids:
                payment.unlink()
        return super(AccountPaymentOrder, self).unlink()

    @api.multi
    def _prepare_move_line_offsetting_account(
            self, amount_company_currency, amount_payment_currency,
            bank_lines):
        vals = {}
        if self.payment_type == 'outbound':
            name = _('Payment order %s') % self.name
        else:
            name = _('Debit order %s') % self.name
        if self.payment_mode_id.offsetting_account == 'bank_account':
            vals.update({'date': bank_lines[0].date})
        else:
            vals.update({'date_maturity': bank_lines[0].date})

        if self.payment_mode_id.offsetting_account == 'bank_account':
            account_id = self.journal_id.default_debit_account_id.id
        elif self.payment_mode_id.offsetting_account == 'transfer_account':
            account_id = self.payment_mode_id.transfer_account_id.id
        partner_id = False
        for index, bank_line in enumerate(bank_lines):
            if index == 0:
                partner_id = bank_line.payment_line_ids[0].partner_id.id
            elif bank_line.payment_line_ids[0].partner_id.id != partner_id:
                # we have different partners in the grouped move
                partner_id = False
                break
        vals.update({
            'name': name,
            'partner_id': partner_id,
            'account_id': account_id,
            'credit': (self.payment_type == 'outbound' and
                       amount_company_currency or 0.0),
            'debit': (self.payment_type == 'inbound' and
                      amount_company_currency or 0.0),
            'ref':name+' - CHECK '+str(int(bank_line.payment_line_ids[0].check_number))
        })
        if bank_lines[0].currency_id != bank_lines[0].company_currency_id:
            sign = self.payment_type == 'outbound' and -1 or 1
            vals.update({
                'currency_id': bank_lines[0].currency_id.id,
                'amount_currency': amount_payment_currency * sign,
                })
        return vals

    @api.multi
    def generate_move(self):
        """
        Create the moves that pay off the move lines from
        the payment/debit order.
        """
        self.ensure_one()
        am_obj = self.env['account.move']
        post_move = self.payment_mode_id.post_move
        # prepare a dict "trfmoves" that can be used when
        # self.payment_mode_id.move_option = date or line
        # key = unique identifier (date or True or line.id)
        # value = bank_pay_lines (recordset that can have several entries)
        trfmoves = {}
        for bline in self.bank_line_ids:
            hashcode = bline.move_line_offsetting_account_hashcode()
            if hashcode in trfmoves:
                trfmoves[hashcode] += bline
            else:
                trfmoves[hashcode] = bline

        for hashcode, blines in trfmoves.iteritems():
            mvals = self._prepare_move(blines)
            total_company_currency = total_payment_currency = 0
            for bline in blines:
                total_company_currency += bline.amount_company_currency
                total_payment_currency += bline.amount_currency
                partner_ml_vals = self._prepare_move_line_partner_account(
                    bline)
                mvals['line_ids'].append((0, 0, partner_ml_vals))
            trf_ml_vals = self._prepare_move_line_offsetting_account(
                total_company_currency, total_payment_currency, blines)
            mvals['line_ids'].append((0, 0, trf_ml_vals))
            mvals['date']=self.date_scheduled
            move = am_obj.create(mvals)
            move.ref = move.line_ids[0].ref
            blines.reconcile_payment_lines()
            if post_move:
                move.post()
                    
                    
class AccountPaymentLine(models.Model):
    _inherit = 'account.payment.line'
    
    status_line = fields.Selection([
                                    ('draft', 'Draft'),
                                    ('open', 'Confirmed'),
                                    ('generated', 'Processing'),
                                    ('rejected', 'Rejected'),
                                    ('partial rejection', 'Partial Rejection'),
                                    ('processed', 'Processed'),
                                    ('cancel', 'Cancel'),
                                    ], string='Transaction Line Status', related='order_id.state')
    return_message = fields.Char('Return Message')
    line_reason = fields.Char('Line reason', compute='_compute_line_reason')
    billpay_id = fields.Many2one('billpay.bills', string="Bill Pay Id")
    invoice_id = fields.Many2one('account.invoice', string="Invoice number")
    acc_number_id = fields.Many2one('account.number', string='Account Number', related='invoice_id.acc_number_id')
    invoice_number = fields.Char('Invoice Number', related='invoice_id.invoice_number')
    ach_sent = fields.Boolean('ACH Sent', readonly=True)
    
    @api.depends('status_line')
    def _compute_line_reason(self):
        for line in self:
            if line.status_line == 'rejected' or line.status_line == 'partial rejection':
                line.line_reason = 'Reopen'

    @api.multi
    def account_id_payment_line_hashcode(self):
        self.ensure_one()
        bplo = self.env['bank.payment.line']
        values = []
        for field in bplo.account_same_fields_payment_line_and_bank_payment_line():
            values.append(unicode(self[field]))
        values.append(unicode(self.move_line_id.account_id or False))
        if self.communication_type != 'normal':
            values.append(unicode(self.id))
        hashcode = '-'.join(values)
        return hashcode
            
    @api.multi           
    def action_line_rejection(self):
        account_obj = self.env['account.invoice'].search([('id','=',self.invoice_id.id)])
        account_obj.write({'state':'open'})
        tid = self.order_id.id
        self.unlink()
        tid_obj = self.env['account.payment.order'].search([('id','=',tid)])
        reason = []
        for line in tid_obj.payment_line_ids:
            reason.append(line.return_message)
        count = list(set(reason))
        if len(count) == 1:
            if count[0] == 'processed':
                tid_obj.state = 'processed'
                
    @api.model
    def create(self, vals):
        move_line_obj = self.env['account.move.line'].search([('id','=',vals.get('move_line_id'))])
        if move_line_obj.move_id.billpay_id:
            vals.update({'billpay_id': move_line_obj.move_id.billpay_id.id})
               
        invoice_obj =  self.env['account.invoice'].search([('move_id','=',move_line_obj.move_id.id)])
        invoice_obj.payment_id = vals.get('order_id')
        vals.update({'invoice_id': invoice_obj.id})
        
        return super(AccountPaymentLine, self).create(vals)
    
    @api.model
    def write(self, vals):
        for line in self:
            if line.invoice_id:
                line.invoice_id.payment_id = line.order_id.id
        
        return super(AccountPaymentLine, self).write(vals)
        
    @api.multi
    def unlink(self):
        for line in self:
            line.action_payment_line_delete()
            if not line.invoice_id:
                invoice_id=self.env['account.invoice'].search([('partner_id','=', line.partner_id.id),('reference','=', line.communication),('amount_total','=', line.amount_currency)])
            else:
                 invoice_id=line.invoice_id
                  
            invoice_id.payment_id = False
            invoice_id.state = 'open'
            # if line.invoice_id.move_id:
            #     line.invoice_id.move_id.button_cancel()
            if invoice_id.billpay_id:
                invoice_id.billpay_id.state = 'posted'
            # if line.bank_line_id:
            #     if line.bank_line_id.amount_currency == line.amount_currency:
            #         line.bank_line_id.unlink()
        # return False
        return super(AccountPaymentLine, self).unlink()
    
    @api.multi
    def action_payment_line_delete(self):
        for rec in self:
            print rec.move_line_id.id
            # ACH payment return process
            if rec.order_id.payment_mode_id.move_option == 'date':
                print rec.order_id.payment_mode_id.move_option
                if not rec.order_id.payment_mode_id.group_lines and not rec.order_id.payment_mode_id.group_vendor_account:
                    print 'not group'
                    move_line_exists = False
                    bank_payment_line = self.env['bank.payment.line'].search([('order_id','=', rec.order_id.id),('partner_id','=', rec.partner_id.id),('amount_currency','=',rec.amount_currency)], limit = 1)

                    if len(bank_payment_line.payment_line_ids) == 1:
                        if bank_payment_line.amount_currency == rec.amount_currency:
                            bank_payment_line.unlink()
                        move_obj = self.env['account.move'].search([('payment_order_id','=',rec.order_id.id)])

                        if move_obj:
                            move_obj.button_cancel()
                            for move_line in move_obj.line_ids:
                                if move_line.partner_id.id == rec.partner_id.id and round(move_line.debit) == round(rec.amount_currency) and not move_line_exists:
                                    move_line_exists = True
                                    move_line.remove_move_reconcile()
                                    sql_query = "delete from account_move_line where id = "+str(move_line.id)
                                    self._cr.execute(sql_query)
                            if move_line_exists:
                                for credit_move_line in move_obj.line_ids:
                                    if credit_move_line.credit > 0.00:                                            
                                        balance_amount = credit_move_line.credit - rec.amount_currency
                                        sql_query = "update account_move_line set credit = "+str(balance_amount)+", credit_cash_basis = "+str(balance_amount)+",  balance_cash_basis = "+str(-balance_amount)+", balance = "+str(-balance_amount)+" where id = "+str(credit_move_line.id)
                                        self._cr.execute(sql_query)
                                for move in move_obj:
                                    total = 0.0
                                    for line in move.line_ids:
                                        total += line.debit
                                    move.amount = total
                                move_obj.post()
                            else:
                                raise ValidationError(_("No matching found to remove payment line"))
                            
                            
                            
                                    
                    else:
                        raise ValidationError(_("Error in return process"))
                else:
                    print 'ACH -- Date if not group checked'
                    move_line_exists = False
                    bank_payment_lines = self.env['bank.payment.line'].search([('order_id','=', rec.order_id.id),('partner_id','=', rec.partner_id.id),('communication','=', rec.communication)])
                    for bank_payment_line in bank_payment_lines:
                        if len(bank_payment_line.payment_line_ids) == 1:
                            print 'payment line = 1'
                            move_obj = self.env['account.move'].search([('payment_order_id','=',rec.order_id.id)])

                            if move_obj:
                                move_obj.button_cancel()
                                for move_line in move_obj.line_ids:

                                    if move_line.bank_payment_line_id.id == bank_payment_line.id and move_line.partner_id.id == rec.partner_id.id and round(move_line.debit,2) == round(rec.amount_currency,2):
                                        move_line_exists = True
                                        move_line.remove_move_reconcile()
                                        sql_query = "delete from account_move_line where id = "+str(move_line.id)
                                        self._cr.execute(sql_query)
                                if move_line_exists:
                                    for credit_move_line in move_obj.line_ids:
                                        if credit_move_line.credit > 0.00:                                            
                                            balance_amount = credit_move_line.credit - rec.amount_currency
                                            sql_query = "update account_move_line set credit = "+str(balance_amount)+", credit_cash_basis = "+str(balance_amount)+",  balance_cash_basis = "+str(-balance_amount)+", balance = "+str(-balance_amount)+" where id = "+str(credit_move_line.id)
                                            self._cr.execute(sql_query)

                                    for move in move_obj:
                                        total = 0.0
                                        for line in move.line_ids:
                                            total += line.debit
                                        move.amount = total
                                    move_obj.post()

                                else:
                                    raise ValidationError(_("No matching found to remove payment line"))
                            
                            bank_payment_line.unlink()   
                                    
                        else:
                            print 'multi bank payment line ids'
                            
                            rec.move_line_id.remove_move_reconcile()                            
                            for payment_line in bank_payment_line.payment_line_ids:
                                if payment_line.amount_currency == rec.amount_currency and not move_line_exists:
                                    #added not move line exists to avoid dublicate amount delete process
                                    move_obj = self.env['account.move'].search([('payment_order_id','=',rec.order_id.id)])
                                    print move_obj,'===='
                                    if move_obj:
                                        move_obj.button_cancel()
                                        for move_line in move_obj.line_ids:

                                            if move_line.partner_id.id == rec.partner_id.id and move_line.debit > 0.00:
                                                move_line_exists = True
                                                print move_line.debit,"-",move_line.debit - rec.amount_currency
                                                
                                                debit_amount = move_line.debit - rec.amount_currency
                                                sql_query = "update account_move_line set debit = "+str(debit_amount)+", debit_cash_basis = "+str(debit_amount)+",  balance_cash_basis = "+str(debit_amount)+", balance = "+str(debit_amount)+" where id = "+str(move_line.id)
                                                self._cr.execute(sql_query)
                                        if move_line_exists:
                                            for credit_move_line in move_obj.line_ids:
                                                if credit_move_line.credit > 0.00:
                                                    
                                                    print credit_move_line.credit,"-",credit_move_line.credit - rec.amount_currency
                                                    balance_amount = credit_move_line.credit - rec.amount_currency
                                                    sql_query = "update account_move_line set credit = "+str(balance_amount)+", credit_cash_basis = "+str(balance_amount)+",  balance_cash_basis = "+str(-balance_amount)+", balance = "+str(-balance_amount)+" where id = "+str(credit_move_line.id)
                                                    self._cr.execute(sql_query)

                                            for move in move_obj:
                                                total = 0.0
                                                for line in move.line_ids:
                                                    total += line.debit
                                                     
                                                move.amount = total - rec.amount_currency
#                                                print move.amount
                                            move_obj.post()

                                
            else:
                
                print rec.order_id.payment_mode_id.move_option
                
                if not rec.order_id.payment_mode_id.group_lines and not rec.order_id.payment_mode_id.group_vendor_account:
                    print 'not group'
                    move_line_exists = False
                    bank_payment_line = self.env['bank.payment.line'].search([('order_id','=', rec.order_id.id),('partner_id','=', rec.partner_id.id),('amount_currency','=',rec.amount_currency)], limit = 1)
                    bank_payment_line.unlink()
                    move_obj = self.env['account.move'].search([('payment_order_id','=',rec.order_id.id),('amount','=', rec.amount_currency)])

                    if move_obj:
                        move_obj.button_cancel()
                        for move_line in move_obj.line_ids:
                            move_line_exists = True
                            move_line.remove_move_reconcile()
                        move_obj.unlink()
                    else:
                        raise ValidationError(_("No matching jounral entry found to remove payment line"))
                else:
                    print 'in group'
                    move_line_exists = False
                    bank_payment_lines = self.env['bank.payment.line'].search([('order_id','=', rec.order_id.id),('partner_id','=', rec.partner_id.id)])
                    for bank_payment_line in bank_payment_lines:
                        if len(bank_payment_line.payment_line_ids) == 1:
                            print 'payment line = 1'
                            bank_payment_line.unlink()
                            move_obj = self.env['account.move'].search([('payment_order_id','=',rec.order_id.id)])
                            #print move_obj
                            if len(move_obj) > 1:
                                for move in move_obj:
                                    if move.amount == rec.amount_currency and move.partner_id == rec.partner_id:
                                        move.button_cancel()
                                        for move_line in move.line_ids:
                                            move_line_exists = True
                                            move_line.remove_move_reconcile()
                                        move.unlink()
                            else:
                                
                                if move_obj:
                                    move_obj.button_cancel()
                                    for move_line in move_obj.line_ids:
                                        move_line_exists = True
                                        move_line.remove_move_reconcile()
                                    move_obj.unlink()
                                else:
                                    raise ValidationError(_("No matching jounral entry found to remove payment line"))
                        else:
                            
                            print 'payment line <> 1'
                            
                                    
                            for payment_line in bank_payment_line.payment_line_ids:

                                if payment_line.amount_currency == rec.amount_currency and not move_line_exists:
                                    #added not move line exists to avoid dublicate amount delete process
                                    move_obj = self.env['account.move'].search([('payment_order_id','=',rec.order_id.id),('amount','=', bank_payment_line.amount_currency)])
                                    print move_obj
                                    if move_obj:
                                        move_obj.button_cancel()
                                        for move_line in move_obj.line_ids:
                                            if move_line.partner_id.id == rec.partner_id.id and move_line.debit > 0.00:                                    
                                                move_line_exists = True
                                                #move_line.remove_move_reconcile()                                                
                                                #print move_line.debit
                                                debit_amount = move_line.debit - rec.amount_currency
                                                sql_query = "update account_move_line set debit = "+str(debit_amount)+", debit_cash_basis = "+str(debit_amount)+",  balance_cash_basis = "+str(debit_amount)+", balance = "+str(debit_amount)+" where id = "+str(move_line.id)
                                                #print sql_query
                                                self._cr.execute(sql_query)
                                        if move_line_exists:
                                            for credit_move_line in move_obj.line_ids:
                                                if credit_move_line.credit > 0.00:
                                                    #print credit_move_line.credit                         
                                                    balance_amount = credit_move_line.credit - rec.amount_currency
                                                    sql_query = "update account_move_line set credit = "+str(balance_amount)+", credit_cash_basis = "+str(balance_amount)+",  balance_cash_basis = "+str(-balance_amount)+", balance = "+str(-balance_amount)+" where id = "+str(credit_move_line.id)
                                                    self._cr.execute(sql_query)

                                            for move in move_obj:
                                                total = 0.0
                                                for line in move.line_ids:
                                                    total += line.debit

                                                move.amount = total - rec.amount_currency
                                            move_obj.post()

                            move_obj = self.env['account.move'].search([('id','=',rec.move_line_id.move_id.id)])    
                                                
                            if move_obj:
                                move_obj.button_cancel()
                                for move_line in move_obj.line_ids:
                                    if move_line.partner_id.id == rec.partner_id.id and move_line.credit > 0.00:                                    
                                        move_line.remove_move_reconcile()
                                move_obj.post()
                                
#         raise ValidationError(_("End"))
    
    @api.multi
    def action_payment_line_test_remove_not_in_payment_line(self):
        i=j=0
        for rec in self.env['account.invoice'].search([('state','=','paid'),('payment_id','=',None),('billpay_id','!=',None)]):
            i+=1
            if len(rec.move_id.line_ids)==2:
                lines=self.env['account.payment.line'].search([('communication','=',rec.reference),('partner_id','=',rec.partner_id.id),('amount_currency','=',rec.amount_total_signed)])
                count=len(lines)                
                if count==0:    
#                     j+=1
                    print rec.amount_total_signed,rec.move_id
                    for move_lines in rec.move_id.line_ids:
#                         if move_lines.full_reconcile_id and move_lines.account_id.name=='Accounts Payable':
                        if move_lines.account_id.name=='Accounts Payable':
#                             print ''
                            move_lines.remove_move_reconcile()
                            j+=1
                    
#                 else:
#                     print count, lines[0].order_id.state
#             else:
#                 print rec.move_line_id.id
        print i, j                            

    @api.multi
    def action_payment_line_test_remove_not_in_payment_line_2(self):
        i=j=0
        for rec in self.env['account.invoice'].search([('state','=','paid'),('payment_id','=',None),('billpay_id','!=',None)]):
            i+=1
            if len(rec.move_id.line_ids)==2:
                lines=self.env['account.payment.line'].search([('communication','=',rec.reference),('partner_id','=',rec.partner_id.id),('amount_currency','=',rec.amount_total_signed)])
                count=len(lines)      
                if count==1:
                    print rec.move_id, lines.order_id.name, rec.amount_total_signed
                    rec.payment_id=lines.order_id.id
                    j+=1

        print i, j    
            
    @api.multi
    def action_payment_line_unreconcile(self):
        i=j=0
        for rec in self.env['account.invoice'].search([('state','=','paid'),('payment_id','=',None),('billpay_id','!=',None)]):
            i+=1
            if len(rec.move_id.line_ids)==2:
                lines=self.env['account.payment.line'].search([('communication','=',rec.reference),('partner_id','=',rec.partner_id.id),('amount_currency','=',rec.amount_total_signed)])
                count=len(lines)      
                if count==1:
                    print rec.move_id, lines.order_id.name, rec.amount_total_signed
                    rec.payment_id=lines.order_id.id
                    j+=1

        print i, j                 
    
            