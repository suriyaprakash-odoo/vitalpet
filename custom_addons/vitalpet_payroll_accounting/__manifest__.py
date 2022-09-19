# -*- coding: utf-8 -*-
{
    'name': 'VitalPet Payroll Accounting',
    'version': '1.1.0.2',
    'category': 'Payroll',
    'author': 'VitalPet',
    'website': 'http://www.vitalpet.com',
    'depends': ['account', 'hr_recruitment', 'payroll_base', 'payroll_period', 'vitalpet_mypractice', 'vitalpet_custom_hr_recruitment', 'vitalpet_daily_summary', 'vitalpet_payroll_inputs'],
    'data': [
        'security/ir.model.access.csv',
        'views/compensation_tag_view.xml',
        'views/payroll_accounting_view.xml',
    ],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
