# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, tools, _

class HrPayrollInputs(models.Model):
    _name = 'hr.payroll.inputs'
    _description='Hr payroll Inputs'
    _rec_name='payroll_period'
    
    payroll_period = fields.Many2one('hr.period', 'Payroll Period')
    company_id = fields.Many2one('res.company',string="Company")
    stage = fields.Selection([('contracts','Contracts'),('leaves','Leaves'),('timesheet','Timesheet'),('production','Production'),('validate','Validate'),('finalized','Finalized')], string = 'Stage')
    task_id = fields.Many2one('project.task',"Task")
    state = fields.Selection(
            [
                ('open', 'Open'),
                ('done', 'Closed')
            ],
            'Status',
            default='open'
        )
    date=fields.Date("Date")

    @api.multi
    def write(self, vals):
        if vals.get('state') == 'done':
            stage_id = self.env['project.task.type'].search([('name', '=', 'Done')])
            for line in self:
                line.task_id.stage_id = stage_id.id
                 
        return super(HrPayrollInputs, self).write(vals)