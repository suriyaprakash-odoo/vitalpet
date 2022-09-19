from odoo import api, fields, models


class CityState(models.Model):
    _name="overwrite.city.state"
    
    city= fields.Char("City")
    state = fields.Many2one("res.country.state",string='State')

    
    @api.multi
    def apply_values(self):
       
        active_id = self.env.context.get('active_id')
        job_position_id = self.env["hr.job"].search([('id','=',active_id)])
       
        if job_position_id:
            job_position_id.write({'city_wizard':self.city,'state_wizard_id':self.state.id})
              
        return {'type': 'ir.actions.act_window_close'}