# -*- coding: utf-8 -*-
# © 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Vitalpet Employee Documents",
    "summary": "Vitalpet Employee Documents",
    "version": "10.0.1.0.0",
    "category": "employee",
    "website": "https://vetzip.vitalpet.net/",
    "author": "VitalPet",
    "depends": ['base','vitalpet_onboarding','hr','mail','employee_documents_expiry'],
    "data": [   
         'security/security.xml',
         'data/employees_expiry_date_cron.xml',
         'data/mail_template_document_expiration.xml',   
         'views/custom_employee.xml', 
         'security/ir.model.access.csv',

    ],
    'installable' : True,
    'auto_install' : False,
    'application' : True,
}
