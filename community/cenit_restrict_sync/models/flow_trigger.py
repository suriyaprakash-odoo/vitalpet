# -*- coding: utf-8 -*-
from odoo.osv import expression
from odoo import api, fields, models, _


class FlowTrigger(models.Model):
    _name = 'flow.trigger'
    
    
    name = fields.Char('Flow Name')
    action = fields.Char('Action')
    office_id = fields.Char('Office ID')
    practice_id = fields.Char('Practice')
    user_id = fields.Many2one('res.users', 'User')
    
