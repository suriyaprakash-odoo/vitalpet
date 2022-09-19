# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.http import request

from odoo.addons.website_helpdesk.controllers.main import WebsiteForm
 
    
# class WebsiteForm(WebsiteForm):
    
#     @http.route('/website_form/<string:model_name>', type='http', auth="public", methods=['POST'], website=True)
#     def website_form(self, model_name, **kwargs):
#         print kwargs,"asdasdsda"
#         if request.params.get('partner_email'):
#             Partner = request.env['res.partner'].sudo().search([('email', '=', kwargs.get('partner_email'))], limit=1)
#             if Partner:
#                 request.params['partner_id'] = Partner.id
#         if kwargs['team_id']:        
#             team_obj = request.env['helpdesk.tag'].search([('id','=',kwargs['team_id'])])
#             kwargs['user_id'] = team_obj.assinged_to.id
#             kwargs['team_id'] = team_obj.helpdesk_team.id
#             print kwargs     
#         
#         return super(WebsiteForm, self).website_form(model_name, **kwargs)