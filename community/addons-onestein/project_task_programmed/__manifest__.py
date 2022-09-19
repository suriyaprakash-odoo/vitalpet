# -*- coding: utf-8 -*-
# Copyright 2016 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Task Reminder Planner',
    'summary': 'Plan task reminders for any date field',
    'author': 'Onestein',
    'license': 'AGPL-3',
    'website': 'http://www.onestein.eu',
    'images': ['static/description/main_screenshot.png'],
    'category': 'Custom',
    'version': '10.0.1.0.0',
    'depends': [
        'project',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/project_task_alert.xml',
        'views/project_task.xml',
        'data/task_alert_cron.xml',
        'menu_items.xml',
    ],
    'installable': True,
}
