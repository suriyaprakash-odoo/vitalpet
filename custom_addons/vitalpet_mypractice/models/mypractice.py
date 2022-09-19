# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
#from odoo import models
from odoo import api, fields, models, _
from datetime import datetime
import datetime
import re 

class ProjectTask(models.Model):
    _inherit = 'project.task'

    @api.depends('startdate_date', 'completed_date')
    def daystocomplete(self):
        for loop in self:
            date_format = "%Y-%m-%d"
            if loop.startdate_date and loop.completed_date:
                a = datetime.datetime.strptime(loop.startdate_date, date_format)
                b = datetime.datetime.strptime(loop.completed_date, date_format)
                delta = b - a
                loop.days_to_complete = delta.days
            else:
                loop.days_to_complete = 0


    days_to_complete = fields.Float(compute='daystocomplete', string='Completed Days')
    startdate_date = fields.Date('Start Date')
    completed_date = fields.Date('Completed Date')
    mypractice = fields.Boolean(string='My Practice')

    def remove_client_payroll_task(self):
        task_complete_sr = self.env['project.task.type'].search([('name', '=', 'Complete')])
        task_new_sr = self.env['project.task.type'].search([('name', '=', 'New')])

        payroll_task_obj = self.env['project.task'].search([('name','ilike','Payroll'),('mypractice','=',True),('stage_id','!=',task_complete_sr.id),('stage_id','!=',task_new_sr.id)])
        
        for payroll_task in payroll_task_obj:
            r = re.compile(r'[0-9]{4}\-[0-9]{2}\-[0-9]{2}')
            data = r.findall(str(payroll_task.name))
            period_start_date = datetime.datetime.strptime(data[0], '%Y-%m-%d').date()
            period_end_date = datetime.datetime.strptime(data[1], '%Y-%m-%d').date()

            period_id = self.env['hr.period'].search([('company_id' , '=' , payroll_task.company_id.id),('date_start' , '=' , period_start_date),('date_stop' , '=' , period_end_date)])
            
            hr_production_obj = self.env['hr.payroll.inputs'].search_count([('payroll_period','=',period_id.id),('company_id','=',payroll_task.company_id.id)])

            if hr_production_obj > 0:
                payroll_task.write({'stage_id':task_complete_sr.id})

        client_visit_obj = self.env['project.task'].search([('name','ilike','Visit'),('mypractice','=',True),('stage_id','!=',task_complete_sr.id),('stage_id','!=',task_new_sr.id)])

        for visit_task in client_visit_obj:
            visit_task.write({'stage_id':task_complete_sr.id})

    def update_completed_date(self):

        task_complete_sr = self.env['project.task.type'].search([('name', '=', 'Complete')])
        task_new_sr = self.env['project.task.type'].search([('name', '=', 'New')])

        payroll_task_obj = self.env['project.task'].search([('name','ilike','Payroll Inputs'),('mypractice','=',True),('stage_id','=',task_complete_sr.id)])

        for payroll_task in payroll_task_obj:
            payroll_task.completed_date = payroll_task.date_last_stage_update

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        if domain:
            ft_domain = [x for x in domain if "|" not in x]
            domain.pop()
            domain = ft_domain 
        return super(ProjectTask, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)

    @api.multi
    def action_all_overdue_complete(self):
        self.env['hr.expense.sheet'].expense_task_complete()
        self.env['hr.period'].action_payroll_overdue_to_complete()
        self.env['hr.period'].action_overdue_to_complete()
        self.env['hr.period'].action_visit_review_overdue_to_complete()
        self.env['sales.summary'].daily_report_overdue_complete()
        
        return True


class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'

    mypractice = fields.Boolean(string='My Practice')

    _sql_constraints = [
        ('name_uniq', 'UNIQUE (name)',  'You can not have two stages with the same name !')
        ]

ProjectTaskType()


class Project(models.Model):
    _inherit = "project.project"

    mypractice = fields.Boolean(string='My Practice')

    _sql_constraints = [
        ('name_uniq', 'UNIQUE (name)',  'Name already exist !')
        ]


class ReportAccountFinancialReport(models.Model):
    _inherit = "account.financial.html.report"
    _description = "Account Report"
 
 
 
 
    def create_action_and_menu_practice(self, practice_parent):
        print "grg1111"
        client_action_practice = self.env['ir.actions.client'].create({
            'name': self.get_title(),
            'tag': 'account_report_generic',
            'context': {
                'url': '/account_reports/output_format/financial_report/' + str(self.id),
                'model': 'account.financial.html.report',
                'id': self.id,
            },
        })
 
        if self.get_title() != 'Profit and Loss (HQ)':
            self.env['ir.ui.menu'].create({
                'name': self.get_title(),
                'parent_id': practice_parent or self.env['ir.model.data'].xmlid_to_res_id('vitalpet_mypractice.mypractice_account_reports_legal_statements_menu'),
                'action': 'ir.actions.client,%s' % (client_action_practice.id,),
            })
            self.write({'menuitem_created': True})
 
 
 
    @api.model
    def create(self, vals):
        parent_id = False
        practice_parent = self.env.ref('vitalpet_mypractice.mypractice_account_reports_legal_statements_menu').id
        if vals.get('parent_id'):
            parent_id = vals['parent_id']
            del vals['parent_id']
 
        res = super(ReportAccountFinancialReport, self).create(vals)
        #res.create_action_and_menu(parent_id)
        res.create_action_and_menu_practice(practice_parent)
        return res
    
class HrEmployee(models.Model):
    _inherit = "hr.employee"
    
    @api.multi
    def update_img_notes(self):
        context = dict(self.env.context or {})
        context.update({"tid":self.id})
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'update.image',
            'target': 'new',
            'context':context,
        }            

class ImageUpdate(models.TransientModel):
    _name = 'update.image'
    _description = 'Update Image and Notes'
    
    notes = fields.Text('Notes')
    image = fields.Binary("Photo",attachment=True,
        help="This field holds the image used as photo for the employee, limited to 1024x1024px.")
   
    @api.multi
    def update_image_notes(self):
        context = dict(self.env.context or {})
        tid = context.get('tid', False)
        context.update({"confirm_id":tid,"image":self.image,"notes":self.notes})
        update_image = self.env['hr.employee'].sudo().search([("id", "=", tid)])
        if not update_image.notes:
            if self.image:
                update_image.sudo().write({'image' : self.image})
            if self.notes:
                update_image.sudo().write({'notes' : self.notes})
        else:
            return {
                    'name': ('Values Already Exist'),
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'update.confirmation',
                    'view_id': self.env.ref('vitalpet_mypractice.update_confirmation_warning').id,
                    'type': 'ir.actions.act_window',
                    'context': context,
                    'target': 'new'
                }
            
class UpdateConfirmation(models.TransientModel):
    _name = 'update.confirmation' 
    
    def continue_to_update(self):        
            notes = self.env.context.get('notes')
            image = self.env.context.get('image')
            tid = self.env.context.get('confirm_id', False)
            print tid
            confirm_update = self.env['hr.employee'].sudo().search([("id", "=", tid)])
            if image:
                confirm_update.sudo().write({'image' : image})
            if notes:
                confirm_update.sudo().write({'notes' : notes})
              
            

