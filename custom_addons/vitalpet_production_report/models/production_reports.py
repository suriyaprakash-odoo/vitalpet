from odoo import api, fields, models, tools, _

class VitalpetHrProductionLine(models.Model):
    _inherit = 'hr.production.line'

    @api.multi
    def _compute_production_per_day(self):
        for production in self:
            if production.days_worked != 0.0:
                production.production_per_day = production.amount/production.days_worked

    days_worked = fields.Float('Days Worked', related="production_line_id.days_worked",)
    production_per_day = fields.Float('Production per day',compute="_compute_production_per_day")
     

class Employee(models.Model):

    _inherit = "hr.employee"
    production_count = fields.Integer(compute='_compute_production_count', string='Production')
    
    def _compute_production_id(self):
        """ get the lastest production """
        production = self.env['hr.production']
        for employee in self:
            employee.contract_id = production.search([('employee_id', '=', employee.id)], order='date_start desc', limit=1)

    def _compute_production_count(self):
        production_data = self.env['hr.production'].sudo().read_group([('employee_id', 'in', self.ids)], ['employee_id'], ['employee_id'])
        result = dict((data['employee_id'][0], data['employee_id_count']) for data in production_data)
        for employee in self:
            employee.production_count = result.get(employee.id, 0)
    