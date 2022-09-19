# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class SyncPracticeWizard(models.TransientModel):

    _name = "sync.practice.wizard"
    _description = "Sync Practice wizard"


    @api.multi
    def sync_practices(self):
        print 'Sync Practice wizard'
        trigger = self.env['flow.trigger'].create({'name':'practices',
                                                   'action': 'load',
                                                   'user_id': self.env.user.id})
        # self.env['cenit.data_type'].browse(1).trigger_flows(trigger)
        return {'type': 'ir.actions.act_window_close'}
