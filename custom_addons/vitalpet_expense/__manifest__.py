# -*- coding: utf-8 -*-
{
    'name': 'Expenses OFX Bank Statement',
    'category': 'Accounting',
    'version': '1.0.6',
    'description': """
Module to import OFX bank statements.
======================================

This module allows you to import the machine readable OFX Files in Odoo: they are parsed and stored in human readable format in
Accounting \ Bank and Cash \ Bank Statements.

Bank Statements may be generated containing a subset of the OFX information (only those transaction lines that are required for the
creation of the Financial Accounting records).
    """,
    'depends': ['base','hr','hr_expense','vitalpet_mypractice','vitalpet_team_scheduler','stock'],
    'data': [
        'security/hr_expense_security.xml',
        'security/ir.model.access.csv',
        'data/hr_expense_data.xml',
        'views/res_partner.xml',
        'views/account_views.xml',
        'views/expense_config_view.xml',
        'views/expense_views.xml',
        'views/bank_statement_import_views.xml',
        'views/hr_expense_mail_attachment.xml',
        'wizards/add_expenses.xml',
    ],
    'installable': True,
    'auto_install': True,
}
