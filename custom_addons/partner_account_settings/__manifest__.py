# -*- coding: utf-8 -*-
{
    'name' : 'Partner Account Settings',
    'version' : '1.1',
    'category' : 'Product',
    'author' : 'PPTS',
    'website': 'http://www.pptssolutions.com',
    'depends': ['product','base','account', 'account_asset','vitalpet_bill_pay'],
    'data': [
        'wizard/account_properties.xml',
        'views/par_acc_setting.xml',
        'wizard/account_entries_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
