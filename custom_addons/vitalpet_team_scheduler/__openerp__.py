# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Team Schduler',
    'version' : '1.0',
    'description': """
        Team Schduler
    """,
    'author': 'VitalPet',
    'images' : [],
    'depends' : ['vitalpet_mypractice','vitalpet_hr_attendance','vitalpet_budgeting_product_category','hr','hr_recruitment','payroll_period','vitalpet_payroll_inputs'],
    'data': [
        'security/team_scheduler_security.xml',
        'views/team.xml',
        'views/actual.xml',
        'views/weekly_report.xml',
        'views/employee.xml',
        'views/widget.xml',
        'data/team_scheduler_data.xml',
        'views/team_scheduler_view.xml',
        'security/ir.model.access.csv'
    ],
    'qweb': [
        'static/src/xml/team_template.xml',
        'static/src/xml/team_hours.xml',
        'static/src/xml/actual_template.xml'],
    'installable': True,
    'auto_install': False,
}
