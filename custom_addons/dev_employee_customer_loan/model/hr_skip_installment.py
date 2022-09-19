
# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 Devintelle Software Solutions (<http://devintellecs.com>).
#
##############################################################################
from odoo import models, fields, api , _
import time
from datetime import datetime, timedelta, date
from odoo.exceptions import UserError


class hr_skip_installment(models.Model):
    _name = 'hr.skip.installment'

    def _get_employee_id(self):
        employee_ids = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)])
        if employee_ids:
            for emp in employee_ids:
                return emp.id
        return False

    name= fields.Char('Reason to Skip',required=True)
    loan_id = fields.Many2one('hr.loan','Loan',domain="[('employee_id','=',employee_id)]",required=True)
    employee_id = fields.Many2one('hr.employee','Employee',required=True, default=_get_employee_id)
    date= fields.Date('Date',required=True, default=fields.Datetime.now)
    state= fields.Selection([('draft', 'Draft'), ('open', 'Waiting Approval'), ('refuse', 'Refused'), ('confirm', 'Approved'), ('cancel', 'Cancelled')], string="Status",required=True, default='draft')

    
    def confirm_request(self):
        self.state = 'open'
        return True
    
    def approve_request(self):
        self.state = 'confirm'
        return True
    
    def refuse_request(self):
        self.state = 'refuse'
        return True
    
    def set_to_draft(self):
        self.state = 'draft'
        return True
    
    def set_to_cancel(self):
        self.state = 'cancel'
        return True
        
    def unlink(self):
        for record in self:
            if record.state not in ['draft', 'refuse']:
                raise osv.except_osv(_('Warning!'),_('You cannot delete a skip installment request which is in %s state.')%(record.state))
        return super(hr_skip_installment,self).unlink()
            
