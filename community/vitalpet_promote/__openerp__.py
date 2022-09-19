# -*- coding: utf-8 -*-
{
    'name': "VitalPet Promote",

    'summary': """
        CRM Calls, News, Blogs, Announces, Discussions""",

    'description': """
        Module for Inbound Call monitoring.
The calls are automatically synced from the the Call operator's Server, and allows the rating of these calls accrording to Audit Parameters.
In addition to the ability to create Posts in the website FrontEnd.
    """,

    'author': "VitalPet",
    'website': "http://www.vitalpet.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'CRM, ERP, Data integration',
    'version': '1.0',

    # any module necessary for this one to work correctly
	'author': 'VitalPet',

    'depends': ['crm','hr','widget_player_audio','board','crm_voip','text_align_tree_view',
                'website_mail', 'website_partner',
        ],


    'installable': True,
    'application': True,



    'data': [
    #user group_user
        'user_groups.xml',
    # from vitalpet_crm, leaderboard
        'menus.xml','frontdesk.xml','call_scorecard_view.xml',
        'res_company_report.xml', 'performance_gauges_view.xml',
        'configuration.xml',
    # from website_blog
        'data/website_blog_data.xml',
        'data/call_summary_data.xml',
        'views/website_blog_views.xml',
        'views/website_blog_templates.xml',
        'views/snippets.xml',
        'security/ir.model.access.csv',
        'security/website_blog_security.xml',
    # from custom_blog
        'views/blog_view.xml',
    ],
    # only loaded in demonstration mode
#     'demo': [
#         'demo.xml',
#     ],
}
