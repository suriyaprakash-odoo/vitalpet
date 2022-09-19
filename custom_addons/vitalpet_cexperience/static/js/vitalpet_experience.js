/*global $, _, PDFJS */
odoo.define('vitalpet_cexperience.vitalpet_experience', function (require) {
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
    template: "vitalpet_cexperience.HomePage",


    events: {
        'click .o_dashboard_action': 'on_dashboard_action_clicked',
        'click .o_dashboard_action_open': 'on_dashboard_action_clicked_open',
        
    },

    init: function(parent, context) {
        this._super(parent, context);
        this.dashboards_templates = ['vitalpet_cexperience.dashboard_visits'];
    },
    start: function() {
        var self = this;
        return this._super().then(function() {
            self.render_dashboards();
            self.$el.parent().addClass('oe_background_grey');
        });
    },
    
    
    on_dashboard_action_clicked: function(ev){
        ev.preventDefault();
        var $action = $(ev.currentTarget);
        var action_name = $action.attr('name');
        var action_id = $action.attr('id');
        var action_extra = $action.data('extra');
        var additional_context = {};
        if (action_name === 'survey.action_survey_user_input' && action_id === 'new'){
           
            additional_context.search_default_new = 1; 
        }
        
        else if (action_name === 'survey.action_survey_user_input' && action_id === 'pending'){
        	
            additional_context.search_default_partially_completed = 1; 
        }
        
        else if (action_name === 'survey.action_survey_user_input' && action_id === 'completed'){
        	
            additional_context.search_default_completed_exp = 1; 
        }
        this.do_action(action_name, {additional_context: additional_context});
    },
    
    
    render_dashboards: function() {
	    var self = this;
	        _.each(this.dashboards_templates, function(template) {
	        	  new Model('experience.visit').call('dash_vals', []).then(function(result){
	        		  google.charts.load('current', {'packages':['corechart']});
				      google.charts.setOnLoadCallback(drawChart);
				
				      function drawChart() {
				    	var data_list = [];
				    	var Header=["Years", "Pre-Exam"];
				    	data_list.push(Header);
				    	var len = 10;
				    	for (var i = 0; i <= len; i++){
	                          data_list.push([result['date_loop'][i],result['pre_score'][i]]);
	                        }
				        var data = google.visualization.arrayToDataTable(data_list);
				
				        var options_stacked = {
				                isStacked: false,
				                height: 300,
				                legend: {position: 'top', maxLines: 2},
				                vAxis: {minValue: 0}
				              };
				        
				        
				        var chart = new google.visualization.AreaChart(document.getElementById('chart_div'));
				        chart.draw(data, options_stacked);
				      }
				      
				      google.charts.load('current', {'packages':['corechart']});
				      google.charts.setOnLoadCallback(drawChart1);
				
				      function drawChart1() {
					    	var data_list1 = [];
					    	var Header1=["Years", "Exam"];
					    	data_list1.push(Header1);
					    	var len = 10;
					    	for (var i = 0; i <= len; i++){
		                          data_list1.push([result['date_loop'][i],result['ex_score'][i]]);
		                        }
					        var data = google.visualization.arrayToDataTable(data_list1);
					
					        var options_stacked = {
					                isStacked: false,
					                height: 300,
					                legend: {position: 'top', maxLines: 2},
					                series: {
					                    0: { color: 'black' },
					                  },
					                vAxis: {minValue: 0}
					              };
				          
				
				        var chart1 = new google.visualization.AreaChart(document.getElementById('chart_div1'));
				        chart1.draw(data, options_stacked);
				      }
				      
				      google.charts.load('current', {'packages':['corechart']});
				      google.charts.setOnLoadCallback(drawChart2);
				
				      function drawChart2() {
					    	var data_list2 = [];
					    	var Header2=["Years", "Post-Exam"];
					    	data_list2.push(Header2);
					    	var len = 10;
					    	for (var i = 0; i <= len; i++){
		                          data_list2.push([result['date_loop'][i],result['post_score'][i]]);
		                        }
					        var data = google.visualization.arrayToDataTable(data_list2);
					
					        var options_stacked = {
					                isStacked: false,
					                height: 300,
					                legend: {position: 'top', maxLines: 2},
					                series: {
					                    0: { color: '#8B0F0F' },
					                  },
					                vAxis: {minValue: 0}
					              };
				          
				
				        var chart2 = new google.visualization.AreaChart(document.getElementById('chart_div2'));
				        chart2.draw(data, options_stacked);
				      }
				      
				      google.charts.load('current', {'packages':['corechart']});
				      google.charts.setOnLoadCallback(drawChart3);
				
				      function drawChart3() {
					    	var data_list3 = [];
					    	var Header3=["Years", "Discounts"];
					    	data_list3.push(Header3);
					    	var len = 10;
					    	var colors =["#F71A1A"]
					    	for (var i = 0; i <= len; i++){
		                          data_list3.push([result['date_loop'][i],result['graph_dis'][i]]);
		                        }
					        var data = google.visualization.arrayToDataTable(data_list3);
					
					        var options_stacked = {
					                isStacked: false,
					                height: 300,
					                legend: {position: 'top', maxLines: 2},
					                series: {
					                    0: { color: '#2618F0' },
					                  },
					                vAxis: {minValue: 0}
					                
					              }; 
				          
				
				        var chart3 = new google.visualization.AreaChart(document.getElementById('chart_div3'));
				        chart3.draw(data, options_stacked);
				      }
				      
	        		  self.$('.o_website_dashboard').append(QWeb.render(template, {widget: self,values: result,}));
	        	  });
	        
	        });
	    }
    
    
    
});
    core.action_registry.add('client_experience_dashboard', Dashboard);
    return Dashboard;
    
    
});



$(document).ready(function(){
	  $("body").delegate(".pre_exam,.exam,.post_exam,.discounts", "click", function() {
		  	var action_cla="."+$(this).attr("data_target")
    	    $(".score").attr("style","visibility:hidden;height:0;");
    	    $(action_cla).attr("style","");
  	  });
});


