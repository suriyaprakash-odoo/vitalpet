from odoo import http
from odoo.http import request

class Website(http.Controller):

    @http.route('/jobs/<int:applicant>/background_check', type='http', auth="public", website=True)
    def background_check(self, applicant):
        return request.render("vitalpet_onboarding.application_encrypt", {"applicant":applicant,"message":""})
    
    
    @http.route('/background_verify_submit', type='http', auth="public", website=True, csrf=False)
    def background_verify_submit(self, **kw):
        applicant = kw.get('applicant_id')
        ssn = kw.get('ssn')
        
        hr_applicant = request.env['hr.applicant'].sudo().search([('id', '=', int(applicant))])
        
        message = "Details submited successfully"
        return request.render("vitalpet_onboarding.application_encrypt", {"applicant":applicant,"message":message})
    


        

