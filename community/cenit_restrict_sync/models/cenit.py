# -*- coding: utf-8 -*-

import logging

from odoo import models, fields, api


_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def create(self, vals):
        if 'global_practice_id' in vals:
            practice = self.env['pims.practice'].search([('global_practice_id', '=', vals['global_practice_id'])], limit=1)
            if not practice or not practice.syncdata:
                return None
        return super(ResPartner, self).create(vals)
    
    

class PimsProvider(models.Model):
    _inherit = 'pims.provider'

    @api.model
    def create(self, vals):
        if 'global_practice_id' in vals:
            practice = self.env['pims.practice'].search([('global_practice_id', '=', vals['global_practice_id'])], limit=1)
            if not practice or not practice.syncdata:
                return None
        return super(PimsProvider, self).create(vals)
    
    