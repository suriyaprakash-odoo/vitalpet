from odoo import api, fields, models, _
from openerp.exceptions import Warning as UserError

class HrPublicHolidays(models.Model):
    _inherit = 'hr.holidays.public'
    _description = "Holidays"
    
    company_id = fields.Many2one('res.company', string='Company')

    
    def _check_year_one(self):
        if self.company_id:
            domain = [('year', '=', self.year),
                      ('company_id', '=', self.company_id.id),
                      ('id', '!=', self.id)]
            
            if self.search_count(domain):
                raise UserError(_('You can\'t create duplicate public holiday  per year and/or company'))
        elif self.year:
            domain = [('year', '=', self.year),
                      ('id', '!=', self.id)]            
            if self.search_count(domain):
                raise UserError(_('You can\'t create duplicate public holiday  per year and/or company'))
            
#         return True

