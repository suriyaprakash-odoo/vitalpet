# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Team Scheduler',
    'version' : '1.0',
    'description': """
        Team Scheduler
    """,
    'author': 'VitalPet',
    'images' : [],
    'depends' : ['vitalpet_mypractice','mail','vitalpet_hr_attendance','vitalpet_budgeting_product_category','hr','hr_recruitment','payroll_period','vitalpet_payroll_inputs','hr_public_holidays'],
    'data': [
        'security/team_scheduler_security.xml',
        'views/team.xml',
        'views/actual.xml',
        'views/weekly_report.xml',
        'views/employee.xml',
        'views/widget.xml',
        'data/team_scheduler_data.xml',
        'views/team_scheduler_view.xml',
        'views/hr_holidays.xml',
        'data/email_template.xml',
        # 'report/report_schedule_view.xml',
        # 'report/report_schedule_templates.xml',
        'report/report_schedule_preview.xml',
        'report/report_schedule_preview_templates.xml',
        'security/ir.model.access.csv'
    ],
    'qweb': [
        'static/src/xml/team_template.xml',
        'static/src/xml/team_hours.xml',
        'static/src/xml/actual_template.xml'],
    'css': ['static/src/css/style.css'],
    'installable': True,
    'auto_install': False,
}
