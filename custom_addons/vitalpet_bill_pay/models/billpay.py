from __future__ import division
import logging
from datetime import datetime,timedelta
from odoo.exceptions import UserError
from odoo import api, fields, models, tools, _
import mimetypes
# from odoo.tools.mimetypes import guess_mimetype
# from odoo.tools import float_round


_logger = logging.getLogger(__name__)

MAX_POP_MESSAGES = 50
MAIL_TIMEOUT = 60

class BillPayDashboard(models.Model):
    _name = 'billpay.dashboard'

    @api.model
    def fetch_dashboard_data(self):
        
        result = {}
        today = datetime.now().date()  
# Open bill details
        currency = self.env.user.company_id.currency_id
        billpay_bills = self.env['billpay.bills'].search([],order='id asc')
        open_bills_credits_amount = 0
        open_bills_credits = 0
        open_bills_credits_today = 0

        approved_bills_credits_amount = 0
        approved_bills_credits = 0
        approved_bills_credits_today = 0


        hold_bills_credits_amount = 0
        hold_bills_credits = 0
        hold_bills_credits_today = 0

        overdue_bills_credits_amount = 0
        overdue_bills_credits = 0
        
        overdue30_bills_credits = 0
        overdue30_bills_credits_amount = 0

        overdue60_bills_credits = 0
        overdue60_bills_credits_amount = 0

        overdue90_bills_credits = 0
        overdue90_bills_credits_amount = 0
        starting_bill = self.env['billpay.bills'].search([],limit=1,order='id asc')
        for bill in billpay_bills:
            if bill.state == 'open':
                open_bills_credits_amount += bill.invoice_amount
                open_bills_credits+=1
                if bill.bill_date == datetime.now():
                    open_bills_credits_today+=1

                elif bill.due_date <= datetime.now().strftime('%Y-%m-%d'):
                    overdue_bills_credits_amount += bill.invoice_amount
                    overdue_bills_credits +=1

                elif bill.due_date < (datetime.now()- timedelta(days=30)).strftime('%Y-%m-%d') and bill.due_date > (datetime.now()- timedelta(days=60)).strftime('%Y-%m-%d'):
                    overdue30_bills_credits +=1
                    overdue30_bills_credits_amount += bill.invoice_amount

                elif bill.due_date < (datetime.now()- timedelta(days=60)).strftime('%Y-%m-%d') and bill.due_date > (datetime.now()- timedelta(days=90)).strftime('%Y-%m-%d'):
                    overdue60_bills_credits +=1
                    overdue60_bills_credits_amount += bill.invoice_amount

                elif bill.due_date < (datetime.now()- timedelta(days=60)).strftime('%Y-%m-%d') and bill.due_date > (datetime.now()- timedelta(days=90)).strftime('%Y-%m-%d'):
                    overdue60_bills_credits +=1
                    overdue60_bills_credits_amount += bill.invoice_amount


            if bill.state == 'toapprove':
                approved_bills_credits_amount += bill.invoice_amount
                approved_bills_credits+=1
                if bill.bill_date == datetime.now():
                    approved_bills_credits_today+=1

            if bill.state == 'hold':
                hold_bills_credits_amount += bill.invoice_amount
                hold_bills_credits+=1
                if bill.bill_date == datetime.now():
                    hold_bills_credits_today+=1

        if starting_bill:
            start_bill_date = datetime.strptime(starting_bill.submit_date, "%Y-%m-%d  %H:%M:%S").date()
            difference_days = days = (today - start_bill_date).days
        else:
            difference_days = days = 0
        if difference_days == 0:
            difference_days = 1
        if len(billpay_bills) > 0 :
            avg_per_day = len(billpay_bills) / difference_days
        else:
            avg_per_day = 0

        
        result['openbills'] = {}
        result['currency'] = currency.symbol
        result['openbills']['count'] = open_bills_credits
        result['openbills']['total_amount'] = "%.2f" % open_bills_credits_amount
        result['openbills']['today_bills'] = open_bills_credits_today
        
