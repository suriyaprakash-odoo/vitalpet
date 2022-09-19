# -*- coding: utf-8 -*-
{
    'name': 'Experience',
    'category': 'HR',
    'version': '1.0',
    'sequence': 5,
    'summary': 'HR,Employee',
    'description': """
    """,
    'depends': ['hr','vitalpet_custom_hr_recruitment','hr_recruitment'],
    'data': [
        'security/experience_security.xml',
        'security/ir.model.access.csv',
        'views/experience_views.xml',
        'views/recruitment_template.xml',
        'views/hr_recruitment_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
