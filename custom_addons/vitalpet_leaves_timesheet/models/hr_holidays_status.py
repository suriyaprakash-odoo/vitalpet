# -*- coding: utf-8 -*-

from odoo import api, fields, models

class HolidaysType(models.Model):

    _inherit = "hr.holidays.status"
    
    minimum_hours = fields.Float('Minimum Hours', default= 0.0, store=True)
    add_approved_leaves = fields.Boolean(string='Add approved leaves to timesheet?')
    timesheet_id = fields.Many2one('account.analytic.account', string='Timesheet')
    activity_id = fields.Many2one('hr.activity', string='Activity')
    
