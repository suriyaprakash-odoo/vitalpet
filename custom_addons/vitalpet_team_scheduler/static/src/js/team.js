odoo.define('vitalpet_team_scheduler.custom_app', function(require) {
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

    var sch_template =  widget.FieldFloat.extend({
        template: "sch_template",
        events: {
            "click .job_positions_click": function (ev) { 

                web_client.action_manager.do_action({
                    type: 'ir.actions.act_window',
                    res_model: "staff.planning.display",
                    res_id: parseInt($(ev.target).attr('display_id')),
                    views: [[false, 'form']],
                    target: 'current',
                    context: {},
                    flags: {initial_mode: "edit",},
                });
            },
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
        	var timsheet_period=this.field_manager.get_field_value("name");
        	var company_id=this.field_manager.get_field_value("company_id");
        	var from_date=this.field_manager.get_field_value("from_date");
        	var to_date=this.field_manager.get_field_value("to_date");
        	if(timsheet_period){
            setTimeout(function(){
            	var staff_planning = new Model('staff.planning');
                staff_planning.call('dates_list', [[1], from_date, to_date,company_id,timsheet_period,c_i]).done( function(dates){          	
            		var wid=$(QWeb.render("widget_top_dates",{
            			widget:self,
            			dates:dates
            		}));
                	console.log(wid);
                	self.$(".sub_widget_dates").html(wid); 	  
                	
                });	  
                
                if(c_i==1){
                	$(".next_btn").show();
                	$(".prev_btn").hide();
            	}else{
                	$(".next_btn").hide();
                	$(".prev_btn").show();            		
            	}
                
            }, 500);
        	}
         
        }

     });

    core.form_widget_registry.add('custom_app', sch_template);

    return {
        sch_template: sch_template
    };



});


