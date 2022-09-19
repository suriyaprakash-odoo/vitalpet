/*global $, _, PDFJS */
odoo.define('vitalpet_payroll_inputs.action_payroll_validation', function (require) {
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
    template: "vitalpet_payroll_inputs.ValidationHomePage",
	searchview_hidden: true,
    //Dashboard cleck events
    events: {
        'click .production_previous': 'on_production_previous_clicked',
        'click .production_next': 'on_production_next_clicked',
        'click .employee_previous': 'on_employee_previous_clicked',
        'click .employee_next': 'on_employee_next_clicked',
        'click .production_weeks': 'on_production_weeks_clicked',
        'change .payroll_period': 'on_payroll_period_changed',
        'change .filter_production': 'on_filter_production_changed',
        'change .bonus_amount': 'on_bonus_amount_changed',
    },


    init: function(parent, context) {
        this._super(parent, context);
        this.dashboards_templates = ['vitalpet_payroll_inputs.ValidationPage'];
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

//    //To update breadcrumbs
    update_cp: function() {
        var self = this;

        this.update_control_panel({
            cp_content: {
                $searchview: this.$searchview,
            },
            breadcrumbs: this.getParent().get_breadcrumbs(),
        });
    },

    on_bonus_amount_changed: function(ev) {
    	var action = $(ev.target);
    	var amount = action.val();
    	var job_id = action.attr('data-job_id');
    	var period_id = $('.payroll_period').val();
    	var bonus_id = action.attr('data-bonus_id');
    	var bonus_date = action.attr('data-date');
    	var employee_id = action.attr('data-employee_id');
    	new Model('hr.production').call('validate_bonus_amount', [amount,period_id,employee_id,job_id,bonus_id,bonus_date]).then(function(result){
    		console.log(result);
    	});
    },

    on_production_previous_clicked: function(ev){
        var additional_context = {};
        additional_context.filter_production = $('.filter_production').val();
        additional_context.period_id = $('.payroll_period').val();
        var week_type = $(".production_weeks.active").attr("data-name");
        additional_context.week_type = week_type
        var week_no = $('.week_no').val();
        if(week_type === 'week') {
        	if(week_no == 1) {
        		week_no = 2
        	}
        	else {
        		week_no = 1
        	}
        }
        additional_context.week_no = week_no
        if(week_no == 2 || week_type == 'two_weeks') {
        	var data_id=$(".payroll_period option[value='"+$('.payroll_period').val()+"']").attr("data_id");
            var previous_id=parseInt(data_id)-1;
            var previous_value = $(".payroll_period option[data_id='"+previous_id+"']").attr("value");
            additional_context.period_id = previous_value;
            $('.payroll_period').val(previous_value);
            if (typeof previous_value === "undefined") {
            	var previous_id=$(".payroll_period option:last").attr("data_id");
            	var previous_value = $(".payroll_period option[data_id='"+previous_id+"']").attr("value");
                additional_context.period_id = previous_value;
                $('.payroll_period').val(previous_value);
            }
        }

        additional_context.employee_number = $('.employee_number').text();
        additional_context.current_employee = $('.current_employee').val();

        _.each(this.dashboards_templates, function(template) {
       	 new Model('vitalpet.payroll.inputs.validation').call('fetch_validation_data', [additional_context]).then(function(result){
	      		 self.$('.o_website_dashboard').html('');

	      		 self.$('.o_website_dashboard').append(QWeb.render(template, {widget: self,values: result,}));

	      	  });

       });
    },

    on_production_next_clicked: function(ev){
    	var additional_context = {};
        additional_context.filter_production = $('.filter_production').val();
        additional_context.period_id = $('.payroll_period').val();
        var week_type = $(".production_weeks.active").attr("data-name");
        additional_context.week_type = week_type
        var week_no = $('.week_no').val();
        if(week_type === 'week') {
        	if(week_no == 2) {
        		week_no = 1
        	}
        	else {
        		week_no = 2
        	}
        }
        additional_context.week_no = week_no
        if(week_no == 1 || week_type == 'two_weeks') {
        	var data_id=$(".payroll_period option[value='"+$('.payroll_period').val()+"']").attr("data_id");
            var next_id=parseInt(data_id)+1;
            var next_value = $(".payroll_period option[data_id='"+next_id+"']").attr("value");
            additional_context.period_id = next_value;
            $('.payroll_period').val(next_value);
            if (typeof next_value === "undefined") {
            	var next_id=$(".payroll_period option:last").attr("data_id");
            	var next_value = $(".payroll_period option[data_id='"+next_id+"']").attr("value");
                additional_context.period_id = next_value;
                $('.payroll_period').val(next_value);
            }
        }
        additional_context.employee_number = $('.employee_number').text();
        additional_context.current_employee = $('.current_employee').val();


        _.each(this.dashboards_templates, function(template) {
       	 new Model('vitalpet.payroll.inputs.validation').call('fetch_validation_data', [additional_context]).then(function(result){
	      		 self.$('.o_website_dashboard').html('');

	      		 self.$('.o_website_dashboard').append(QWeb.render(template, {widget: self,values: result,}));

	      	  });

       });
    },

    on_employee_previous_clicked: function(ev){
        var additional_context = {};
        additional_context.period_id = $('.payroll_period').val();
        additional_context.filter_production = $('.filter_production').val();
        var data_id=$(".current_employee option[value='"+$('.current_employee').val()+"']").attr("data_id");
        var previous_id=parseInt(data_id)-1;
        var employee_number = parseInt(data_id)-1;
        var previous_value = $(".current_employee option[data_id='"+previous_id+"']").attr("value");
        if (typeof previous_value === "undefined") {

        	var previous_id=$(".current_employee option:last").attr("data_id");
        	var employee_number = previous_id;
        	var previous_value = $(".current_employee option[data_id='"+previous_id+"']").attr("value");
        }


        additional_context.employee_number = employee_number;
        additional_context.current_employee = previous_value;
        $('.employee_number').text(employee_number);
        $('.filter_employee_id').val(previous_value);
        _.each(this.dashboards_templates, function(template) {
       	 new Model('vitalpet.payroll.inputs.validation').call('fetch_validation_data', [additional_context]).then(function(result){
	      		 self.$('.o_website_dashboard').html('');

	      		 self.$('.o_website_dashboard').append(QWeb.render(template, {widget: self,values: result,}));

	      	  });

       });
    },

    on_employee_next_clicked: function(ev){
    	var additional_context = {};
        additional_context.period_id = $('.payroll_period').val();
        additional_context.filter_production = $('.filter_production').val();
        var data_id=$(".current_employee option[value='"+$('.current_employee').val()+"']").attr("data_id");
        var next_id=parseInt(data_id)+1;
        var employee_number = parseInt(data_id)+1;
        var next_value = $(".current_employee option[data_id='"+next_id+"']").attr("value");
        if (typeof next_value === "undefined") {

        	var next_id=$(".current_employee option:first").attr("data_id");
        	var employee_number = next_id;
        	var next_value = $(".current_employee option[data_id='"+next_id+"']").attr("value");
        }


        additional_context.employee_number = employee_number;
        additional_context.current_employee = next_value;
        $('.employee_number').text(employee_number);
        $('.filter_employee_id').val(next_value);
        _.each(this.dashboards_templates, function(template) {
       	 new Model('vitalpet.payroll.inputs.validation').call('fetch_validation_data', [additional_context]).then(function(result){
	      		 self.$('.o_website_dashboard').html('');

	      		 self.$('.o_website_dashboard').append(QWeb.render(template, {widget: self,values: result,}));

	      	  });

       });
    },

    on_production_weeks_clicked : function(ev) {
    	var additional_context = {};
        additional_context.period_id = $('.payroll_period').val();
        additional_context.filter_production = $('.filter_production').val();
        var action = $(ev.target);
        var week_type = action.attr('data-name');
        additional_context.week_type = week_type
        var week_no = $('.week_no').val()
        additional_context.week_type = week_type
        $('.payroll_period').val($('.payroll_period').val());

        additional_context.employee_number = $('.employee_number').text();
        additional_context.current_employee = $('.current_employee').val();

        _.each(this.dashboards_templates, function(template) {
       	 new Model('vitalpet.payroll.inputs.validation').call('fetch_validation_data', [additional_context]).then(function(result){
	      		 self.$('.o_website_dashboard').html('');
	      		 self.$('.o_website_dashboard').append(QWeb.render(template, {widget: self,values: result,}));

	      	  });

       });
    },



//    on_production_weeks_clicked : function(ev) {
//    	var additional_context = {};
//        additional_context.period_id = $('.payroll_period').val();
//        additional_context.filter_production = $('.filter_production').val();
//        var action = $(ev.target);
//        var week_type = action.attr('data-name');
//        additional_context.week_type = week_type
//        var week_no = $('.week_no').val()
//        additional_context.week_type = week_type
//        $('.payroll_period').val($('.payroll_period').val());
//
//        additional_context.employee_number = $('.employee_number').text();
//        additional_context.current_employee = $('.current_employee').val();
//
//        _.each(this.dashboards_templates, function(template) {
//       	 new Model('vitalpet.payroll.inputs.production').call('fetch_production_data', [additional_context]).then(function(result){
//	      		 self.$('.o_website_dashboard').html('');
//	      		 self.$('.o_website_dashboard').append(QWeb.render(template, {widget: self,values: result,}));
//
//	      	  });
//
//       });
//    },

 // Change events
    on_payroll_period_changed: function(ev){
        var additional_context = {};
        additional_context.period_id = $(ev.target).val();
        $('.payroll_period').val($(ev.target).val());
        additional_context.filter_production = $('.filter_production').val();
        additional_context.employee_number = $('.employee_number').text();
        additional_context.current_employee = $('.current_employee').val();

        _.each(this.dashboards_templates, function(template) {
       	 new Model('vitalpet.payroll.inputs.validation').call('fetch_validation_data', [additional_context]).then(function(result){
	      		 self.$('.o_website_dashboard').html('');

	      		 self.$('.o_website_dashboard').append(QWeb.render(template, {widget: self,values: result,}));

	      	  });

       });
    },

    on_filter_production_changed: function(ev){
        var additional_context = {};
        additional_context.filter_production = $(ev.target).val();
        $('.filter_production').val($(ev.target).val());
        additional_context.employee_number = 1;
        additional_context.period_id = $('.payroll_period').val();
        additional_context.employee_number = $('.employee_number').text();
        additional_context.current_employee = $('.current_employee').val();

        _.each(this.dashboards_templates, function(template) {
       	 new Model('vitalpet.payroll.inputs.validation').call('fetch_validation_data', [additional_context]).then(function(result){
	      		 self.$('.o_website_dashboard').html('');

	      		 self.$('.o_website_dashboard').append(QWeb.render(template, {widget: self,values: result,}));

	      	  });

       });
    },

    // fetch_dashboard_data will contains all data related to dashboard
    render_dashboards: function() {
	    var self = this;
	    console.log(this.context)
	        _.each(this.dashboards_templates, function(template) {
	        	 new Model('vitalpet.payroll.inputs.validation').call('fetch_validation_data', []).then(function(result){
		      		 self.$('.o_website_dashboard').append(QWeb.render(template, {widget: self,values: result,}));
		      	  });

	        });
	    }
});
    core.action_registry.add('action_payroll_validation', Dashboard);
    return Dashboard;
});

