# -*- coding: utf-8 -*-
###############################################################################
#
#   account_statement_completion_label for OpenERP
#   Copyright (C) 2013 Akretion (http://www.akretion.com). All Rights Reserved
#   @author Benoît GUILLOT <benoit.guillot@akretion.com>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

{
    'name': 'Supplier Enhancement',
    'version': '1.0.0.1',
    'category': 'Generic Modules/Others',
    'description': """
    """,
    'author': 'Vitalpet',
    'website': 'http://www.vitalpet.com',
    'depends': ['base', 'account', 'website_sign','account_payment_order'],
    'data': [   
                'security/ir.model.access.csv',
                'views/supplier.xml',
                'views/res_partner_bank.xml',
                'data/supplier_enhancement_cron.xml',

    ],
    'demo': [],
    'application': True,
    'installable': True,
    'active': False,
    'auto_install': False,
}
