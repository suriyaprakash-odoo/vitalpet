from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    corporate_card = fields.Boolean(string="Corporate Card")
    assigned_to_id = fields.Many2one("hr.employee",string="Assigned To")
    
   
    @api.model
    def create(self, vals):
        res=super(ResPartner, self).create(vals)
         
        if vals.get('assigned_to_id'):           
            emp_rec = self.env["hr.employee"].search([('id', '=',vals.get('assigned_to_id'))]) 
            if emp_rec.credit_card_id:
                res_card = self.env["res.partner"].search([('id', '=',emp_rec.credit_card_id.id)])
                raise UserError(_('A Credit Card has been assigned already to this employee. Already Assigned card is - ' + res_card.name) ) 
            else:    
                emp_rec.write({
                    'credit_card_id': res.id,
                    })
         
        return res
     
    @api.multi
    def write(self, vals): 
        for line in self:
            if vals.get('assigned_to_id'):
                hr_employee = self.env["hr.employee"].search([('credit_card_id', '=',line.id)]) 
                if hr_employee:
                    raise UserError(_('A Credit Card has been assigned already to this employee. Employee name - ' + hr_employee.name) ) 
                    
                emp_rec = self.env["hr.employee"].search([('id', '=',vals.get('assigned_to_id'))]) 
                if emp_rec.credit_card_id:
                    res_card = self.env["res.partner"].search([('id', '=',emp_rec.credit_card_id.id)])
                    raise UserError(_('The employee already has credit card. Already Assigned card is - ' + res_card.name) ) 
                emp_rec.write({
                    'credit_card_id': self.id,
                    })
            if vals.get('assigned_to_id') == False:
                emp_rec = self.env["hr.employee"].search([('id', '=',line.assigned_to_id.id)]) 
                emp_rec.write({
                    'credit_card_id': False,
                    })
                 
        res=super(ResPartner, self).write(vals)        
        return res
