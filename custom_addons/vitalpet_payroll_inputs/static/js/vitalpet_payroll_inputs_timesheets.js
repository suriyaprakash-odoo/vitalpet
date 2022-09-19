/*global $, _, PDFJS */
odoo.define('vitalpet_payroll_inputs.action_payroll_input_timesheets', function (require) {
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
    template: "vitalpet_payroll_inputs.HomePage",
	searchview_hidden: true,
    //Dashboard cleck events
    events: {
        'click .timesheet_previous': 'on_timesheet_previous_clicked',
        'click .timesheet_next': 'on_timesheet_next_clicked',
        'click .employee_previous': 'on_employee_previous_clicked',
        'click .employee_next': 'on_employee_next_clicked',
        'click .time_sheet_weeks': 'on_timesheet_weeks_clicked',
        'change .payroll_period': 'on_payroll_period_changed',
        'change .filter_timesheet': 'on_filter_timesheet_changed',
        'change .filter_module': 'on_filter_module_changed',
        'click .work_hours_copy': 'on_work_hours_copy_clicked',
        'change .work_hours_col input': 'on_filter_work_hours_change'
    },


    init: function(parent, context) {
        this._super(parent, context);
        this.dashboards_templates = ['vitalpet_payroll_inputs.TimesheetPage'];
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
    
    on_timesheet_previous_clicked: function(ev){
        var additional_context = {};
        additional_context.period_id = $('.payroll_period').val();
        additional_context.filter_module = $('.filter_module').val();
        additional_context.filter_timesheet = $('.filter_timesheet').val();

        
        var week_type = $(".time_sheet_weeks.active").attr("data-name");
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
       	 new Model('vitalpet.payroll.inputs.timesheets').call('fetch_timesheet_data', [additional_context]).then(function(result){
	      		 self.$('.o_website_dashboard').html('');

	      		 self.$('.o_website_dashboard').append(QWeb.render(template, {widget: self,values: result,}));
	      		  
	      	  });
       	
       });
    },

    on_employee_previous_clicked: function(ev){
        var additional_context = {};
        additional_context.period_id = $('.payroll_period').val();
        additional_context.filter_module = $('.filter_module').val();
        additional_context.filter_timesheet = $('.filter_timesheet').val();
        var data_id=$(".current_employee option[value='"+$('.current_employee').val()+"']").attr("data_id");
        var previous_id=parseInt(data_id)-1;
        var employee_number = parseInt(data_id)-1;
        var previous_value = $(".current_employee option[data_id='"+previous_id+"']").attr("value");
        if (typeof previous_value === "undefined") {
        	
        	var previous_id=$(".current_employee option:last").attr("data_id");
        	var employee_number = previous_id;
        	var previous_value = $(".current_employee option[data_id='"+previous_id+"']").attr("value");
        }

        var week_type = $(".time_sheet_weeks.active").attr("data-name");
        additional_context.week_type = week_type
        var week_no = $('.week_no').val();
        additional_context.week_no = week_no

        additional_context.employee_number = employee_number;
        additional_context.current_employee = previous_value;
        $('.employee_number').text(employee_number);
        $('.filter_employee_id').val(previous_value);
        _.each(this.dashboards_templates, function(template) {
       	 new Model('vitalpet.payroll.inputs.timesheets').call('fetch_timesheet_data', [additional_context]).then(function(result){
	      		 self.$('.o_website_dashboard').html('');

	      		 self.$('.o_website_dashboard').append(QWeb.render(template, {widget: self,values: result,}));
	      		  
	      	  });
       	
       });
    },
    
    on_employee_next_clicked: function(ev){
        var additional_context = {};
        additional_context.period_id = $('.payroll_period').val();
        additional_context.filter_module = $('.filter_module').val();
        additional_context.filter_timesheet = $('.filter_timesheet').val();
        var data_id=$(".current_employee option[value='"+$('.current_employee').val()+"']").attr("data_id");
        var next_id=parseInt(data_id)+1;
        var employee_number = parseInt(data_id)+1;
        var next_value = $(".current_employee option[data_id='"+next_id+"']").attr("value");

        if (typeof next_value === "undefined") {
        	var next_id=$(".current_employee option:first").attr("data_id");
        	var employee_number = next_id;
        	var next_value = $(".current_employee option[data_id='"+next_id+"']").attr("value");
        }
        
        var week_type = $(".time_sheet_weeks.active").attr("data-name");
        additional_context.week_type = week_type
        var week_no = $('.week_no').val();
        additional_context.week_no = week_no
        
        additional_context.employee_number = employee_number;
        additional_context.current_employee = next_value;
        $('.employee_number').text(employee_number);
        $('.filter_employee_id').val(next_value);
        _.each(this.dashboards_templates, function(template) {
       	 new Model('vitalpet.payroll.inputs.timesheets').call('fetch_timesheet_data', [additional_context]).then(function(result){
	      		 self.$('.o_website_dashboard').html('');

	      		 self.$('.o_website_dashboard').append(QWeb.render(template, {widget: self,values: result,}));
	      		  
	      	  });
       	
       });
    },
    on_timesheet_next_clicked: function(ev){
        var additional_context = {};
        additional_context.period_id = $('.payroll_period').val();
        additional_context.filter_module = $('.filter_module').val();
        additional_context.filter_timesheet = $('.filter_timesheet').val();
        additional_context.week_type = $('.week_type').attr('data-name');
        
        var week_type = $(".time_sheet_weeks.active").attr("data-name");
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
       	 new Model('vitalpet.payroll.inputs.timesheets').call('fetch_timesheet_data', [additional_context]).then(function(result){
	      		 self.$('.o_website_dashboard').html('');

	      		 self.$('.o_website_dashboard').append(QWeb.render(template, {widget: self,values: result,}));
	      		  
	      	  });
       	
       });
    },
    
    on_timesheet_weeks_clicked : function(ev) {
    	var additional_context = {};
        additional_context.period_id = $('.payroll_period').val();
        additional_context.filter_module = $('.filter_module').val();
        additional_context.filter_timesheet = $('.filter_timesheet').val();
        $(".time_sheet_weeks").removeClass('active');
        var action = $(ev.target);
        $(ev.target).addClass('active');
        var week_type = action.attr('data-name');
        additional_context.week_type = week_type
        $('.payroll_period').val($('.payroll_period').val());

        _.each(this.dashboards_templates, function(template) {
       	 new Model('vitalpet.payroll.inputs.timesheets').call('fetch_timesheet_data', [additional_context]).then(function(result){
	      		 self.$('.o_website_dashboard').html('');
	      		 self.$('.o_website_dashboard').append(QWeb.render(template, {widget: self,values: result,}));
	      		  
	      	  });
       	
       }); 	
    },
    
 // Change events
    on_payroll_period_changed: function(ev){
        var additional_context = {};
        additional_context.period_id = $(ev.target).val();
        $('.payroll_period').val($(ev.target).val());
        additional_context.filter_timesheet = $('.filter_timesheet').val();
        additional_context.filter_module = $('.filter_module').val();
        
        var week_type = $(".time_sheet_weeks.active").attr("data-name");
        additional_context.week_type = week_type
        var week_no = $('.week_no').val();
        additional_context.week_no = week_no
        
        
        _.each(this.dashboards_templates, function(template) {
       	 new Model('vitalpet.payroll.inputs.timesheets').call('fetch_timesheet_data', [additional_context]).then(function(result){
	      		 self.$('.o_website_dashboard').html('');

	      		 self.$('.o_website_dashboard').append(QWeb.render(template, {widget: self,values: result,}));
	      		  
	      	  });
       	
       });
    },
    
    on_filter_timesheet_changed: function(ev){
        var additional_context = {};
        additional_context.filter_timesheet = $(ev.target).val();
        $('.filter_timesheet').val($(ev.target).val());
        additional_context.filter_module = $('.filter_module').val();
        additional_context.employee_number = 1;
        additional_context.current_employee_id = $('.filter_employee_id').val();
        additional_context.period_id = $('.payroll_period').val();
        
        var week_type = $(".time_sheet_weeks.active").attr("data-name");
        additional_context.week_type = week_type
        var week_no = $('.week_no').val();
        additional_context.week_no = week_no

        _.each(this.dashboards_templates, function(template) {
       	 new Model('vitalpet.payroll.inputs.timesheets').call('fetch_timesheet_data', [additional_context]).then(function(result){
	      		 self.$('.o_website_dashboard').html('');

	      		 self.$('.o_website_dashboard').append(QWeb.render(template, {widget: self,values: result,}));
	      		  
	      	  });
       });
    },
    
    on_filter_module_changed: function(ev){
        var additional_context = {};
        additional_context.filter_module = $(ev.target).val();
        $('.filter_module').val($(ev.target).val());
        additional_context.filter_timesheet = $('.filter_timesheet').val();
        additional_context.employee_number = 1;
        additional_context.current_employee_id = $('.filter_employee_id').val();
        additional_context.period_id = $('.payroll_period').val();
        
        var week_type = $(".time_sheet_weeks.active").attr("data-name");
        additional_context.week_type = week_type
        var week_no = $('.week_no').val();
        additional_context.week_no = week_no

        _.each(this.dashboards_templates, function(template) {
       	 new Model('vitalpet.payroll.inputs.timesheets').call('fetch_timesheet_data', [additional_context]).then(function(result){
	      		 self.$('.o_website_dashboard').html('');

	      		 self.$('.o_website_dashboard').append(QWeb.render(template, {widget: self,values: result,}));
	      		  
	      	  });
       });
    },
    on_work_hours_copy_clicked: function(ev){

        $("tr.attendance_emp_row").each(function(){

        	var data_index = $(this).attr("data_index");
        	var data_checkbox = $("input.data_checkbox"+data_index).is(':checked')
        	if(data_checkbox == true) {
        		$(this).find("td").each(function(){
                    
                    var data_val=$(this).find(".o_grid_input").attr("data-attendance");
                    var res=$(this).find(".o_grid_input").text();
                    $("[data-workhours='"+data_val+"']").val(res);

                    //Update in work hours table
                    var value=res;
                    var id=data_val;
                    var week_type = $(".time_sheet_weeks.active").attr("data-name");
                    if(week_type == 'two_weeks') {
                    	var week_days = 14;
                    }        	
                    else {
                    	var week_days = 7;
                    }
               
                    
                    var mod = id % week_days;
                    if(mod == 0) {
                    	var date_no = week_days
                    }
                    else {
                    	var date_no = mod
                    }
                    var additional_context = {};
                    additional_context.attendance_value=value;
                    additional_context.payroll_period= $('.payroll_period').val();
                    additional_context.attendance_emp_id=$("[data-workhours='"+data_val+"']").closest('tr').find(".emp_id_find_work_hours").attr("emp_id");
                    additional_context.attendance_job_id=$("[data-workhours='"+data_val+"']").closest('tr').find(".emp_id_find_work_hours").attr("job_id");
                    additional_context.attendance_date=$("[record_date_num='"+date_no+"']").attr("record_date");
                    new Model('vitalpet.payroll.inputs.timesheets').call('update_work_hours', [additional_context]).then(function(result){
                             console.log(result);
                    });
                });
        	}
            
        });

    },
    on_filter_work_hours_change: function(ev){
        var value=$(ev.target).val();
        var week_type = $(".time_sheet_weeks.active").attr("data-name");
        if(week_type == 'two_weeks') {
        	var week_days = 14;
        }        	
        else {
        	var week_days = 7;
        }
   
        
        var id=$(ev.target).attr("data-workhours");
        var mod = id % week_days;
        if(mod == 0) {
        	var date_no = week_days
        }
        else {
        	var date_no = mod
        }
        var additional_context = {};
        additional_context.attendance_value=value;
        additional_context.payroll_period= $('.payroll_period').val();
        additional_context.attendance_emp_id=$(ev.target).closest('tr').find(".emp_id_find_work_hours").attr("emp_id");
        additional_context.attendance_job_id=$(ev.target).closest('tr').find(".emp_id_find_work_hours").attr("job_id");
        additional_context.attendance_date=$("[record_date_num='"+date_no+"']").attr("record_date");
        new Model('vitalpet.payroll.inputs.timesheets').call('update_work_hours', [additional_context]).then(function(result){
                 console.log(result);
        });
    },
    
    // fetch_dashboard_data will contains all data related to dashboard
    render_dashboards: function() {
	    var self = this;
	    console.log(this.context)
	        _.each(this.dashboards_templates, function(template) {
	        	 new Model('vitalpet.payroll.inputs.timesheets').call('fetch_timesheet_data', []).then(function(result){
		      		 self.$('.o_website_dashboard').append(QWeb.render(template, {widget: self,values: result,}));
		      		  
		      	  });
	        	
	        });
	    }
});
    core.action_registry.add('action_payroll_input_timesheets', Dashboard);
    return Dashboard;
});

