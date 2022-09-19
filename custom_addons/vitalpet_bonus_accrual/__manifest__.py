# -*- coding: utf-8 -*-
{
    'name' : 'Bonus Accrual',
    'version' : '1.1',
    'category' : 'My Practice',
    'author' : 'VitalPet',
    'website': 'http://www.vitalpet.com',
    'depends': [ 'hr','hr_contract','account','payroll_contract_jobs','payroll_base','vitalpet_payroll_inputs','payroll_employee_benefit','payroll_period'],
    'data': [
            'security/ir.model.access.csv',
            'security/bonus_accrual_security.xml',
            'views/bonus_accrual_view.xml',
            'views/hr_employee_view.xml',
            'views/hr_payslip_view.xml',
            'views/mail_template.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
