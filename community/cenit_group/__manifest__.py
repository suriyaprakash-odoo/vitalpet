# -*- coding: utf-8 -*-

{
    'name': 'Cenit IO Group',
    'version': '0.0.1',
    'application': False,
    'author': 'Esousy',
    'website': 'https://cenit.io',
    #~ 'license': 'LGPL-3',
    'category': 'Extra Tools',
    'summary': 'Odoo, Cenit, Integration Access Right Group, ',
    'description': """
        Add access right group to Cenit module
    """,
    'depends': ['base', 'cenit_base'],
    'data': [
        'security/cenit_security.xml',
        'security/ir.model.access.csv',
        'view/menu.xml',
    ],
    'installable': True
}
