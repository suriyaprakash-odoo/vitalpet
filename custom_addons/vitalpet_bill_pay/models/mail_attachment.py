from odoo import api, fields, models, tools, _
from odoo.tools import email_split
from odoo.exceptions import UserError, ValidationError
import mimetypes

class BillPayAttachment(models.Model):
    _name = 'bill.pay.attachment'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Bill Pay Email Attachment"
    
    name=fields.Char('Attachment Name')
    partner_id = fields.Many2one('res.partner')
    sender_email = fields.Char()
    subject= fields.Char()

    
    
    @api.model
    def message_new(self, msg_dict, custom_values=None):
        if custom_values is None:
            custom_values = {}
 
        email_address = email_split(msg_dict.get('email_from', False))[0]
 
        partner = self.env['res.partner'].search([
            ('email', 'ilike', email_address),
        ], limit=1)
         
        if partner:
            custom_values.update({
                'partner_id': partner.id,
            })
 
        name = msg_dict.get('subject', '')
 
         
 
        custom_values.update({
            'name': name.strip(),
            'subject':name.strip(),
            'sender_email':email_address,
        })
#     
        return super(BillPayAttachment, self).message_new(msg_dict, custom_values)
    
  

class IrAttachment(models.Model):
    _inherit = "ir.attachment"
      
    @api.model
    def create(self, vals):
        if vals.get('res_model'):
            if vals.get('res_model') == 'bill.pay.attachment':
                if vals.get('res_id'):
                    bill_pay_attachment = self.env['bill.pay.attachment'].search([('id', '=', vals.get('res_id'))])
                    billpay_inbox = self.env['billpay.inbox']
                      
                    file_name = vals.get('datas_fname')
                    file_buffer = vals.get('datas')
                      
#                     if '.jpg' in file_name or '.jpeg' in  file_name:
#                         new_file_buffer=file_buffer.replace("data:image/jpeg;base64,", "")
#                     if '.png' in file_name:
#                         new_file_buffer = file_buffer.replace("data:image/png;base64,", "")
#                     if '.pdf' in file_name:
#                         new_file_buffer = file_buffer.replace("data:application/pdf;base64,", "")
#                     if '.PDF' in file_name:
#                         new_file_buffer = file_buffer.replace("data:application/pdf;base64,", "")
#                   
                    new_file_buffer=False
                                
                    if '.jpg' in file_name or '.jpeg' in  file_name or '.JPG' in file_name or '.JPEG' in  file_name :
                        new_file_buffer=file_buffer.replace("data:image/jpeg;base64,", "")
                    if '.png' in file_name or '.PNG' in file_name:
                        new_file_buffer = file_buffer.replace("data:image/png;base64,", "")
                    if '.pdf' in file_name or '.PDF' in file_name:
                        new_file_buffer = file_buffer.replace("data:application/pdf;base64,", "")
                    if '.xls' in file_name or '.XLS' in file_name or '.xlsx' in file_name or '.XLSX' in file_name or '.csv' in file_name or '.CSV' in file_name:
                        new_file_buffer = file_buffer.replace("data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,", "")
                    if '.doc' in file_name or '.DOC' in file_name or '.docx' in file_name or '.DOCX' in file_name:
                        new_file_buffer = file_buffer.replace("data:application/vnd.openxmlformats-officedocument.wordprocessingml.document;base64,", "")
                    
                        
                    mimetype = mimetypes.guess_type(file_name)[0]
                      
                    if not new_file_buffer:
                        return super(IrAttachment, self).create(vals)
                    if bill_pay_attachment.partner_id:
                        partner = bill_pay_attachment.partner_id.id
                    else:
                        partner = False
                        
                    attachment_value = {
                          
                        'sender':bill_pay_attachment.sender_email,
                        'subject':bill_pay_attachment.subject,
                        'partner_id':partner,
                        'attachment': new_file_buffer,
                        'billsource': 'email',
                        'mimetype': mimetype,
                     }
                    billpay_inbox.create(attachment_value)
                  
        return super(IrAttachment, self).create(vals)
        
        
            

    

