# -*- coding: utf-8 -*-
{
    'name' : 'Daily Summary',
    'version' : '10.0.1',
    'category' : 'Tools',
    'author' : 'VitalPet',
    'website': 'http://www.vitalpet.com',
    'depends': ['web','account','mail','base','product_category_company_parameter','account_voucher','account_accountant', 'vitalpet_mypractice','vitalpet_additional_fiscal_periods'],
    'data': [
        'views/sales_summary_view.xml',
        'views/res_config_view.xml',
        'views/dailysummary_config_view.xml',
        'data/summary_data.xml',
        'security/sales_summary_security.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
