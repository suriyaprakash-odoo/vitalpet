# -*- coding: utf-8 -*-
from odoo.osv import expression
from odoo import api, fields, models, _


class ExternalHRMapping(models.Model):
    _name = 'external.hr.mapping'
    
    
    job_id = fields.Many2one('hr.job', 'Job')
    company_id = fields.Many2one('res.company', 'Company')
    external_job_id = fields.Char('External Job ID')
    external_location_id = fields.Char('External Work Location ID')
    external_job_description = fields.Char('External Job Description')
    external_location_description = fields.Char('External Location Description')
    working_address_id = fields.Integer('Working Address')
    seniority_id = fields.Many2one('hr.job.seniority.title', 'Job Seniority Title')
    
