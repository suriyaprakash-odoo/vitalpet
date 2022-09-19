# -*- coding: utf-8 -*-
{
    'name': 'VitalPet GL Payroll Accounting',
    'version': '1.0',
    'category': 'Others',
    'description': """
    """,
    'author': 'Vitalpet',
    'website': 'http://www.vitalpet.com',
    'depends': ['base', 'account'],
    'data': [
        'security/ir.model.access.csv',        
        'wizard/income_expense_view.xml',
        'views/gi_payroll_view.xml',
    ],
    'demo': [],
    'application': True,
    'installable': True,
    'auto_install': False,
}
