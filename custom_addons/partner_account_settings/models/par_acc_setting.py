from odoo import api, fields, models, _

class Company(models.Model):
    _inherit = "res.company"
    
    property_account_receivable_id = fields.Many2one('account.account', string='Receivable Account')
    property_account_payable_id = fields.Many2one('account.account', string='Payable Account')
    
    
    
class Partner(models.Model):
    _inherit = "res.partner"


    property_account_receivable_id = fields.Many2one('account.account', string='Receivable Account', domain="[('internal_type', '=', 'receivable'), ('deprecated', '=', False)]")
    property_account_payable_id = fields.Many2one('account.account', string='Payable Account',domain="[('internal_type', '=', 'payable'), ('deprecated', '=', False)]")
    
    @api.multi
    def write(self, vals):
        for rec in self:
            if rec.parent_id:
                if not rec.property_account_receivable_id:
                    vals['property_account_receivable_id'] = rec.parent_id.property_account_receivable_id
                if not rec.property_account_payable_id:
                    vals['property_account_payable_id'] = rec.parent_id.property_account_payable_id
                
        return super(Partner, self).write(vals) 
    
    @api.model
    def default_get(self, fields):
        res = super(Partner, self).default_get(fields)
        if self.env.uid:
            company_sr = self.env["res.users"].search([('id','=',self.env.uid)])
            property_account_receivable_id = company_sr.company_id.property_account_receivable_id.id
            property_account_payable_id = company_sr.company_id.property_account_payable_id.id
        res.update({'property_account_receivable_id': property_account_receivable_id,'property_account_payable_id':property_account_payable_id})
        return res
   
    @api.model  
    def confirm(self):
        categ_obj = self.env['res.partner']
        vals = {}
        for loop in self.env.context['active_ids']:
            categ_br = categ_obj.browse(loop)
            if not categ_br.property_account_receivable_id:
                vals['property_account_receivable_id'] = self.income_account_id.id
            if not categ_br.property_account_payable_id:
                vals['property_account_payable_id'] = self.expense_account_id.id
            categ_br.write(vals)
        return True
    
    