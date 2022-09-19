# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

class RefuseReasonWizard(models.TransientModel):

    _name = "refuse.reason.wizard"
    _description = "Refuse Reason"

    description = fields.Char(string='Reason', required=True)

    @api.multi
    def refuse_reason(self):      
        self.ensure_one()        
        context = dict(self._context or {})       
        active_ids = context.get('active_ids', [])       
        for rec in active_ids:           
            if rec:
                billpay_sheet = self.env['billpay.bills'].browse(rec)
                billpay_sheet.refuse_reason=self.description
                billpay_sheet.state = 'refuse'
        return {'type' : 'ir.actions.act_window_close'}
