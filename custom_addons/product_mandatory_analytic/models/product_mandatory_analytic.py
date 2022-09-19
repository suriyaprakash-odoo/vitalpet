from odoo import api, fields, models, tools, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    require_analytic = fields.Boolean(string='Require Analytic Account')
    
    
    
class BillPayLines(models.Model):
    _inherit = 'billpay.lines'
    
    req_analytic = fields.Boolean(related='product_id.require_analytic', string ="Analytic account mandatory")
    
class HrExpense(models.Model):
    _inherit = "hr.expense"
    
    exp_analytic = fields.Boolean(related='product_id.require_analytic', string ="Analytic account mandatory")

class HrExpenseImport(models.TransientModel):
    _inherit = 'expense.bank.statement.line'
    exp_analytic = fields.Boolean(related='product_id.require_analytic', string ="Analytic account mandatory")
    
class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"
    
    acc_analytic = fields.Boolean(related='product_id.require_analytic', string ="Analytic account mandatory")

class AccountVoucherLine(models.Model):
    _inherit = 'account.voucher.line'
    
    acc_voc_analytic = fields.Boolean(related='product_id.require_analytic', string ="Analytic account mandatory")
    
class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'
    
    pur_analytic = fields.Boolean(related='product_id.require_analytic', string ="Analytic account mandatory")
