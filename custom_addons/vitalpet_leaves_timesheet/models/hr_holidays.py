# -*- coding: utf-8 -*-
import logging
from datetime import datetime

from odoo import api, fields, models
from odoo.exceptions import ValidationError, UserError
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)


class HrHolidays(models.Model):
    _inherit = "hr.holidays"
    date_from = fields.Date('Start Date', readonly=True, index=True, copy=False,
        states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]})
    date_to = fields.Date('End Date', readonly=True, copy=False,
        states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]})
    hours_readonly = fields.Boolean('Hours Readonly')
    leave_days = fields.Integer('Leave Days', readonly=True)
    company_id=fields.Many2one(related='employee_id.company_id',string="Company")
    
    
    @api.model
    def create(self, vals):
        if vals.get('type') == 'remove':
            holidays_status_obj = self.env['hr.holidays.status']
            date_format = "%Y-%m-%d"
            date_from =  vals.get('date_from')
            date_to = vals.get('date_to')
            diff_days = datetime.strptime(date_to, date_format) - datetime.strptime(date_from, date_format)
            if diff_days.days > 0:
                vals['number_of_hours_temp'] = (diff_days.days+1)  * 8
            vals['leave_days'] = diff_days.days+1
            if vals.get('number_of_hours_temp') and vals.get('holiday_status_id'):
#                 if vals.get('number_of_hours_temp') > 8  and diff_days.days == 0:
#                     raise ValidationError(_('Hours should not be more than 8 hours.'))
                holidays_status_br = holidays_status_obj.search([('id', '=', vals.get('holiday_status_id'))])
                if holidays_status_br:
                    if holidays_status_br.minimum_hours > vals.get('number_of_hours_temp'):
                        raise ValidationError(_(
                        'Please select the minimum hours'))
        return super(HrHolidays, self).create(vals)
            
    @api.multi
    def write(self, vals):
        if vals.get('type') == 'remove':
            holidays_status_obj = self.env['hr.holidays.status']
            date_format = "%Y-%m-%d"
            hours_temp = 0
            holidays_status_br = False
            if vals.get('holiday_status_id'):
                    holidays_status_br = holidays_status_obj.search([('id', '=', vals.get('holiday_status_id'))])
            else:
                holidays_status_br = self.holiday_status_id
            if vals.get('date_from'):
                date_from =  vals.get('date_from')
            else:
                date_from = self.date_from
                
            if vals.get('date_to'):
                date_to =  vals.get('date_to')
            else:
                date_to = self.date_to
            diff_days = datetime.strptime(date_to, date_format) - datetime.strptime(date_from, date_format)
            if diff_days.days > 0:
                vals['number_of_hours_temp'] = (diff_days.days+1)  * 8
            
            vals['leave_days'] = diff_days.days+1
            if vals.get('number_of_hours_temp'):
                hours_temp = vals.get('number_of_hours_temp') 
            else:
                hours_temp = self.number_of_hours_temp
#             if hours_temp > 8 and diff_days.days == 0:
#                 raise ValidationError(_('Hours should not be more than 8 hours.'))
            if holidays_status_br:
                if holidays_status_br.minimum_hours > hours_temp:
                    raise ValidationError(_(
                        'Please select the minimum hours'))
        return super(HrHolidays, self).write(vals)

    @api.onchange('number_of_hours_temp', 'holiday_status_id')
    def _check_hours(self):
        if self.number_of_hours_temp != 0.00 and self.holiday_status_id and self.holiday_status_id.minimum_hours > self.number_of_hours_temp:
            raise ValidationError(_(
                    'Please select the minimum hours.'))


    number_of_hours_temp = fields.Float(
        string='Allocation in Hours',
        digits=(2, 2))
    
    @api.onchange('number_of_days_temp')
    def _number_of_hours_temp(self):
        if self.number_of_days_temp:
            self.number_of_hours_temp=self.number_of_days_temp*8
            
    @api.onchange('number_of_hours_temp')
    def _number_of_days_temp(self):
        if self.number_of_hours_temp:
            if self.number_of_hours_temp>0:
                self.number_of_days_temp=self.number_of_hours_temp/8
                
    @api.multi
    def name_get(self):
        res = []
        for leave in self:
            res.append((leave.id, _("%s on %s : %.2f hour(s)") % (
                leave.employee_id.name,
                leave.holiday_status_id.name,
                leave.number_of_hours_temp
            )))
        return res


    @api.multi
    def action_approve(self):
        # if double_validation: this method is the first approval approval
        # if not double_validation: this method calls action_validate() below
        if not self.env.user.has_group('hr_holidays.group_hr_holidays_user'):
            raise UserError(_('Only an HR Officer or Manager can approve leave requests.'))

        manager = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        for holiday in self:
            if holiday.employee_id.parent_id:
                manager_id = holiday.employee_id.parent_id
                if manager_id.user_id.id != self.env.uid:
                    raise UserError(_('Leave request must be approve by your manager.'))
            if holiday.state != 'confirm':
                raise UserError(_('Leave request must be confirmed ("To Approve") in order to approve it.'))

            if holiday.double_validation:
                return holiday.write({'state': 'validate1', 'manager_id': manager.id if manager else False})
            else:
                holiday.action_validate()
                
    @api.onchange('date_from','date_to')
    def _get_hours(self):
        date_format = "%Y-%m-%d"
        if self.date_from and self.date_to:
            diff_days = datetime.strptime(self.date_to, date_format) - datetime.strptime(self.date_from, date_format)
            self.number_of_hours_temp = (diff_days.days+1)  * 8
            self.leave_days = diff_days.days+1
#             self.number_of_days_temp = diff_days.days+1
#             res = {'readonly': {
#             'number_of_hours_temp': False,
#             }}
            if diff_days.days > 0:
                self.hours_readonly = True
            else:
                self.hours_readonly = False
#         if self.type == 'add':
#             self.number_of_days_temp = 10
#              
#         return res
class HolidaysType(models.Model):
    _inherit = "hr.holidays.status"
    
    @api.multi
    def name_get(self):
        if not self._context.get('employee_id'):
            # leave counts is based on employee_id, would be inaccurate if not based on correct employee
            return super(HolidaysType, self).name_get()      
        res = []
        for record in self:
            name = record.name
            if not record.limit:
                name = "%(name)s (%(count)s)" % {
                    'name': name,
                    'count': _('%g days remaining out of %g and %g hours remaining out of %g') % (record.virtual_remaining_leaves or 0.0 , record.max_leaves or 0.0, record.virtual_remaining_leaves*8 or 0.0, record.max_leaves*8 or 0.0)
                }
            res.append((record.id, name))
        return res
    

