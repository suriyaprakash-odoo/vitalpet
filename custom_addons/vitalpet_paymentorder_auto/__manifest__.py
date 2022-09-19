# -*- coding: utf-8 -*-
{
    'name' : 'Vendor Payments and Bank Reconciliation',
    'summary': 'Vendor Payments and Bank Reconciliation',
    'version' : '1.1',
    'category' : 'Banking addons',
    'author' : 'VitalPet',
    'website': 'http://www.vitalpet.com',
    'depends': ['base','account','account_banking_pain_base', 'account_payment_order', 'account_payment_mode','account_cancel','mail','vitalpet_additional_fiscal_periods'],
    'data': [        
        'data/mail_template_data.xml',
        'views/account_payment_view.xml',
        'views/account_payment_mode.xml',
        'views/account_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
