# -*- coding: utf-8 -*-
from odoo.osv import expression
from odoo import api, fields, models, _


class TimekeepingMappingTable(models.Model):
    _name = 'timekeeping.mapping.table'
    
    
    file_type = fields.Selection(selection=[('Daily', 'Daily'), ('Bi-weekly', 'Bi-weekly')], string='File Type')
    is_mapped = fields.Boolean('Mapped')
    code = fields.Char('Code')
    column = fields.Char('Column')
    model_id = fields.Many2one('ir.model', 'Map to Model')
    mapped_field = fields.Char('Map to Field')
    activity_id = fields.Many2one('hr.activity', 'Activity')
    activity_lookup = fields.Boolean('Activity Lookup')
    is_validated = fields.Boolean('Validated')
    description = fields.Char('Description')
    
