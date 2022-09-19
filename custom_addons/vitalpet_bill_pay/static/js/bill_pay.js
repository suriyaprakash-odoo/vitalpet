odoo.define('vitalpet_bill_pay.inbox', function (require) {
"use strict";
var core = require('web.core');
var formats = require('web.formats');
var Model = require('web.Model');
var session = require('web.session');
var KanbanView = require('web_kanban.KanbanView');

var QWeb = core.qweb;

var _t = core._t;
var _lt = core._lt;

var BillpayInboxView = KanbanView.extend({
	display_name: _lt('Inbox'),
	searchview_hidden: false,
    events: {
        'change .o_image_upload': 'on_file_upload',
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
            var sales_dashboard = QWeb.render('vitalpet_bill_pay.BillpayInbox', {
                widget: self,
                show_demo: self.show_demo,
                values: result,
            });
            super_render.call(self);
            $(sales_dashboard).prependTo(self.$el);
        });
    },
    
    save_file: function (file_buffer, file_name) {
        var self = this;
        new Model("billpay.inbox").call("create_record_inbox", [file_buffer, file_name]).then(function(data) {
            console.log(data);
            location.reload();
        });
    },
    
    
    on_file_upload: function (ev) {
        var self = this,
            file = ev.target.files[0],
            is_image = /^image\/.*/.test(file.type),
            loaded = false;
        var file_name = file.name;
        var file_type = file.type;
        
        if (file.size / 1024 / 1024 > 25) {
            this.display_alert(_t("File is too big. File size cannot exceed 25MB"));
            this.reset_file();
            return;
        }
        var BinaryReader = new FileReader();
		// file read as DataURL
        BinaryReader.readAsDataURL(file);
        BinaryReader.onloadend = function (upload) {
            var file_buffer = upload.target.result;
            self.save_file(file_buffer, file.name);
        };
    }
});

core.view_registry.add('billpay_inbox_upload', BillpayInboxView);

return BillpayInboxView;

});
