/*global $, _, PDFJS */
odoo.define('vitalpet_onboarding.vitalpet_onboarding', function (require) {
"use strict";

var ajax = require('web.ajax');
var ControlPanelMixin = require('web.ControlPanelMixin');
var core = require('web.core');
var Dialog = require('web.Dialog');
var Model = require('web.Model');
var session = require('web.session');
var utils = require('web.utils');
var web_client = require('web.web_client');
var Widget = require('web.Widget');
var NotificationManager = require('web.notification').NotificationManager;

var _t = core._t;
var QWeb = core.qweb;


var Dashboard = Widget.extend(ControlPanelMixin, {
    template: "vitalpet_onboarding.HomePage",


    events: {
        'click .applicant_link': 'on_dashboard_applicant_clicked',
        'click .contract_link': 'on_dashboard_contract_clicked',
        'click .contract_link_draft': 'on_dashboard_contract_draft_clicked',
        'click .contract_link_active': 'on_dashboard_contract_active_clicked',
        'click .contract_link_torenew': 'on_dashboard_contract_torenew_clicked',
        'click .contract_link_expired': 'on_dashboard_contract_expired_clicked',
    },


    init: function(parent, context) {
        this._super(parent, context);
        this.dashboards_templates = ['vitalpet_onboarding.dashboard_visits'];
    },
    start: function() {
        var self = this;
        return this._super().then(function() {
        	self.update_cp();
            self.render_dashboards();
            self.$el.parent().addClass('oe_background_grey');
        });
    },
    

  //To update breadcrumbs
    update_cp: function() {
        var self = this;
        
        this.update_control_panel({
            cp_content: {
                $searchview: this.$searchview,
            },
            breadcrumbs: this.getParent().get_breadcrumbs(),
        });
    },

    on_dashboard_applicant_clicked: function(ev){
        // alert(  $(ev.currentTarget).attr("test_id") );
        window.open($(".applicant_link").attr("test")+"&active_id="+ $(ev.currentTarget).attr("test_id") ,'_blank');
    },

    on_dashboard_contract_clicked: function(ev){
        var job = $(ev.currentTarget).attr("test_id");
        web_client.action_manager.do_action({
            views: [[false, 'list']],
            view_type: 'tree',
            view_mode: 'tree,form',
            res_model: 'hr.contract',
            domain:  [['job_id', '=', parseInt(job)]],
            type: 'ir.actions.act_window',
            target: 'current',
        });
    },

    on_dashboard_contract_draft_clicked: function(ev){
        var job = $(ev.currentTarget).attr("test_id");
        web_client.action_manager.do_action({
            views: [[false, 'list']],
            view_type: 'tree',
            view_mode: 'tree,form',
            res_model: 'hr.contract',
            domain:  [['job_id', '=', parseInt(job)]],
            context :{
                'search_default_grp_draft':'True',
            },
            type: 'ir.actions.act_window',
            target: 'current',
        });
    },

    on_dashboard_contract_active_clicked: function(ev){
        var job = $(ev.currentTarget).attr("test_id");
        web_client.action_manager.do_action({
            views: [[false, 'list']],
            view_type: 'tree',
            view_mode: 'tree,form',
            res_model: 'hr.contract',
            domain:  [['job_id', '=', parseInt(job)]],
            context :{
                'search_default_grp_running':'True',
            },
            type: 'ir.actions.act_window',
            target: 'current',
        });
    },

    on_dashboard_contract_torenew_clicked: function(ev){
        var job = $(ev.currentTarget).attr("test_id");
        web_client.action_manager.do_action({
            views: [[false, 'list']],
            view_type: 'tree',
            view_mode: 'tree,form',
            res_model: 'hr.contract',
            domain:  [['job_id', '=', parseInt(job)]],
            context :{
                'search_default_grp_renew':'True',
            },
            type: 'ir.actions.act_window',
            target: 'current',
        });
    },

    on_dashboard_contract_expired_clicked: function(ev){
        var job = $(ev.currentTarget).attr("test_id");
        web_client.action_manager.do_action({
            views: [[false, 'list']],
            view_type: 'tree',
            view_mode: 'tree,form',
            res_model: 'hr.contract',
            domain:  [['job_id', '=', parseInt(job)]],
            context :{
                'search_default_grp_expire':'True',
            },
            type: 'ir.actions.act_window',
            target: 'current',
        });
    },
   
    render_dashboards: function() {
	    var self = this;
	        _.each(this.dashboards_templates, function(template) {
	        	  new Model('onboard.dashboard').call('retrieve_onboard_dashboard', []).then(function(result){
	        		  self.$('.o_website_onboard_dashboard').append(QWeb.render(template, {widget: self,values: result,}));
	        	  });
	        });
	    }
});
    core.action_registry.add('onboarding_dashboard', Dashboard);
    return Dashboard;
});
