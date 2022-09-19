odoo.define('vitalpet_team_scheduler.actual_app', function(require) {
    "use strict";

    var core = require('web.core');
    var widget = require('web.form_widgets');
    var FormView = require('web.FormView');

	var SystrayMenu = require('web.SystrayMenu');
	var Widget = require('web.Widget');
	var tree=require('web.TreeView');
	var Model = require('web.Model');
	var web_client = require('web.web_client');

    var QWeb = core.qweb;
    var _t = core._t;

    var ach_template =  widget.FieldFloat.extend({
        template: "ach_template",
		events: {
            "click .next_btn": function (ev) { 
            	var c_i=2;
            	var self=this;        	
            	this.displayResults(c_i);
            	this.field_manager.on("load_record", this, function() {	    
            		this.displayResults(c_i);
            	});             
            },
            "click .prev_btn": function (ev) { 
            	var c_i=1;
            	var self=this;        	
            	this.displayResults(c_i);
            	this.field_manager.on("load_record", this, function() {	    
            		this.displayResults(c_i);
            	});             
            },
        },
        
        init: function() {
            this._super.apply(this, arguments);
            var self=this;
            self.partner="123456";            
            self.partner_list=JSON.parse('{"recs": [{"d2": "2017-09-17", "d1": "Sun Sep 17"}, {"d2": "2017-09-18", "d1": "Mon Sep 18"}]}');

        },

        start : function() {
        	var self=this;      
        	var c_i=1;  	
        	this.displayResults(c_i);
        	this.field_manager.on("load_record", this, function() {	    
        		this.displayResults(c_i);
        	});
        },

        renderElement: function () {
        	this._super();         
        },
        
        displayResults: function (c_i) {
        	var company_id=this.field_manager.get_field_value("company_id");
        	var from_date=this.field_manager.get_field_value("from_date");
        	var to_date=this.field_manager.get_field_value("to_date");
        	var job_position=this.field_manager.get_field_value("name");
        	
        	if(company_id){
            setTimeout(function(){
            	var staff_planning = new Model('actual.labour.cost');
            	//alert($(".form_from_date ").text());
                staff_planning.call('actual_list', [[1], from_date, to_date,company_id,job_position,c_i]).done( function(dates){          	
            		var wid=$(QWeb.render("widget_top_actual",{
            			widget:self,
            			dates:dates
            		}));
                	console.log(wid);
                	self.$(".sub_widget_actuals").html(wid); 
                });         	  
            }, 500);  
        	}
        }

     });
    core.form_widget_registry.add('actual_app', ach_template);
    return {
        ach_template: ach_template
    };


});
