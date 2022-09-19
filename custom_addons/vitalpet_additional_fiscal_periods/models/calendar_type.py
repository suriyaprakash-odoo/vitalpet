# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class CalendarType(models.Model):
    _name = 'calendar.type'

    name = fields.Char("Calendar Name", required=True)
    code = fields.Char("Code")
    
    

        
        
#         while(self.from_year < self.to_year)