# -*- coding: utf-8 -*-


from odoo import models, fields, api, exceptions, _, SUPERUSER_ID


class HrWorkHours(models.Model):
    _inherit = "hr.work.hours"
    _description = "Work Hours"

    
    external_employee_id = fields.Char('External Employee ID')
    external_location_description = fields.Char('External Location Description')
    external_job_description = fields.Char('External Job Description')
    
    
#     @api.model
#     def create(self, vals):
#         if 'external_job_description' in vals and 'external_location_description' in vals:
#             external = self.env['external.hr.mapping'].sudo().search([('external_job_description', '=', vals['external_job_description']),
#                                                                       ('external_location_description', '=', vals['external_location_description'])],
#                                                                      limit=1)
#             if external:
#                 vals['job_id'] = external.job_id.id
#                 vals['company_id'] = external.company_id.id
#         if 'external_employee_id' in vals:
#             empl = self.env['hr.employee'].sudo().search([('employee_id', '=', vals['external_employee_id'])], limit=1)
#             vals['employee_id'] = empl and empl.id or None
#         print vals
#         if 'date' in vals and 'period_id' not in vals:
#             period = self.env['hr.period'].sudo().search([('date_start', '<=', vals['date']), 
#                                                           ('date_stop', '>=', vals['date']),
#                                                           ('company_id', '=', vals['company_id'])], limit=1)
#             vals['period_id'] = period and period.id or None
#         if 'status' not in vals:
#             vals['status'] = 'validate'
#             
#         return super(HrWorkHours, self).create(vals)
#     
#     @api.multi
#     def write(self, vals):
#         if 'external_job_description' in vals and 'external_location_description' in vals:
#             external = self.env['external.hr.mapping'].sudo().search([('external_job_description', '=', vals['external_job_description']),
#                                                                       ('external_location_description', '=', vals['external_location_description'])],
#                                                                      limit=1)
#             if external:
#                 vals['job_id'] = external.job_id.id
#                 vals['company_id'] = external.company_id.id
#         return super(HrWorkHours, self).write(vals)
    