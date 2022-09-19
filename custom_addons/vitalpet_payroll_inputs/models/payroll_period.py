from odoo import api, fields, models, tools, _
from datetime import datetime,timedelta,date

class Company(models.Model):
    _inherit = 'res.company'

    journal_id = fields.Many2one("account.journal",string="Payroll Journal")
    parent_journal_id = fields.Many2one("account.journal", string="Payroll Parent Journal")
    payroll_manager_id = fields.Many2one("res.users", string="Payroll Manager")
    payroll_company_id = fields.Many2one("res.company", string="Payroll Company")
    payroll = fields.Boolean(string="Payroll Enable", default=False)

class MypracticeConfigSettings(models.TransientModel):
    _inherit = "mypractice.config.settings"

    payroll = fields.Boolean(string="Enabled", related='company_id.payroll', default=False, store=True)
    payroll_company_id = fields.Many2one("res.company", related='company_id.payroll_company_id', string="Payroll Company",store=True)
    payroll_manager_id = fields.Many2one("res.users", related='company_id.payroll_manager_id', string="Payroll Manager",store=True)
    journal_id = fields.Many2one("account.journal", related='company_id.journal_id', string="Payroll Journal",store=True)
    parent_journal_id = fields.Many2one("account.journal", related='company_id.parent_journal_id', string="Payroll Parent Journal",store=True)

class HrPeriod(models.Model):
    _inherit = "hr.period"

    @api.multi
    def _create_payroll_tasks_cron(self):
        company_obj = self.env['res.company']
        company_sr = company_obj.search([('payroll', '=', True)])
        for company in company_sr:
            task_type_sr = self.env['project.task.type'].search([('name', '=', 'To Do')])
            task_complete_sr = self.env['project.task.type'].search([('name', '=', 'Complete')])
            current_date= date.today()
            tid_period = self.env['hr.period'].search([('company_id','=',company.id),('date_start', '<=', current_date),('date_stop', '>=', current_date)])
            project_tag_sr = self.env['project.tags'].search([('name', '=', 'Payroll')])
            project_sr = self.env['project.project'].search([('name', '=', 'My Practice'),('company_id', '=', company.id)])
                
  
            if tid_period.date_stop == str(current_date):
                name = company.code + "-Payroll Inputs-" + tid_period.fiscalyear_id.name+ "-" + tid_period.date_start+" - "+ tid_period.date_stop
                project_tk = self.env['project.task'].search([('name','=',name)])
                if not project_tk: 
                    project_obj=self.env['project.task'].create({
                                                            'name': name,
                                                            'user_id':company.manager_user_id.id,
                                                            'company_id':company.id,
                                                            'project_id': project_sr.id,
                                                            'date_deadline': datetime.strptime(tid_period.date_stop, '%Y-%m-%d') + timedelta(days=1),   
                                                            'mypractice': True,                  
                                                            'tag_ids': [(6, 0, [project_tag_sr.id])],
                                                            'stage_id': task_type_sr.id,
                                                            'startdate_date':tid_period.date_start,        
                                                            })
                    payroll_status= self.env['hr.payroll.inputs'].search([('payroll_period','=',tid_period.id),('company_id','=',company.id)])
                    if not payroll_status:
                        status=self.env['hr.payroll.inputs'].create({
                                                                'payroll_period':tid_period.id,
                                                                'company_id':company.id,
                                                                'state':'open',
                                                                'stage':'timesheet',
                                                                'task_id':project_obj.id,
                                                                'date':datetime.strptime(tid_period.date_stop, '%Y-%m-%d') + timedelta(days=1),
                                                                })
                    else:
                        payroll_status.task_id=project_obj.id
                        
            else:
                if tid_period:
                    from_date  = datetime.strptime(tid_period.date_start, '%Y-%m-%d')
                    current_date = from_date + timedelta(days=-1)
                    tid_period = self.env['hr.period'].search([('company_id','=',company.id),('date_start', '<=', current_date),('date_stop', '>=', current_date)])
                    if tid_period:
                        name = company.code + "-Payroll Inputs-" + tid_period.fiscalyear_id.name+ "-" + tid_period.date_start+" - "+ tid_period.date_stop
                        
                        project_obj_sr = self.env['project.task'].search([('name','=', name)])
                        if project_obj_sr:
                            deadline_date = datetime.now() + timedelta(days=3)
                            date_start_plus_five = datetime.strptime(project_obj_sr.startdate_date[:10], '%Y-%m-%d') + timedelta(days=1)
                            date_start_plus_seven = datetime.strptime(project_obj_sr.startdate_date[:10], '%Y-%m-%d') + timedelta(days=7)
                            
                            if project_obj_sr.stage_id != task_complete_sr:
                                if deadline_date > date_start_plus_five and deadline_date <= date_start_plus_seven:
                                    task_todo_sr = self.env['project.task.type'].search([('name', '=', 'Overdue < 1 Week')])
                                    project_obj_sr.write({'stage_id':task_todo_sr.id})
                                elif deadline_date > date_start_plus_seven :
                                    task_todo_sr = self.env['project.task.type'].search([('name', '=', 'Overdue > 1 Week')])
                                    project_obj_sr.write({'stage_id':task_todo_sr.id})
        
        task_complete_sr = self.env['project.task.type'].search([('name', '=', 'Complete')])
        payroll_task_obj = self.env['project.task'].search([('mypractice','=',True),('stage_id','!=',task_complete_sr.id)])

        for payroll_task in payroll_task_obj:
            hr_obj = self.env['hr.payroll.inputs'].search([('task_id','=',payroll_task.id)], limit=1)
            if hr_obj:
                if hr_obj.stage == 'validate' or hr_obj.stage == 'finalized':
                    payroll_task.write({'stage_id':task_complete_sr.id})
                    payroll_task.completed_date = datetime.now().date()

        return True


    @api.multi
    def action_payroll_overdue_to_complete(self):
        task_complete_sr = self.env['project.task.type'].search([('name', '=', 'Complete')])
        payroll_task_obj = self.env['project.task'].search([('mypractice','=',True),('stage_id','!=',task_complete_sr.id)])

        for payroll_task in payroll_task_obj:
            hr_obj = self.env['hr.payroll.inputs'].search([('task_id','=',payroll_task.id)], limit=1)
            if hr_obj:
                if hr_obj.stage == 'validate' or hr_obj.stage == 'finalized':
                    payroll_task.write({'stage_id':task_complete_sr.id})
                    payroll_task.completed_date = datetime.now().date()

