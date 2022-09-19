# -*- coding: utf-8 -*-
# Copyright 2016 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Leave Signature',
    'version': '10.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'Adds a signature field to a leave request',
    'license': 'AGPL-3',
    'author': 'Onestein',
    'website': 'http://www.onestein.eu',
    'depends': [
        'hr_holidays',
        'web_draw'
    ],
    'data': [
        'views/hr_holidays_signature.xml'
    ],
    'installable': True,
}
