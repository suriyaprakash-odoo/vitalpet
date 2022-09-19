/*global $, _, PDFJS */
odoo.define('vitalpet_bill_pay.vitalpet_bill_pay_dashboard', function (require) {
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
    template: "vitalpet_bill_pay.HomePage",
	searchview_hidden: true,
    //Dashboard cleck events
    events: {
        'click .o_dashboard_action'	: 	'on_dashboard_action_clicked',
		'click .add_new_vendor'		:	'on_add_new_vendor_clicked'
    },


    init: function(parent, context) {
        this._super(parent, context);
        this.dashboards_templates = ['vitalpet_bill_pay.dashboard_bills'];
    },
    start: function() {
        var self = this;
        return this._super().then(function() {
        	self.update_cp();
            self.render_dashboards();
            self.$el.parent().addClass('oe_background_grey');
        });
    },
    
    on_reverse_breadcrumb: function() {
        web_client.do_push_state({});
        this.update_cp();
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
// Click events
    on_dashboard_action_clicked: function(ev){
        ev.preventDefault();
        var $action = $(ev.currentTarget);
        var action_name = $action.attr('name');
        var action_id = $action.attr('id');
        var action_extra = $action.data('extra');
        var additional_context = {};
        // TODO: find a better way to add defaults to search view
        if (action_id === 'today')  {
            additional_context.search_default_today = 1;
        }
        if (action_id === 'overdue')  {
            additional_context.search_default_overdue = 1;
        } 
        if (action_id === 'overdue_30days')  {
            additional_context.search_default_overdue_30days = 1;
        }
        if (action_id === 'overdue_60days')  {
            additional_context.search_default_overdue_60days = 1;
        } 
        if (action_id === 'overdue_90days')  {
            additional_context.search_default_overdue_90days = 1;
        }
		if (action_id === 'manual_payment')  {
            additional_context.search_default_manual_payment = 1;
        }
		if (action_id === 'ach')  {
            additional_context.search_default_ach = 1;
        }
		if (action_id === 'no_activity_12_month')  {
            additional_context.search_default_no_activity_12_month = 1;
        }
		if (action_id === 'billpayintercompany')  {
            additional_context.search_default_billpayintercompany = 1;
        }
		if (action_id === 'echeck')  {
            additional_context.search_default_echeck = 1;
        }
        

        this.do_action(action_name, {additional_context: additional_context});
    },

	on_add_new_vendor_clicked : function(ev) {
		web_client.action_manager.do_action({
			views: [[false, 'form']],
            view_type: 'form',
            view_mode: 'form',
            res_model: 'res.partner',
            context:{default_supplier:'True'},
            type: 'ir.actions.act_window',
            target: 'current',
		});
	},
    // fetch_dashboard_data will contains all data related to dashboard
    render_dashboards: function() {
	    var self = this;
	        _.each(this.dashboards_templates, function(template) {
	        	 new Model('billpay.dashboard').call('fetch_dashboard_data', []).then(function(result){
		      		  self.$('.o_website_dashboard').append(QWeb.render(template, {widget: self,values: result,}));
		      	  });
	        	
	        });
	    }
});
    core.action_registry.add('vitalpet_bill_pay_dashboard', Dashboard);
    return Dashboard;
});