# Approved bill details

        result['approvedbills'] = {}
        result['approvedbills']['count'] = approved_bills_credits
        result['approvedbills']['total_amount'] = "%.2f" % approved_bills_credits_amount
        result['approvedbills']['today_bills'] = approved_bills_credits_today

        
        result['overduebills'] = {}
        result['overduebills']['count'] = overdue_bills_credits
        result['overduebills']['total_amount'] = "%.2f" % overdue_bills_credits_amount

        
        result['overdue30bills'] = {}
        result['overdue30bills']['count'] = overdue30_bills_credits
        result['overdue30bills']['total_amount'] = "%.2f" % overdue30_bills_credits_amount
        
        

        
        result['overdue60bills'] = {}
        result['overdue60bills']['count'] = overdue60_bills_credits
        result['overdue60bills']['total_amount'] = "%.2f" % overdue60_bills_credits_amount
        

        result['overdue90bills'] = {}
        result['overdue90bills']['count'] = overdue90_bills_credits
        result['overdue90bills']['total_amount'] = "%.2f" % overdue90_bills_credits_amount


        result['holdbills'] = {}
        result['holdbills']['count'] = hold_bills_credits
        result['holdbills']['total_amount'] = "%.2f" % hold_bills_credits_amount
        result['holdbills']['today_bills'] = hold_bills_credits_today


            
        
        result['avg_per_day'] = round(avg_per_day)
        
        
        inbox = self.env['billpay.inbox'].search([('state', '=', 'open')])
        inbox_today = 0
        d1 = datetime.strftime(today, "%Y-%m-%d 00:00:00")
        d2 = datetime.strftime(today, "%Y-%m-%d 23:59:59")
        for inbox_rec in inbox:
            if inbox_rec.submit_date >= d1 and inbox_rec.submit_date <= d2: 
                inbox_today += 1

        result['inbox'] = {}
        result['inbox']['count'] = len(inbox)
        result['inbox']['today'] = inbox_today


        company_obj = self.env['res.company'].search([('id','=',self.env.user.company_id.id)], limit=1)
        if company_obj.child_payable_tag:            
            payables = self.env['account.move.line'].search([('account_id.tag_ids', 'in',[company_obj.child_payable_tag.id]), ('billpay_id', '=', None)])
        else:
            payables = self.env['account.move.line'].search([('billpay_id', '=', None)], limit = 1)
        payables_amount =  sum([line.credit for line in payables])

        result['payables'] = {}
        result['payables']['count'] = len(payables)
        result['payables']['total_amount'] = "%.2f" % payables_amount


        
        if company_obj.child_receivable_tag:
            receivables = self.env['account.move.line'].search([('account_id.tag_ids', 'in',[company_obj.child_receivable_tag.id]), ('billpay_id', '=', None), ('debit', '!=', 0.0)])
            print receivables
        else:
            receivables = self.env['account.move.line'].search([('billpay_id', '=', None)] , limit = 1)
        receivables_amount =  sum([line.debit for line in receivables])
                
        result['receivables'] = {}
        result['receivables']['count'] = len(receivables)
        result['receivables']['total_amount'] = "%.2f" % receivables_amount


        
        result['total_inbox'] = len(inbox)+len(payables)+len(receivables)
        
        
        vendors = self.env['res.partner'].search([('supplier', '=', True)])
        ach_vendors_lists = self.env['res.partner'].search([('supplier', '=', True),('vendor_payment_mode','=', 'ACH')])
        ach_vendors = len(ach_vendors_lists)
        print ach_vendors
        manual_payment_vendors_lists = self.env['res.partner'].search([('supplier', '=', True),('vendor_payment_mode','=', 'Manual Payment')])
        manual_payment_vendors = len(manual_payment_vendors_lists)
        print manual_payment_vendors
        echeck_vendors_lists = self.env['res.partner'].search([('supplier', '=', True),('vendor_payment_mode','=', 'eCheck')])
        echeck_vendors = len(echeck_vendors_lists)
        print echeck_vendors
        no_activity_percentage = 0

        last_year_date = (datetime.now()- timedelta(days=365)).strftime('%Y-%m-%d')
        sql = "select count(distinct partner_id) total_partner from account_invoice where partner_id in (select id from res_partner where supplier = True) and date_invoice >= '"+last_year_date+"'"
        self.env.cr.execute(sql)
        no_activity_vendors =  self.env.cr.dictfetchall()[0]['total_partner']
        no_activity_percentage = (no_activity_vendors / len(vendors)) * 100

            

        percent_of_manual_payment_vendors = int(manual_payment_vendors / len(vendors) * 100)
        percent_of_ach = int(ach_vendors / len(vendors) * 100)
        percent_of_echeck_vendors = int(echeck_vendors / len(vendors) * 100)
            


        result['vendors'] = {}
        result['vendors']['count'] = len(vendors)
        result['vendors']['no_activity'] = no_activity_vendors
        result['vendors']['no_activity_percentage'] = int(no_activity_percentage)
        
        
        result['vendors']['manual_payment_count'] = manual_payment_vendors
        result['vendors']['manual_payment_percentage'] = percent_of_manual_payment_vendors
        

        result['vendors']['ach_count'] = ach_vendors
        result['vendors']['ach_percentage'] = percent_of_ach
        
        result['vendors']['echeck_count'] = echeck_vendors
        result['vendors']['echeck_percentage'] = percent_of_echeck_vendors


        sql = "SELECT sum(credit) credit, sum(debit) debit from account_move_line where account_id in (select account_account_id from account_account_account_tag where account_account_tag_id in (select id from account_account_tag where name = 'BillPayIntercompany'))"
        
        
        self.env.cr.execute(sql)
        results = self.env.cr.dictfetchall()
        credit =  results[0]['credit']
        debit =  results[0]['debit']
        balance = credit - debit
        result['balance'] = "%.2f" % balance
        
        return result
    

BillPayDashboard()

# This class maintains all the bill sync data
class BillPayInbox(models.Model):
    _name = 'billpay.inbox'
    _description = "BillPay"
    _inherit = ['mail.thread']
    _order = 'id asc'
    _rec_name = 'sender'
    name = fields.Char(string = 'Name',  copy = False, index = True)
    state = fields.Selection([('open', 'Open'), ('processed', 'Processed')], string = 'Status',
                         copy = False, index = True, default = 'open')
    billsource = fields.Selection([('email', 'Email'), ('fax', 'Fax'), ('upload','Upload') ], string = 'Source',
                        copy = False, default = 'upload')
    partner_id = fields.Many2one('res.partner', string = 'Vendor')
    sender = fields.Char(string = 'Sender', copy = False, default = lambda  self:self.env.user.email)
    subject = fields.Char('Subject')
    submit_date = fields.Datetime(string = 'Submit Date', readonly = True, states = {'open': [('readonly', False)]},
                                 default = lambda self: fields.datetime.now())
    
    attachment = fields.Binary('Attachment', attachment=True)
    mimetype = fields.Char()

    @api.multi
    def view_file(self):
        context = dict(self._context or {})
        context.update({'default_attachment':self.attachment})
        view_id = self.env.ref('vitalpet_bill_pay.view_pdf_files_form').id
        return {
            'name': _('Attachment'),           
            'view_type': 'form',
            'type': 'ir.actions.act_window',
            "views": [[view_id, "form"]],
            'target': 'new',
            'res_model': 'view.file',
            'context':context,                
        }

    @api.multi
    def action_duplicate(self):        
        self.ensure_one()
        billpay_inbox_copy = self.copy()
        if billpay_inbox_copy:
            return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'bill_pay.billpay_inbox',
                'res_id': billpay_inbox_copy.id,
                'context': self.env.context,
                'flags': {'initial_mode': 'edit'},
            }
        return False


    
    @api.model
    def create_record_inbox(self, file_buffer, file_name):
        # create the new ir_attachment
        new_file_buffer = None
        print file_buffer
        if '.jpg' in file_name or '.jpeg' in  file_name or '.JPG' in file_name or '.JPEG' in  file_name :
            new_file_buffer=file_buffer.replace("data:image/jpeg;base64,", "")
        if '.png' in file_name or '.PNG' in file_name:
            new_file_buffer = file_buffer.replace("data:image/png;base64,", "")
        if '.pdf' in file_name or '.PDF' in file_name:
            new_file_buffer = file_buffer.replace("data:application/pdf;base64,", "")
        if '.xls' in file_name or '.XLS' in file_name or '.xlsx' in file_name or '.XLSX' in file_name or '.csv' in file_name or '.CSV' in file_name:
            new_file_buffer = file_buffer.replace("data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,", "")
        
        
        mimetype = mimetypes.guess_type(file_name)[0]
        
        if not new_file_buffer:
            raise UserError(_('Invalid File Type'))
            
        attachment_value = {
            
            'sender':self.env.user.email,
            'attachment': new_file_buffer,
            'mimetype': mimetype,
         }
        super(BillPayInbox, self).create(attachment_value)


