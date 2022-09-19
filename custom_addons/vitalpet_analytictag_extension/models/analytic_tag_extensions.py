from odoo import api, fields, models, tools, _
import odoo.addons.decimal_precision as dp


class AccountAnalyticTags(models.Model):
    _inherit = 'account.analytic.tag'

    code = fields.Char(string="Code")
    rate = fields.Float(string="Rate",digits=dp.get_precision('Analytic Tag Extension'))
    subtract_amount = fields.Boolean(string="Subtract Amount")
    payout = fields.Integer(string="Payout")
    salary_rule_id = fields.Many2one('hr.salary.rule',string="Salary Rule")
    double_validation = fields.Boolean(string="Apply Double Validation")