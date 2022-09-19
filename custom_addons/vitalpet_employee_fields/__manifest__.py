# -*- coding: utf-8 -*-
{
    'name' : 'Vitalpet Employee Additional Fields',
    'version' : '1.1',
    'category' : 'Employee',
    'author' : 'VitalPet',
    'website': 'http://www.vitalpet.com',
    'depends': ['hr','base','hr_contract','hr_attendance','vitalpet_custom_hr_recruitment'],
    'data': [
        'security/ir.model.access.csv',
        'security/employee_security.xml',
        'wizard/terminate_team_member_view.xml',
        'wizard/demographics_wizard_views.xml',
        'views/hr_views.xml',
        'views/demographics_views.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
