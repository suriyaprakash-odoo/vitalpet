/*global $, _, PDFJS */
odoo.define('vitalpet_mypractice.vitalpet_mypractice', function (require) {
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
    template: "vitalpet_mypractice.HomePage",


    events: {
        'click .o_dashboard_action': 'on_dashboard_action_clicked',
        'click .o_dashboard_action_open': 'on_dashboard_action_clicked_open',
        
    },

    init: function(parent, context) {
        this._super(parent, context);
        this.dashboards_templates = ['vitalpet_mypractice.dashboard_visits'];
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

    on_dashboard_action_clicked: function(ev){
        ev.preventDefault();
        var $action = $(ev.currentTarget);
        var action_name = $action.attr('name');
        var action_id = $action.attr('id');
        var action_extra = $action.data('extra');
        var additional_context = {};
        // TODO: find a better way to add defaults to search view
        if (action_name === 'vitalpet_mypractice.action_calendar_event_today' && action_id === 'today')  {
            console.log('Today');
            additional_context.search_default_mymeetings = 1;
        } 
        else if(action_name === 'vitalpet_mypractice.action_calendar_event_next2week' && action_id === 'nextweek')  {
            console.log('nextweek');
            additional_context.search_default_mymeetings = 1;
        }
        else if (action_name === 'vitalpet_mypractice.open_view_mypractice_todo_task_all' && action_id === 'today') {
            additional_context.search_default_today = 1;
           }
        else if (action_name === 'vitalpet_mypractice.open_view_mypractice_todo_task_all' && action_id === 'next2week') {
            additional_context.search_default_next2week = 1;
           }
        else if (action_name === 'vitalpet_mypractice.open_view_mypractice_todo_task_all' && action_id === 'overdue') {
            additional_context.search_default_overdue = 1;
           }

        else if (action_name === 'hr_holidays.act_hr_employee_holiday_request') {
            additional_context.search_default_approve = 1; 
        }
        else if (action_name === 'vitalpet_mypractice.mypractice_action_hr_contract' && action_id === 'running'){
            additional_context.search_default_grp_running = 1; 
        }
        else if (action_name === 'vitalpet_mypractice.mypractice_action_hr_contract_renew' && action_id === 'renew'){
            additional_context.search_default_grp_renew = 1; 
        }
        else if (action_name === 'vitalpet_mypractice.mypractice_action_hr_contract_draft' && action_id === 'draft'){
            additional_context.search_default_grp_draft= 1; 
        }
        else if (action_name === 'vitalpet_mypractice.mypractice_action_expense_refuse' && action_id === 'refuse'){
            additional_context.search_default_refuse = 1; 
        }
        else if (action_name === 'vitalpet_mypractice.mypractice_action_custom_expire' && action_id === 'custom_over_due'){
            additional_context.search_default_grp_custom_over_due = 1; 
        }
        else if (action_name === 'vitalpet_mypractice.mypractice_action_hr_applicant_offer'){
            additional_context.search_default_offer_letter = 1; 
        }
        else if (action_name === 'vitalpet_mypractice.mypractice_action_hr_applicant_interview'){
            additional_context.search_default_interview = 1; 
        }
        else if (action_name === 'vitalpet_mypractice_dashboard.mypractice_action_hr_onboarding_today_filter_inherit'){
            additional_context.search_default_onboarding_today = 1; 
        }
        else if (action_name === 'vitalpet_mypractice_dashboard.mypractice_action_hr_onboarding_open_filter_inherit'){
            additional_context.search_default_onboarding_open = 1; 
        }
        else if (action_name === 'vitalpet_mypractice_dashboard.mypractice_action_hr_onboarding_to_onboard_filter_inherit'){
            additional_context.search_default_to_onboard = 1; 
        }
        else if (action_name === 'vitalpet_payroll_inputs.hr_payroll_inputs_action_menu' && action_id === 'pending'){
        	additional_context.search_default_pending = 1;
        	additional_context.search_default_open = 0;
        }
        else if (action_name === 'vitalpet_payroll_inputs.hr_payroll_inputs_action_menu' && action_id === 'today'){
        	additional_context.search_default_today = 1;
        	additional_context.search_default_open = 0;
        }
        else if (action_name === 'vitalpet_payroll_inputs.hr_payroll_inputs_action_menu' && action_id === 'overdue_pending'){
        	additional_context.search_default_overdue_pending = 1;
        	additional_context.search_default_open = 0;
        }
        /*else if (action_name === 'vitalpet_mypractice.hr_attendance_mypractice_action' && action_id === 'today_chkout'){
            additional_context.search_default_grp_expire = 1; 
        }*/
        this.do_action(action_name, {additional_context: additional_context});
    },


  //   on_dashboard_action_clicked_open: function(ev){
  //       // var onboard_obj = $(ev.currentTarget).attr("test_id");
  //       var job = new Model('mypractice.dashboard');
  //       job.call('onboarding_open_request', [[1]])
		// .then(function(onboarding_open_list) {
	 //        web_client.action_manager.do_action({
	 //            views: [[false, 'list']],
	 //            view_type: 'tree',
	 //            view_mode: 'tree,form',
	 //            res_model: 'hr.employee.onboarding',
	 //            domain:  [['id', 'in', onboarding_open_list]],
	 //            type: 'ir.actions.act_window',
	 //            target: 'current',
	 //        });
		// });
  //   },
    
    render_dashboards: function() {
	    var self = this;
	        _.each(this.dashboards_templates, function(template) {
	        	  new Model('mypractice.dashboard').call('retrieve_sales_dashboard', []).then(function(result){
	        		  self.$('.o_website_dashboard').append(QWeb.render(template, {widget: self,values: result,}));
	        	  });
	        });
	    }
});
    core.action_registry.add('mypractice_dashboard', Dashboard);
    return Dashboard;
});

