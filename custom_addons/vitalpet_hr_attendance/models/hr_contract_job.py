from odoo import api, fields, models
from odoo.exceptions import UserError
class HrContractJob(models.Model):
    """Contract Job"""

    _inherit = 'hr.contract.job'
    seniority_id = fields.Many2one('hr.job.seniority.title',string="Job Seniority Title", required=True)
    seniority_ids = fields.Many2many('hr.job.seniority.title',string="Job Seniority Title",compute="get_job_seniority_title")
    
    @api.depends('job_id')
    def get_job_seniority_title(self):
        for job in self:
            if job.job_id and job.job_id.job_template.job_seniority_id:
                job.seniority_ids = [(6, 0, job.job_id.job_template.job_seniority_id.ids)]

    @api.onchange('job_id')
    def onchange_get_job_seniority_title(self):
        for job in self:
            seniority_id = False
            res = {'domain': {
            'seniority_id': "[('id', '=', False)]",
            }}
            if job.job_id and job.job_id.job_template.job_seniority_id:
                jrl_ids = job.job_id.job_template.job_seniority_id.ids
                res['domain']['seniority_id'] = "[('id', 'in', %s)]" % jrl_ids
            job.seniority_id = seniority_id
        return res
                



class Contract(models.Model):

    _inherit = 'hr.contract'
    _description = 'Contract'


    date_end = fields.Date('End Date', required=True)
    contract_renewal_due_soon = fields.Boolean(compute='_compute_contract_reminder', string='Has Contracts to renew', multi='contract_info')
    contract_renewal_overdue = fields.Boolean(compute='_compute_contract_reminder', string='Has Contracts Overdue', multi='contract_info')

    def _compute_contract_reminder(self):
        for record in self:
            overdue = False
            due_soon = False
            for element in record:
                if element.date_end:
                    current_date_str = fields.Date.context_today(record)
                    due_time_str = element.date_end
                    current_date = fields.Date.from_string(current_date_str)
                    due_time = fields.Date.from_string(due_time_str)
                    diff_time = (due_time - current_date).days
                    if diff_time < 0:
                        overdue = True
                        element.state = 'close'
                    if diff_time < 15 and diff_time >= 0:
                        due_soon = True
                        element.state = 'pending'
            record.contract_renewal_overdue = overdue
            record.contract_renewal_due_soon = due_soon


            
            
            
            
            