from odoo import api, fields, models, tools, _
from odoo.tools import email_split
from odoo.exceptions import ValidationError, UserError
import mimetypes
  

class HrExpenseMailAttachment(models.Model):
    _name = 'hr.expense.mail.attachment'
    _inherit = ['mail.thread']
    _description = "Expense Email Attachment"
    
    name=fields.Char('Attachment Name')
    employee_id = fields.Many2one('hr.employee')
    sender_email = fields.Char()
    subject= fields.Char()
    
    
    @api.model
    def message_new(self, msg_dict, custom_values=None):
        if custom_values is None:
            custom_values = {}
 
        email_address = email_split(msg_dict.get('email_from', False))[0]
 
        employee = self.env['hr.employee'].search([
            '|',
            ('work_email', 'ilike', email_address),
            ('user_id.email', 'ilike', email_address)
        ], limit=1)
        if employee:
            custom_values.update({
                'employee_id': employee.id,
            })
 
        name = msg_dict.get('subject', '')
 
         
 
        custom_values.update({
            'name': name.strip(),
            'subject':name.strip(),
            'sender_email':email_address,
        })
#
        return super(HrExpenseMailAttachment, self).message_new(msg_dict, custom_values)
    
  

class IrAttachment(models.Model):
    _inherit = "ir.attachment"
      
    @api.model
    def create(self, vals):
        if vals.get('res_model'):
            if vals.get('res_model') == 'hr.expense.mail.attachment':
                if vals.get('res_id'):
                    hr_expense_mail_attachment = self.env['hr.expense.mail.attachment'].search([('id', '=', vals.get('res_id'))])
                    print hr_expense_mail_attachment  
                    hr_expense_myreceipt = self.env['hrexpense.myreceipt']
                      
                    file_name = vals.get('datas_fname')
                    file_buffer = vals.get('datas')
                      
                    if '.jpg' in file_name or '.jpeg' in  file_name:
                        new_file_buffer=file_buffer.replace("data:image/jpeg;base64,", "")
                    if '.png' in file_name:
                        new_file_buffer = file_buffer.replace("data:image/png;base64,", "")
                    if '.pdf' in file_name:
                        new_file_buffer = file_buffer.replace("data:application/pdf;base64,", "")
                      
                      
                    mimetype = mimetypes.guess_type(file_name)[0]
                    company_id = self.env.user.company_id.id
                      
                    if not new_file_buffer:
                        raise UserError(_('Invalid File Type'))
                    if hr_expense_mail_attachment.employee_id:
                        employee = hr_expense_mail_attachment.employee_id.id
                        if hr_expense_mail_attachment.employee_id.company_id:
                            company_id = hr_expense_mail_attachment.employee_id.company_id.id
                    else:
                        employee = False
                        
                    
                   
                    attachment_value = {
                        'name':file_name, 
                        'sender':hr_expense_mail_attachment.sender_email,
                        'subject':hr_expense_mail_attachment.subject,
                        'employee_id':employee,
                        'company_id':company_id,
                        'attachment': new_file_buffer,
                        'mimetype': mimetype,
                     }
                    hr_expense_myreceipt.create(attachment_value)
                  
              
        return super(IrAttachment, self).create(vals)
        