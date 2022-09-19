# -*- coding: utf-8 -*-
# © 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Vitalpet Client Experience",
    "summary": "Client Experience",
    "version": "10.0.1.0.0",
    "website": "https://vetzip.vitalpet.net/",
    "author": "VitalPet",
     'description': """
Manage The Experience of Clients
==================================
This Module Contains a visit review form that allows users to audit a client visit, fill out pre-selected form values, and upload an several attachments.
    """,
    "depends": ['base','hr','survey','vitalpet_mypractice'
                ],
    "data": [
            'security/security.xml',
            'security/ir.model.access.csv',
            'data/mail_template_visit_review.xml',
            'data/visit_review_mail_cron.xml',  
            'client_experience_dashboard.xml',
            'views/configuration_settings_view.xml',
            'views/client_experience_view.xml',
            'views/custom_employee_view.xml',
            'views/custom_survey_view.xml',
    ],
    'qweb': ['static/xml/vitalpet_experience.xml'],
    'installable' : True,
    'auto_install' : False,
    'application' : True,
}
