odoo.define('vitalpet_custom_hr_recruitment', function (require) {
	"use strict";

//	var core = require('web.core');
//	var SystrayMenu = require('web.SystrayMenu');
	var Widget = require('web.Widget');
//	var tree=require('web.TreeView');
//	var QWeb = core.qweb;
	var Model = require('web.Model');
//	var web_client = require('web.web_client');
//	var utils = require('web.utils');

$(document).ready(function(){
    $("body").delegate(".o_website_form_send_apply", "click", function() {
    	new LeaveView();
         });
  });

	var LeaveView = Widget.extend ({
      
	   init: function() {
		    var self = this;
			var hr_employee = new Model('hr.applicant');
			hr_employee.call('website_job_reapply', [[1], $("input[name='email_from']").val(), $(".s_website_form").attr("data-form_field_job_id")])
			.then(function(result) {
				if(result==1){
					alert("You have already applied for the same job position.");
				}if(result==0){
					$(".o_website_form_send").click();
				}
			});
	   },

	});
});

