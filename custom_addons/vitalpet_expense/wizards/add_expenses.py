# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError 
import random

class AddExpenses(models.TransientModel):

    _name = "add.expenses"
    _description = "Add to Expenses"
    
    receipt_id = fields.Many2one('hrexpense.myreceipt')
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    from_date = fields.Date('From Date')
    to_date = fields.Date('To Date')
    line_ids = fields.One2many('add.expenses.lines', 'parent_id', 'Lines')
    
    @api.onchange('employee_id','from_date', 'to_date')
    def onchange_employee(self):
        
        domain = [('state', '=', 'draft')]
        if self.from_date and self.to_date:
            domain.append(('date','>=',self.from_date))
            domain.append(('date','<=',self.to_date))            
        if self.employee_id:
            domain.append(('employee_id', '=', self.employee_id.id))
            print domain
            expense_obj = self.env['hr.expense'].search(domain)
            if expense_obj:
                self.line_ids = [(0, 0, {'expense_id': i.id}) for i in expense_obj]
            else:
                self.line_ids = []

    @api.multi
    def add_to_expenses(self):
        count = 0
        if len(self.line_ids) == 0:
            raise UserError(_('No records found.'))
        for line in self.line_ids:
            if line.select:
                count+=1
                expense_id = line.expense_id.id
                
        if count == 1:
            if self.receipt_id.name:
                name = self.receipt_id.name
            else:
                name = random.randint(0,5877844)
            self.env['ir.attachment'].create({'datas':self.receipt_id.attachment, 'name':name, 'res_model':'hr.expense', 'res_id':expense_id, 'datas_fname':self.receipt_id.name})
            self.receipt_id.write({'state': 'processed'})
            action = self.env.ref('hr_expense.hr_expense_actions_all')
            view_id = self.env.ref('hr_expense.hr_expense_form_view').id
            return {
                'name': action.name,
                'help': action.help,
                'type': action.type,
                "views": [[view_id, "form"]],
                'target': action.target,
                'res_model': action.res_model,
                'res_id': expense_id,                
                'flags':{'options': {'mode': 'edit'}},            
#                 'domain': [('id', '=', line.bill_id.id)],
            }
        else:
            raise UserError(_('Select any one of the item.'))
#         
    
    
class AddExpensesLines(models.TransientModel):
    _name = 'add.expenses.lines'
    
    select = fields.Boolean('Select')
    expense_id = fields.Many2one('hr.expense', 'Expenses')
    unit_amount = fields.Float(related='expense_id.unit_amount', readonly=True)
    product_id = fields.Many2one(related='expense_id.product_id', readonly=True)
    description = fields.Char(related='expense_id.name', readonly=True)
    parent_id = fields.Many2one('add.expenses', 'Parent Bill')
    
