# -*- coding: utf-8 -*-
# © 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "VitalPet Custom HR Recruitment",
    "summary": "Custom Recruitment",
    "version": "10.0.4",
    "category": "Account",
    "website": "https://vetzip.vitalpet.net/",
    "author": "VitalPet",
    "depends": ['base','account','survey','hr_recruitment','hr_appraisal','website_hr_recruitment','hr_recruitment_survey','website_form','mail','payroll_employee_benefit', 'payroll_activity','vitalpet_production_model','utm' ],
    "data": [
            'security/hr_recruitment_security.xml',
            'security/ir.model.access.csv',
            'report/hr_applicant.xml',
            'report/hr_applicant_template.xml',
            'data/mail_template_data.xml',
            'views/partner_employee.xml',
            'views/survey.xml',
            'views/recruitment.xml',
            'views/recruitment_menus.xml',
            'views/recruitment_template.xml'
    ],
    'installable' : True,
    'auto_install' : False,
    'application' : True,
}
