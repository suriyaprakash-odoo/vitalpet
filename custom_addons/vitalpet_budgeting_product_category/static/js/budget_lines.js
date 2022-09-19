odoo.define('vitalpet_budgeting_product_category.inbox', function (require) {
"use strict";
var core = require('web.core');
var formats = require('web.formats');
var Model = require('web.Model');
var session = require('web.session');
var KanbanView = require('web_kanban.KanbanView');
var web_client = require('web.web_client');

var QWeb = core.qweb;

var _t = core._t;
var _lt = core._lt;

var BillpayInboxView = KanbanView.extend({
    display_name: _lt('Inbox'),
    events: {
        'click .kanban_budget_lines': 'on_click_multi_practice',
        'click .kanban_budget_lines_monthly': 'on_click_multi_practice_monthly',
        'click .kanban_budget_lines_quarterly': 'on_click_multi_practice_quarterly',
        'click .kanban_budget_lines_yearly': 'on_click_multi_practice_yearly',
        'click .kanban_budget_lines_yearly_consolidate': 'on_click_multi_practice_yearly_consolidate',
        'click .kanban_budget_lines_quarterly_consolidate': 'on_click_multi_practice_quarterly_consolidate',
        'click .kanban_budget_lines_monthly_consolidate': 'on_click_multi_practice_monthly_consolidate',
    },  
    fetch_data: function() {
        // Overwrite this function with useful data
        return $.when();
    },
    render: function() {
        var super_render = this._super;
        var self = this;

        return this.fetch_data().then(function(result){
            self.show_demo = result && result.nb_opportunities === 0;
            console.log(result);
            var sales_dashboard = QWeb.render('vitalpet_budgeting_product_category.BillpayInbox', {
                widget: self,
                show_demo: self.show_demo,
                values: result,
            });
            super_render.call(self);
            $(sales_dashboard).prependTo(self.$el);

           setTimeout(function(){
                $(".new_button_budget").remove();  
                $(".o_control_panel .o_cp_left .o_cp_buttons").html("");
                $(".breadcrumb li").hide();
                $(".breadcrumb li:first,.breadcrumb li:last").show();
                if($(".o_control_panel li.active").text()=="Budget Category Quarterly" || $(".o_control_panel li.active").text()=="Budget Category Yearly"){
                    $(".o_control_panel .o_cp_left .o_cp_buttons").append('<button class="new_button_budget_monthly" style="margin-left:30px;background: #875a7b;border: 0;color: #fff;padding: 7px 15px;margin-left: 0;margin-top: 0px;font-size: 15px;" >Monthly</button>');
                }
                if($(".o_control_panel li.active").text()=="Budget" || $(".o_control_panel li.active").text()=="Budget Category Yearly"){
                    $(".o_control_panel .o_cp_left .o_cp_buttons").append('<button class="new_button_budget_quarterly" style="margin-left:30px;background: #875a7b;border: 0;color: #fff;padding: 7px 15px;margin-left: 0;margin-top: 0px;font-size: 15px;" >Quarterly</button>');
                }
                if($(".o_control_panel li.active").text()=="Budget Category Quarterly" || $(".o_control_panel li.active").text()=="Budget"){
                    $(".o_control_panel .o_cp_left .o_cp_buttons").append('<button class="new_button_budget_yearly" style="margin-left:30px;background: #875a7b;border: 0;color: #fff;padding: 7px 15px;margin-left: 0;margin-top: 0px;font-size: 15px;" >Yearly</button>');
                }
                if($(".o_control_panel li.active").text()=="Budget Consolidation Quarterly" || $(".o_control_panel li.active").text()=="Budget Consolidation Monthly"){
                    $(".o_control_panel .o_cp_left .o_cp_buttons").append('<button class="consolidate_button_budget_yearly" style="margin-left:30px;background: #875a7b;border: 0;color: #fff;padding: 7px 15px;margin-left: 0;margin-top: 0px;font-size: 15px;" >Yearly</button>');
                }
                if($(".o_control_panel li.active").text()=="Budget Consolidation Monthly" || $(".o_control_panel li.active").text()=="Budget Consolidation Yearly"){
                    $(".o_control_panel .o_cp_left .o_cp_buttons").append('<button class="consolidate_button_budget_quarterly" style="margin-left:30px;background: #875a7b;border: 0;color: #fff;padding: 7px 15px;margin-left: 0;margin-top: 0px;font-size: 15px;" >Quarterly</button>');
                }
                if($(".o_control_panel li.active").text()=="Budget Consolidation Quarterly" || $(".o_control_panel li.active").text()=="Budget Consolidation Yearly"){
                    $(".o_control_panel .o_cp_left .o_cp_buttons").append('<button class="consolidate_button_budget_monthly" style="margin-left:30px;background: #875a7b;border: 0;color: #fff;padding: 7px 15px;margin-left: 0;margin-top: 0px;font-size: 15px;" >Monthly</button>');
                }
            });

        });
    },

    on_click_multi_practice: function (ev) {
        var self = this;
        new Model("budget.category.lines").call("get_budget_lines", ["test"]).then(function(data) {
            var arr=data.toString().split(",");
            var cont="";
            for(name=0;name<arr.length;name++){
                var c_tot_act=0,c_tot_plan=0,m_tot_act=0,m_tot_plan=0,p_tot_act=0,p_tot_plan=0;
                $('.o_kanban_view .o_kanban_record').each(function () {
                    console.log($(this).find(".c_name span").text()+"--"+arr[name]);
                    if($(this).find(".c_name span").text()==arr[name]){
                        c_tot_plan=c_tot_plan+parseFloat($(this).find(".c_planned_value span").text().replace(",", ""));
                        c_tot_act=c_tot_act+parseFloat($(this).find(".c_actual_value").text().replace(",", ""));

                        m_tot_plan=m_tot_plan+parseFloat($(this).find(".m_planned_value span").text().replace(",", ""));
                        m_tot_act=m_tot_act+parseFloat($(this).find(".m_actual_value").text().replace(",", ""));

                        p_tot_plan=p_tot_plan+parseFloat($(this).find(".p_planned_value span").text().replace(",", ""));
                        p_tot_act=p_tot_act+parseFloat($(this).find(".p_actual_value").text().replace(",", ""));
                    }
                });

                cont=cont+'<div style="width:100%;background:#c7d5ff;border-radius: 2px;background: #fff;padding: 6px;margin-bottom: 5px;" ><table class="oe_budget_oneline" style="width: 100%;border:0;"><thead><tr style="background:#c7d5ff;"><td style="max-width:120px; font-size: 9px;border-top:1px solid #000;border-left:1px solid #000; text-align: right;" class="c_name">Total</td><td style="max-width:60px;white-space: normal;border-top:1px solid #000;border-left:1px solid #000;border-right:1px solid #000;border-bottom:1px solid #000; font-size: 10px; text-align: center;" title="Amount on Global budget"><span>Planned</span></td><td style="max-width:60px;white-space: normal;border-top:1px solid #000;border-left:1px solid #000;border-right:1px solid #000;border-bottom:1px solid #000; font-size: 10px;text-align: center; " title="Amount computed"><span>Actual</span></td><td style="max-width:60px;white-space: normal;border-top:1px solid #000;border-left:1px solid #000;border-right:1px solid #000;border-bottom:1px solid #000; font-size: 9px; text-align: center;" title="Amount computed"><span>Var/Grth v LY</span></td></tr><tr style="background:#ffc7c7;"><td style="max-width:120px; font-size: 9px;border-top:1px solid #000;border-left:1px solid #000; text-align: right;">'+arr[name]+'</td><td style="max-width:60px;white-space: normal;border-top:1px solid #000;border-left:1px solid #000;border-right:1px solid #000;border-bottom:1px solid #000; font-size: 10px; text-align: center;" title="Amount on Global budget" class="c_planned_value" ><span>'+c_tot_plan+'</span></td><td style="max-width:60px;white-space: normal;border-top:1px solid #000;border-left:1px solid #000;border-right:1px solid #000;border-bottom:1px solid #000; font-size: 10px;text-align: center; " title="Amount computed" class="c_actual_value" >'+c_tot_act+'</td><td style="max-width:60px;white-space: normal;border-top:1px solid #000;border-left:1px solid #000;border-right:1px solid #000;border-bottom:1px solid #000; font-size: 9px; text-align: center;" title="Amount computed" class="c_var"><span>0.00</span></td></tr><tr t-if="record.margin" style="background:#c7d5ff;"><td style="max-width:120px; font-size: 9px;border-top:1px solid #000;border-left:1px solid #000; text-align: right;border-bottom: 1px solid #000">Margin</td><td style="max-width:60px;white-space: normal;border-top:1px solid #000;border-left:1px solid #000;border-right:1px solid #000;border-bottom:1px solid #000; font-size: 10px; text-align: center;" title="Amount on Global budget" class="m_planned_value"><span>'+m_tot_plan+'</span></td><td style="max-width:60px;white-space: normal;border-top:1px solid #000;border-left:1px solid #000;border-right:1px solid #000;border-bottom:1px solid #000; font-size: 10px;text-align: center; " title="Amount computed" class="m_actual_value"><span>'+m_tot_act+'</span></td><td style="max-width:60px;white-space: normal;border-top:1px solid #000;border-left:1px solid #000;border-right:1px solid #000;border-bottom:1px solid #000; font-size: 9px; text-align: center;" title="Amount computed" class="m_var"><span>0.00</span></td></tr><tr style="background:#c7d5ff;"><td style="max-width:120px; font-size: 9px;border-top:1px solid #000;border-left:1px solid #000; text-align: right;border-bottom: 1px solid #000">%Of Net Revenue</td><td style="max-width:60px;white-space: normal;border-top:1px solid #000;border-left:1px solid #000;border-right:1px solid #000;border-bottom:1px solid #000; font-size: 10px; text-align: center;" title="Amount on Global budget" class="p_planned_value"><span>'+p_tot_plan+'</span></td><td style="max-width:60px;white-space: normal;border-top:1px solid #000;border-left:1px solid #000;border-right:1px solid #000;border-bottom:1px solid #000; font-size: 10px;text-align: center; " title="Amount computed" class="p_actual_value"><span>'+p_tot_act+'</span></td><td style="max-width:60px;white-space: normal;border-top:1px solid #000;border-left:1px solid #000;border-right:1px solid #000;border-bottom:1px solid #000; font-size: 9px; text-align: center;" title="Amount computed" class="p_var"><span>'+0.00+'</span></td></tr></thead></table></div><div class="oe_clear"></div>'
            }
            cont='<div style="font-size: 18px;font-weight: 300;max-width: 100%;white-space: nowrap;overflow: hidden;text-overflow: ellipsis;vertical-align: top;padding-top: 5px;color: #fff;padding-bottom: 16px;">Cumulative Result</div>'+cont;
            $(".o_kanban_view").html('<div class="o_kanban_record" style="background: #878787;box-shadow: none;">'+cont+'</div>');
        });

    },
    on_click_multi_practice_monthly: function (ev) {
        var budget = new Model('budget.category.lines');
        budget.call('validate_budget_lines', [[1], 0])
        .then(function(result) {

            web_client.action_manager.do_action(result);
                
        });
    },
    on_click_multi_practice_quarterly: function (ev) {
        var budget = new Model('budget.category.lines');
        budget.call('validate_budget_lines', [[1], 1])
        .then(function(result) {

            web_client.action_manager.do_action(result);
                
        });
    },
    on_click_multi_practice_yearly: function (ev) {
        var budget = new Model('budget.category.lines');
        budget.call('validate_budget_lines', [[1], 2])
        .then(function(result) {

            web_client.action_manager.do_action(result);
        
        });
    },
    on_click_multi_practice_yearly_consolidate: function (ev) {
        var budget = new Model('budget.consolidate.monthly');
        budget.call('validate_budget_consolidate', [[1], 2])
        .then(function(result) {

            web_client.action_manager.do_action(result);
        
        });
    },
    on_click_multi_practice_quarterly_consolidate: function (ev) {
        var budget = new Model('budget.consolidate.monthly');
        budget.call('validate_budget_consolidate', [[1], 1])
        .then(function(result) {

            web_client.action_manager.do_action(result);
        
        });
    },
    on_click_multi_practice_monthly_consolidate: function (ev) {
        var budget = new Model('budget.consolidate.monthly');
        budget.call('validate_budget_consolidate', [[1], 0])
        .then(function(result) {

            web_client.action_manager.do_action(result);
        
        });
    }
});

core.view_registry.add('budget_kanban_view', BillpayInboxView);
//
//return BillpayInboxView;




});



$(document).ready(function(){
    $('body').delegate('.new_button_budget','click',function() {
        $(".kanban_budget_lines").click();
    });
    $('body').delegate('.new_button_budget_monthly','click',function() {
        $(".kanban_budget_lines_monthly").click();
    });
    $('body').delegate('.new_button_budget_quarterly','click',function() {
        $(".kanban_budget_lines_quarterly").click();
    });
    $('body').delegate('.new_button_budget_yearly','click',function() {
        $(".kanban_budget_lines_yearly").click();
    });
    $('body').delegate('.consolidate_button_budget_yearly','click',function() {
        $(".kanban_budget_lines_yearly_consolidate").click();
    });
    $('body').delegate('.consolidate_button_budget_quarterly','click',function() {
        $(".kanban_budget_lines_quarterly_consolidate").click();
    });
    $('body').delegate('.consolidate_button_budget_monthly','click',function() {
        $(".kanban_budget_lines_monthly_consolidate").click();
    });
});



