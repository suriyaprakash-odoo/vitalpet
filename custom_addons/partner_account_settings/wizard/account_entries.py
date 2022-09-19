
from odoo import api, fields, models


class AccountEntries(models.TransientModel):
    _name = 'account.entries' 
    
    def continue_to_new_entry(self):    	
    	account_receivable = self.env.context.get('account_receivable_id')    	
    	account_payable = self.env.context.get('account_payable_id')    	
        partners = self.env['res.partner'].browse(self.env.context.get('active_ids'))
        for partner in  partners:
#         	if account_receivable is not False:
        		partner.write({'property_account_receivable_id':account_receivable})
#         	if account_payable is not False:
        		partner.write({'property_account_payable_id':account_payable})
        
   
