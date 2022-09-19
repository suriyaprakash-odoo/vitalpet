# -*- coding: utf-8 -*-

from odoo import http, fields, _
from odoo.addons.website.models.website import slug, unslug
from odoo.http import request
from odoo.addons.vitalpet_custom_hr_recruitment.controllers.main import WebsiteHrRecruitment


class WebsiteJob(WebsiteHrRecruitment):
    

    @http.route(['/jobs/detail/<model("hr.job"):job>','/jobs/detail/<model("hr.job"):job>/<string:city>'], type='http', auth="public", website=True)
    def jobs_detail(self, job, city='', **kwargs):
        print city
        request.session['redirect_page'] = 'redirect' in kwargs and kwargs.get('redirect') or False
        
        over_write_city = request.env['over_write.city'].sudo().search([('job_temp_id', '=', job.id), ('city_wizard', '=', city)])
        
        return request.render("website_hr_recruitment.detail", {
            'job': job.sudo(),
            'main_object': job.sudo(),
            'redirect': 'redirect' in kwargs and kwargs.get('redirect') or False,
            'over_write_city':over_write_city or False
        })
        
       

    
    @http.route('/jobs/continue', type='http', auth="public", website=True)
    def jobs_continue(self, **kwargs):
        request.session.pop('redirect_page')
        return request.redirect("/")
