# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api , _


class SurveyUserInput(models.Model):
    _inherit = "survey.user_input"

    exp_id = fields.Many2one('experience.visit', string='Experience')

    @api.model
    def create(self, vals):
        ctx = self.env.context
        if ctx.get('active_id') and ctx.get('active_model') == 'experience.visit':
            vals['exp_id'] = ctx.get('active_id')
        return super(SurveyUserInput, self).create(vals)