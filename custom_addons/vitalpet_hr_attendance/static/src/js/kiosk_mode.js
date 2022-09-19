odoo.define('vitalpet_hr_attendance.kiosk_mode', function (require) {
"use strict";

var core = require('web.core');
var Model = require('web.Model');
var Widget = require('web.Widget');
var Session = require('web.session');
var web_client = require('web.web_client');

var BarcodeHandlerMixin = require('barcodes.BarcodeHandlerMixin');

var QWeb = core.qweb;
var _t = core._t;


var KioskMode = Widget.extend(BarcodeHandlerMixin, {
    events: {
    	
        "click .o_hr_attendance_button_employees": function(){ 
			var hr_employee = new Model('hr.employee');
			hr_employee.call('get_current_contract_employees', [])
	            .then(function(result) {
					web_client.action_manager.do_action({
						views: [[result['view_id'], 'kanban']],
						view_id: [result['view_id']],
			            view_type: 'form',
			            view_mode: 'kanban',
			            res_model: 'hr.employee',
			            name: "Employees",
			            type: 'ir.actions.act_window',
			            domain:  [['id', 'in',result['employee_list']]],
			            target: 'current',
					});
	            });
		},
		
		
		
		
		
		
		
//        "click .o_hr_attendance_button_employees": function(){ this.do_action('hr_attendance.hr_employee_attendance_action_kanban'); },
    },

    
   
    
    
    
    
    
    
    init: function (parent, action) {
        // Note: BarcodeHandlerMixin.init calls this._super.init, so there's no need to do it here.
        // Yet, "_super" must be present in a function for the class mechanism to replace it with the actual parent method.
        this._super;
        BarcodeHandlerMixin.init.apply(this, arguments);
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
    
    
    start: function () {
        var self = this;
        self.session = Session;
        var res_company = new Model('res.company');
        res_company.query(['name'])
           .filter([['id', '=', self.session.company_id]])
           .all()
           .then(function (companies){
                self.company_name = companies[0].name;
                self.company_image_url = self.session.url('/web/image', {model: 'res.company', id: self.session.company_id, field: 'logo',})
                self.$el.html(QWeb.render("HrAttendanceKioskMode", {widget: self}));
                self.$el.html(QWeb.render("HrLeavesKioskMode", {widget: self}));
                self.start_clock();
            });
        return self._super.apply(this, arguments);
    },
    
    start_clock: function() {
        this.clock_start = setInterval(function() {this.$(".o_hr_attendance_clock").text(new Date().toLocaleTimeString(navigator.language, {hour: '2-digit', minute:'2-digit'}));}, 500);
        // First clock refresh before interval to avoid delay
        this.$(".o_hr_attendance_clock").text(new Date().toLocaleTimeString(navigator.language, {hour: '2-digit', minute:'2-digit'}));
    },

    destroy: function () {
        clearInterval(this.clock_start);
        this._super.apply(this, arguments);
    },

    
});

core.action_registry.add('hr_attendance_kiosk_mode', KioskMode);

return KioskMode;

});
