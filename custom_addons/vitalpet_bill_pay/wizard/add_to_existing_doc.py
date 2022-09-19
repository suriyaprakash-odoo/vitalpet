# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError 

class AddExistingDoc(models.TransientModel):

    _name = "add.existing.doc"
    _description = "Add to Existing"
    
    inbox_id = fields.Many2one('billpay.inbox')
    partner_id = fields.Many2one('res.partner', string='Vendor', required=True)
    bill_credit_type = fields.Selection([('document','Document'),('contract','Contract')], string='Vendor Document Contract Type', track_visibility='onchange')
  
    @api.multi  
    def add_to_existing_doc(self):  
       
        self.env['ir.attachment'].create({'datas':self.inbox_id.attachment, 'name':self.bill_credit_type, 'res_model':'res.partner', 'res_id':self.partner_id.id, 'datas_fname':self.partner_id.name})
        self.partner_id.write({'attachment':self.inbox_id.attachment})
        self.inbox_id.write({'state': 'processed'})
        action = self.env.ref('base.action_partner_form_view2')        
        view_id = self.env.ref('base.view_partner_form').id       

        return {
            'name': _('Attachment'),           
            'view_type': 'form',
            'type': 'ir.actions.act_window',
            "views": [[view_id, "form"]],
            'target': 'current',
            'res_model': 'res.partner',
            'res_id': self.partner_id.id,                
            'flags':{'options': {'mode': 'edit'}},            
            
        }

       

