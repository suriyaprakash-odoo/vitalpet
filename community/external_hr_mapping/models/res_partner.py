# -*- coding: utf-8 -*-


from odoo import models, fields, api, exceptions, _, SUPERUSER_ID


class ResPartner(models.Model):
    _inherit = "res.partner"
    _description = "Partner"

    
    external_employee_id = fields.Char('External Employee ID')
    external_location_id = fields.Char('External Work Location ID')
    external_location_description = fields.Char('External Location Description')
    
    
    @api.model
    def create(self, vals):
        if 'external_state_code' in vals:
            state = self.env['res.country.state'].sudo().search([('code', '=', vals['external_state_code']), ('country_id', '=', 235)],
                                                                     limit=1)
            vals['state_id'] = state and state.id or None
        return super(ResPartner, self).create(vals)
    
    @api.multi
    def write(self, vals):
        if 'external_state_code' in vals:
            state = self.env['res.country.state'].sudo().search([('code', '=', vals['external_state_code']), ('country_id', '=', 235)],
                                                                     limit=1)
            vals['state_id'] = state and state.id or None
        return super(ResPartner, self).write(vals)
