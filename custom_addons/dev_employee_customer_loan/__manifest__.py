# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 Devintelle Software Solutions (<http://devintellecs.com>).
#
##############################################################################

{
    'name': 'Employee / Customer Loan Management ',
    'version': '1.0',
    'sequence':'1',
    'category': 'HR',
    'description': """
        Add the Loan Functioality in Employee /Customer 
    """,
    'summary': 'Add the Loan Functioality in Employee / Customer',
    'author': 'DevIntelle Consulting Service Pvt.Ltd.',
    'website': 'http://devintellecs.com/',
    'images': [],
    'depends': ['account','account_voucher','account_asset'],
    'data': [
        "security/hr_loan_access.xml",
        "security/ir.model.access.csv",
        "views/hr_loan_view.xml",
        "views/hr_skip_installment_view.xml",
#         "data/hr_loan_data.xml",
        
        "wizard/loan_payment.xml",
        "views/partner_loan.xml",
        "report/partner_loan_report.xml",
        "report/report_menu.xml",
        
    ],
    'installable': True,
    'auto_install': False,
    'auto_install': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
