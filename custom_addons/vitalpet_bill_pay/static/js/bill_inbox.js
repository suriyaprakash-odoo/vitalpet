/*global $, _, PDFJS */
odoo.define('vitalpet_bill_pay.vitalpet_bill_pay', function (require) {
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
    template: "vitalpet_bill_pay.HomePage",

    events: {
        "change input.o_form_input_file": "on_file_upload",
        'click i.attachment_delete': 'delete_inbox',
    },

    init: function(parent, context) {
        this._super(parent, context);
        this.dashboards_templates = ['vitalpet_bill_pay.dashboard_visits'];
    },
    willStart: function() {
        var self = this;
        return this._super().then(function() {
            return $.when(
                self.fetch_data()
            );
        });
    },

    start: function() {
        var self = this;
        return this._super().then(function() {
            self.render_dashboards();
            self.$el.parent().addClass('oe_background_grey');
        });
    },

    delete_inbox: function(e) {
        var retVal = confirm("Do you really want to unlink this product from sale?");
        if (retVal == true) {
            new Model("billpay.inbox").call('unlink_inbox', [[e.currentTarget.id]]).done();
            $("#" + e.currentTarget.id).remove();
            return true;
        }
    },

// Display uploaded data
    fetch_data: function() {
        var self = this;
        self.$('.o_web_settings_dashboard_col').empty();
        new Model("billpay.inbox").call("get_inbox", []).then(function(records){
            _.each(records, function (line) {
                var html_content ='<div class="col-sm-3 o_web_settings_dashboard_col">\n'+
                          '  <div class="o_kanban_card_manage_section o_kanban_manage_view">\n'+
                          '     <div class="oe_kanban_color_0 o_kanban_record" style="margin-top: -20px;margin-left: -15px;">\n'+
                          '          <div class="container o_kanban_card_manage_pane o_visible">\n'+

                          '              <div class="row inbox_header">\n'+
                          '                 <div class="col-xs-10" style="padding-left: 6px;padding-top: 2px;font-size: 13px;">\n'+
                          '                  '+line['file_name']+'</div>\n'+
                          '                 <div class="col-xs-2" style="padding-left: 38px;padding-top: 2px;font-size: 13px;">\n'+
                          '                  <i class="fa fa-trash-o oe_right attachment_delete panel-title" aria-hidden="true" style="color:#ffffff;" id='+line['file_id']+' ></i></div></div>\n'+
                          '                 <div class="row">\n'+
                          '                 <div class="col-xs-8 o_kanban_card_manage_section o_kanban_manage_view" style="width: 269px;margin-left: -2px;margin-top: 0px;min-height: 175px;/* border: 1px solid #ccc !important; */!importantmargin-top: 5px;height: 188px;overflow-x: hidden;">\n'+
                          '                      <img id="image_preview" src="'+line['file_data']+'" style="width: 266px;margin-left: -15px;margin-top: 1px;"> </img>\n'+
                          '                 </div>\n'+
                          '                 <div class="col-xs-4 o_kanban_card_manage_section o_kanban_manage_operations" style="margin-top: 2px;">\n'+
                          '                      <ul style="line-height: 14px;list-style: none;-webkit-padding-start: 0;padding-start: 0;">\n'+
                          '                          <li style="line-height: 15px;">\n'+
                          '                              <div class="o_kanban_card_manage_title">\n'+
                          '                                  <span style="font-size: 1.1em;font-weight: 400;">Create</span>\n'+
                          '                              </div>\n'+
                          '                          </li>\n'+
                          '                          <li style="line-height: 15px;"><a class="o_app o_menuitem" href="#menu_id='+line['id']+'&amp;action='+ line['action'] +'" data-menu='+line['id']+' data-action-model="ir.actions.act_window" data-action-id='+line['action']+'> <span class="oe_menu_text">Bills</span></a></li>\n'+
                          '                          <li style="line-height: 15px;"><a type="object" name="action_create_new_credit">Vendor Credit</a></li>\n'+
                          '                      </ul>\n'+
                          '                      <ul style="line-height: 14px;list-style: none;-webkit-padding-start: 0;padding-start: 0;">\n'+
                          '                          <li style="line-height: 15px;">\n'+
                          '                              <div class="o_kanban_card_manage_title">\n'+
                          '                                  <span style="font-size: 1.1em;font-weight: 400;">Add to Existing</span>\n'+
                          '                              </div>\n'+
                          '                          </li>\n'+
                          '                          <li style="line-height: 15px;"><a type="object" name="action_create_new_bill">Bill</a></li>\n'+
                          '                          <li style="line-height: 15px;"><a type="object" name="action_create_new_bill">Vendor Credit</a></li>\n'+
                          '                          <li style="line-height: 15px;"><a type="object" name="action_create_new_bill">Vendor Doc</a></li>\n'+
                          '                          <li style="line-height: 15px;"><a type="object" name="action_create_new_bill">Vendor Contract</a></li>\n'+
                          '                      </ul>\n'+
                          '                  </div>\n'+
                          '              </div>\n'+
                          '          </div>\n'+
                          '      </div>\n'+
                          '  </div>\n'+
                        '</div>\n';
                $(html_content).appendTo('.display_file');
            });
        });
    },

    render_dashboards: function() {
    var self = this;
        _.each(this.dashboards_templates, function(template) {
            self.$('.o_website_dashboard').append(QWeb.render(template, {widget: self}));
        });
    },
// Save file
    save_file: function (file_buffer, file_name) {
        var self = this;
        new Model("billpay.inbox").call("save_new_file", [file_buffer, file_name]).then(function(data) {
            console.log(data);
            self.fetch_data();
        });
    },

    reset_file: function () {
        var control = this.$('#upload');
        control.replaceWith(control = control.clone(true));
        this.file_name = false;
    },

    display_alert: function (message) {
        this.do_warn(_t('Input File Type Error'),_t(message));
    },

    on_file_upload: function (ev) {
        $('.initial_preview').css('display', '')
        var self = this,
            file = ev.target.files[0],
            is_image = /^image\/.*/.test(file.type),
            loaded = false;
        var file_name = file.name;
        var file_type = file.type;
        if (!(is_image || file_type === 'application/pdf')) {
            this.display_alert(_t("Invalid file type. Please select pdf or image file"));
            this.reset_file();
            return;
        }
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
			//if the file type is image make it preview imediatly
            if (file_type != 'application/pdf') {
                console.log('Image Called');
                self.save_file(file_buffer, file.name, file.type);
            }
            //if the file type is image make it preview imediatly
            if (is_image) {
                self.$("#image_initial_preview").attr("src", file_buffer);
                self.$(".preview_lable").html(file.name);
            }
            file_buffer = file_buffer.split(',')[1];
            var data = file_buffer;

        };

		//If file is PDF generate thumbnail image and make it preview
        if (file_type === 'application/pdf') {
            var ArrayReader = new FileReader();
            this.$('.save').button('loading');
			// file read as ArrayBuffer for PDFJS get_Document API
            ArrayReader.readAsArrayBuffer(file);
            ArrayReader.onload = function (evt) {
                var file_buffer = evt.target.result;
                var passwordNeeded = function () {
                    self.display_alert(_t("You can not upload password protected file."));
                    self.reset_file();
                    self.$('.save').button('reset');
                };

                PDFJS.getDocument(new Uint8Array(file_buffer), null, passwordNeeded).then(function getPdf(pdf) {
                    pdf.getPage(1).then(function getFirstPage(page) {
                        var scale = 1;
                        var viewport = page.getViewport(scale);
                        var canvas = document.getElementById('data_canvas');
                        var context = canvas.getContext('2d');
                        canvas.height = viewport.height;
                        canvas.width = viewport.width;
						// Render PDF page into canvas context
                        page.render({
                            canvasContext: context,
                            viewport: viewport
                        }).then(function () {
                            var image_data = self.$('#data_canvas')[0].toDataURL();
						// Send file to save
                            console.log('PDF Called');
                            self.save_file(image_data, file.name);
						// Make PDF thumbnail preview
                            self.$("#image_initial_preview").attr("src", image_data);
                            self.$(".preview_lable").html(file.name);
                            if (loaded) {
                                self.$('.save').button('reset');
                            }
                            loaded = true;
                        });
                    });
                });
            };
        }
    }

});
    core.action_registry.add('billpay_inbox', Dashboard);
    return Dashboard;
});

