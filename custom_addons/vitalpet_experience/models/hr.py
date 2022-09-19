# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models,_
from odoo.exceptions import ValidationError, UserError

class Employee(models.Model):
    _inherit = "hr.employee"
    
    academic_experience_ids = fields.One2many('hr.experience.academics', 'academic_experience_id', string="Academic Experience",required=True)
    professional_experience_ids = fields.One2many('hr.experience.professional', 'professional_experience_id', string="Professional Experience")
    certification_ids = fields.One2many('hr.experience.certification', 'certification_id', string="Certifications")
    job_country_id = fields.Many2one("res.country",string="Applied Job Country")

    @api.onchange('job_id')
    def onchange_job_country_id(self):
        self.job_country_id = self.job_id.company_id.country_id

    @api.model
    def create(self, vals):

        if not vals.get('academic_experience_ids'):
            raise ValidationError("Please enter academic experience")

        return super(Employee, self).create(vals)

    
class AcademicExperiences(models.Model):
    _name = "hr.experience.academics"
    _rec_name = "employee"
    
    employee = fields.Many2one('hr.employee',string="Employee",required="True")
    academics = fields.Char("Academics")
    institute = fields.Char("Institution")
    diploma = fields.Char("Diploma")
    field_of_study = fields.Char("Field of Study")
    start_date = fields.Date("Start Date")
    end_date = fields.Date("End Date")
    academic_experience_id = fields.Many2one('hr.employee', string="Academic Experience Ref")


class ProfessionalExperiences(models.Model):
    _name = "hr.experience.professional"
    _rec_name = "employee"
    
    employee = fields.Many2one('hr.employee',string="Employee",required="True")
    position = fields.Char("Position")
    employer = fields.Char("Employer")
    start_date = fields.Date("Start Date")
    end_date = fields.Date("End Date")
    professional_experience_id = fields.Many2one('hr.employee', string="Professional Experience Ref")


class CertificationDetail(models.Model):
    _name = "hr.experience.certification"
    _rec_name = "employee"
    
    employee = fields.Many2one('hr.employee',string="Employee",required="True")
    certifications = fields.Char("Certifications")
    certification_number = fields.Char("Certification #")
    issued_by = fields.Char("Issued By")
    professional_license = fields.Boolean("Professional License")
    country_id = fields.Many2one('res.country',"Applied Job Country")
    state_issued_id = fields.Many2one('res.country.state',"State Issued")
    start_date = fields.Date("Start Date")
    end_date = fields.Date("End Date")
    certification_id = fields.Many2one('hr.employee', string="Certification Ref")
    
    
