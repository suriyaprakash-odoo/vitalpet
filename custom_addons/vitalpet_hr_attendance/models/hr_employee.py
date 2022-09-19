# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from random import choice
from string import digits
import datetime
from odoo import models, fields, api, exceptions, _, SUPERUSER_ID


class HrEmployee(models.Model):
    _inherit = "hr.employee"
    _description = "Employee"

	
    allowed_companies = fields.Many2many("res.company", string="Allowed Companies")
	
    # Check In
    @api.multi
    def attendance_manual_new(self, next_action, entered_pin=None):
        self.ensure_one()
        if not (entered_pin is None) or self.env['res.users'].browse(SUPERUSER_ID).has_group(
                'hr_attendance.group_hr_attendance_use_pin') and (
                self.user_id and self.user_id.id != self._uid or not self.user_id):
            if entered_pin != self.pin:
                return {'warning': _('Wrong PIN')}
        
        today = datetime.datetime.now().date()
        contracts = self.env['hr.contract'].search([('employee_id', '=', self.id)])
        job = ""
        for empid in contracts:
            if not empid.contract_renewal_overdue:
                job_id = self.env['hr.contract.job'].sudo().search([('contract_id', '=', empid.id)])
                for rec in job_id:
                    if rec.job_id.company_id == self.env.user.company_id:
                        if job == "":
                            job = "<button style=width:300px; class='btn-primary btn-lg job_btn' next_action='" + (
                            next_action) + "' emp_id='" + str(self.id) + "' attr_id='" + str(
                                rec.job_id.id) + "'>" + rec.job_id.name + "</button><br/>"
                        else:
                            job = job + "<br /><button style=width:300px; class='btn-primary btn-lg job_btn' next_action='" + (
                            next_action) + "' emp_id='" + str(self.id) + "' attr_id='" + str(
                                rec.job_id.id) + "'>" + rec.job_id.name + "</button><br/>"

        if self.attendance_state != 'checked_in':
            return {'action': 'test', 'job': job}
        else:
            return self.attendance_action_new(next_action, job)

    @api.multi
    def attendance_action_new(self, next_action, job):

        """ Changes the attendance of the employee.
            Returns an action to the check in/out message,
            next_action defines which menu the check in/out message should return to. ("My Attendances" or "Kiosk Mode")
        """
        self.ensure_one()
        action_message = self.env.ref('hr_attendance.hr_attendance_action_greeting_message').read()[0]
        action_message['previous_attendance_change_date'] = self.last_attendance_id and (
        self.last_attendance_id.check_out or self.last_attendance_id.check_in) or False
        if action_message['previous_attendance_change_date']:
            action_message['previous_attendance_change_date'] = \
                fields.Datetime.to_string(fields.Datetime.context_timestamp(self, fields.Datetime.from_string(
                    action_message['previous_attendance_change_date'])))
        action_message['employee_name'] = self.name
        action_message['next_action'] = next_action

        modified_attendance = self.sudo(self.env.user).attendance_action_change()

        action_message['attendance'] = modified_attendance.read()[0]

        return {'action': action_message, 'job': job}

    @api.multi
    def attendance_action_change(self):
        """ Check In/Check Out action
            Check In: create a new attendance record
            Check Out: modify check_out field of appropriate attendance record
        """
        if len(self) > 1:
            raise exceptions.UserError(_('Cannot perform check in or check out on multiple employees.'))
        action_date = fields.Datetime.now()


        if self.attendance_state != 'checked_in':
            vals = {
                #                 'activity':job_id,
                'employee_id': self.id,
                'check_in': action_date,
            }
            return self.env['hr.attendance'].create(vals)
        else:
            attendance = self.env['hr.attendance'].sudo().search(
                [('employee_id', '=', self.id), ('check_out', '=', False)], limit=1)
            if attendance:
                #                 job_det= self.env['hr.job'].search([('id', '=', attendance.activity_id)])
                attendance.check_out = action_date
                attendance.company_out = self.env.user.company_id.id
            else:
                raise exceptions.UserError(
                    _('Cannot perform check out on %(empl_name)s, could not find corresponding check in. '
                      'Your attendances have probably been modified manually by human resources.') % {
                        'empl_name': self.name, })
            return attendance

    @api.multi
    def attendance_manual_antr(self, next_action, job_id, emp_id):

        self = self.env['hr.employee'].search([('id', '=', emp_id)])
        self.ensure_one()
        job = ""
        return self.attendance_action_antr(next_action, job, job_id)

    @api.multi
    def attendance_action_antr(self, next_action, job, job_id):
        """ Changes the attendance of the employee.
            Returns an action to the check in/out message,
            next_action defines which menu the check in/out message should return to. ("My Attendances" or "Kiosk Mode")
        """
        self.ensure_one()
        action_message = self.env.ref('hr_attendance.hr_attendance_action_greeting_message').read()[0]
        action_message['previous_attendance_change_date'] = self.last_attendance_id and (
        self.last_attendance_id.check_out or self.last_attendance_id.check_in) or False
        if action_message['previous_attendance_change_date']:
            action_message['previous_attendance_change_date'] = \
                fields.Datetime.to_string(fields.Datetime.context_timestamp(self, fields.Datetime.from_string(
                    action_message['previous_attendance_change_date'])))
        action_message['employee_name'] = self.name
        action_message['next_action'] = next_action
        if self.user_id:
            modified_attendance = self.sudo(self.user_id.id).attendance_action_change_new(job_id)
        else:
            modified_attendance = self.sudo().attendance_action_change_new(job_id)
        action_message['attendance'] = modified_attendance.read()[0]
        return {'action': action_message, 'job': job}

    @api.multi
    def attendance_action_change_new(self, job_id):

        """ Check In/Check Out action
            Check In: create a new attendance record
            Check Out: modify check_out field of appropriate attendance record
        """
        job_det = self.env['hr.job'].sudo().browse(int(job_id))
        job_activity = self.env['hr.activity'].sudo().search([('job_id', '=', job_det.id)])
        if len(self) > 1:
            raise exceptions.UserError(_('Cannot perform check in or check out on multiple employees.'))
        action_date = fields.Datetime.now()

        if self.attendance_state != 'checked_in':
            vals = {
                'activity_id': job_activity.id,
                'company_in': job_det.company_id.id,
                'employee_id': self.id,
                'check_in': action_date,
            }
            return self.env['hr.attendance'].create(vals)
        else:
            attendance = self.env['hr.attendance'].search([('employee_id', '=', self.id), ('check_out', '=', False)],
                                                          limit=1)
            if attendance:
                attendance.check_out = action_date
            else:
                raise exceptions.UserError(
                    _('Cannot perform check out on %(empl_name)s, could not find corresponding check in. '
                      'Your attendances have probably been modified manually by human resources.') % {
                        'empl_name': self.name, })
            return attendance
        
    @api.model
    def get_current_contract_employees(self):
        
        result = {}
        hr_employee = self.env['hr.employee'].search([])
        view_id = self.env.ref("hr_attendance.hr_employees_view_kanban")
        result['view_id'] = view_id.id
        employee_list = []
        for employee in hr_employee:
            hr_contract = self.env['hr.contract'].search([('employee_id', '=', employee.id)])
            if hr_contract:
                for cont in hr_contract:
                    if cont.contract_job_ids and not cont.contract_renewal_overdue:
                        
