/*global $, _, PDFJS */
odoo.define('vitalpet_budgeting_product_category.vitalpet_budgeting_category_dashboard', function (require) {
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
    template_search: "vitalpet_budgeting_product_category.searchView",
    template: "vitalpet_budgeting_product_category.HomePage",
	searchview_hidden: true,
    //Dashboard cleck events
    events: {
        'click .o_dashboard_action': 'on_dashboard_action_clicked', 
    },


    init: function(parent, context) {
        this._super(parent, context);
        this.dashboards_templates = ['vitalpet_budgeting_product_category.dashboard_bills'];
    },


    willStart: function() {
        return this.get_html();
    },



    start: function() {
        var self = this;
        return this._super().then(function() {
        	/*self.update_cp();*/
            self.render_dashboards();
            self.$el.parent().addClass('oe_background_grey');
        });
    },


    restart: function(given_context) {
        var self = this;
        this.given_context = given_context;
        return this.get_html().then(function() {
            self.set_html();
        });
    },



    
  /*  on_reverse_breadcrumb: function() {
        web_client.do_push_state({});
        this.update_cp();
    },
*/

    get_html: function() {
        var self = this;
        var defs = [];
/*        self.render_buttons();*/
        self.render_searchview_buttons();
        self.render_searchview();
        /*self.render_pager();*/
        /*defs.push(self.update_cp())*/;
        return $.when.apply($, defs);
    },



    render_searchview: function() {
        this.$searchview = '';
        return this.$searchview;
    },

    render_searchview_buttons: function() {
        var self = this;
        // Render the searchview buttons and bind them to the correct actions
        this.$searchview_buttons = $(QWeb.render("vitalpet_budgeting_product_category.searchView", {report_type: this.report_type, context: this.report_context}));
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
            self.restart(report_context);
        });
        this.$searchview_buttons.find('.o_account_reports_one-filter-bool').bind('click', function (event) { // Same for the boolean filters
            var report_context = {};
            report_context[$(event.target).parents('li').data('value')] = !$(event.target).parents('li').hasClass('selected');
            self.restart(report_context);
        });
       /* if (this.report_context.multi_company) {*/ // Same for th ecompany filter
            this.$searchview_buttons.find('.o_account_reports_one-company').bind('click', function (event) {
                var report_context = {};
                var value = $(event.target).parents('li').data('value');
                if(self.report_context.company_ids.indexOf(value) === -1){
                    report_context.add_company_ids = value;
                }
                else {
                    report_context.remove_company_ids = value;
                }
                self.restart(report_context);
            });
/*        }*/
        /*if (this.report_context.journal_ids) { // Same for the journal
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
        }*/
        /*if (this.report_context.account_type) { // Same for the account types
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
        }*/
        return this.$searchview_buttons;
    },



   /* //To update breadcrumbs
    update_cp: function() {
        var self = this;
        
        this.update_control_panel({
            cp_content: {
                $searchview: this.$searchview,
            },
            breadcrumbs: this.getParent().get_breadcrumbs(),
        });
    },*/
// Click events
    on_dashboard_action_clicked: function(ev){
        ev.preventDefault();
        var $action = $(ev.currentTarget);
        var action_name = $action.attr('name');
        var action_id = $action.attr('id');
        var action_extra = $action.data('extra');
        var additional_context = {};
        // TODO: find a better way to add defaults to search view
        if (action_id === 'today')  {
            additional_context.search_default_today = 1;
        }
        if (action_id === 'overdue')  {
            additional_context.search_default_overdue = 1;
        } 
        if (action_id === 'overdue_30days')  {
            additional_context.search_default_overdue_30days = 1;
        }
        if (action_id === 'overdue_60days')  {
            additional_context.search_default_overdue_60days = 1;
        } 
        if (action_id === 'overdue_90days')  {
            additional_context.search_default_overdue_90days = 1;
        }
		if (action_id === 'manual_check')  {
            additional_context.search_default_manual_check = 1;
        }
		if (action_id === 'ach')  {
            additional_context.search_default_ach = 1;
        }
		if (action_id === 'no_activity_12_month')  {
            additional_context.search_default_no_activity_12_month = 1;
        }
 
        

        this.do_action(action_name, {additional_context: additional_context});
    },
    // fetch_dashboard_data will contains all data related to dashboard
    render_dashboards: function() {
	    var self = this;
	        _.each(this.dashboards_templates, function(template) {
	        	 new Model('budget.dashboard').call('fetch_dashboard_data', []).then(function(result){
		      		  self.$('.o_website_dashboard').append(QWeb.render(template, {widget: self,values: result,}));
		      	  });
	        	
	        });
	    }
});
    core.action_registry.add('vitalpet_budgeting_category_dashboard', Dashboard);
    return Dashboard;
});

