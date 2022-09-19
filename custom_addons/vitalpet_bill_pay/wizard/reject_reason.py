# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

class RejectReasonWizard(models.TransientModel):

    _name = "reject.reason.wizard"
    _description = "Reject Reason"

    description = fields.Char(string='Reason', required=True)

    @api.multi
    def reject_reason(self):
        self.ensure_one()
        context = dict(self._context or {})
        active_ids = context.get('active_ids', [])
        if active_ids:
            billpay_sheet = self.env['billpay.approvals'].browse(active_ids)
            billpay_sheet.notes=self.description
            billpay_sheet.state = 'reject'
            if billpay_sheet:
                bill_source_obj=self.env['billpay.bills'].search([('bill_credit_id', '=', billpay_sheet.bill_credit_id)])
                if bill_source_obj:
                    bill_source_obj.state='hold'
            
        return {'type': 'ir.actions.act_window_close'}
