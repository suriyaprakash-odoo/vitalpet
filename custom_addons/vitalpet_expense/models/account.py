from odoo import api, fields, models, tools, _

  

class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'  
  
    expensed = fields.Boolean(string="Can be Expensed")  