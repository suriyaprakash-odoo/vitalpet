# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
#from odoo import models
from odoo import api, fields, models, _
from odoo.osv import expression

# Empty class but required since it's overridden by sale & crm


class Company(models.Model):
    _inherit = 'res.company'


    daily_report = fields.Boolean(string='Daily Report Enabled')
    source = fields.Selection([('manual', 'Manual'), ('feed', 'Feed')], string='Manual / Feed')
    local_tax_partner = fields.Many2one('res.partner', string='Local Tax Partner', domain=[('supplier', '=', True)])
    daily_report_todo = fields.Selection([('never', 'Never'),('day_shift', 'Each Day and Shift')], string='Daily Report To Do')
    deposit_todo = fields.Selection([('never', 'Never'),('day_shift', 'Each Day and Shift')], string='Deposit To Do')
    ss_roundof = fields.Float('Tolerance')
    ss_adjustments_id = fields.Many2one('account.account','Adjustment Account ')
#     replacement_account_id = fields.Many2one('daily.summary.account','Replacement Journal')


 
    @api.multi
    def name_get(self):
        return [(record.id, (record.code or '')+" - "+(record.name or '')) for record in self]   
    
    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('code', '=ilike', name + '%'), ('name', operator, name)]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&', '!'] + domain[1:]
        companies = self.search(domain + args, limit=limit)
        return companies.name_get() 


class MypracticeConfigSettings(models.TransientModel):
    _inherit = 'mypractice.config.settings'

    daily_report = fields.Boolean(string='Enabled', related='company_id.daily_report',store=True)
    source = fields.Selection([('manual', 'Manual'), ('feed', 'Feed')], string='Manual / Feed', required=True, related='company_id.source',store=True)
    local_tax_partner = fields.Many2one('res.partner', string='Local Tax Partner', domain=[('supplier', '=', True)], related='company_id.local_tax_partner',store=True)
    daily_report_todo = fields.Selection([('never', 'Never'),('day_shift', 'Each Day and Shift')], string='Daily Report To Do', related='company_id.daily_report_todo',store=True)
    deposit_todo = fields.Selection([('never', 'Never'),('day_shift', 'Each Day and Shift')], string='Deposit To Do', related='company_id.deposit_todo',store=True)
    ss_roundof = fields.Float('Tolerance', related='company_id.ss_roundof',store=True)
    ss_adjustments_id = fields.Many2one('account.account','Adjustment Account ', related='company_id.ss_adjustments_id',store=True)
#     replacement_account_id = fields.Many2one('daily.summary.account','Replacement Journal',related='company_id.replacement_account_id',store=True)

# class DailySummaryAccount(models.Model):
#     _name = 'daily.summary.account'
#     
#     name = fields.Char('Name',store=True)
#     account = fields.Char('Account',store=True)
#     journal = fields.Char('Journal',store=True)
#     journal_use_instead = fields.Char('Journal To Use Instead',store=True)
#     account_use_instead = fields.Char('Account To Use Instead',store=True)




class ProjectTask(models.Model):
    _inherit = 'project.task'

    summary_id = fields.Many2one('sales.summary','Summary')