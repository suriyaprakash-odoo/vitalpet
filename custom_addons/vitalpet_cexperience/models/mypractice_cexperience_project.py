from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime,timedelta

class ProjectTask(models.Model):
    _inherit = "project.task"

    current_period_id = fields.Many2one('hr.period', 'Current Period')


class HrPeriod(models.Model):
    _inherit = "hr.period"

    @api.multi
    def _create_client_experience_tasks_cron(self):
    	company_obj = self.env['res.company'].search([('daily_report','=',True)])

    	for company in company_obj:
            ref = company.code+'-'+'Veterinarian'
            veterinarian_rec_obj = self.env['hr.employee'].search_count([('job_id','=',ref),('company_id', '=', company.id)])
            
            task_type_sr = self.env['project.task.type'].search([('name', '=', 'To Do')])
            task_complete_sr = self.env['project.task.type'].search([('name', '=', 'Complete')])
            date_next_period = datetime.now() + timedelta(days=14)
            date_now = datetime.now()
            tid_period_now = self.env['hr.period'].search([('company_id','=',company.id),('date_start', '<=', date_now),('date_stop', '>=', date_now)])
            tid_period = self.env['hr.period'].search([('company_id','=',company.id),('date_start', '<=', date_next_period),('date_stop', '>=', date_next_period)])

            name = company.code + '-Visit Review Report-' + str(tid_period.date_start) + ' To -' + str(tid_period.date_stop)
            project_tag_sr = self.env['project.tags'].search([('name', '=', 'Visit')])
            project_sr = self.env['project.project'].search([('name', '=', 'My Practice'),('company_id', '=', company.id)])

            project_obj_sr = self.env['project.task'].search([('name','=', name)])
            if project_obj_sr:
                for record in project_obj_sr:
                    deadline_date = datetime.now()
                    date_start_plus_five = datetime.strptime(record.startdate_date[:10], '%Y-%m-%d') + timedelta(days=5)
                    date_start_plus_seven = datetime.strptime(record.startdate_date[:10], '%Y-%m-%d') + timedelta(days=7)
                    
                    if record.stage_id != task_complete_sr:
                        if deadline_date > date_start_plus_five and deadline_date <= date_start_plus_seven:
                            task_todo_sr = self.env['project.task.type'].search([('name', '=', 'Overdue < 1 Week')])
                            record.write({'stage_id':task_todo_sr.id})
                        elif deadline_date > date_start_plus_seven :
                            task_todo_sr = self.env['project.task.type'].search([('name', '=', 'Overdue > 1 Week')])
                            record.write({'stage_id':task_todo_sr.id})
            else:
                if company.tasks_per_week > 0:
                    task_count = company.tasks_per_week * veterinarian_rec_obj
                    print task_count
                    for rec in range(task_count):
                        project_obj=self.env['project.task'].create({
                                                                'name': name,
                                                                'user_id':company.manager_user_id.id,
                                                                'project_id': project_sr.id,
                                                                'date_deadline': datetime.strptime(tid_period_now.date_start, '%Y-%m-%d') + timedelta(days=4),   
                                                                'mypractice': True,                  
                                                                'tag_ids': [(6, 0, [project_tag_sr.id])],
                                                                'stage_id': task_type_sr.id,
                                                                'current_period_id': tid_period_now.id,
                                                                'startdate_date':tid_period_now.date_start,
                                                                'company_id': company.id,        
                                                                })
        # self.action_visit_review_overdue_to_complete()

        return True

    @api.multi
    def action_visit_review_overdue_to_complete(self):
        task_complete_sr = self.env['project.task.type'].search([('name', '=', 'Complete')])
        team_task_obj = self.env['project.task'].search([('mypractice','=',True)])
        for team_task in team_task_obj:
            ref = team_task.company_id.code+'-'+'Veterinarian'
            veterinarian_rec_obj = self.env['hr.employee'].search_count([('job_id','=',ref),('company_id', '=', team_task.company_id.id)])
            total_task = team_task.company_id.tasks_per_week * veterinarian_rec_obj
            if team_task.current_period_id:
                visit_obj = self.env['experience.visit'].search_count([('company_id','=',team_task.company_id.id),('visit_date','<=',team_task.current_period_id.date_start),('visit_date','>=',team_task.current_period_id.date_stop)])
                if visit_obj >= total_task:
                    team_task.write({'stage_id':task_complete_sr.id})
                    team_task.completed_date = datetime.now().date()

                
                