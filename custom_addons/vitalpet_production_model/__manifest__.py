# -*- coding: utf-8 -*-
# � 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "VitalPet Production Model",
    "summary": "Production Model",
    "version": "1.0.1",
    "category": "Account",
    "website": "https://vetzip.vitalpet.net/",
    "author": "VitalPet",
    "depends": ['base','hr','payroll_base','payroll_period','mail','hr_contract'],
    "data": [
            'security/ir.model.access.csv',
            'views/production.xml',
            'views/mail_template.xml',
    ],
    'installable' : True,
    'auto_install' : False,
    'application' : True,
}
