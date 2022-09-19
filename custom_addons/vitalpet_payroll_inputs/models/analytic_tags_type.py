# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, tools, _


class HrPeriod(models.Model):
    """HR Payroll Period"""

    _inherit = 'hr.period'


    state = fields.Selection(
            [
                ('draft', 'Draft'),
                ('inputs', 'Inputs'),
                ('payslip', 'Payslips'),
                ('export', 'Export'),
                ('import', 'Import'),
                ('allocate', 'Allocate'),
                ('open', 'Open'),
                ('done', 'Closed')
            ],
            'Status',
            readonly=True,
            required=True,
            default='draft'
        )   





class PayrollDashboard(models.Model):
    _name = 'payroll.dashboard'

    name = fields.Char('name')