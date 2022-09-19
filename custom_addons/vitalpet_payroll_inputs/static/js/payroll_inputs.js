odoo.define('vitalpet_payroll_inputs', function (require) {
"use strict";

	var core = require('web.core');
	var SystrayMenu = require('web.SystrayMenu');
	var Widget = require('web.Widget');
	var tree=require('web.TreeView');
	var QWeb = core.qweb;
	var Model = require('web.Model');
	var web_client = require('web.web_client');

	var ContractView = Widget.extend ({

		init: function() {
		    var self = this;
			var hr_employee = new Model('hr.contract');
			hr_employee.call('validate_payroll_contract', [[1], 1])
			.then(function(result) {
					if(result=='Pending contracts is there'){
						alert(result);
					}else{
							web_client.action_manager.do_action(result);

					}
			});
	   },

	});
	var LeaveView = Widget.extend ({

		   init: function() {
			    var self = this;
				var hr_employee = new Model('hr.holidays');
				hr_employee.call('validate_payroll_leaves', [[1], 1])
				.then(function(result) {

						if(result=='Pending Leaves is there'){
							alert(result);
						}else{
							web_client.action_manager.do_action(result);
						}
				});
		   },

		});
	var TimesheetView = Widget.extend ({

		   init: function() {
			    var self = this;
				var hr_employee = new Model('hr.holidays');
				var payroll_period=-1;
				                if(localStorage.getItem("payroll_period")!=""){
				                    payroll_period=parseInt(localStorage.getItem("payroll_period"));
				                }
				hr_employee.call('production_page', [[1], payroll_period])
				.then(function(result) {
						if(result=='Pending Leaves is there'){
							alert(result);
						}else{
							web_client.action_manager.do_action(result);
						}
				});
		   },

		});

	var ProductionView = Widget.extend ({

		   init: function() {
			    var self = this;
				var hr_employee = new Model('hr.holidays');
				var payroll_period=-1;
				                if(localStorage.getItem("payroll_period")!=""){
				                    payroll_period=parseInt(localStorage.getItem("payroll_period"));
				                }
				hr_employee.call('validation_page', [[1], payroll_period])
				.then(function(result) {
						if(result=='Pending Leaves is there'){
							alert(result);
						}else{
							web_client.action_manager.do_action(result);
						}
				});
		   },

		});

        var ValidationView = Widget.extend ({

		   init: function() {
			    var self = this;
				var hr_employee = new Model('hr.holidays');

                var payroll_period=-1;
                if(localStorage.getItem("payroll_period")!=""){
                    payroll_period=parseInt(localStorage.getItem("payroll_period"));
                }
				hr_employee.call('finalized_page', [[1], payroll_period])
				.then(function(result) {

						if(result=='Pending Leaves is there'){
							alert(result);
						}else{
							web_client.action_manager.do_action(result);
						}
				});
		   },

		});


	$(document).ready(function(){
		var payroll = {
			    checkPayrollBtns: function () {

						setTimeout(function(){
							var str=window.location.href;
                            var btns=0;
                            var hr_contract = new Model('hr.contract');
                            hr_contract.call('contract_page', [[1], 1])
                            .then(function(result) {
                                             if (str.indexOf("action="+result) >= 0){
                                                btns=btns+1;
                                                var buttons='<div class="o_form_view"><div class="row o_form_statusbar"><div class="col-sm-6"><button type="button" class="btn btn-arrow-right btn-primary btn_validate_contract" style="margin-top: 2px;" >Validate and Go to Next Step</button></div>\
                                                     <div class="col-sm-6 text-right o_statusbar_status">\
                                                     <button type="button" class="btn btn-sm o_arrow_button btn-default">Finalized</button>\
                                                     <button name="button" class="btn btn-sm o_arrow_button btn-default">Validate</button>\
                                                     <button type="button" class="btn btn-sm o_arrow_button btn-default">Production</button>\
                                                     <button type="button" class="btn btn-sm o_arrow_button btn-default">Timesheet</button>\
                                                     <button name="button" class="btn btn-sm o_arrow_button btn-default">Leaves</button>\
                                                     <button type="button" class="btn btn-sm o_arrow_button btn-primary disabled">Contracts</button>\
                                                     </div></div></div>'
							                    $("div.payroll_btns").remove();
                                                $("<div style='background:#fff;' class='payroll_btns'>"+buttons+"</div>").insertBefore(".o_control_panel");

                                            }
                            });

                            var hr_holidays = new Model('hr.holidays');
                            hr_holidays.call('leaves_page', [[1], 1])
                            .then(function(result) {

                                    if(str.indexOf("action="+result) >= 0){
                                                btns=btns+1;
                                                var buttons='<div class="o_form_view"><div class="row o_form_statusbar"><div class="col-sm-6"><button type="button" class="btn btn-arrow-right btn-primary btn_validate_leave" style="margin-top: 2px;" >Validate and Go to Next Step</button></div>\
                                                     <div class="col-sm-6 text-right o_statusbar_status">\
                                                     <button type="button" class="btn btn-sm o_arrow_button btn-default">Finalized</button>\
                                                     <button name="button" class="btn btn-sm o_arrow_button btn-default">Validate</button>\
                                                     <button type="button" class="btn btn-sm o_arrow_button btn-default">Production</button>\
                                                     <button type="button" class="btn btn-sm o_arrow_button btn-default">Timesheet</button>\
                                                     <button name="button" class="btn btn-sm o_arrow_button btn-primary disabled">Leaves</button>\
                                                     <button type="button" class="btn btn-sm o_arrow_button btn-default">Contracts</button>\
                                                     </div></div></div>'
							                    $("div.payroll_btns").remove();
                                                $("<div style='background:#fff;' class='payroll_btns'>"+buttons+"</div>").insertBefore(".o_control_panel");

                                    }
                            });

                            var hr_holidays = new Model('hr.holidays');
                            hr_holidays.call('timesheet_page', [[1], 1])
                            .then(function(result) {
                                    if(str.indexOf("action="+result) >= 0){
                                                btns=btns+1;
                                                var buttons='<div class="o_form_view"><div class="row o_form_statusbar"><div class="col-sm-6"><button type="button" class="btn btn-arrow-right btn-primary btn_validate_timesheet" style="margin-top: 2px;" >Validate and Go to Next Step</button></div>\
                                                     <div class="col-sm-6 text-right o_statusbar_status">\
                                                     <button type="button" class="btn btn-sm o_arrow_button btn-default">Finalized</button>\
                                                     <button name="button" class="btn btn-sm o_arrow_button btn-default">Validate</button>\
                                                     <button type="button" class="btn btn-sm o_arrow_button btn-default">Production</button>\
                                                     <button type="button" class="btn btn-sm o_arrow_button btn-primary disabled">Timesheet</button>\
                                                     <button name="button" class="btn btn-sm o_arrow_button btn-default">Leaves</button>\
                                                     <button type="button" class="btn btn-sm o_arrow_button btn-default">Contracts</button>\
                                                     </div></div></div>'
							                    $("div.payroll_btns").remove();
                                                $("<div style='background:#fff;' class='payroll_btns'>"+buttons+"</div>").insertBefore(".o_control_panel");

                                    }
                            });

                            var hr_holidays = new Model('hr.holidays');
                            hr_holidays.call('production_page_view', [[1], 1])
                            .then(function(result) {
                                    if(str.indexOf("action="+result) >= 0){
                                    	setTimeout(function(){
                                            $(".o_view_manager_content input").prop("readonly", true);
                                    	},2000);
                                    }
                            });

                            var hr_holidays = new Model('hr.holidays');
                            hr_holidays.call('production_page', [[1], 1])
                            .then(function(result) {
                                    if(str.indexOf("action="+result) >= 0){
                                                btns=btns+1;
                                                var buttons='<div class="o_form_view"><div class="row o_form_statusbar"><div class="col-sm-6"><button type="button" class="btn btn-arrow-right btn-primary btn_validate_production" style="margin-top: 2px;" >Validate and Go to Next Step</button></div>\
                                                     <div class="col-sm-6 text-right o_statusbar_status">\
                                                     <button type="button" class="btn btn-sm o_arrow_button btn-default">Finalized</button>\
                                                     <button name="button" class="btn btn-sm o_arrow_button btn-default">Validate</button>\
                                                     <button type="button" class="btn btn-sm o_arrow_button btn-primary disabled">Production</button>\
                                                     <button type="button" class="btn btn-sm o_arrow_button btn-default">Timesheet</button>\
                                                     <button name="button" class="btn btn-sm o_arrow_button btn-default">Leaves</button>\
                                                     <button type="button" class="btn btn-sm o_arrow_button btn-default">Contracts</button>\
                                                     </div></div></div>'
							                    $("div.payroll_btns").remove();
                                                $("<div style='background:#fff;' class='payroll_btns'>"+buttons+"</div>").insertBefore(".o_control_panel");
                                    }
                            });

                            var hr_holidays = new Model('hr.holidays');
                            hr_holidays.call('validation_page', [[1], 1])
                            .then(function(result) {
                                    if(str.indexOf("action="+result) >= 0){
                                                btns=btns+1;
                                                var buttons='<div class="o_form_view"><div class="row o_form_statusbar"><div class="col-sm-6"><button type="button" class="btn btn-arrow-right btn-primary btn_double_validation" style="margin-top: 2px;" >Validate and Go to Next Step</button></div>\
                                                     <div class="col-sm-6 text-right o_statusbar_status">\
                                                     <button type="button" class="btn btn-sm o_arrow_button btn-default">Finalized</button>\
                                                     <button name="button" class="btn btn-sm o_arrow_button btn-primary disabled">Validate</button>\
                                                     <button type="button" class="btn btn-sm o_arrow_button btn-default">Production</button>\
                                                     <button type="button" class="btn btn-sm o_arrow_button btn-default">Timesheet</button>\
                                                     <button name="button" class="btn btn-sm o_arrow_button btn-default">Leaves</button>\
                                                     <button type="button" class="btn btn-sm o_arrow_button btn-default">Contracts</button>\
                                                     </div></div></div>'
							                    $("div.payroll_btns").remove();
                                                $("<div style='background:#fff;' class='payroll_btns'>"+buttons+"</div>").insertBefore(".o_control_panel");
                                    }
                            });

                            var hr_holidays = new Model('hr.holidays');
                            hr_holidays.call('finalized_page', [[1]])
                            .then(function(result) {
                                    if(str.indexOf("action="+result) >= 0){
                                                btns=btns+1;
                                                var buttons='<div class="o_form_view"><div class="row o_form_statusbar"><div class="col-sm-6"></div>\
                                                     <div class="col-sm-6 text-right o_statusbar_status">\
                                                     <button type="button" class="btn btn-sm o_arrow_button btn-primary disabled">Finalized</button>\
                                                     <button name="button" class="btn btn-sm o_arrow_button btn-default">Validate</button>\
                                                     <button type="button" class="btn btn-sm o_arrow_button btn-default">Production</button>\
                                                     <button type="button" class="btn btn-sm o_arrow_button btn-default">Timesheet</button>\
                                                     <button name="button" class="btn btn-sm o_arrow_button btn-default">Leaves</button>\
                                                     <button type="button" class="btn btn-sm o_arrow_button btn-default">Contracts</button>\
                                                     </div></div></div>'
							                    $("div.payroll_btns").remove();
                                                $("<div style='background:#fff;' class='payroll_btns'>"+buttons+"</div>").insertBefore(".o_control_panel");
                                    }
                            });

                            if(btns==0){
                                $("div.payroll_btns").remove();
                            }

						}, 500);
			    }
		}

        $(window).hashchange(hashchanged);
        hashchanged();
        function hashchanged(){
            payroll.checkPayrollBtns();
        }
		$('body').delegate('.o_main_navbar li','click',function() {    		
        	if($(this).text().trim()=='Production'){
        		payroll.checkPayrollBtns();
        	}
		});		
		$('body').delegate('.btn_validate_contract','click',function() {
			new ContractView();
		});
		$('body').delegate('.btn_validate_leave','click',function() {
			new LeaveView();
		});
		$('body').delegate('.btn_validate_timesheet','click',function() {
            localStorage.setItem("payroll_period", $(".payroll_period").val());
			new TimesheetView();
		});
		$('body').delegate('.btn_validate_production','click',function() {
			new ProductionView();
		});
		$('body').delegate('.btn_double_validation','click',function() {
			new ValidationView();
		});

	});

});