# # Create bill pay through incoming mail and update partner who sent this mail
#     @api.model
#     def message_new(self, msg, custom_values = None):
#         """ Override to updates the document according to the email. """
#         if custom_values is None:
#             custom_values = {}
#         defaults = {'billsource': 'email'}
#         if msg:
#             # Get partner Mail ID
#             email_list = tools.email_split((msg.get('from') or ''))
#             print email_list
#             if email_list:
#                 print email_list[0]
#                 supplier_ids = self.env['res.partner'].search([('email', '=', email_list[0])])
#                 if supplier_ids:
#                     # If Multiple partner mail exist consider a partner not all of them
#                     for supplier_id in supplier_ids:
#                         partner_id = supplier_id.id
#                     # Force updated parner and sender mail ID in the form
#                     defaults.update({'partner_id': partner_id, 'sender': email_list[0]})
#                 else:
#                     defaults.update({'sender': str(email_list[0]) + '(' + str('Unknown') + ')'})
#             attachment_email = msg.get('attachments')
#             print attachment_email
#             if attachment_email:
#                 defaults.update({'attachment':attachment_email})
# 
#         defaults.update(custom_values)
#         res = super(BillPayInbox, self).message_new(msg, custom_values = defaults)
#         return res
    
    @api.multi
    def action_create_new_bill(self):
        ctx = self._context.copy()
        model = 'billpay.bills'
        if self.partner_id:
            ctx.update({'default_partner_id':self.partner_id.id})
            
        attachment = self.env['ir.attachment'].search([('res_model','=','billpay.inbox'),('res_field', '=', 'attachment'), ('res_id', '=', self.id)])
#       
        domain = [
            ('type', '=', 'purchase'),
            ('company_id', '=', self.env.user.company_id.id),
        ]
        journal = self.env['account.journal'].search(domain, limit=1)
        if journal:
            ctx.update({'default_journal_id':journal.id})
        ctx.update({'default_bill_credit_type':'bill','default_bill_credit_source':'inbox','default_bill_date':self.submit_date, 'default_inbox_id':self.id,'default_attachment':self.attachment,'default_attachment_type':attachment.mimetype})
