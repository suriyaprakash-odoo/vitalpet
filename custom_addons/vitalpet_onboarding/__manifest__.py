# -*- coding: utf-8 -*-
# © 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "VitalPet Onboarding",
    "summary": "Onboarding",
    "version": "10.0.1.0.0",
    "category": "Human Resource",
    "website": "https://vetzip.vitalpet.net/",
    "author": "VitalPet",
    "depends": ['base',
                'hr_recruitment',
                'vitalpet_custom_hr_recruitment',
                'website_hr_recruitment',
                'calendar',
                'mail',
                'account',
                'website',
                'website_sign',
                'web_planner',
                'hr_contract',
                'vitalpet_document_enhancement',
                'vitalpet_experience',
                'vitalpet_payroll_inputs'],
    "data": [
            'security/onboarding_security.xml',
            'security/ir.model.access.csv',
            'data/onboarding_cron.xml',
            'data/mail_template_data.xml',
            'views/onboarding_config_views.xml',
            'views/onboarding_views.xml',
            'views/hr_applicant.xml',
            'views/hr_applicant_templates.xml',
            'vitalpet_onboarding.xml',
            'data/web_planner_data.xml'
            
            
    ],
    'qweb': ['static/xml/onboard_dashboard_view.xml'],
    'installable' : True,
    'auto_install' : False,
    'application' : True,
}
