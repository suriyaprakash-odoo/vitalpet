# -*- coding: utf-8 -*-


from odoo import models, fields, api, exceptions, _, SUPERUSER_ID


class HrHolidays(models.Model):
    _inherit = "hr.holidays"

    
    external_employee_id = fields.Char('External Employee ID')
    
    @api.model
    def create(self, vals):
        if 'external_employee_id' in vals:
            empl = self.env['hr.employee'].sudo().search([('employee_id', '=', vals['external_employee_id'])], limit=1)
            vals['employee_id'] = empl and empl.id or None
            
        return super(HrHolidays, self).create(vals)
    
