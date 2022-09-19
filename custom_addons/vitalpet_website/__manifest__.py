# -*- coding: utf-8 -*-

{
    'name':'Custom website',
    'version': '1.0.4',
    'summary': 'Website creation',
    'description': """
===========================
    """,
    'author': 'VitalPet',
    'website': 'http://www.vitalpet.com',
    'category': 'Custom Website',
    
    'depends': ['base','mail','vitalpet_promote', 'vitalpet_custom_hr_recruitment'],
    
    'data': [
        'security/ir.model.access.csv',
        'views/website.xml',
        'views/vitalpet_website_job_templates.xml',
       
           ],
    'application': True,
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: