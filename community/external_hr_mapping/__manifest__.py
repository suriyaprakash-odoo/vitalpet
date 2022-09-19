# -*- coding: utf-8 -*-

{
    'name': 'External HR Mapping',
    'version': '1.0.0',
    'author': 'Esousy',
    'category': 'Extra Tools',
    'summary': "Vetzip collection.",
    'description': "Vetzip collection.",
    'depends': ['hr', 'hr_attendance', 'hr_contract', 'payroll_activity', 'vitalpet_contract_enhancements'],
    'data': [
             'security/ir.model.access.csv',
             'views/external_hr_mapping_view.xml',
             'views/timekeeping_mapping_table_view.xml',
    ],
    'installable': True
}
