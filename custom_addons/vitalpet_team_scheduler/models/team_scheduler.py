from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime,timedelta




class ProjectTask(models.Model):
    _inherit = "project.task"

    team_scheduler_id = fields.Many2one('staff.planning', 'Team Scheduler')


class HrPeriod(models.Model):
    _inherit = "hr.period"


    @api.multi
    def _create_team_schedule_tasks_cron(self):
        company_obj = self.env['res.company'].search([('daily_report','=',True)])
        for company in company_obj:
            task_type_sr = self.env['project.task.type'].search([('name', '=', 'To Do')])
            task_complete_sr = self.env['project.task.type'].search([('name', '=', 'Complete')])
            date_next_period = datetime.now() + timedelta(days=14)
            date_now = datetime.now()
            tid_period_now = self.env['hr.period'].search([('company_id','=',company.id),('date_start', '<=', date_now),('date_stop', '>=', date_now)])
            tid_period = self.env['hr.period'].search([('company_id','=',company.id),('date_start', '<=', date_next_period),('date_stop', '>=', date_next_period)])
            if tid_period:
                if not self.env['staff.planning'].search([('name','=',tid_period.id)]):
                    print company.code
                    staff_obj=self.env['staff.planning'].create({
                                                                'name': tid_period.id,
                                                                'company_id': company.id,
                                                                'from_date': tid_period.date_start,
                                                                'to_date': tid_period.date_stop,            
                                                                })
 
                name = company.code + '-Team Schedule Report-' + str(tid_period.date_start) + ' To -' + str(tid_period.date_stop)
                project_tag_sr = self.env['project.tags'].search([('name', '=', 'Team Schedule')])
                project_sr = self.env['project.project'].search([('name', '=', 'My Practice'),('company_id', '=', company.id)])
                 
                project_obj_sr = self.env['project.task'].search([('name','=', name)])
                if project_obj_sr:
                    deadline_date = datetime.now()
                    date_start_plus_five = datetime.strptime(project_obj_sr.startdate_date[:10], '%Y-%m-%d') + timedelta(days=5)
                    date_start_plus_seven = datetime.strptime(project_obj_sr.startdate_date[:10], '%Y-%m-%d') + timedelta(days=7)
                    
                    if project_obj_sr.stage_id != task_complete_sr:
                        if deadline_date > date_start_plus_five and deadline_date <= date_start_plus_seven:
                            task_todo_sr = self.env['project.task.type'].search([('name', '=', 'Overdue < 1 Week')])
                            project_obj_sr.write({'stage_id':task_todo_sr.id})
                        elif deadline_date > date_start_plus_seven :
                            task_todo_sr = self.env['project.task.type'].search([('name', '=', 'Overdue > 1 Week')])
                            project_obj_sr.write({'stage_id':task_todo_sr.id})
                else:
                    project_obj=self.env['project.task'].create({
                                                            'name': name,
                                                            'user_id':company.manager_user_id.id,
                                                            'project_id': project_sr.id,
                                                            'date_deadline': datetime.strptime(tid_period_now.date_start, '%Y-%m-%d') + timedelta(days=4),   
                                                            'mypractice': True,                  
                                                            'tag_ids': [(6, 0, [project_tag_sr.id])],
                                                            'stage_id': task_type_sr.id,
                                                            'team_scheduler_id': staff_obj.id,
                                                            'startdate_date':tid_period_now.date_start,
                                                            'company_id': company.id,        
                                                            })

                    print project_obj,'Project id'
        task_complete_sr = self.env['project.task.type'].search([('name', '=', 'Complete')])
        team_task_obj = self.env['project.task'].search([('mypractice','=',True),('stage_id','!=',task_complete_sr.id)])
        for team_task in team_task_obj:
            if team_task.team_scheduler_id:
                if team_task.team_scheduler_id.state == 'validated':
                    team_task.write({'stage_id':task_complete_sr.id})
                    team_task.completed_date = datetime.now().date()
        return True

    @api.multi
    def action_overdue_to_complete(self):
        task_complete_sr = self.env['project.task.type'].search([('name', '=', 'Complete')])
        team_task_obj = self.env['project.task'].search([('mypractice','=',True)])
        for team_task in team_task_obj:
            if team_task.team_scheduler_id:
                if team_task.team_scheduler_id.state == 'validated':
                    team_task.write({'stage_id':task_complete_sr.id})
                    team_task.completed_date = datetime.now().date()




