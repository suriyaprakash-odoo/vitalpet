from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError
from urlparse import urljoin
import werkzeug
import base64


class HrRecruitmentStage(models.Model):
    _inherit = "hr.recruitment.stage"
    
    send_verification_mail = fields.Boolean("Send Verification Mail", default=False)
    
    
    
class HrApplicant(models.Model):
    _inherit = "hr.applicant"

    background_check_url = fields.Char(compute='_compute_background_check_url', string='Signup URL')
    btn_send_verification_mail = fields.Boolean("Send Verification Mail", related="stage_id.send_verification_mail")
    
    ssn = fields.Char('SSN original')
    ssn_encrypt = fields.Char("SSN", compute="_compute_ssn_encrypt")
    contract_type_id = fields.Many2one("hr.contract.type","Contract Type")
    
    @api.multi
    def _compute_ssn_encrypt(self):
        for applicant in self:
            if applicant.ssn:
                applicant.ssn_encrypt = base64.b64encode(applicant.ssn)
        
    
    def send_background_check_mail(self):      
        template = self.env.ref('vitalpet_onboarding.email_background_check_template')
        assert template._name == 'mail.template'
        template.send_mail(self.id, force_send=True, raise_exception=True)
            
        
    @api.multi
    def _compute_background_check_url(self):
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        for applicant in self:
            applicant.background_check_url = urljoin(base_url, "/jobs/%s/background_check" % (applicant.id))

