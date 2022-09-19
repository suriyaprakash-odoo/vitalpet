# -*- coding: utf-8 -*-
# Â© 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Vitalpet Weekly Report",
    "summary": "Vitalpet Weekly Report",
    "version": "10.0.1.0.0",
    "category": "Uncategorized",
    "website": "https://vetzip.vitalpet.net/",
    "author": "VitalPet",
    "depends": ['base','vitalpet_mypractice'],
    "data": [
            'views/weekly_report.xml',
            'security/weekly_report_security.xml',
            'security/ir.model.access.csv',
    ],    
    'installable' : True,
    'auto_install' : False,
    'application' : True,
}
