# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import UserError
from datetime import datetime


class BillpayReverseRefund(models.TransientModel):
    """Refunds invoice"""

    _name = "reverse.apply.credit"
    _description = "Bill Pay Refund"

    @api.model
    def _get_reason(self):
        context = dict(self._context or {})
        active_id = context.get('active_id', False)
        if active_id:
            inv = self.env['account.invoice'].search([('billpay_id','=',active_id)])
            return inv.name
        return ''

    date_invoice = fields.Date(string='Refund Date', default=fields.Date.context_today, required=True)
    date = fields.Date(string='Accounting Date')
    description = fields.Char(string='Reason', required=True,)
    refund_only = fields.Boolean(string='Technical field to hide filter_refund in case invoice is partially paid')
    filter_refund = fields.Selection([('refund_validate', 'Refund & Validate: Reverse and Validate invoice'),('refund', 'Create a draft refund'), ('cancel', 'Cancel: create refund and reconcile'), ('modify', 'Modify: create refund, reconcile and create a new draft invoice')],
        default='refund_validate', string='Refund Method', required=True, help='Refund base on this type. You can not Modify and Cancel if the invoice is already reconciled')

    @api.depends('date_invoice')
    @api.one
    def _get_refund_only(self):

        invoice_id = self.env['account.invoice'].search([('billpay_id','=',self._context.get('active_id',False))])
        if len(invoice_id.payment_move_line_ids) != 0 and invoice_id.state != 'paid':
            self.refund_only = True
        else:
            self.refund_only = False

    @api.multi
    def compute_refund(self, mode='refund'):
        inv_obj = self.env['account.invoice']
        inv_tax_obj = self.env['account.invoice.tax']
        inv_line_obj = self.env['account.invoice.line']
        context = dict(self._context or {})
        xml_id = False
        for form in self:
            created_inv = []
            date = False
            description = False
            bill_pay_id = self._context.get('active_id',False)
                
            
            for inv in inv_obj.search([('billpay_id','=', self._context.get('active_id',False)),('state','!=','cancel')]):
                if inv.state in ['draft', 'proforma2']:
                    raise UserError(_('Cannot refund draft/proforma/cancelled invoice.'))
                if inv.reconciled and mode in ('cancel', 'modify'):
                    raise UserError(_('Cannot refund invoice which is already reconciled, invoice should be unreconciled first. You can only refund this invoice.'))

                date = form.date or form.date_invoice or datetime.today()
                description = form.description or inv.name
                refund = inv.with_context({'type': 'in_invoice'}).refund(form.date_invoice, date, description, inv.journal_id.id)
                refund.compute_taxes()

                created_inv.append(refund.id)
                if mode == 'refund_validate':
                    refund.action_invoice_open()
                    if bill_pay_id:
                        billpay_bills = self.env['billpay.bills'].browse(bill_pay_id)
                        account_move = self.env['account.move'].search([('billpay_id', '=', billpay_bills.id)])
                        for i in account_move:
                            if i.company_id.id in [line.company_id.id for line in billpay_bills.bill_line_ids]:
                                res = i.reverse_moves(self.date)
                                res_move = self.env['account.move'].search([('id', '=', res[0])])
                                res_move.write({'state':'draft'}) 
                    
                    
                
                if mode in ('cancel', 'modify'):
                    movelines = inv.move_id.line_ids
                    to_reconcile_ids = {}
                    to_reconcile_lines = self.env['account.move.line']
                    for line in movelines:
                        if line.account_id.id == inv.account_id.id:
                            to_reconcile_lines += line
                            to_reconcile_ids.setdefault(line.account_id.id, []).append(line.id)
                        if line.reconciled:
                            line.remove_move_reconcile()
                    refund.action_invoice_open()
                    for tmpline in refund.move_id.line_ids:
                        if tmpline.account_id.id == inv.account_id.id:
                            to_reconcile_lines += tmpline
                            to_reconcile_lines.filtered(lambda l: l.reconciled == False).reconcile()
                    if mode == 'modify':
                        invoice = inv.read(
                            ['name', 'type', 'number', 'reference',
                             'comment', 'date_due', 'partner_id',
                             'partner_insite', 'partner_contact',
                             'partner_ref', 'payment_term_id', 'account_id',
                             'currency_id', 'invoice_line_ids', 'tax_line_ids',
                             'journal_id', 'date'])
                        invoice = invoice[0]
                        del invoice['id']
                        invoice_lines = inv_line_obj.browse(invoice['invoice_line_ids'])
                        invoice_lines = inv_obj.with_context(mode='modify')._refund_cleanup_lines(invoice_lines)
                        tax_lines = inv_tax_obj.browse(invoice['tax_line_ids'])
                        tax_lines = inv_obj._refund_cleanup_lines(tax_lines)
                        invoice.update({
                            'type': inv.type,
                            'date_invoice': form.date_invoice,
                            'state': 'draft',
                            'number': False,
                            'invoice_line_ids': invoice_lines,
                            'tax_line_ids': tax_lines,
                            'date': date,
                            'origin': inv.origin,
                            'fiscal_position_id': inv.fiscal_position_id.id,
                        })
                        for field in ('partner_id', 'account_id', 'currency_id',
                                      'payment_term_id', 'journal_id'):
                            invoice[field] = invoice[field] and invoice[field][0]
                        inv_refund = inv_obj.create(invoice)
                        if inv_refund.payment_term_id.id:
                            inv_refund._onchange_payment_term_date_invoice()
                        created_inv.append(inv_refund.id)
                xml_id = (inv.type in ['out_refund', 'out_invoice']) and 'action_invoice_tree1' or \
                         (inv.type in ['in_refund', 'in_invoice']) and 'action_invoice_tree2'
                # Put the reason in the chatter
                subject = _("Invoice refund")
                body = description
                refund.message_post(body=body, subject=subject)

            bill_pay_id = self.env["billpay.bills"].search([('id','=',self._context.get('active_id',False))])
            bill_pay_id.state = "open"
            bill_pay_id.reversal_reason = self.description

        if xml_id:
            result = self.env.ref('account.%s' % (xml_id)).read()[0]
            invoice_domain = safe_eval(result['domain'])
            invoice_domain.append(('id', 'in', created_inv))
            result['domain'] = invoice_domain
            return result
        return True

    @api.multi
    def reverse_apply_refund(self):
        bill_pay_id = self.env["billpay.bills"].search([('id','=',self._context.get('active_id',False))])
        data_refund = self.read(['filter_refund'])[0]['filter_refund']
        
        assets= self.env['account.asset.asset'].search([('bill_id', '=', bill_pay_id.bill_credit_id)])
        for line in assets:
            if line.state == 'draft':
                line.unlink()
            else:
                raise UserError(_('The state has been already moved from draft to running in assets.')) 
        
        return self.compute_refund(data_refund)