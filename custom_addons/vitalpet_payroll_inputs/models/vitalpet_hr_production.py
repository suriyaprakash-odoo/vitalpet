# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, tools, _
import datetime
import re
from odoo.exceptions import ValidationError, UserError

        
class VitalpetHrProductions(models.Model):
    _inherit = 'hr.production'
   
    @api.model
    def update_bonus_amount(self,amount,period_id,employee_id,job_id,bonus_id,bonus_date):
        try:
            float(amount)
        except ValueError:
            raise ValidationError(_('Enter valid input.'))
        flag = self.env['res.users'].has_group('vitalpet_mypractice.group_my_practice_manager')             
        if bonus_id:
            tag_id = self.env['hr.production.tag'].search([('id','=',bonus_id)])[0]
            if tag_id.double_validation == True and flag != True:
                status = "non_validate"
            else:
                # if flag == True:
                status = "validate"
                # else:
                #     status = "non_validate"
            print status,'==',flag

        hr_period = self.env['hr.period'].search([('id', '=', int(period_id))])
        hr_employee = self.env['hr.employee'].sudo().search([('id', '=', int(employee_id))])
        if hr_period.company_id != hr_employee.company_id:
            select_period = self.env['hr.period'].sudo().search([('company_id', '=', hr_employee.company_id.id),
                                                          ('date_start', '=', hr_period.date_start),
                                                          ('date_stop', '=', hr_period.date_stop)])
            
            period_id = select_period.id
            
        hr_productions = self.env['hr.production'].search([('employee_id', '=', int(employee_id)),
                                                                   ('period_id', '=', int(period_id))])
        if hr_productions:
            hr_production_line = self.env['hr.production.line'].search([('job_id', '=', int(job_id)),
                                                                           ('bonus_id', '=', int(bonus_id)),
                                                                           ('date', '=', bonus_date),
                                                                           ('production_line_id', '=', hr_productions.id)])

            if hr_production_line:
                hr_production_line.write({'amount':amount,'status' : status})
            else:
                print status,'--',hr_productions
                hr_production_line=hr_production_line.create({
                    'empolyee_id':employee_id,
                    'amount':amount,
                    'job_id':job_id,
                    'company_id': self.env.user.company_id.id,
                    'bonus_id':bonus_id,
                    'date':bonus_date,
                    'production_line_id':hr_productions.id,
                    'status' : status
                    })
                if status=='validate':
                    if self.env['hr.production.line'].search_count([('status','=','non_validate'),('production_line_id','=',hr_productions.id)]) == 0:
                        hr_production_line.production_line_id.status='validated'
                    else:
                        hr_production_line.production_line_id.status='draft'
                else:
                    if hr_productions:
                        hr_productions.write({'status':'draft'})
                        hr_productions.write({'state':'draft'})
                    
        else:
            line_vals = {
                    'empolyee_id': employee_id,
                    'amount':amount,
                    'job_id':job_id,
                    'company_id': self.env.user.company_id.id,
                    'bonus_id':bonus_id,
                    'status': status,
                    'date':bonus_date}
                    
            self.env['hr.production'].create({
                    'employee_id': int(employee_id),
                    'company_id': self.env.user.company_id.id,
                    'period_id':period_id,
                    'production_line_ids':[(0, 0, line_vals)],
                    'status':'validated' if status=='validate' else 'draft',
                    'state':'validated' if status=='validate' else 'draft'
                })
            
        return True

    @api.model
    def validate_bonus_amount(self, amount, period_id, employee_id, job_id, bonus_id, bonus_date):

        try:
            float(amount)
        except ValueError:
            raise ValidationError(_('Enter valid input.'))
        hr_period = self.env['hr.period'].search([('id', '=', int(period_id))])
        hr_employee = self.env['hr.employee'].sudo().search([('id', '=', int(employee_id))])
        if hr_period.company_id != hr_employee.company_id:
            select_period = self.env['hr.period'].sudo().search([('company_id', '=', hr_employee.company_id.id),
                                                          ('date_start', '=', hr_period.date_start),
                                                          ('date_stop', '=', hr_period.date_stop)])
            period_id = select_period.id

        hr_productions = self.env['hr.production'].search([('employee_id', '=', int(employee_id)),
                                                                     ('period_id', '=', int(period_id))])
        if hr_productions:
            hr_production_line = self.env['hr.production.line'].search([('job_id', '=', int(job_id)),
                                                                                 ('bonus_id', '=', int(bonus_id)),
                                                                                 ('date', '=', bonus_date),
                                                                                 ('production_line_id', '=', hr_productions.id)])

            if hr_production_line:
                hr_production_line.write({'amount': amount})
            else:
                hr_production_line.create({
                    'empolyee_id': employee_id,
                    'amount': amount,
                    'job_id': job_id,
                    'bonus_id': bonus_id,
                    'company_id': self.env.user.company_id.id,
                    'date': bonus_date,
                    'production_line_id': hr_productions.id,
                    'status': 'validate'
                })
                hr_production_line.production_line_id.status='validated'
        else:
            line_vals = {
                'empolyee_id': employee_id,
                'amount': amount,
                'job_id': job_id,
                'company_id': self.env.user.company_id.id,
                'bonus_id': bonus_id,
                'status': 'validate',
                'date': bonus_date
            }

            res_production=self.env['hr.production'].create({
                'employee_id': int(employee_id),
                'company_id': self.env.user.company_id.id,
                'period_id': period_id,
                'production_line_ids': [(0, 0, line_vals)],
                'status': 'validated',
            })

        return True

    @api.model
    def run_validate_script_exiting(self):
        for rec in self.env['hr.production'].sudo().search([('status', '=', 'draft')]):
            i=0
            print rec
            for prod in rec.production_line_ids:
                if i==0:
                    if prod.status=='validate':
                        rec.status='validated'
                        i+=1
                        
class VitalpetHrProductionLine(models.Model):
    _inherit = 'hr.production.line'
    
    @api.model
    def default_get(self, fields):
        res = super(VitalpetHrProductionLine, self).default_get(fields)
        if self.env.context.get('employee_id', False):
            employee_id = self.env.context.get('employee_id', False)
            hr_contracts = self.env['hr.contract'].search([('employee_id', '=', employee_id)])
            if hr_contracts:
                for contract in hr_contracts:
                    if contract.contract_job_ids:
                        res.update({'job_ids': [(6, 0, [i.job_id.id for i in contract.contract_job_ids])]})
                    else:
                        raise UserError('Please add jobs in contracts')
            else:
                raise UserError('Please create contract for employee')                          
        return res
    
    @api.onchange('job_id')
    def on_change_job_id(self):
        if self.env.context.get('employee_id', False):
            res = {'domain': {
            'bonus_id': "[('id', '=', False)]",
            }}
            if self.job_id and self.job_id.production_type_ids:
                jrl_ids = self.job_id.production_type_ids.ids
                res['domain']['bonus_id'] = "[('id', 'in', %s)]" % jrl_ids
            return res
        else:
            raise UserError('Please select employee')  
   
    


    


    
    
        
        