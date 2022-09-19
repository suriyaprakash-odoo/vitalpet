# -*- coding: utf-8 -*-
{
    'name' : 'Vitalpet Leave Module',
    'version' : '1.1',
    'category' : 'Leaves',
    'author' : 'VitalPet',
    'website': 'http://www.vitalpet.com',
    'depends': ['hr_holidays', 'payroll_activity'],
    'data': [
#         'security/ir.model.access.csv',
          'security/hr_holiday_security.xml',
          'views/hr_holidays_status_views.xml',
          'views/hr_holidays.xml',
          'views/payroll_activity.xml',
    ],
    'demo': [   
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
