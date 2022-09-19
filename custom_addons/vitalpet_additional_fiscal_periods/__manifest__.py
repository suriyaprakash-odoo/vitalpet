# -*- coding: utf-8 -*-
{
    "name": "Vitalpet Additional Fiscal Periods",
    "summary": "Manage all kind of date periods",
    "version": "10.0.1.0.0",
    "category": "Uncategorized",
    "website": "https://vetzip.vitalpet.net/",
    "author": "VitalPet",
    "application": True,
    "installable": True,
    "depends": [
        "web",'account','account_asset','hr_expense'
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/account_fiscal_periods_security.xml",
        "views/assets.xml",
        "views/account_fiscal_periods_view.xml",
        "views/account_view.xml",
        "views/hr_expense_view.xml",
        "views/account_config.xml",
    ],
    "qweb": [
        "static/src/xml/date_range.xml",
    ]
}
