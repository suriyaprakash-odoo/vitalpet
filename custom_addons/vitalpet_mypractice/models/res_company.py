# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
#from odoo import models
from odoo import api, fields, models, _

# Empty class but required since it's overridden by sale & crm
class Company(models.Model):
    _inherit = 'res.company'

    manager_user_id = fields.Many2one('res.users', string='Manager')
    designee_user_id = fields.Many2one('res.users', string='Designee')
    vat_state  = fields.Char(string='State Tax ID')
    vat_city  = fields.Char(string='City Tax ID')
    
    # Operations Days Open
    Sunday = fields.Boolean(string='Sunday')
    Monday = fields.Boolean(string='Monday')
    Tuesday = fields.Boolean(string='Tuesday')
    Wednesday = fields.Boolean(string='Wednesday')
    Thursday = fields.Boolean(string='Thursday')
    Friday = fields.Boolean(string='Friday')
    Saturday = fields.Boolean(string='Saturday')
    # Operations Shifts
    sunday_shift = fields.Selection([('0', 'Day'),('1', 'Night'),('2', 'Day &amp;Night')],'Sunday Shift')
    monday_shift = fields.Selection([('0', 'Day'),('1', 'Night'),('2', 'Day &amp;Night')],'Monday Shift')
    tuesday_shift = fields.Selection([('0', 'Day'),('1', 'Night'),('2', 'Day &amp;Night')],'Tuesday Shift')
    wednesday_shift = fields.Selection([('0', 'Day'),('1', 'Night'),('2', 'Day &amp;Night')],'Wednesday Shift')
    thursday_shift = fields.Selection([('0', 'Day'),('1', 'Night'),('2', 'Day &amp;Night')],'Thursday Shift')
    friday_shift = fields.Selection([('0', 'Day'),('1', 'Night'),('2', 'Day &amp;Night')],'Friday Shift')
    saturday_shift = fields.Selection([('0', 'Day'),('1', 'Night'),('2', 'Day &amp;Night')],'Saturday Shift')
    # for Dashboard To Dos
    expense = fields.Boolean(string='Expenses', help='Tip: Stay alerted when a inbound calls needs attention.')
    recruitment = fields.Boolean(string='Recruitment', help='Tip: Stay alerted regarding requisitions and new applicants.')
    onboarding = fields.Boolean(string='Onboarding', help='Tip: Stay alerted regarding onboarding activities.')
    leaves = fields.Boolean(string='Time Off', help='Tip: Stay alerted regarding time off requests.')
    attendance = fields.Boolean(string='Time Keeping', help='Tip: Stay alerted regarding time punches.')
    payroll_conf = fields.Boolean(string='Payroll', help='Tip: Stay alerted regarding payroll approval.')
    performance = fields.Boolean(string='Appraisal', help='Tip: Stay alerted regarding performance reviews.')
    contract = fields.Boolean(string='Contract', help='Tip: Stay alerted regarding performance reviews.')
    total_capacity = fields.Integer("Total Capacity")
    total_day_camp_capacity = fields.Integer("Total Capacity")


