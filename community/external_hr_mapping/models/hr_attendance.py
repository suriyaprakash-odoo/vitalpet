# -*- coding: utf-8 -*-


from odoo import models, fields, api, exceptions, _, SUPERUSER_ID


class HrAttendance(models.Model):
    _inherit = "hr.attendance"
    _description = "Attendance"

    
    external_employee_id = fields.Char('External Employee ID')
    external_job_id = fields.Char('External Job ID')
    external_location_id = fields.Char('External Work Location ID')
    external_job_description = fields.Char('External Job Description')
    external_location_description = fields.Char('External Location Description')
    regular_hours = fields.Float('Regular Hours')
    ot_hours = fields.Float('OT Hours')
    
    
    @api.model
    def create(self, vals):
        if 'external_job_description' in vals and 'external_location_description' in vals:
            external = self.env['external.hr.mapping'].sudo().search([('external_job_description', '=', vals['external_job_description']),
                                                                      ('external_location_description', '=', vals['external_location_description'])],
                                                                     limit=1)
            if external:
                activity = self.env['hr.activity'].sudo().search([('job_id', '=', external.job_id.id)], limit=1)
                vals['company_in'] = external.company_id.id
                vals['company_out'] = external.company_id.id
                vals['activity_id'] = activity and activity.id or False
        if 'external_employee_id' in vals:
            empl = self.env['hr.employee'].sudo().search([('employee_id', '=', vals['external_employee_id'])], limit=1)
            vals['employee_id'] = empl and empl.id or None
        return super(HrAttendance, self).create(vals)

    
    @api.multi
    def write(self, vals):
        if 'external_job_description' in vals and 'external_location_description' in vals:
            external = self.env['external.hr.mapping'].sudo().search([('external_job_description', '=', vals['external_job_description']),
                                                                      ('external_location_description', '=', vals['external_location_description'])],
                                                                     limit=1)
            if external:
                activity = self.env['hr.activity'].sudo().search([('job_id', '=', external.job_id.id)], limit=1)
                vals['company_in'] = external.company_id.id
                vals['company_out'] = external.company_id.id
                vals['activity_id'] = activity and activity.id or False
        return super(HrAttendance, self).write(vals)
