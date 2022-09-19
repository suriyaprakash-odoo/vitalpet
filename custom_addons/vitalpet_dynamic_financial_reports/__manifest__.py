# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Dynamic Financial Reports Customization',
    'summary': 'View and create reports',
    'category': 'Accounting',
    "website": "https://vetzip.vitalpet.net/",
    'description': """
Accounting Reports
====================
New Financial Reporting module is to provide high level financials, it will rely on live feed from the appropriate accounts; it should not be using following reports: P&L, Cash Flow statement and Balance Sheet. Instead of existing reports, new module should create P&L with HQ, P&L without HQ, Cash Flow statement and Balance Sheet with custom calculation. It should work with account fiscal period for respective companies.



    """,
    'depends': ['account','account_reports','vitalpet_additional_fiscal_periods'],
    'data': [
        
        'data/account_financial_report.xml',
        'data/account_financial_report_data.xml',
        'data/account_financial_report_pl_data.xml',
        'data/account_financial_report_bs_data.xml',
        'data/account_financial_report_cf_data.xml',
        'views/report_financial.xml',
        'views/account_view.xml',
    ],
    'qweb': [
        'static/xml/dynamic_reports.xml',
    ],
    'installable': True,
    'application':True,
    'author': 'VitalPet'
}
