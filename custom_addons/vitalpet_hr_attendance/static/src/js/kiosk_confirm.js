odoo.define('kiosk_confirm', function (require) {
"use strict";

var core = require('web.core');
var Model = require('web.Model');
var Widget = require('web.Widget');
var web_client = require('web.web_client');

var QWeb = core.qweb;
var _t = core._t;


var KioskConfirm = Widget.extend({
    events: {
        "click .o_hr_attendance_back_button": function () { this.do_action(this.next_action, {clear_breadcrumbs: true}); },
        "click .o_hr_attendance_sign_in_out_icon": function () {
            var self = this;
            this.$('.o_hr_attendance_sign_in_out_icon').attr("disabled", "disabled");
            var hr_employee = new Model('hr.employee');
            hr_employee.call('attendance_manual', [[this.employee_id], this.next_action])
            .then(function(result) {
                if (result.action) {
                    self.do_action(result.action);
                } else if (result.warning) {
                    self.do_warn(result.warning);
                    self.$('.o_hr_attendance_sign_in_out_icon').removeAttr("disabled");
                }
            });
        },
        'click .o_hr_attendance_pin_pad_button_0': function() { this.$('.o_hr_attendance_PINbox').val(this.$('.o_hr_attendance_PINbox').val() + 0); },
        'click .o_hr_attendance_pin_pad_button_1': function() { this.$('.o_hr_attendance_PINbox').val(this.$('.o_hr_attendance_PINbox').val() + 1); },
        'click .o_hr_attendance_pin_pad_button_2': function() { this.$('.o_hr_attendance_PINbox').val(this.$('.o_hr_attendance_PINbox').val() + 2); },
        'click .o_hr_attendance_pin_pad_button_3': function() { this.$('.o_hr_attendance_PINbox').val(this.$('.o_hr_attendance_PINbox').val() + 3); },
        'click .o_hr_attendance_pin_pad_button_4': function() { this.$('.o_hr_attendance_PINbox').val(this.$('.o_hr_attendance_PINbox').val() + 4); },
        'click .o_hr_attendance_pin_pad_button_5': function() { this.$('.o_hr_attendance_PINbox').val(this.$('.o_hr_attendance_PINbox').val() + 5); },
        'click .o_hr_attendance_pin_pad_button_6': function() { this.$('.o_hr_attendance_PINbox').val(this.$('.o_hr_attendance_PINbox').val() + 6); },
        'click .o_hr_attendance_pin_pad_button_7': function() { this.$('.o_hr_attendance_PINbox').val(this.$('.o_hr_attendance_PINbox').val() + 7); },
        'click .o_hr_attendance_pin_pad_button_8': function() { this.$('.o_hr_attendance_PINbox').val(this.$('.o_hr_attendance_PINbox').val() + 8); },
        'click .o_hr_attendance_pin_pad_button_9': function() { this.$('.o_hr_attendance_PINbox').val(this.$('.o_hr_attendance_PINbox').val() + 9); },
        'click .o_hr_attendance_pin_pad_button_C': function() { this.$('.o_hr_attendance_PINbox').val(''); },
        'click .o_hr_attendance_pin_pad_button_ok': function() {
        	
            var self = this;            
            this.$('.o_hr_attendance_pin_pad_button_ok').attr("disabled", "disabled");
            var hr_employee = new Model('hr.employee');
            hr_employee.call('attendance_manual_new', [[this.employee_id], this.next_action, this.$('.o_hr_attendance_PINbox').val()])
            .then(function(result) {
                if (result.action) {                    
                    if (result.action=='test') { 
	                	$(".job_select").show();
	                	$(".job_pin").hide();
	                	$(".class1").hide();
	                	$(".class2").hide();
	                	$(".jobs").html(result.job)
                    }else{
                    	self.do_action(result.action);
                    }
               	
                } else if (result.warning) {
                    self.do_warn(result.warning);
                    setTimeout( function() { self.$('.o_hr_attendance_pin_pad_button_ok').removeAttr("disabled"); }, 500);
                }
            });
        },
        
        'click .job_btn': function() {  	
        	var self = this; 
        	setTimeout(function(){ 
        	var job_id=localStorage.getItem("job_id");
        	var emp_id=localStorage.getItem("emp_id");
        	var next_action=localStorage.getItem("next_action");  
            console.log(this);
            var hr_employee = new Model('hr.employee');
            var hr_employee = new Model('hr.employee');
            hr_employee.call('attendance_manual_antr', [[this.employee_id], next_action,job_id,emp_id])          
            .then(function(result) {
            	console.log(self);
                if (result.action) {
                	 self.do_action(result.action);
                } else if (result.warning) {                	
                    self.do_warn(result.warning);
                    setTimeout( function() { self.$('.job_btn').removeAttr("disabled"); }, 500);
                }
            });
            
        	}, 100);
        },
        
        /*"click .btn_logout": function(){
        	var self = this;
        	var base_url = new Model('ir.config_parameter');
        	alert(base_url);
        	base_url.call('get_logout_url', [])
            .then(function(result) {
        });
       };*/
        
        
        
        "click .o_hr_leave_kiosk_mode_container": function(){
    		var self = this; 
			var hr_holidays = new Model('hr.holidays');
			var emp_id=localStorage.getItem("employee_id");
			hr_holidays.call('get_employee_list', [[this.employee_id]])
            .then(function(result) {
				web_client.action_manager.do_action({
					views: [[result['form_view_id'], 'form']],
					view_id: [result['form_view_id']],
		            view_type: 'form',
		            view_mode: 'form',
		            res_model: 'hr.holidays',
		            name: "Leaves",
		            context:{default_employee_id:result['employee_id'],'flag':'True'},
		            type: 'ir.actions.act_window',
		            target: 'current',
				});
            });
        },
        
        "click .o_hr_leave_button_list": function(){
			var self = this; 
			var hr_holidays = new Model('hr.holidays');
			var emp_id=localStorage.getItem("employee_id");
			hr_holidays.call('get_holidays_list', [[this.employee_id]])
	            .then(function(result) {
					web_client.action_manager.do_action({
						views: [[result['view_id'], 'list']],
						view_id: [result['view_id']],
			            view_type: 'form',
			            view_mode: 'tree',
			            res_model: 'hr.holidays',
			            name: "Leaves",
			            type: 'ir.actions.act_window',
			            domain:  [['id', 'in',result['employee_list']]],
			            target: 'current',
					});
	            });
		},
        

    },

    init: function (parent, action) {
        this._super.apply(this, arguments);
        this.next_action = 'hr_attendance.hr_attendance_action_kiosk_mode';
        this.employee_id = action.employee_id;
        this.employee_name = action.employee_name;
        this.employee_state = action.employee_state;
        var self = this;
    },

    start: function () {
        var self = this;
        self.session.user_has_group('hr_attendance.group_hr_attendance_use_pin').then(function(has_group){
            self.use_pin = has_group;
            self.$el.html(QWeb.render("HrAttendanceKioskConfirm", {widget: self}));
            self.start_clock();
        });
        return self._super.apply(this, arguments);
    },

    start_clock: function () {
        this.clock_start = setInterval(function() {this.$(".o_hr_attendance_clock").text(new Date().toLocaleTimeString(navigator.language, {hour: '2-digit', minute:'2-digit'}));}, 500);
        // First clock refresh before interval to avoid delay
        this.$(".o_hr_attendance_clock").text(new Date().toLocaleTimeString(navigator.language, {hour: '2-digit', minute:'2-digit'}));
    },

    destroy: function () {
        clearInterval(this.clock_start);
        this._super.apply(this, arguments);
    },
});

core.action_registry.add('hr_attendance_kiosk_confirm', KioskConfirm);

    var new_string="";
    $(window).hashchange(hash_time_changed);

    function hash_time_changed(){
        setTimeout( function() {
            if ($("ol.breadcrumb").html() == null){
            }else{
            if ($("ol.breadcrumb").html().indexOf("Kiosk Mode") >= 0){
                $(".breadcrumb li").hide();
                $(".breadcrumb li:first").show();
            }
            }
        }, 500);
    }
	
return KioskConfirm;

});
