# -*- coding: utf-8 -*-
{
    'name': 'Account Bank Statement Reconcilation Info',
    'version': '1.0',
    'description': 'Know more details about reconciled bank statement with correspondent journal',
    'category': 'account',
    'author': 'PPTS [India] Pvt.Ltd.',
    "website": "http://www.pptssolutions.com",
    'sequence': 4,
    'depends': ['base', 'web','account','account_bank_statement_import', 'account_cancel'],
    'data': [
            'views/account_views.xml'
    ],
    'qweb': [
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'web_preload': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
