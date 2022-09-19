from odoo import models, fields, api, _


class LogsScheduledActions(models.Model):
    _description = "Error log"
    _inherit = 'logs.action'


    @api.model
    def create(self, vals):
    	res = super(LogsScheduledActions, self).create(vals)
    	template_id = self.env.ref('vitalpet_cron_notification_enhancement.cron_failed_to_run').id
        mail_template = self.env['mail.template'].browse(template_id)

        if mail_template:
            mail_template.send_mail(res.id, force_send=True)

        if res:
            stage_live_id = self.env['project.task.type'].search([('name','=','Live')]).id
            stage_cancel_id = self.env['project.task.type'].search([('name','=','Cancelled')]).id
            stage_analysis_obj = self.env['project.task.type'].search([('name','=','Analysis')])
            project_task_obj = self.env['project.task'].search([('id','=',445)])
            partner_obj = self.env['res.partner'].search([('id','=',31110)])
            project_ppts_obj = self.env['project.project'].search([('id','=',136)])
            user_obj = self.env['res.users'].search([('id','=',31)])

            project_obj =  self.env['project.issue'].search([('name','=','Cron Failed - '+res.name),('partner_id','=',partner_obj.id),('project_id','=',project_ppts_obj.id),('stage_id','not in',[stage_live_id,stage_cancel_id])])
            
            if not project_obj:
                print project_obj,'--'
                project_issue_obj = self.env['project.issue'].create({
                    'name': 'Cron Failed - '+res.name,
                    'task_id' : project_task_obj.id,
                    'partner_id' : partner_obj.id,
                    'project_id' : project_ppts_obj.id,
                    'user_id' : user_obj.id,
                    'description' : res.error_details,
                    'stage_id' : stage_analysis_obj.id
                    })

        return res