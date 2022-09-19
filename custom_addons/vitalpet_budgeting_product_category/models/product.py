# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class ProductCategory(models.Model):
    _inherit = 'product.category'

    income_expense_detail = fields.Boolean('Included in Income and Expense Detail', copy=False, help="Checks to include income and expense detail")
    income_view_parent = fields.Char('Income view Parent', copy=False)
    income_view_code = fields.Char('Income View Code',copy=False)
    income_budget_code = fields.Char('Income Budget Code', copy=False)
    expense_view_parent = fields.Char('Expense view Parent', copy=False)
    expense_view_code = fields.Char('Expense View Code',copy=False)
    expense_budget_code = fields.Char('Expense Budget Code', copy=False)
    index_products = fields.Boolean('Index Products in This Category', copy=False)
    total_budget = fields.Integer(compute='_budget_total', string="Total Invoiced")

    
    @api.one
    def _budget_total(self):
        budget_obj = self.env['budget.category.lines']
        budget_lines = budget_obj.search([('product_category', '=', self.id)])
        self.total_budget = len(budget_lines)
    
    
    
    
    def open_budget_history(self):
            '''
            This function returns an action that display invoices/refunds made for the given partners.
            '''
            action = self.env.ref('vitalpet_budgeting_product_category.act_budget_category_lines_view')
            result = action.read()[0]
            result['domain'] = [('product_category', 'in', self.ids)]
            return result