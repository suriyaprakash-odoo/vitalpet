# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError 

class AddExistingBill(models.TransientModel):

    _name = "add.existing.bill"
    _description = "Add to Existing"
    
    inbox_id = fields.Many2one('billpay.inbox')
    partner_id = fields.Many2one('res.partner', string='Vendor', required=True)
    bill_credit_type = fields.Selection([('bill', 'Bill'), ('credit', 'Credit')], string='Bill Credit Type', track_visibility='onchange')
    from_date = fields.Date('From Date')
    to_date = fields.Date('To Date')
    line_ids = fields.One2many('add.existing.bill.lines', 'parent_id', 'Lines')
    
    @api.onchange('partner_id','from_date', 'to_date')
    def onchange_partner(self):
        
        domain = [('state', '=', 'open'),('bill_credit_type','=',self.bill_credit_type)]
        if self.from_date and self.to_date:
            domain.append(('bill_date','>=',self.from_date))
            domain.append(('bill_date','<=',self.to_date))            
        if self.partner_id:
            domain.append(('partner_id', '=', self.partner_id.id))
            bill_obj = self.env['billpay.bills'].search(domain)
            if bill_obj:
                self.line_ids = [(0, 0, {'bill_id': i.id}) for i in bill_obj]
            else:
                self.line_ids = []

    @api.multi
    def add_to_existing_bills(self):
        count = 0
        if len(self.line_ids) == 0:
            raise UserError(_('No records found.'))
        for line in self.line_ids:
            if line.select:
                count+=1
                
        if count == 1:
            self.env['ir.attachment'].create({'datas':line.bill_id.attachment, 'name':line.bill_id.bill_credit_id, 'res_model':'billpay.bills', 'res_id':line.bill_id.id, 'datas_fname':line.bill_id.bill_credit_id})
            line.bill_id.write({'attachment':self.inbox_id.attachment})
            self.inbox_id.write({'state': 'processed'})
            action = self.env.ref('vitalpet_bill_pay.action_billpay_bills_open')
            view_id = self.env.ref('vitalpet_bill_pay.view_billpay_bills_form_with_image').id
            return {
                'name': action.name,
                'help': action.help,
                'type': action.type,
                "views": [[view_id, "form"]],
                'target': action.target,
                'res_model': action.res_model,
                'res_id': line.bill_id.id,                
                'flags':{'options': {'mode': 'edit'}},            
#                 'domain': [('id', '=', line.bill_id.id)],
            }
        else:
            raise UserError(_('Select any one of the item.'))
#         
    
    
class AddExistingBillLines(models.TransientModel):
    _name = 'add.existing.bill.lines'
    
    select = fields.Boolean('Select')
    bill_id = fields.Many2one('billpay.bills', 'Existing Bill')
    # invoice_number = fields.Char(related='bill_id.invoice_number', readonly=True)
    invoice_amount = fields.Float(related='bill_id.invoice_amount', readonly=True)
    parent_id = fields.Many2one('add.existing.bill', 'Parent Bill')
    
