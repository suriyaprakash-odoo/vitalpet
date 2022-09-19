# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.http import request

from odoo.addons.website_helpdesk_form.controller.main import WebsiteForm
from suds import null

class WebsiteForm(WebsiteForm):

    @http.route(['/helpdesk/tags/stringchar'], type='http', auth="public", website=True)
    def website_helpdesk_tags(self, stringchar=null, **kwargs):
        print id
        if id:
            return "Yes"
        else:
            return "No"
        
    @http.route(['/helpdesk/', '/helpdesk/<model("helpdesk.team"):team>'], type='http', auth="public", website=True)
    def website_helpdesk_teams(self, team=None, **kwargs):
        search = kwargs.get('search')
        # For breadcrumb index: get all team
        teams = request.env['helpdesk.team'].sudo().search(['|', '|', ('use_website_helpdesk_form', '=', True), ('use_website_helpdesk_forum', '=', True), ('use_website_helpdesk_slides', '=', True)], order="id asc")
        if not request.env.user.has_group('helpdesk.group_helpdesk_manager'):
            teams = teams.filtered(lambda team: team.website_published)
        if not teams:
            return request.render("website_helpdesk.not_published_any_team")
        result = self.get_helpdesk_team_data(team or teams[0], search=search)
        # For breadcrumb index: get all team
        result['teams'] = teams
        return request.render("website_helpdesk.team", result)

    @http.route('''/helpdesk/<model("helpdesk.team", "[('use_website_helpdesk_form','=',True)]"):team>/submit''', type='http', auth="public", website=True)
    def website_helpdesk_form(self, team, **kwargs):
        default_values = {}
        stage = request.env['helpdesk.tag'].sudo().search([('helpdesk_team','=',team.id)])
        if request.env.user.partner_id != request.env.ref('base.public_partner'):
            default_values['name'] = request.env.user.partner_id.name
            default_values['email'] = request.env.user.partner_id.email
                                 
        return request.render("website_helpdesk_form.ticket_submit", {'team': team, 'default_values': default_values,'stage':stage})
    
    
    @http.route(['/my/tickets'], type='http', auth="user", website=True)
    def my_helpdesk_tickets(self, **kw):
        
        partner = request.env.user.partner_id
        # get customer sales rep
        if partner.user_id:
            sales_rep = partner.user_id
        else:
            sales_rep = False
        values = {
            'sales_rep': sales_rep,
            'company': request.website.company_id,
            'user': request.env.user
        }
    
        user = request.env.user
        tickets = request.env['helpdesk.ticket'].sudo().search([('partner_email', '=', user.login)])
        values.update({
            'tickets': tickets,
            'default_url': '/my/tickets',
        })
        return request.render("website_helpdesk.portal_helpdesk_ticket", values)
    