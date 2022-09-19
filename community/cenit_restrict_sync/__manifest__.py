# -*- coding: utf-8 -*-

{
    'name': 'Restric Cenit Sync by Practices',
    'version': '0.0.1',
    'author': 'Esousy',
    'website': 'https://cenit.io',
    # ~ 'license': 'LGPL-3',
    'category': 'Extra Tools',
    'summary': "Vetzip collection.",
    'description': "Vetzip collection.",
    'depends': ['base', 'vitalpet_mapping', 'cenit_group'],
    'data': [
             'views/sync_button_view.xml',
             'views/res_config_view.xml',
             'views/flow_trigger_view.xml',
             'wizard/sync_practice_wizard_view.xml',
             'data/cenit_data.xml'
    ],
    
    'js': 'static/src/js/sync_button.js',
    'qweb': ['static/src/xml/sync_button.xml',],  
    'installable': True
}
