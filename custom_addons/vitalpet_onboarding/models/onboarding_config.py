from odoo import api, fields, models

class OnboardingDefaultService(models.Model):
    _name = 'onboarding.default.service'

    name = fields.Char()

class ResCompany(models.Model):
    _inherit = 'res.company'
    
    
    hr_supervisor = fields.Many2one('res.users')
    handbook_template = fields.Many2one('signature.request.template')
    handbook_file = fields.Binary('Handbook File')
    benefits_survey = fields.Many2one('survey.survey')
    inc_detailed_job_desc = fields.Boolean()
    benefits_enrollment_delay = fields.Integer()
    eligible_for_benefits = fields.Many2one('hr.contract.type')
    benefits_eligibility_desc = fields.Text()
    
    provider = fields.Many2one('res.partner')
    acc_number = fields.Char()
    user_name = fields.Char()
    password = fields.Char()
    return_url = fields.Char()
    default_service = fields.Many2many('background.config')
    total_cost = fields.Integer()
    
    onboarding_processing_company = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id)

class OnboardingConfigSettings(models.TransientModel):
    _name = 'onboarding.config.settings'
    _inherit = 'res.config.settings'
    
    onboarding_processing_company = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id)
    
    hiring_manager = fields.Many2one('res.users',string="Manager",related='onboarding_processing_company.manager_user_id')
    hr_supervisor = fields.Many2one('res.users',string="HR Supervisor",related='onboarding_processing_company.hr_supervisor')
    payroll_manager = fields.Many2one('res.users',string="Payroll Manager",related='onboarding_processing_company.payroll_manager_id')
    handbook_template = fields.Many2one('signature.request.template',string="Handbook Template",related='onboarding_processing_company.handbook_template')
    handbook_file = fields.Binary(string="Handbook File",related='onboarding_processing_company.handbook_file')
    benefits_survey = fields.Many2one('survey.survey',"Benefits Survey",related='onboarding_processing_company.benefits_survey')
    inc_detailed_job_desc = fields.Boolean("Include Detailed Job Description",related='onboarding_processing_company.inc_detailed_job_desc')
    benefits_enrollment_delay = fields.Integer("Benefits Enrollment Delay",related='onboarding_processing_company.benefits_enrollment_delay')
    eligible_for_benefits = fields.Many2one('hr.contract.type',string="Eligibile for Benefits",related='onboarding_processing_company.eligible_for_benefits')
    benefits_eligibility_desc = fields.Text("Benefits Eligibility Description",related='onboarding_processing_company.benefits_eligibility_desc')
    

    provider = fields.Many2one('res.partner',string="Provider",related='onboarding_processing_company.provider')
    acc_number = fields.Char("Account Number",related='onboarding_processing_company.acc_number')
    user_name = fields.Char("Username",related='onboarding_processing_company.user_name')
    password = fields.Char("Password",related='onboarding_processing_company.password')
    return_url = fields.Char("Return URL",related='onboarding_processing_company.return_url')
    default_service = fields.Many2many('background.config',string="Default Services",related='onboarding_processing_company.default_service')
    total_cost = fields.Integer("Total Cost on Selected Services",related='onboarding_processing_company.total_cost')
    
    
    @api.onchange('provider')
    def _onchange_default_services(self):
        service_obj = self.env['background.check.settings'].search([('name' , '=' , self.provider.id)])

        if service_obj:
            service_list= []
            if self.provider!=self.onboarding_processing_company.provider:
                for service in service_obj.background_config_ids:
                    if service.default:
                        service_list.append(service.id)

                self.default_service = service_list