#                         for job in cont.contract_job_ids:
#                             print cont.contract_job_ids, 'oooooo'
#                             if job.job_id.company_id.id:
#                                 print self.env.user.company_id.id, 'uuu', job.job_id.company_id.id
#                                 if (self.env.user.company_id.id == job.job_id.company_id.id):
#                                     print self.env.user.company_id.id, job.job_id.company_id.id, 'iiiiii'
                        
                        jb_list = cont.contract_job_ids.sudo().filtered(lambda s: s.job_id.company_id.id == self.env.user.company_id.id)
                        if jb_list:
                            employee_list.append(employee.id)
        result['employee_list'] = employee_list
        return result



class HrHolidays(models.Model):
    _inherit = "hr.holidays"
    _description = "Holidays"

    leave_days = fields.Integer('Leave Days', readonly=True)

    @api.model
    def get_holidays_list(self, emp_id):
        result = {}
        hr_holidays = self.env['hr.holidays'].search([('employee_id', '=', emp_id[0])])
        view_id = self.env.ref("vitalpet_hr_attendance.view_holiday_allocation_tree_kiosk")
        result['view_id'] = view_id.id
        employee_list = []
        for employee in hr_holidays:
            employee_list.append(employee.id)
        result['employee_list'] = employee_list
        return result
    
    
    @api.model
    def get_employee_list(self, emp_id):
        result = {}
        view_id = self.env.ref("vitalpet_hr_attendance.view_holiday_kiosk_new_calendar")
        form_view_id = self.env.ref("vitalpet_hr_attendance.kiosk_holiday_new")
        result['view_id'] = view_id.id
        result['form_view_id'] = form_view_id.id
        employee_list = []
        result['employee_id'] = emp_id[0]
        return result
    
    
    def action_exit(self):
        return {
            'type': 'ir.actions.client',
            'name':'Attendances',
            'tag':'hr_attendance_kiosk_mode',
        }
        

        
    
    