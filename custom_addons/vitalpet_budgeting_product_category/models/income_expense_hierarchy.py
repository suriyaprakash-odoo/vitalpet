from odoo import api, fields, models, _
import time
import datetime


class IncomeExpenseHierarchy(models.Model):
    _name = "income.expense.hierarchy"
    _order = "sequence"

    category_id = fields.Many2one('product.category', 'Product Category')
    name = fields.Char(related='category_id.name', string='Name', store=True)
    sequence = fields.Char('Hierarchy Sequence')
    sign = fields.Selection([('preserve','Preserve Balance Sign'),('reverse','Reverese Balance Sign')], string='Sign on Reports')
    hierarchy_line = fields.One2many('hierarchy.line', 'hierarchy_id', string='Hierarchy Lines')
    include = fields.Boolean(string='Included in Income and Expense Detail')
    tag = fields.Selection([('grossrevenue', 'Revenue'), ('discounts', 'Discounts and Adjustments'), ('netrevenue', 'Net Revenue'), ('costofgoods', 'Cost of Goods Sold'),('grossmargin', 'Gross Margin'),('expenses', 'Expenses'),('EBITDA', 'EBITDA'),('depreciation','Depreciation Expenses')],string='Tags')
    type = fields.Selection([
        ('revenue', 'Revenue'),
        ('income', 'Income'),
        ('expense', 'Expense'),
        ], string='Type')
    view_type = fields.Selection([
        ('view', 'View'), ('regular', 'Regular')],string='View')
    formula = fields.Char('Formula')
    code = fields.Char('Code')



class HierarchyLine(models.Model):
    _name = "hierarchy.line"
    _order = "sequence"


    hierarchy_id = fields.Many2one('income.expense.hierarchy', string='IncomeExpense Id')
    parent_id = fields.Many2one('hierarchy.line', string='Parent')
    view_type = fields.Selection([
        ('view', 'View'), ('regular', 'Regular')],string='View')
    children_ids = fields.One2many('hierarchy.line', 'parent_id', string='Children')
    category_id = fields.Many2one('product.category', 'Product Category')
    name = fields.Char(related='category_id.name', string='Name', store=True)
    code = fields.Char('Code')
    type = fields.Selection([
        ('revenue', 'Revenue'),
        ('income', 'Income'),
        ('expense', 'Expense'),
        ], 'Type')
    sequence = fields.Char('Sequence')
    sign = fields.Selection(related='hierarchy_id.sign' , string='Sign on Reports')
    include = fields.Boolean(string='Included in Income and Expense Detail')
    formula = fields.Char('Formula')
    subtract = fields.Boolean(string='Subtract')







    