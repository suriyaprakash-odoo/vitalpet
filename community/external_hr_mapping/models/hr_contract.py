# -*- coding: utf-8 -*-
import logging
import datetime

from odoo import models, fields, api, exceptions, _, SUPERUSER_ID

_logger = logging.getLogger(__name__)

class HrContract(models.Model):
    _inherit = "hr.contract"
    _description = "Contract"

    
    external_employee_id = fields.Char('External Employee ID')
    external_job_id = fields.Char('External Job ID')
    external_location_id = fields.Char('External Work Location ID')
    x_pay_hourly = fields.Float('Hourly Rate')
    
    
    @api.model
    def create(self, vals):
        _logger.error('Create Contract Vals: %s', vals)
        if 'external_job_id' in vals and 'external_location_id' in vals: 
            _logger.error('Create Contract job: %s: %s', vals['external_job_id'], vals['external_location_id'])
            external = self.env['external.hr.mapping'].sudo().search([('external_job_id', '=', vals['external_job_id']),
                                                                      ('external_location_id', '=', vals['external_location_id'])],
                                                                     limit=1)
            vals['job_id'] = external.job_id.id
            hourly_rate_class_id = None
            if vals['salary_computation_method'] == 'hourly' and 'x_pay_hourly' in vals:
                x_pay_hourly = float(vals.get('x_pay_hourly', 0.0))
                hourly_rate = self.env['hr.hourly.rate'].sudo().search([('rate', '=', x_pay_hourly)], limit=1)
                if not hourly_rate:
                    cl_vals = {'name': "{:.2f}".format(x_pay_hourly) ,
                               'line_ids': [(0,0, {'rate': x_pay_hourly, 
                                                   'date_start': datetime.datetime.today().strftime('%Y-%m-%d')})]
                               }
                    hourly_rate_class = self.env['hr.hourly.rate.class'].sudo().create(cl_vals)
                else:
                    hourly_rate_class = hourly_rate.class_id
                    
                vals['contract_job_ids'] = [(0, 0, {'job_id': external.job_id.id, 
                                                'seniority_id': external.seniority_id.id,
                                                'hourly_rate_class_id': hourly_rate_class.id,
                                                'is_main_job': True})]
        if 'external_employee_id' in vals:
            empl = self.env['hr.employee'].sudo().search([('employee_id', '=', vals['external_employee_id'])], limit=1)
            vals['employee_id'] = empl and empl.id or None
        return super(HrContract, self).create(vals)
    
    @api.multi
    def write(self, vals):
        _logger.error('Write Contract Vals: %s', vals)
        if 'external_job_id' in vals and 'external_location_id' in vals:
            _logger.error('Write Contract job: %s: %s', vals['external_job_id'], vals['external_location_id'])
            external = self.env['external.hr.mapping'].sudo().search([('external_job_id', '=', vals['external_job_id']),
                                                                      ('external_location_id', '=', vals['external_location_id'])],
                                                                     limit=1)
            vals['job_id'] = external.job_id.id
            hourly_rate_class_id = None
            if vals['salary_computation_method'] == 'hourly' and 'x_pay_hourly' in vals:
                x_pay_hourly = float(vals.get('x_pay_hourly', 0.0))
                hourly_rate = self.env['hr.hourly.rate'].sudo().search([('rate', '=', x_pay_hourly)], limit=1)
                if not hourly_rate:
                    cl_vals = {'name': "{:.2f}".format(x_pay_hourly) ,
                               'line_ids': [(0,0, {'rate': x_pay_hourly, 
                                                   'date_start': datetime.datetime.today().strftime('%Y-%m-%d')})]
                               }
                    hourly_rate_class = self.env['hr.hourly.rate.class'].sudo().create(cl_vals)
                else:
                    hourly_rate_class = hourly_rate.class_id
                if self.contract_job_ids:    
                    vals['contract_job_ids'] = [(1, self.contract_job_ids[0].id, {'job_id': external.job_id.id, 
                                                'seniority_id': external.seniority_id.id,
                                                'hourly_rate_class_id': hourly_rate_class.id,
                                                'is_main_job': True})]
                else:
                    vals['contract_job_ids'] = [(0, 0, {'job_id': external.job_id.id, 
                                                'seniority_id': external.seniority_id.id,
                                                'hourly_rate_class_id': hourly_rate_class.id,
                                                'is_main_job': True})]
            
        return super(HrContract, self).write(vals)