# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp


class Company(models.Model):
    _inherit = 'res.company'

    accounting = fields.Boolean("Accounting Enabled", default=False)

class MypracticeConfigSettings(models.TransientModel):
    _inherit = "mypractice.config.settings"

    accounting = fields.Boolean("Enabled",related='company_id.accounting', default=False, store=True)

class HrExpenseConfigSettings(models.TransientModel):
    _inherit = 'hr.expense.config.settings'

#     company_id=fields.Many2one('res.company', 'Company',
#                     default = lambda self : self.env.user.company_id)

    credit_limit_check = fields.Float( string='Expense Limit', digits=dp.get_precision('Account'))

    @api.model
    def get_default_credit_limit_check(self, fields):
        res= {
            'credit_limit_check': self.env['ir.values'].get_default('hr.expense', 'credit_limit_check'),
            }
        return res
    
    
    @api.multi
    def set_default_credit_limit_check(self):
        ir_values_obj = self.env['ir.values']
         
        if self.credit_limit_check:
            ir_values_obj.sudo().set_default('hr.expense', "credit_limit_check", self.credit_limit_check, for_all_users=True)
#             ir_values_obj.sudo().set_default('hr.expense.config.settings', "credit_limit_check", self.credit_limit_check, for_all_users=True)
         