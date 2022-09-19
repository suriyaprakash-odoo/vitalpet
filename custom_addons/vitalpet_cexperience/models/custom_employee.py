# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields,api,_
                                            
class Employee(models.Model):
    _inherit = "hr.employee"
    
    visits = fields.Integer(compute='_count_emp_visit', groups="vitalpet_cexperience.group_client_experience_user")  
    
    @api.multi
    def action_employee_rec_view(self):
        
        visit_id = self.env['experience.visit'].search(['|','|','|',('doctor_id', '=', self.name),('tech_id', '=', self.name),('rec_in_id', '=', self.name),('rec_out_id', '=', self.name)]).ids
        action = self.env.ref('vitalpet_cexperience.action_client_experience_view').read()[0]
        if visit_id:
            action['domain'] = [('id', 'in', visit_id)]
        else:
            action['domain'] = [('id', 'in', False)]
        return action
    
    @api.one
    def _count_emp_visit(self):
        
        visit_count_id = self.env['experience.visit'].search(['|','|','|',('doctor_id', '=', self.id),('tech_id', '=', self.id),('rec_in_id', '=', self.id),('rec_out_id', '=', self.id)])
        if visit_count_id:
            if len(visit_count_id) > 0:
                self.visits = len(visit_count_id)
        else:
            self.visits = 0    
            