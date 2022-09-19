# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models,_
from odoo.exceptions import UserError, ValidationError


class Applicant(models.Model):
    _inherit = "hr.applicant"

    academic_experience_ids = fields.One2many('hr.applicant.academics', 'academic_experience_id', string="Academic Experience")
    professional_experience_ids = fields.One2many('hr.applicant.professional', 'professional_experience_id', string="Professional Experience")
    certification_ids = fields.One2many('hr.applicant.certification', 'certification_id', string="Certifications")
    academic_info_dict = fields.Text("Academic Info Ref")
    professional_info_dict = fields.Text("Professional Info Ref")
    certification_info_dict = fields.Text("Certification Info Ref")
    job_id_country_id = fields.Many2one('res.country',string="Applied Job Country")

    @api.onchange('job_id')
    def onchange_job_id_country_id(self):
        self.job_id_country_id = self.job_id.company_id.country_id
        

    @api.model
    def create(self,vals):
        res=super(Applicant, self).create(vals)
        if vals.get('academic_info_dict'):
            academics_list = []
            for record in eval(vals.get('academic_info_dict')):
                academics_list.append((0,0,{'academics':record[1] or None, 
                    'institute':record[2] or None, 
                    'diploma':record[3] or None, 
                    'field_of_study':record[4] or None, 
                    'start_date':record[5] or None, 
                    'end_date':record[6] or None}))
            for item in academics_list:
                self.env['hr.applicant.academics'].create({
                    'academics':item[2]['academics'],
                    'institute':item[2]['institute'],
                    'diploma':item[2]['diploma'],
                    'field_of_study':item[2]['field_of_study'],
                    'start_date':item[2]['start_date'],
                    'end_date':item[2]['end_date'],
                    'academic_experience_id':res.id,
                    'employee':res.id
                    })

        if vals.get('professional_info_dict'):
            professional_list = []
            for record in eval(vals.get('professional_info_dict')):
                professional_list.append((0,0,{'position':record[1] or None, 
                    'employer':record[2] or None, 
                    'start_date':record[3] or None, 
                    'end_date':record[4] or None}))
            for item in professional_list:
                self.env['hr.applicant.professional'].create({
                    'position':item[2]['position'],
                    'employer':item[2]['employer'],
                    'start_date':item[2]['start_date'],
                    'end_date':item[2]['end_date'],
                    'professional_experience_id':res.id,
                    'employee':res.id
                    })
                
        if vals.get('certification_info_dict'):
            certification_list = []
            for record in eval(vals.get('certification_info_dict')):
                certification_list.append((0,0,{'certifications':record[1] or None, 
                    'certification_number':record[2] or None, 
                    'issued_by':record[3] or None, 
                    'professional_license':True if int(record[4])==1 else False, 
                    'state_issued':record[5] or None, 
                    'start_date':record[6] or None, 
                    'end_date':record[7] or None}))
            for item in certification_list:
                self.env['hr.applicant.certification'].create({
                    'certifications':item[2]['certifications'],
                    'certification_number':item[2]['certification_number'],
                    'issued_by':item[2]['issued_by'],
                    'professional_license': item[2]['professional_license'],
                    'state_issued':item[2]['issued_by'],
                    'start_date':item[2]['start_date'],
                    'end_date':item[2]['end_date'],
                    'certification_id':res.id,
                    'employee':res.id
                    })

        return res
    
class AcademicExperiencesApplicant(models.Model):
    _name = "hr.applicant.academics"
    _rec_name = "employee"
    
    employee = fields.Many2one('hr.applicant',string="Employee",required="True")
    academics = fields.Char("Academics")
    institute = fields.Char("Institution")
    diploma = fields.Char("Diploma")
    field_of_study = fields.Char("Field of Study")
    start_date = fields.Date("Start Date")
    end_date = fields.Date("End Date")
    academic_experience_id = fields.Many2one('hr.applicant', string="Academic Experience Ref")


class ProfessionalExperiencesApplicant(models.Model):
    _name = "hr.applicant.professional"
    _rec_name = "employee"
    
    employee = fields.Many2one('hr.applicant',string="Employee",required="True")
    position = fields.Char("Position")
    employer = fields.Char("Employer")
    start_date = fields.Date("Start Date")
    end_date = fields.Date("End Date")
    professional_experience_id = fields.Many2one('hr.applicant', string="Professional Experience Ref")


class CertificationDetailApplicant(models.Model):
    _name = "hr.applicant.certification"
    _rec_name = "employee"
    
    employee = fields.Many2one('hr.applicant',string="Employee",required="True")
    certifications = fields.Char("Certifications")
    certification_number = fields.Char("Certification #")
    issued_by = fields.Char("Issued By")
    professional_license = fields.Boolean("Professional License")
    country_id = fields.Many2one('res.country',string="Applied Job Country")
    state_issued_id = fields.Many2one('res.country.state',"State Issued")
    start_date = fields.Date("Start Date")
    end_date = fields.Date("End Date")
    certification_id = fields.Many2one('hr.applicant', string="Certification Ref")
    