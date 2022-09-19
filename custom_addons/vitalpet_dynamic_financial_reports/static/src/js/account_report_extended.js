odoo.define('account_reports.account_report_extended', function (require) {
'use strict';

var core = require('web.core');
var Widget = require('web.Widget');
var formats = require('web.formats');
var Model = require('web.Model');
var time = require('web.time');
var ControlPanelMixin = require('web.ControlPanelMixin');
var ReportWidget = require('account_reports.ReportWidget');
var Dialog = require('web.Dialog');
var session = require('web.session');
var framework = require('web.framework');
var crash_manager = require('web.crash_manager');

var QWeb = core.qweb;
var FollowupReportWidget = require('account_reports.FollowupReportWidget');
var account_report_generic = require('account_reports.account_report_generic');
account_report_generic.include({
    init: function(parent, action) {
        this.actionManager = parent;
        this.controller_url = action.context.url;
        this.report_model = action.context.model;
        // in case of a financial report, an id is defined in the action declaration
        this.report_id = action.context.id ? parseInt(action.context.id, 10) : undefined;
        this.given_context = {};
        if (action.context.context) {
            this.given_context = action.context.context;
        }
        this.given_context.from_report_id = action.context.from_report_id;
        this.given_context.from_report_model = action.context.from_report_model;
        this.given_context.force_account = action.context.force_account;
        this.given_context.active_id = action.context.active_id;
        this.odoo_context = action.context;
        setTimeout(function(){
        	$(".o_account_reports_date-filter .o_account_reports_one-filter.selected a").click();
        }, 3000);
        return this._super.apply(this, arguments);
        
    },
    
// Fetches the html and is previous report.context if any, else create it
    get_html: function() {
        var self = this;
        var defs = [];
        return new Model('account.report.context.common').call('return_context', [self.report_model, self.given_context, self.report_id]).then(function (result) {
            self.context_model = new Model(result[0]);
            self.context_id = result[1];
            // Finally, actually get the html and various data
            return self.context_model.call('get_html_and_data', [self.context_id, self.given_context], {context: session.user_context}).then(function (result) {
                self.report_type = result.report_type;
                self.html = result.html;
                self.xml_export = result.xml_export;
                self.fy = result.fy;
                self.report_context = result.report_context;
                self.report_context.available_companies = result.available_companies;
                self.report_context.fiscal_periods = result.fiscal_periods;
                if (result.available_journals) {
                    self.report_context.available_journals = result.available_journals;
                }
                self.render_buttons();
                self.render_searchview_buttons();
                self.render_searchview();
                self.render_pager();
                defs.push(self.update_cp());
                return $.when.apply($, defs);
            });
        });
    },

    render_searchview_buttons: function() {

        var self = this;

        // Render the searchview buttons and bind them to the correct actions
        this.$searchview_buttons = $(QWeb.render("accountReports.searchView", {report_type: this.report_type, context: this.report_context}));
        var $dateFilter = this.$searchview_buttons.siblings('.o_account_reports_date-filter');
        var $dateFilterCmp = this.$searchview_buttons.siblings('.o_account_reports_date-filter-cmp');
        var $useCustomDates = $dateFilter.find('.o_account_reports_use-custom');
        var $CustomDates = $dateFilter.find('.o_account_reports_custom-dates');
        $useCustomDates.bind('click', function () {self.toggle_filter($useCustomDates, $CustomDates);});
        var $usePreviousPeriod = $dateFilterCmp.find('.o_account_reports_use-previous-period');
        var $previousPeriod = $dateFilterCmp.find('.o_account_reports_previous-period');
        $usePreviousPeriod.bind('click', function () {self.toggle_filter($usePreviousPeriod, $previousPeriod);});
        var $useSameLastYear = $dateFilterCmp.find('.o_account_reports_use-same-last-year');
        var $SameLastYear = $dateFilterCmp.find('.o_account_reports_same-last-year');
        $useSameLastYear.bind('click', function () {self.toggle_filter($useSameLastYear, $SameLastYear);});
        var $useCustomCmp = $dateFilterCmp.find('.o_account_reports_use-custom-cmp');
        var $CustomCmp = $dateFilterCmp.find('.o_account_reports_custom-cmp');
        $useCustomCmp.bind('click', function () {self.toggle_filter($useCustomCmp, $CustomCmp);});
        this.$searchview_buttons.find('.o_account_reports_one-filter').bind('click', function (event) {
            self.onChangeDateFilter(event); // First trigger the onchange
            $('.o_account_reports_datetimepicker input').each(function () { // Parse all the values of the date pickers
                $(this).val(formats.parse_value($(this).val(), {type: 'date'}));
            });

			//Set timeout created for delay 100 milli seconds. Without that delay it is not working properly
			setTimeout(function(){ 
				var report_context = { // Create the context that will be given to the restart method
	                date_filter: $(event.target).parents('li').data('value'),
	                date_from: self.$searchview_buttons.find("input[name='date_from']").val(),
	                date_to: self.$searchview_buttons.find("input[name='date_to']").val(),
	            };
	            if (self.date_filter_cmp !== 'no_comparison') { // Add elements to the context if needed
	                report_context.date_from_cmp = self.$searchview_buttons.find("input[name='date_from_cmp']").val();
	                report_context.date_to_cmp = self.$searchview_buttons.find("input[name='date_to_cmp']").val();
	            }
	            self.restart(report_context); // Then restart the report
	

 			}, 100);
			
        });
        this.$searchview_buttons.find('.o_account_reports_one-filter-cmp').bind('click', function (event) { // Same for the comparison filter
            self.onChangeCmpDateFilter(event);
            $('.o_account_reports_datetimepicker input').each(function () {
                $(this).val(formats.parse_value($(this).val(), {type: 'date'}));
            });
            var filter = $(event.target).parents('li').data('value');
            var report_context = {
                date_filter_cmp: filter,
                date_from_cmp: self.$searchview_buttons.find("input[name='date_from_cmp']").val(),
                date_to_cmp: self.$searchview_buttons.find("input[name='date_to_cmp']").val(),
            };
            if (filter === 'previous_period' || filter === 'same_last_year') {
                report_context.periods_number = $(event.target).siblings("input[name='periods_number']").val();
            }
			console.log(report_context);
            self.restart(report_context);
        });
        this.$searchview_buttons.find('.o_account_reports_one-filter-bool').bind('click', function (event) { // Same for the boolean filters
            var report_context = {};
            report_context[$(event.target).parents('li').data('value')] = !$(event.target).parents('li').hasClass('selected');
            self.restart(report_context);
        });
        if (this.report_context.multi_company) { // Same for th ecompany filter
            var def_company;
            new Model('account.financial.html.report').call('get_default_company',[this.odoo_context]).then(function(result) {
                def_company = result
            });
            this.$searchview_buttons.find('.o_account_reports_one-company').bind('click', function (event) {
                var report_context = {};
                var value = $(event.target).parents('li').data('value');
                console.log(value, 'value');
                console.log(def_company);
                new Model('account.financial.html.report').call('get_parent_company',[value]).then(function(result) {
                for (i=0;i<result.length;i++)
                    {    
                        if(self.report_context.company_ids.indexOf(value) === -1){
                            report_context.add_company_ids = result[i];
                        }
                        else {
                            report_context.remove_company_ids = result[i];
                        }
                        self.restart(report_context);
                    }
                });
            });
        }
        if (this.report_context.journal_ids) { // Same for the journal
            this.$searchview_buttons.find('.o_account_reports_one-journal').bind('click', function (event) {
                var report_context = {};
                var value = $(event.target).parents('li').data('value');
                if(self.report_context.journal_ids.indexOf(value) === -1){
                    report_context.add_journal_ids = value;
                }
                else {
                    report_context.remove_journal_ids = value;
                }
                self.restart(report_context);
            });
        }
        if (this.report_context.account_type) { // Same for the account types
            this.$searchview_buttons.find('.o_account_reports_one-account_type').bind('click', function (event) {
                var value = $(event.target).parents('li').data('value');
                self.restart({'account_type': value});
            });
        }
        if (this.report_type.analytic && this.report_context.analytic) { // Same for the tags filter
            this.$searchview_buttons.find(".o_account_reports_analytic_account_auto_complete").select2();
            var selection = [];
            for (i = 0; i < this.report_context.analytic_account_ids.length; i++) { 
                selection.push({id:i+1, text:this.report_context.analytic_account_ids[i][1]});
            }
            this.$searchview_buttons.find('.o_account_reports_analytic_account_auto_complete').data().select2.updateSelection(selection);
            this.$searchview_buttons.find(".o_account_reports_analytic_tag_auto_complete").select2();
            selection = [];
            var i;
            for (i = 0; i < this.report_context.analytic_tag_ids.length; i++) { 
                selection.push({id:i+1, text:this.report_context.analytic_tag_ids[i][1]});
            }
            this.$searchview_buttons.find('.o_account_reports_analytic_tag_auto_complete').data().select2.updateSelection(selection);
            this.$searchview_buttons.find('.o_account_reports_add_analytic_account').bind('click', function (event) {
                var report_context = {};
                var value = self.$searchview_buttons.find(".o_account_reports_analytic_account_auto_complete").select2("val");
                report_context.analytic_account_ids = value;
                self.restart(report_context);
            });
            this.$searchview_buttons.find('.o_account_reports_add_analytic_tag').bind('click', function (event) {
                var report_context = {};
                var value = self.$searchview_buttons.find(".o_account_reports_analytic_tag_auto_complete").select2("val");
                report_context.analytic_tag_ids = value;
                self.restart(report_context);
            });
        }
        this.$searchview_buttons.find('li').bind('click', function (event) {event.stopImmediatePropagation();});
        var l10n = core._t.database.parameters; // Get the localisation parameters
        var $datetimepickers = this.$searchview_buttons.find('.o_account_reports_datetimepicker');
        var options = { // Set the options for the datetimepickers
            language : moment.locale(),
            format : time.strftime_to_moment_format(l10n.date_format),
            icons: {
                date: "fa fa-calendar",
            },
            pickTime: false,
        };
        $datetimepickers.each(function () { // Start each datetimepicker
            $(this).datetimepicker(options);
            if($(this).data('default-value')) { // Set its default value if there is one
                $(this).data("DateTimePicker").setValue(moment($(this).data('default-value')));
            }
        });
        if (this.report_context.date_filter !== 'custom') { // For each foldable element in the dropdowns
            this.toggle_filter($useCustomDates, $CustomDates, false); // First toggle it so it is closed
            $dateFilter.bind('hidden.bs.dropdown', function () {self.toggle_filter($useCustomDates, $CustomDates, false);}); // When closing the dropdown, also close the foldable element
        }
        if (this.report_context.date_filter_cmp !== 'previous_period') {
            this.toggle_filter($usePreviousPeriod, $previousPeriod, false);
            $dateFilterCmp.bind('hidden.bs.dropdown', function () {self.toggle_filter($usePreviousPeriod, $previousPeriod, false);});
        }
        if (this.report_context.date_filter_cmp !== 'same_last_year') {
            this.toggle_filter($useSameLastYear, $SameLastYear, false);
            $dateFilterCmp.bind('hidden.bs.dropdown', function () {self.toggle_filter($useSameLastYear, $SameLastYear, false);});
        }
        if (this.report_context.date_filter_cmp !== 'custom') {
            this.toggle_filter($useCustomCmp, $CustomCmp, false);
            $dateFilterCmp.bind('hidden.bs.dropdown', function () {self.toggle_filter($useCustomCmp, $CustomCmp, false);});
        }
		
		this.$searchview_buttons.find('.date_year_select').bind('change', function (event) {
			var value = $('.date_year_select').val();
			$('.date_month').remove();
			$('.date_year').append('<select name="date_month" class="date_month"></select>');
			$('.date_month').append('<option value="">Select Period</option>');
			new Model('account.financial.html.report').call('get_fiscal_period_lines',[value]).then(function(result) {
				
				for (var res in result) {
					$('.date_month').append('<option value="'+result[res][0]+'">'+result[res][1]+'</option>');
				}
			});
		
        });

		$(document).on('change', '.date_month', function(event){ 
		    var value = $('.date_month').val();
			new Model('account.financial.html.report').call('start_end_date_for_months',[value]).then(function(result) {
				self.$searchview_buttons.find("input[name='date_from']").val(result[0]);
                self.$searchview_buttons.find("input[name='date_to']").val(result[1]);
				var result_months = []
				new Model('account.financial.html.report').call('get_fiscal_period_lines',[self.$searchview_buttons.find("select[name='year']").val()]).then(function(result) {
					var result_months = result;
					var report_context = { 
						// Create the context that will be given to the restart method
		                date_filter: $(event.target).parents('li').data('value'),
		                date_from: self.$searchview_buttons.find("input[name='date_from']").val(),
		                date_to: self.$searchview_buttons.find("input[name='date_to']").val(),
						year: self.$searchview_buttons.find("select[name='year']").val(),
						months : result_months,
		            };
		            if (self.date_filter_cmp !== 'no_comparison') { // Add elements to the context if needed
		                report_context.date_from_cmp = self.$searchview_buttons.find("input[name='date_from_cmp']").val();
		                report_context.date_to_cmp = self.$searchview_buttons.find("input[name='date_to_cmp']").val();
		            }
		            self.restart(report_context); // Then restart the report
				});
				
			});
		}); 

        return this.$searchview_buttons;
    },
    
    onChangeDateFilter: function(event) {
        var self = this;
        var no_date_range = !this.report_type.date_range;
        var today = new Date();
        var dt;
        switch($(event.target).parents('li').data('value')) {
            case 'today':
                dt = new Date();
                self.$searchview_buttons.find("input[name='date_to']").parents('.o_account_reports_datetimepicker').data("DateTimePicker").setValue(moment(dt));
                break;
            case 'last_month':
				dt = new Date();
				var month = dt.getUTCMonth() + 1; //months from 1-12
				var day = dt.getUTCDate();
				var year = dt.getUTCFullYear();				
				var newdate = year + "-" + month + "-" + day;
				new Model('account.financial.html.report').call('get_last_month_fiscal_period',[newdate]).then(function(result) {
		     		if(result.from_date == 'No Period') {
						dt = new Date();
		                dt.setDate(0); // Go to last day of last month (date to)
		                self.$searchview_buttons.find("input[name='date_to']").parents('.o_account_reports_datetimepicker').data("DateTimePicker").setValue(moment(dt));
		                if (!no_date_range) {
		                    dt.setDate(1); // and then first day of last month (date from)
		                    self.$searchview_buttons.find("input[name='date_from']").parents('.o_account_reports_datetimepicker').data("DateTimePicker").setValue(moment(dt));
		                }
	                 
					}
					else {
						self.$searchview_buttons.find("input[name='date_from']").val(result.from_date);
                        self.$searchview_buttons.find("input[name='date_to']").val(result.to_date);
						var report_context = { 
							// Create the context that will be given to the restart method
			                date_filter: $(event.target).parents('li').data('value'),
			                date_from: self.$searchview_buttons.find("input[name='date_from']").val(),
			                date_to: self.$searchview_buttons.find("input[name='date_to']").val(),
			            };
			            if (self.date_filter_cmp !== 'no_comparison') { // Add elements to the context if needed
			                report_context.date_from_cmp = self.$searchview_buttons.find("input[name='date_from_cmp']").val();
			                report_context.date_to_cmp = self.$searchview_buttons.find("input[name='date_to_cmp']").val();
			            }
			            self.restart(report_context); // Then restart the report
					}
				});
                
                break;
            case 'last_quarter':
				dt = new Date();
				var month = dt.getUTCMonth() + 1; //months from 1-12
				var day = dt.getUTCDate();
				var year = dt.getUTCFullYear();				
				var newdate = year + "-" + month + "-" + day;
				new Model('account.financial.html.report').call('get_last_quarter_fiscal_period',[newdate]).then(function(result) {
		     		if(result.from_date == 'No Period') {
						dt = new Date();
		                dt.setMonth((moment(dt).quarter() - 1) * 3); // Go to the first month of this quarter
		                dt.setDate(0); // Then last day of last month (= last day of last quarter)
		                self.$searchview_buttons.find("input[name='date_to']").parents('.o_account_reports_datetimepicker').data("DateTimePicker").setValue(moment(dt));
		                if (!no_date_range) {
		                    dt.setDate(1);
		                    dt.setMonth(dt.getMonth() - 2);
		                    self.$searchview_buttons.find("input[name='date_from']").parents('.o_account_reports_datetimepicker').data("DateTimePicker").setValue(moment(dt));
		                }
	                 
					}
					else {
						self.$searchview_buttons.find("input[name='date_from']").val(result.from_date);
                        self.$searchview_buttons.find("input[name='date_to']").val(result.to_date);
						var report_context = { 
							// Create the context that will be given to the restart method
			                date_filter: $(event.target).parents('li').data('value'),
			                date_from: self.$searchview_buttons.find("input[name='date_from']").val(),
			                date_to: self.$searchview_buttons.find("input[name='date_to']").val(),
			            };
			            if (self.date_filter_cmp !== 'no_comparison') { // Add elements to the context if needed
			                report_context.date_from_cmp = self.$searchview_buttons.find("input[name='date_from_cmp']").val();
			                report_context.date_to_cmp = self.$searchview_buttons.find("input[name='date_to_cmp']").val();
			            }
			            self.restart(report_context); // Then restart the report
					}
				});
                
                break;
            case 'last_year':
				dt = new Date();
				var month = dt.getUTCMonth() + 1; //months from 1-12
				var day = dt.getUTCDate();
				var year = dt.getUTCFullYear();				
				var newdate = year + "-" + month + "-" + day;
				new Model('account.financial.html.report').call('get_last_year_fiscal_period',[newdate]).then(function(result) {
		     		if(result.from_date == 'No Period') {
						if (today.getMonth() + 1 < self.fy.fiscalyear_last_month || (today.getMonth() + 1 === self.fy.fiscalyear_last_month && today.getDate() <= self.fy.fiscalyear_last_day)) {
		                    dt = new Date(today.getFullYear() - 1, self.fy.fiscalyear_last_month - 1, self.fy.fiscalyear_last_day, 12, 0, 0, 0);
		                }
		                else {
		                    dt = new Date(today.getFullYear(), self.fy.fiscalyear_last_month - 1, self.fy.fiscalyear_last_day, 12, 0, 0, 0);
		                }
		                $("input[name='date_to']").parents('.o_account_reports_datetimepicker').data("DateTimePicker").setValue(moment(dt));
		                if (!no_date_range) {
		                    dt.setDate(dt.getDate() + 1);
		                    dt.setFullYear(dt.getFullYear() - 1);
		                    self.$searchview_buttons.find("input[name='date_from']").parents('.o_account_reports_datetimepicker').data("DateTimePicker").setValue(moment(dt));
		                }
	                 
					}
					else {
						self.$searchview_buttons.find("input[name='date_from']").val(result.from_date);
                        self.$searchview_buttons.find("input[name='date_to']").val(result.to_date);
						var report_context = { 
							// Create the context that will be given to the restart method
			                date_filter: $(event.target).parents('li').data('value'),
			                date_from: self.$searchview_buttons.find("input[name='date_from']").val(),
			                date_to: self.$searchview_buttons.find("input[name='date_to']").val(),
			            };
			            if (self.date_filter_cmp !== 'no_comparison') { // Add elements to the context if needed
			                report_context.date_from_cmp = self.$searchview_buttons.find("input[name='date_from_cmp']").val();
			                report_context.date_to_cmp = self.$searchview_buttons.find("input[name='date_to_cmp']").val();
			            }
			            self.restart(report_context); // Then restart the report
					}
				});
                
                break;
            case 'this_month':
                dt = new Date();
				var month = dt.getUTCMonth() + 1; //months from 1-12
				var day = dt.getUTCDate();
				var year = dt.getUTCFullYear();				
				var newdate = year + "-" + month + "-" + day;
				new Model('account.financial.html.report').call('get_fiscal_period_start_date',[newdate]).then(function(result) {
		     		if(result == 'No Period')
					{
						dt.setDate(1);
						self.$searchview_buttons.find("input[name='date_from']").parents('.o_account_reports_datetimepicker').data("DateTimePicker").setValue(moment(dt));
						
					}
					else {
						self.$searchview_buttons.find("input[name='date_from']").val(result);
					}
					
		     	});

                
                
                new Model('account.financial.html.report').call('get_fiscal_period_end_date',[newdate]).then(function(result) {
				
				if(result == 'No Period')
					{
						dt.setMonth(dt.getMonth() + 1);
                		dt.setDate(0);
						self.$searchview_buttons.find("input[name='date_to']").parents('.o_account_reports_datetimepicker').data("DateTimePicker").setValue(moment(dt));
						
					}
					else {
						self.$searchview_buttons.find("input[name='date_to']").val(result);
					}
				var report_context = { 
							// Create the context that will be given to the restart method
			                date_filter: $(event.target).parents('li').data('value'),
			                date_from: self.$searchview_buttons.find("input[name='date_from']").val(),
			                date_to: self.$searchview_buttons.find("input[name='date_to']").val(),
			            };
			            if (self.date_filter_cmp !== 'no_comparison') { // Add elements to the context if needed
			                report_context.date_from_cmp = self.$searchview_buttons.find("input[name='date_from_cmp']").val();
			                report_context.date_to_cmp = self.$searchview_buttons.find("input[name='date_to_cmp']").val();
			            }
			            self.restart(report_context); // Then restart the report
		     	});
                break;
            case 'this_quarter':
                dt = new Date();
				if(!no_date_range) {
					var month = dt.getUTCMonth() + 1; //months from 1-12
					var day = dt.getUTCDate();
					var year = dt.getUTCFullYear();				
					var newdate = year + "-" + month + "-" + day;
					new Model('account.financial.html.report').call('get_fiscal_period_quarter',[newdate]).then(function(result) {
						if(result.from_date == 'No Period') {
							dt = new moment();
	                        self.$searchview_buttons.find("input[name='date_to']").parents('.o_account_reports_datetimepicker').data("DateTimePicker").setValue(dt.endOf('quarter'));
	                        self.$searchview_buttons.find("input[name='date_from']").parents('.o_account_reports_datetimepicker').data("DateTimePicker").setValue(dt.startOf('quarter'));
						}
						else {
							self.$searchview_buttons.find("input[name='date_from']").val(result.from_date);
                        	self.$searchview_buttons.find("input[name='date_to']").val(result.to_date);
						var report_context = { 
							// Create the context that will be given to the restart method
			                date_filter: $(event.target).parents('li').data('value'),
			                date_from: self.$searchview_buttons.find("input[name='date_from']").val(),
			                date_to: self.$searchview_buttons.find("input[name='date_to']").val(),
			            };
			            if (self.date_filter_cmp !== 'no_comparison') { // Add elements to the context if needed
			                report_context.date_from_cmp = self.$searchview_buttons.find("input[name='date_from_cmp']").val();
			                report_context.date_to_cmp = self.$searchview_buttons.find("input[name='date_to_cmp']").val();
			            }
			            self.restart(report_context); // Then restart the report
						}
                    
					});
				}
				else {
					self.$searchview_buttons.find("input[name='date_to']").parents('.o_account_reports_datetimepicker').data("DateTimePicker").setValue(dt.endOf('quarter'));
				}
                
                break;
            case 'this_year':
				dt = new Date();
				var month = dt.getUTCMonth() + 1; //months from 1-12
				var day = dt.getUTCDate();
				var year = dt.getUTCFullYear();				
				var newdate = year + "-" + month + "-" + day;
				new Model('account.financial.html.report').call('get_fiscal_period_year',[newdate]).then(function(result) {
					if(result.from_date == 'No Period') {
						if (today.getMonth() + 1 < self.fy.fiscalyear_last_month || (today.getMonth() + 1 === self.fy.fiscalyear_last_month && today.getDate() <= self.fy.fiscalyear_last_day)) {
					        dt = new Date(today.getFullYear(), self.fy.fiscalyear_last_month - 1, self.fy.fiscalyear_last_day, 12, 0, 0, 0);
					    }
					    else {
					        dt = new Date(today.getFullYear() + 1, self.fy.fiscalyear_last_month - 1, self.fy.fiscalyear_last_day, 12, 0, 0, 0);
					    }
					    self.$searchview_buttons.find("input[name='date_to']").parents('.o_account_reports_datetimepicker').data("DateTimePicker").setValue(moment(dt));
					    if (!no_date_range) {
					        dt.setDate(dt.getDate() + 1);
					        dt.setFullYear(dt.getFullYear() - 1);
					        self.$searchview_buttons.find("input[name='date_from']").parents('.o_account_reports_datetimepicker').data("DateTimePicker").setValue(moment(dt));
					    }
					}
					else {
						self.$searchview_buttons.find("input[name='date_from']").val(result.from_date);
						self.$searchview_buttons.find("input[name='date_to']").val(result.to_date);
						var report_context = { 
							// Create the context that will be given to the restart method
			                date_filter: $(event.target).parents('li').data('value'),
			                date_from: self.$searchview_buttons.find("input[name='date_from']").val(),
			                date_to: self.$searchview_buttons.find("input[name='date_to']").val(),
			            };
			            if (self.date_filter_cmp !== 'no_comparison') { // Add elements to the context if needed
			                report_context.date_from_cmp = self.$searchview_buttons.find("input[name='date_from_cmp']").val();
			                report_context.date_to_cmp = self.$searchview_buttons.find("input[name='date_to_cmp']").val();
			            }
			            self.restart(report_context); // Then restart the report
					}
                
				});
                
                break;
        }
        if (this.$searchview_buttons.find("input[name='date_to_cmp']").length !== 0) {
            self.onChangeCmpDateFilter(event, true);
        }
    },

	
	
});

});





