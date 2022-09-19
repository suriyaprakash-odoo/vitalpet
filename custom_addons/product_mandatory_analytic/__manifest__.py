# -*- coding: utf-8 -*-

{
    'name':'Product Mandatory Analytic Account',
    'version': '1.3',
    'summary': 'Product Analytic Account Creation',
    'description': """
===========================
    """,
    'author': 'VitalPet',
    'website': 'http://www.vitalpet.com',
    'category': 'Product',
    
    'depends': ['base','product','vitalpet_bill_pay','vitalpet_expense','account','account_voucher','purchase'],
    
    'data': [
        'views/product_mandatory_analytic.xml',
       
           ],
    'application': True,
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: