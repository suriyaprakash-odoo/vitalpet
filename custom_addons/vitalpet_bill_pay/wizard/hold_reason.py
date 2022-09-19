# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

class HoldReasonWizard(models.TransientModel):

    _name = "hold.reason.wizard"
    _description = "Hold Reason"

    description = fields.Char(string='Reason', required=True)

    @api.multi
    def hold_reason(self):      
        self.ensure_one()        
        context = dict(self._context or {})       
        active_ids = context.get('active_ids', [])       
        for rec in active_ids:           
            if rec:
                billpay_sheet = self.env['billpay.bills'].browse(rec)
                billpay_sheet.notes=self.description
                billpay_sheet.state = 'hold'
        return {'type' : 'ir.actions.act_window_close'}
