# -*- coding: utf-8 -*-
# © 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "HR Attendance",
    "summary": "HR Attendance",
    "version": "10.0.1.0.0",
    "category": "Uncategorized",
    "website": "https://vetzip.vitalpet.net/",
    "author": "VitalPet",
    "depends": ['base', 'mail', 'web', 'hr_attendance', 'hr', 'hr_timesheet_sheet','hr_timesheet','hr_contract','payroll_contract_jobs','payroll_activity','vitalpet_leaves_timesheet'],
    "data": [  
            'security/hr_attendance.xml',
            'security/ir.model.access.csv', 
            'views/web_asset_backend_template.xml', 
            'views/hr_attendance.xml',
            'views/hr_contract_job_view.xml',
    ],
    
    'qweb': [
        "static/src/xml/attendance.xml",
    ],
    'installable' : True,
    'auto_install' : False,
    'application' : True,
}
