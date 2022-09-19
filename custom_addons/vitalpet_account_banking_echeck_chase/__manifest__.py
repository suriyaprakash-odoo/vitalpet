# -*- coding: utf-8 -*-
{
    'name' : 'Account Banking NACHA Credit Transfer',
    'summary': 'Create NACHA XML files for Credit Transfers',
    'version' : '1.1',
    'category' : 'Banking addons',
    'author' : 'VitalPet',
    'website': 'http://www.vitalpet.com',
    'depends': ['base','account','account_banking_pain_base', 'account_payment_order'],
    'data': [        
        'data/account_payment_echeck_method.xml',
        'data/ir_sequence_data.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