#         ctx.update({'journal_type': self.type, 'default_type': 'out_invoice', 'type': 'out_invoice', 'default_journal_id': self.id})
        view_id = self.env.ref('vitalpet_bill_pay.view_billpay_bills_form_with_image').id
        return {
            'name': _('Create bill / credit'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': model,
            'view_id': view_id,
            'context': ctx,
        }
        
    @api.multi
    def action_create_new_credit(self):
        ctx = self._context.copy()
        model = 'billpay.bills'
        if self.partner_id:
            ctx.update({'default_partner_id':self.partner_id.id})
            
        attachment = self.env['ir.attachment'].search([('res_model','=','billpay.inbox'),('res_field', '=', 'attachment'), ('res_id', '=', self.id)])
        domain = [
            ('type', '=', 'purchase'),
            ('company_id', '=', self.env.user.company_id.id),
        ]
        journal = self.env['account.journal'].search(domain, limit=1)
        if journal:
            ctx.update({'default_journal_id':journal.id})
        ctx.update({'default_bill_credit_type':'credit', 'default_bill_credit_source': 'inbox','default_bill_date':self.submit_date, 'default_inbox_id':self.id,'default_attachment':self.attachment,'default_attachment_type':attachment.mimetype})
#         ctx.update({'journal_type': self.type, 'default_type': 'out_invoice', 'type': 'out_invoice', 'default_journal_id': self.id})
        view_id = self.env.ref('vitalpet_bill_pay.view_billpay_bills_form_with_image').id
        return {
            'name': _('Create bill / credit'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': model,
            'view_id': view_id,
            'context': ctx,
        }

    @api.multi
    def action_create_existing_bill(self):
        active_ids=[]
        context = dict(self._context)
        for bill in self:
            active_ids.append(bill.id)

        context['active_ids'] = active_ids
        context['default_bill_credit_type'] = 'bill'
        context['default_inbox_id'] = self.id
        return {
            'name': _('Add to Existing Bill'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'add.existing.bill',
            'view_id': self.env.ref('vitalpet_bill_pay.add_existing_bill_view_form').id,
            'type': 'ir.actions.act_window',
            'context': context,
            'target': 'new'
        }
        
    @api.multi
    def action_create_existing_credit(self):        
        active_ids=[]
        context = dict(self._context)
        for bill in self:
            active_ids.append(bill.id)

        context['active_ids'] = active_ids
        context['default_bill_credit_type'] = 'credit'
        context['default_inbox_id'] = self.id
        return {
            'name': _('Add to Existing Credit'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'add.existing.bill',
            'view_id': self.env.ref('vitalpet_bill_pay.add_existing_credit_view_form').id,
            'type': 'ir.actions.act_window',
            'context': context,
            'target': 'new'
        }
        
    @api.multi
    def action_create_vendor_doc(self):        
        active_ids=[]
        context = dict(self._context)
        for bill in self:
            active_ids.append(bill.id)
        context['active_ids'] = active_ids
        context['default_bill_credit_type'] = 'document'
        context['default_inbox_id'] = self.id
        return {
            'name': _('Add to Existing Document'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'add.existing.doc',
            'view_id': self.env.ref('vitalpet_bill_pay.add_existing_doc_view_form').id,
            'type': 'ir.actions.act_window',
            'context': context,
            'target': 'new'
        }
        
    @api.multi
    def action_create_vendor_contract(self):  
        active_ids=[]
        context = dict(self._context)
        for bill in self:
            active_ids.append(bill.id)
        context['active_ids'] = active_ids
        context['default_bill_credit_type'] = 'contract'
        context['default_inbox_id'] = self.id
        return {
            'name': _('Add to Existing Contract'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'add.existing.doc',
            'view_id': self.env.ref('vitalpet_bill_pay.add_existing_cont_view_form').id,
            'type': 'ir.actions.act_window',
            'context': context,
            'target': 'new'
        }
    
    @api.model
    def unlink_inbox(self, file_id):
        attachment_obj=self.env['ir.attachment'].search([('id', '=', file_id)])
        if attachment_obj:
            attachment_obj.unlink()
        return True


    @api.model
    def save_new_file(self, file_buffer, file_name):
        # create the new ir_attachment
        if '.jpg' in file_name:
            file_buffer=file_buffer.replace("data:image/jpeg;base64,", "")
        if '.png' in file_name:
            file_buffer = file_buffer.replace("data:image/png;base64,", "")
        if '.pdf' in file_name:
            file_name = file_name.replace(".pdf", ".png")
            if 'data:application/pdf;base64' in file_buffer:
                file_buffer = file_buffer.replace("data:application/pdf;base64,", "")
            if 'data:image/png;base64' in file_buffer:
                file_buffer = file_buffer.replace("data:image/png;base64,", "")
        attachment_value = {
            'name': file_name,
            'res_name': file_name,
            'res_model': 'billpay.inbox',
            'datas': file_buffer,
            'datas_fname' : file_name,
         }
        attachment=self.env['ir.attachment'].create(attachment_value)
        attachment=({'attachment_id':attachment.id})
        return attachment
  
    @api.model
    def get_inbox(self) :
        menu_items = self.env['ir.ui.menu'].search([('name', 'ilike', 'Bills'), ('active', '=', True)], limit=1, order = 'name asc')
        inbox_files = self.env['ir.attachment'].search([('res_model', '=', 'billpay.inbox')], order = 'create_date desc')
        attachments = []
        for file in inbox_files:
            files = {}
            if '.jpg' in file.name:
                files.update({'file_id':file.id,'file_data': "data:image/jpeg;base64," + file.datas, 'file_name': file.name.replace('.jpg','')})
            if '.png' in file.name:
                files.update({'file_id':file.id,'file_data': "data:image/png;base64," + file.datas, 'file_name': file.name.replace('.png','')})
            if '.pdf' in file.name:
                files.update({'file_id':file.id,'file_data': file.datas, 'file_name' : file.name.replace('.pdf','')})
 
            files.update({'id': menu_items.id, 'action' : menu_items.action.id, 'menu_model' : menu_items.action.type, 'menu_obj': menu_items.action.res_model})
            attachments.append(files)
        return attachments
 
class MailMessage(models.Model):
    _inherit = 'mail.message'
 
    mail_message_id = fields.Many2one('billpay.log', 'Bill Pay Log')
 
# Fixme This need to be updated
    @api.multi
    def send_error_mail(self, MailMessage_objs) :
        mails_to_send = self.env['mail.mail']
        rendering_context = dict(self._context)
        rendering_context.update({'email_from': 'vetzip.vitalpet.net',})
        invitation_template = self.env.ref('bill_pay.email_template_bill_pay_error')
        invitation_template = invitation_template.with_context(rendering_context)
        MailMessage_id=MailMessage_objs.id
        mail_id = invitation_template.send_mail(MailMessage_id)
        current_mail = self.env['mail.mail'].browse(mail_id)
        current_mail.write({'email_to': 'gvincent.sk@gmail.com'})
        mails_to_send |= current_mail
        if mails_to_send:
            mails_to_send.send()
        return True
#          
# class BillPayLog(models.Model):
#     _name = 'billpay.log'
#     _rec_name = 'sync_date'
#  
#     sync_date = fields.Date('Date')
#     lastsync = fields.Datetime('Last Sync Date')
#     incoming_mail_ids = fields.One2many('mail.message', 'mail_message_id', string = 'Event Mails')
# # 
# # 
# BillPayLog()
#   
class ImageUpdate(models.TransientModel):
    _name = 'view.file'
    
    attachment = fields.Binary('Attachment', attachment=True)
   

        
        


