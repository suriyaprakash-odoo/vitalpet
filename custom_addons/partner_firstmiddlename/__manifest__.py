# -*- coding: utf-8 -*-
# © 2013 Nicolas Bessi (Camptocamp SA)
# © 2014 Agile Business Group (<http://www.agilebg.com>)
# © 2015 Grupo ESOC (<http://www.grupoesoc.es>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'First name, Middle name and Last name',
    'summary': "Split first name and last name for non company partners",
    'version': '10.0.2.0.0',
    'author': "PPTS",
    'maintainer': 'Camptocamp, Acsone',
    'category': 'Extra Tools',
    'depends': ['base_setup','hr','resource'],
    'data': [
        'views/base_config_view.xml',
        'views/res_partner.xml',
        # 'views/res_user.xml',
        'views/hr_employee_view.xml',
        'data/res_partner.yml',
#         'data/hr_employee.yml',
        
    ],
    'auto_install': False,
    'installable': True,
    'application' : True,
}