odoo.define('vitalpet_team_scheduler.custom_hours_app', function(require) {
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

    var custom_hours =  widget.FieldFloat.extend({
        template: "custom_hours",
        events: {
            "change .emp_hours": function (ev) { 
            	var staff_planning = new Model('staff.planning.display');
            	var this_target=$(ev.target);
            	var value=$(ev.target).val();
            	  var check_val=0;
            	  if(value.split(':')[1]){
            		if(parseInt(value.split(':')[0]) || parseInt(value.split(':')[0])==0 ){
            			if(parseInt(value.split(':')[1]) || parseInt(value.split(':')[1])==0 ){
            				if(parseInt(value.split(':')[0])<24){
            					if(parseInt(value.split(':')[1])<60){
            						check_val=1;
            					}				
            				}
            			}		
            		}
            	  }
            	  
            	  if(check_val==1){
            		if(parseInt(value.split(':')[0]).toString().length==1){
            			var hours="0"+parseInt(value.split(':')[0]).toString();
            		}else{
            			var hours=parseInt(value.split(':')[0]).toString();
            		}
            		
            		if(parseInt(value.split(':')[1]).toString().length==1){
            			var mins="0"+parseInt(value.split(':')[1]).toString();
            		}else{
            			var mins=parseInt(value.split(':')[1]).toString();
            		}
            		
            		value=hours+":"+mins;
                	
                	staff_planning.call('update_hours', [[1], 
                		$(ev.target).attr('data-date'), 
                		$(ev.target).attr('data-empid'),
                		$(ev.target).attr('jobid'),
                		$(ev.target).attr('work_id'),
                		$(ev.target).attr('day_id'),
                		value]).done( function(dates){ 
                		console.log(dates);
                		this_target.parent().find(".emp_pto_circles").click();
                	});
                	
            	  }else{
            		alert("Time is not a valid format");
            	  }
            	  
	        },
            "change .emp_pto_hours": function (ev) {            
                var staff_planning = new Model('staff.planning.display');
                var emp_id=$(ev.target).attr('data-empid');
                var pto_hrs=$(ev.target).val();
                
                var value=$(ev.target).val();
                  var check_val=0;
                  if(value.split(':')[1]){
                    if((parseInt(value.split(':')[0]) || parseInt(value.split(':')[0])==0) && (parseInt(value.split(':')[1]) || parseInt(value.split(':')[1])==0)){                     

                        
                        staff_planning.call('update_pto_hours', [[1],
                            $(ev.target).attr('data-date'), 
                            $(ev.target).attr('data-empid'),
                            $(ev.target).attr('jobid'),
                            $(ev.target).attr('work_id'),
                            $(ev.target).attr('day_id'),
                            $(ev.target).attr('paid'),
                            $(ev.target).val()]).done( function(dates){ 
                               console.log(dates);
                            });
                        
                        $("input[data-date='"+$(ev.target).attr('data-date')+"'][data-empid='"+$(ev.target).attr('data-empid')+"']").attr("pto-hours", $(ev.target).val());
                      
                    }
                  }
            },
            "change .emp_break_start": function (ev) {            
                var staff_planning = new Model('staff.planning.display');
                var emp_id=$(ev.target).attr('data-empid');
                var pto_hrs=$(ev.target).val();
                
                var value=$(ev.target).val();
                  var check_val=0;
                  if(value.split(':')[1]){
                    if((parseInt(value.split(':')[0]) || parseInt(value.split(':')[0])==0) && (parseInt(value.split(':')[1]) || parseInt(value.split(':')[1])==0)){                     

                        
                        staff_planning.call('update_break_start', [[1],
                            $(ev.target).attr('data-date'), 
                            $(ev.target).attr('data-empid'),
                            $(ev.target).attr('jobid'),
                            $(ev.target).attr('work_id'),
                            $(ev.target).attr('day_id'),
                            $(ev.target).attr('paid'),
                            $(ev.target).val()]).done( function(dates){ 
                               console.log(dates);
                            });
                        
                        $("input[data-date='"+$(ev.target).attr('data-date')+"'][data-empid='"+$(ev.target).attr('data-empid')+"']").attr("break-start", $(ev.target).val());
                      
                    }
                  }
            },
            "change .emp_break_end": function (ev) {            
                var staff_planning = new Model('staff.planning.display');
                var emp_id=$(ev.target).attr('data-empid');
                var pto_hrs=$(ev.target).val();
                
                var value=$(ev.target).val();
                  var check_val=0;
                  if(value.split(':')[1]){
                    if((parseInt(value.split(':')[0]) || parseInt(value.split(':')[0])==0) && (parseInt(value.split(':')[1]) || parseInt(value.split(':')[1])==0)){                     

                        
                        staff_planning.call('update_break_end', [[1],
                            $(ev.target).attr('data-date'), 
                            $(ev.target).attr('data-empid'),
                            $(ev.target).attr('jobid'),
                            $(ev.target).attr('work_id'),
                            $(ev.target).attr('day_id'),
                            $(ev.target).attr('paid'),
                            $(ev.target).val()]).done( function(dates){ 
                               console.log(dates);
                            });
                        
                        $("input[data-date='"+$(ev.target).attr('data-date')+"'][data-empid='"+$(ev.target).attr('data-empid')+"']").attr("break-end", $(ev.target).val());
                      
                    }
                  }
            },
            "click .close_pto_hours": function (ev) {       
                var value=$(ev.target).parent().parent().find(".emp_pto_hours").val();
                var break_start_time=$(ev.target).parent().parent().find(".emp_break_start").val();
                var break_end_time=$(ev.target).parent().parent().find(".emp_break_end").val();
                  var check_val=0;
                  
                    if (value.indexOf('-') !== -1){
                        alert("Time In is required and must be valid format - 09:30 ");
                        ev.preventDefault();
                        ev.stopPropagation();
                    }
                    else if(value.indexOf('+') !== -1){
                        alert("Time In is required and must be valid format - 09:30 ");
                        ev.preventDefault();
                        ev.stopPropagation();

                    }else if(parseInt(value.split(':')[0])>=24){
                        alert("Time In is required and must be valid format - 09:30 ");
                        ev.preventDefault();
                        ev.stopPropagation();

                    }else if(parseInt(value.split(':')[1])>=60){
                        alert("Time In is required and must be valid format - 09:30 ");
                        ev.preventDefault();
                        ev.stopPropagation();

                    }else if(isNaN(value.split(':')[0])){
                        alert("Time In is required and must be valid format - 09:30 ");
                        ev.preventDefault();
                        ev.stopPropagation();

                    }else if(isNaN(value.split(':')[1])){
                        alert("Time In is required and must be valid format - 09:30 ");
                        ev.preventDefault();
                        ev.stopPropagation();
                    }else if (break_start_time.indexOf('-') !== -1){
                        alert("Time In is required and must be valid format - 09:30 ");
                        ev.preventDefault();
                        ev.stopPropagation();
                    }
                    else if(break_start_time.indexOf('+') !== -1){
                        alert("Time In is required and must be valid format - 09:30 ");
                        ev.preventDefault();
                        ev.stopPropagation();

                    }else if(parseInt(break_start_time.split(':')[0])>=24){
                        alert("Time In is required and must be valid format - 09:30 ");
                        ev.preventDefault();
                        ev.stopPropagation();

                    }else if(parseInt(break_start_time.split(':')[1])>=60){
                        alert("Time In is required and must be valid format - 09:30 ");
                        ev.preventDefault();
                        ev.stopPropagation();

                    }else if(isNaN(break_start_time.split(':')[0])){
                        alert("Time In is required and must be valid format - 09:30 ");
                        ev.preventDefault();
                        ev.stopPropagation();

                    }else if(isNaN(break_start_time.split(':')[1])){
                        alert("Time In is required and must be valid format - 09:30 ");
                        ev.preventDefault();
                        ev.stopPropagation();
                    }else if (break_end_time.indexOf('-') !== -1){
                        alert("Time In is required and must be valid format - 09:30 ");
                        ev.preventDefault();
                        ev.stopPropagation();
                    }
                    else if(break_end_time.indexOf('+') !== -1){
                        alert("Time In is required and must be valid format - 09:30 ");
                        ev.preventDefault();
                        ev.stopPropagation();

                    }else if(parseInt(break_end_time.split(':')[0])>=24){
                        alert("Time In is required and must be valid format - 09:30 ");
                        ev.preventDefault();
                        ev.stopPropagation();

                    }else if(parseInt(break_end_time.split(':')[1])>=60){
                        alert("Time In is required and must be valid format - 09:30 ");
                        ev.preventDefault();
                        ev.stopPropagation();

                    }else if(isNaN(break_end_time.split(':')[0])){
                        alert("Time In is required and must be valid format - 09:30 ");
                        ev.preventDefault();
                        ev.stopPropagation();

                    }else if(isNaN(break_end_time.split(':')[1])){
                        alert("Time In is required and must be valid format - 09:30 ");
                        ev.preventDefault();
                        ev.stopPropagation();
                    }
                    else{
                      if(value.split(':')[1]){
                          if((parseInt(value.split(':')[0]) || parseInt(value.split(':')[0])==0) && (parseInt(value.split(':')[1]) || parseInt(value.split(':')[1])==0) && value!="00:00"){                     
                            $(".close_model").click();
                            
                        }else{
                            alert("Time In is required and must be valid format - 09:30 ");

                               ev.preventDefault();
                               ev.stopPropagation();
                        }
                      }else{
                        alert("Time In is required and must be valid format - 09:30 ");

                       ev.preventDefault();
                       ev.stopPropagation();
                      }
                    }      
            },
            "click .copy_prev_btn": function (ev) {      
                var name = this.field_manager.get_field_value("name");
                var planning_id = this.field_manager.get_field_value("planning_id");
                var staff_planning = new Model('staff.planning.display');
                staff_planning.call('copy_previous_week', [[1],name,planning_id]).then(function() {     
                });

                var c_i=2;
                var self=this;    
                setTimeout(function(){  
                    self.displayResults(c_i);
                    self.field_manager.on("load_record", self, function() {     
                        this.displayResults(c_i);
                    }); 
                }, 1000);
            },
            
            "click .copy_prev_btn_2": function (ev) {      
            	var name = this.field_manager.get_field_value("name");
                var planning_id = this.field_manager.get_field_value("planning_id");
                var staff_planning = new Model('staff.planning.display');
                staff_planning.call('copy_previous_week_new', [[1],name,planning_id]).then(function() {  
                	
                });
                
                var c_i=2;
                var self=this;    
                setTimeout(function(){  
                    self.displayResults(c_i);
                    self.field_manager.on("load_record", self, function() {     
                        this.displayResults(c_i);
                    }); 
                }, 1000);

            },
            
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
        	if(job_position){
            setTimeout(function(){
            	var staff_planning = new Model('staff.planning.display');
            	//alert($(".form_from_date ").text());
                staff_planning.call('hours_list', [[1], from_date, to_date,company_id,job_position,c_i]).done( function(dates){          	
            		var wid=$(QWeb.render("hours_top_dates",{
            			widget:self,
            			dates:dates
            		}));
                	console.log(wid);
                	self.$(".sub_hours_dates").html(wid); 
                });         	  
            }, 500);
        	}
        }

     });

    core.form_widget_registry.add('custom_hours_app', custom_hours);

    return {
        custom_hours: custom_hours
    };
    //o_form_button_edit
});

