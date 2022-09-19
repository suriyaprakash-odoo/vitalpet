# -*- coding: utf-8 -*-


from odoo import models, fields, api, exceptions, _, SUPERUSER_ID


class HrEmployee(models.Model):
    _inherit = "hr.employee"
    _description = "Employee"

    
    external_parent_id = fields.Char('External Manager ID')
    external_job_id = fields.Char('External Job ID')
    external_location_id = fields.Char('External Work Location ID')
    external_job_description = fields.Char('External Job Description')
    external_location_description = fields.Char('External Location Description')
    
    
    @api.model
    def create(self, vals):
        if 'external_job_id' in vals and 'external_location_id' in vals:
            external = self.env['external.hr.mapping'].sudo().search([('external_job_id', '=', vals['external_job_id']),
                                                                      ('external_location_id', '=', vals['external_location_id'])],
                                                                     limit=1)
            vals['company_id'] = external.company_id.id
            vals['work_phone'] = external.company_id.phone
            vals['address_id'] = external.working_address_id
            vals['job_id'] = external.job_id.id
        if 'external_parent_id' in vals:
            parent = self.env['hr.employee'].sudo().search([('employee_id', '=', vals['external_parent_id'])],
                                                                     limit=1)
            vals['parent_id'] = parent and parent.id or None
        return super(HrEmployee, self).create(vals)
    
    @api.multi
    def write(self, vals):
        if 'external_job_id' in vals and 'external_location_id' in vals:
            external = self.env['external.hr.mapping'].sudo().search([('external_job_id', '=', vals['external_job_id']),
                                                                      ('external_location_id', '=', vals['external_location_id'])],
                                                                     limit=1)
            vals['company_id'] = external.company_id.id
            vals['work_phone'] = external.company_id.phone
            vals['address_id'] = external.working_address_id
            vals['job_id'] = external.job_id.id
        if 'external_parent_id' in vals:
            parent = self.env['hr.employee'].sudo().search([('employee_id', '=', vals['external_parent_id'])],
                                                                     limit=1)
            vals['parent_id'] = parent and parent.id or None
        return super(HrEmployee, self).write(vals)
