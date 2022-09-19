
import logging
from odoo import api, fields, models, _

class Employee(models.Model):

    _inherit = 'hr.employee'
    
    schedule_count = fields.Integer( compute='_compute_timesheet_count',string="Timesheet")
    in_time = fields.Char(string="In Time", default="00:00")
    break_start = fields.Char(string="Break Start", default="00:00")
    break_end = fields.Char(string="Break End", default="00:00")
    

    def _compute_timesheet_count(self):
        for record in self:
            record.schedule_count=self.env['staff.planning.display.week'].search_count([('employee_id', '=', record.id)])
    
    @api.multi
    def click_schedule(self):         
        self.ensure_one()
        schedule_list =self.env['staff.planning.display.week'].search([('employee_id', '=', self.id)])

        if schedule_list:
            return {
                'name': ('Schedule'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'domain': [('employee_id', '=', schedule_list[0].employee_id.id)],
                'view_mode': 'tree',
                'res_model': 'staff.planning.display.week',
                'view_id': self.env.ref('vitalpet_team_scheduler.staff_planning_display_week_tree').id,
                'context': self.env.context,
                }
    
    