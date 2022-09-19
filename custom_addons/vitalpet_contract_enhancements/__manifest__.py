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
    'name': 'VitalPet Contract Enhancements',
    'version': '1.0',
    'category': 'Generic Modules/Others',
    'description': """
    """,
    'author': 'Vitalpet',
    'website': 'http://www.vitalpet.com',
    'depends': ['base','hr','vitalpet_bonus_accrual', 'account', 'hr_contract', 'payroll_base', 'payroll_contract_jobs'],
    'data': [
                'security/contract_enhancements_security.xml',
                'security/ir.model.access.csv',
#                 'wizard/contract_wizard.xml',
#                 'wizard/logs_approval.xml',
                'data/contract_enhancement.xml',
                'data/contract_cron.xml',
                'data/email_template.xml',
                'views/contract_view.xml',
                'views/contract_job_form_view.xml',
    ],
    'demo': [],
    'application': True,
    'installable': True,
    'active': False,
    'auto_install': False,
}
