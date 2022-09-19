# -*- coding: utf-8 -*-
{
    'name': "Vitalpet Promote Campaigns",

    'summary': """
    Module for managing Report Card Campaign for VitalPet.
        twilio should be installed in server.
        pip install twilio in Windows.
        """,

    'description': """
        Long description of module's purpose
    """,

    'author': "VitalPet",
    'website': "http://www.vitalpet.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Data integration, ERP',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['vitalpet_mapping','vitalpet_promote','product', 'cenit_twilio'],

    'installable': True,
    'application': True,


    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        #'user_groups.xml',
        'templates.xml',
        'menus.xml',
        'paper_format.xml',
        'report_card.xml',
        'report_card_pet_mass_mailing.xml',
        'pet_mass_mailing.xml',
        'cron_view.xml',
        'reportcard_ir_value.xml','res_company.xml'
    ],
    # only loaded in demonstration mode
    #'demo': [
    #    'demo.xml',
    #],
}
