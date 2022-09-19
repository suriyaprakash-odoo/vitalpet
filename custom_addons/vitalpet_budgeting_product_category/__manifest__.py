# -*- coding: utf-8 -*-
{
    'name': 'Vitalpet Budgeting Product Category',
    'version': '1.1',
    'category': 'My Practice',
    'author': 'VitalPet',
    'website': 'http://www.vitalpet.com',
    'depends': ['account', 'base', 'account_budget', 'vitalpet_mypractice', 'product'],
    'data': [
        'security/budget_product_security.xml',
        'wizard/income_expense_view.xml',
        'views/dashboard_view.xml',
        'views/budget_view.xml',
        'views/budget_product_category_views.xml',
        'views/income_expense_hierarchy_view.xml',
        'views/product_views.xml',
        'views/budget_cron_view.xml',
        'views/consolidate_report_views.xml',
        'security/ir.model.access.csv',
    ],
    'qweb': ['static/xml/budget_lines.xml',
            'static/xml/dashboard.xml'],


    'installable': True,
    'application': True,
    'auto_install': False,
}
