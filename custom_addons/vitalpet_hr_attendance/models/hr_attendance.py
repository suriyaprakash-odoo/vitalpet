from odoo import api, fields, models, _
from datetime import timedelta, datetime


class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    name = fields.Char('Name')
    activity_id = fields.Many2one('hr.activity', string='Activity')
    company_in = fields.Many2one('res.company', 'Company In')
    company_out = fields.Many2one('res.company', 'Company Out')
    time_difference = fields.Char(compute='_time_compute', string='Attendance Hours')
#     work_hours=fields.Char('Wrok Hours')


    @api.multi
    @api.depends('check_in','check_out')
    def _time_compute(self):
        for loop in self:
            if loop.check_in and loop.check_out:
                check_in_time = datetime.strptime(loop.check_in,'%Y-%m-%d %H:%M:%S')
                check_out_time = datetime.strptime(loop.check_out,'%Y-%m-%d %H:%M:%S')
                diff = check_out_time - check_in_time
                s = str(diff)
                print len(s)
                if len(s)==7:
                    diff_value = s[:4]
                    loop.time_difference = "0"+diff_value
                else:
                    diff_value = s[:5]
                    loop.time_difference = diff_value
            else:
                loop.time_difference = "00:00"


    def automatic_record_create(self):
        current_date = datetime.today().date()
        intime = '00:00:01'
        checkin_time = str(current_date) + " " + intime
        attendance = self.env['hr.attendance'].search([('check_out', '=', False)])
        for rec in attendance:
            time = '23:59:00'
            emp = self.env['hr.employee'].search([('id', '=', rec.employee_id.id)])
            company = self.env['res.company'].search([('id', '=', rec.company_in.id)])
            previous_date = datetime.today().date() - timedelta(days=1)
            checkout_time = str(previous_date) + " " + time
            rec.check_out = checkout_time
            rec.company_out = company.id
            attendance = self.env['hr.attendance'].create(
                {'check_in': checkin_time, 'employee_id': emp.id, 'activity_id': rec.activity_id.id,
                 'company_in': company.id})
