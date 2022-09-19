odoo.define('cenit_restrict_sync.sync_button', function (require) {
"use strict";

var Model = require('web.Model');
var WebClient = require('web.WebClient');
var core = require('web.core');
var ListView = require('web.ListView');

var _t = core._t;
        var self = this;
        
        ListView.include({  
        	render_buttons: function() {
                var self = this;
                var add_button = false;
                if (!this.$buttons) { // Ensures that this is only done once
                    add_button = true;
                }
                this._super.apply(this, arguments); // Sets this.$buttons
                if(add_button) {
                    this.$buttons.on('click', '.oe_new_button', do_the_job.bind(this));
                }
            }
        });

        function do_the_job () { 

                  this.do_action({               

                           type: "ir.actions.act_window",               

                           name: "Sync Practices",               

                           res_model: "sync.practice.wizard",               

                           views: [[false,'form']],               

                           target: 'new',               

                           view_type : 'form',               

                           view_mode : 'form'               

                           //flags: {'form': {'action_buttons': true, 'options': {'mode': 'edit'}}}
                  });
                 return { 'type': 'ir.actions.client',                    'tag': 'reload', } } 
});