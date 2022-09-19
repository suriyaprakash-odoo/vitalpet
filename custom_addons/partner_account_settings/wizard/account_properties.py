# -*- coding: utf-8 -*-

from odoo import api, fields, models


class AccountAssetProperties(models.TransientModel):
    _name = 'account.asset.properties'   
   

    company_id = fields.Many2one('res.company',"Company",default=lambda self: self.env.user.company_id.id, readonly=True)
    account_payable_id = fields.Many2one('account.account', company_dependent=True,
        string="Account Payable")
    account_receivable_id = fields.Many2one('account.account', company_dependent=True,
        string="Account Receivable")

    @api.multi
    def action_account_property(self):
        context = dict(self._context)
        partners = self.env['res.partner'].browse(self.env.context.get('active_ids'))
        context['account_receivable_id'] = self.account_receivable_id.id or self.account_receivable_id.id or False
        context['account_payable_id'] = self.account_payable_id.id or self.account_payable_id.id or False 
        
        for partner in  partners:  
#             if self.account_receivable_id:
                if partner.property_account_receivable_id:
                    return {
                        'name': ('Account Entry Existing'),
                        'view_type': 'form',
                        'view_mode': 'form',
                        'res_model': 'account.entries',
                        'view_id': self.env.ref('partner_account_settings.account_entries_warnig_form').id,
                        'type': 'ir.actions.act_window',
                        'context': context,
                        'target': 'new'
                    }
                else:
                    partner.write({'property_account_receivable_id':self.account_receivable_id})
#             if self.account_payable_id: 
                if partner.property_account_payable_id:               
                    return {
                        'name': ('Account Entry Existing'),
                        'view_type': 'form',
                        'view_mode': 'form',
                        'res_model': 'account.entries',
                        'view_id': self.env.ref('partner_account_settings.account_entries_warnig_form').id,
                        'type': 'ir.actions.act_window',
                        'context': context,
                        'target': 'new'
                    }
                else:
                    partner.write({'property_account_payable_id':self.account_payable_id})
        return True 