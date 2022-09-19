odoo.define('vitalpet_employee_fields', function(require) {
'use strict';

var core = require('web.core');
var QWeb = core.qweb;
var form_widget = require('web.form_widgets');

var _t = core._t;
var FieldChar = form_widget.FieldChar;
	FieldChar.include({
		

		start: function() {
	        this.field_manager.on("field_changed:encrypt_value", this, function() {
            this.initialize_content();
        	});
	        this._super();
	    },

		initialize_content: function() {
	    	if (this.node.attrs.password === 'encrypt_value') {
	    		this.password = this.field_manager.get_field_value('encrypt_value');
	    	}
	        if(!this.get('effective_readonly') && !this.$input) {
	            this.$input = this.$el;
	        }
	        this.setupFocus(this.$el);
	    },

	});
});