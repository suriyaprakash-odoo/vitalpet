# -*- coding: utf-8 -*-
# Â© 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Document Enhancement",
    "summary": "Document Enhancement",
    "version": "10.0.6",
    "category": "Uncategorized",
    "website": "https://vetzip.vitalpet.net/",
    "author": "VitalPet",
    "depends": ['base','mail','web','website_sign','hr'],
    "data": [
            'security/security.xml',
            'security/ir.model.access.csv',
            'views/document_enhancement.xml',
            'views/signature_request_item.xml',
            'data/signature_request_data.xml',
    ],
    'qweb': ['static/src/xml/*.xml'],
    'installable' : True,
    'application' : True,
}
