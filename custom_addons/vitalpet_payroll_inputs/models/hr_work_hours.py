# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, tools, _
import datetime
from odoo.exceptions import ValidationError, UserError

class HrWorkHours(models.Model):
    _name = 'hr.work.hours'
    
    _rec_name = 'employee_id'
    employee_id = fields.Many2one('hr.employee', 'Employee', required=True)
    job_id = fields.Many2one('hr.job', 'Job Position', required=True)
    date = fields.Date('Date', required=True)
    work_hours = fields.Float('Work Hours', required=True)
    period_id = fields.Many2one('hr.period',string='Period')
    account_id = fields.Many2one('account.account', string='Account')
    amount = fields.Monetary(currency_field='company_currency_id')
    unit_amount = fields.Float('Quantity', default=0.0)
    user_id = fields.Many2one('res.users', string='User')
    partner_id = fields.Many2one('res.partner', string='Partner')
    name = fields.Char('Description', required=False)
    code = fields.Char(size=8)
    currency_id = fields.Many2one('res.currency', string='Account Currency', store=True, help="The related account currency if not equal to the company one.", readonly=True)
    ref = fields.Char(string='Ref.')
    general_account_id = fields.Many2one('account.account', string='Financial Account', ondelete='restrict', readonly=True, store=True)
    move_id = fields.Many2one('account.move.line', string='Move Line', ondelete='cascade', index=True)
    product_id = fields.Many2one('product.product', string='Product')
    product_uom_id = fields.Many2one('product.uom', string='Unit of Measure')
    amount_currency = fields.Monetary( store=True, help="The amount expressed in the related account currency if not equal to the company one.", readonly=True)
#     so_line = fields.Many2one('sale.order.line', string='Sale Order Line')
    project_id = fields.Many2one('project.project', 'Project')
    department_id = fields.Many2one('hr.department', "Department",store=True, readonly=True)
    task_id = fields.Many2one('project.task', 'Task')
    validated = fields.Boolean("Validated line",  store=True)
    sheet_id = fields.Many2one('hr_timesheet_sheet.sheet',string='Sheet', store=True)
    worked_days_id = fields.Many2one(
        'hr.payslip.worked_days',
        'Payslip Worked Days',
    )
    company_id = fields.Many2one('res.company', string="Company")
    status = fields.Selection([('validate', 'Validated'), ('non_validate', 'Non Validated')], string='Status')

    company_currency_id = fields.Many2one('res.currency', readonly=True,
        help='Utility field to express amount currency')
        
        