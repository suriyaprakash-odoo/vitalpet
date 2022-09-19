# -*- coding: utf-8 -*-

import datetime
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, tools, SUPERUSER_ID


class OnboardingeDashboard(models.Model):
    _name = 'onboard.dashboard'

    @api.model
    def retrieve_onboard_dashboard(self):
        result = {}
        
        result['recruitment'] = []
        result['contract'] = []
        
        job_obj = self.env['hr.job'].search([('company_id', 'child_of', [self.env.user.company_id.id])])
        for line_job in job_obj:
            job = {}
            job['name'] = line_job.name
            if line_job.state == 'recruit':
                job['status'] = 'Yes'
            else:
                job['status'] = 'No'
            job['applicant'] = len(self.env['hr.applicant'].search([('job_id', '=', line_job.id)])) or 0
            save_later_sr = self.env['hr.recruitment.stage'].search([('name', '=', 'Save for Later')])
            job['later'] = len(self.env['hr.applicant'].search([('job_id', '=', line_job.id), ('stage_id', '=', save_later_sr.id)])) or 0
            job['active_id'] = line_job.id

            result['recruitment'].append(job)
            
            job_contract = {}
            job_contract['name'] = line_job.name
            job_contract['draft'] = len(self.env['hr.contract.job'].search([('job_id', '=', line_job.id), ('contract_id.state', '=', 'draft')])) or 0
            job_contract['open'] = len(self.env['hr.contract.job'].search([('job_id', '=', line_job.id), ('contract_id.state', '=', 'open')])) or 0
            job_contract['pending'] = len(self.env['hr.contract.job'].search([('job_id', '=', line_job.id), ('contract_id.state', '=', 'pending')])) or 0
            job_contract['close'] = len(self.env['hr.contract.job'].search([('job_id', '=', line_job.id), ('contract_id.state', '=', 'close')])) or 0
            job_contract['active_id'] = line_job.id
            
            result['contract'].append(job_contract)
        
        result['hiring'] = {}
        
        offer_state = self.env['hr.employee.onboarding'].search([('state_id', '=', 'offer')])
        result['hiring']['offer'] = len(offer_state)
        
        background_state = self.env['hr.employee.onboarding'].search([('state_id', '=', 'background')])
        result['hiring']['background'] = len(background_state)
        
        to_approve_state = self.env['hr.employee.onboarding'].search([('state_id', '=', 'to_approve')])
        result['hiring']['to_approve'] = len(to_approve_state)
        
        hire_state = self.env['hr.employee.onboarding'].search([('state_id', '=', 'hire')])
        result['hiring']['hire'] = len(hire_state)
        
        benefits_state = self.env['hr.employee.onboarding'].search([('state_id', '=', 'benefits')])
        result['hiring']['benefits'] = len(benefits_state)
        
        contract_state = self.env['hr.employee.onboarding'].search([('state_id', '=', 'contract')])
        result['hiring']['contract'] = len(contract_state)
        
        complete_state = self.env['hr.employee.onboarding'].search([('state_id', '=', 'complete')])
        result['hiring']['complete'] = len(complete_state)
        
        result['benefits'] = {}
        
        not_eligible = self.env['hr.employee.onboarding'].search([('benefits_states', '=', 'not_eligible')])
        result['benefits']['not_eligible'] = len(not_eligible)
        pending_election = self.env['hr.employee.onboarding'].search([('benefits_states', '=', 'pending')])
        result['benefits']['pending_election'] = len(pending_election)
        to_approve = self.env['hr.employee.onboarding'].search([('benefits_states', '=', 'to_approve')])
        result['benefits']['to_approve'] = len(to_approve)
        send_to_provider = self.env['hr.employee.onboarding'].search([('benefits_states', '=', 'send')])
        result['benefits']['send_to_provider'] = len(send_to_provider)
        enrolled = self.env['hr.employee.onboarding'].search([('benefits_states', '=', 'enrolled')])
        result['benefits']['enrolled'] = len(enrolled)
        
        return result
