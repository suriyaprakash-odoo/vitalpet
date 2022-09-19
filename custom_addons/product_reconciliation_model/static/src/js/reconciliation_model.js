odoo.define('product_reconciliation_model.reconciliation_model', function(require) {
	'use strict';
	
	var core = require('web.core');
	var ControlPanelMixin = require('web.ControlPanelMixin');
	var Widget = require('web.Widget');
	var Reconciliation = require('account.reconciliation')
	var ActionManager = require('web.ActionManager');
	var CrashManager = require('web.CrashManager');
	var Model = require('web.Model');
	
	var _t = core._t;
	
	var FieldMany2One = core.form_widget_registry.get('many2one');
	var FieldChar = core.form_widget_registry.get('char');
	var FieldFloat = core.form_widget_registry.get('float');
	
	
	Reconciliation.abstractReconciliation.include({
		init: function(parent, context) {
	        this._super(parent);

	        // Only for statistical purposes
	        this.lines_reconciled_with_ctrl_enter = 0;
	        this.time_widget_loaded = Date.now();

	        this.action_manager = this.findAncestor(function(ancestor){ return ancestor instanceof ActionManager });
	        this.crash_manager = new CrashManager();
	        this.formatCurrencies; // Method that formats the currency ; loaded from the server
	        this.model_res_users = new Model("res.users");
	        this.model_tax = new Model("account.tax");
	        this.model_presets = new Model("account.reconcile.model");
	        this.max_move_lines_displayed = 5;
	        // Number of reconciliations loaded initially and by clicking 'show more'
	        this.num_reconciliations_fetched_in_batch = 10;
	        this.animation_speed = 100; // "Blocking" animations
	        this.aestetic_animation_speed = 300; // eye candy
	        // We'll need to get the code of an account selected in a many2one field (which returns the id)
	        this.map_account_id_code = {};
	        // NB : for presets to work correctly, a field id must be the same string as a preset field
	        this.presets = {};
	        // Description of the fields to initialize in the "create new line" form
	        var domain_account_id = [['deprecated', '=', false]];
	        if (context && context.context && context.context.company_ids) {
	        	console.log(context.context.company_ids);
	            domain_account_id.push(['company_id', 'in', context.context.company_ids]);
	        }
	        this.create_form_fields = {
	            account_id: {
	                id: "account_id",
	                index: 0, // position in the form
	                corresponding_property: "account_id", // a account.move.line field name
	                label: _t("Account"),
	                required: true,
	                constructor: FieldMany2One,
	                field_properties: {
	                    relation: "account.account",
	                    string: _t("Account"),
	                    type: "many2one",
	                    domain: domain_account_id,
	                },
	            },
	            label: {
	                id: "label",
	                index: 5,
	                corresponding_property: "label",
	                label: _t("Label"),
	                required: true,
	                constructor: FieldChar,
	                field_properties: {
	                    string: _t("Label"),
	                    type: "char",
	                },
	            },
	            tax_id: {
	                id: "tax_id",
	                index: 10,
	                corresponding_property: "tax_id",
	                label: _t("Tax"),
	                required: false,
	                constructor: FieldMany2One,
	                field_properties: {
	                    relation: "account.tax",
	                    string: _t("Tax"),
	                    type: "many2one",
	                    domain: [['type_tax_use','!=','none']],
	                },
	            },
	            amount: {
	                id: "amount",
	                index: 15,
	                corresponding_property: "amount",
	                label: _t("Amount"),
	                required: true,
	                constructor: FieldFloat,
	                field_properties: {
	                    string: _t("Amount"),
	                    type: "float",
	                },
	            },
	            analytic_account_id: {
	                id: "analytic_account_id",
	                index: 20,
	                corresponding_property: "analytic_account_id",
	                label: _t("Analytic Acc."),
	                required: false,
	                group:"analytic.group_analytic_accounting",
	                constructor: FieldMany2One,
	                field_properties: {
	                    relation: "account.analytic.account",
	                    string: _t("Analytic Acc."),
	                    type: "many2one",
	                },
	            },
	            product_id: {
	                id: "product_id",
	                index: 25, // position in the form
	                corresponding_property: "product_id", // a account.move.line field name
	                label: _t("Product"),
	                required: true,
	                constructor: FieldMany2One,
	                field_properties: {
	                    relation: "product.product",
	                    string: _t("Product"),
	                    type: "many2one",
	                },
	            },
	            partner_id: {
	                id: "partner_id",
	                index: 30, // position in the form
	                corresponding_property: "partner_id", // a account.move.line field name
	                label: _t("Partner"),
	                required: true,
	                constructor: FieldMany2One,
	                field_properties: {
	                    relation: "res.partner",
	                    string: _t("Partner"),
	                    type: "many2one",
	                },
	            },
	        };
	    },
	    

	    fetchPresets: function() {
	        var self = this;
	        var deferred_last_update = self.model_presets.query(['write_date']).order_by('-write_date').first().then(function (data) {
	            self.presets_last_write_date = (data ? data.write_date : undefined);
	        });
	        
	        
	        var getUrlParameter = function getUrlParameter(str_url,sParam) {
            var sPageURL = decodeURIComponent(str_url),
                sURLVariables = sPageURL.split('&'),
                sParameterName, i;
        	
            for (i = 0; i < sURLVariables.length; i++) {
                sParameterName = sURLVariables[i].split('=');
                if (sParameterName[0] === sParam) {
                    return sParameterName[1] === undefined ? true : sParameterName[1];
                }
            }
        };
        
        var str_url=window.location.href;
        str_url=str_url.replace("#", "&");
        var active_id = getUrlParameter(str_url,'active_id');
        var active_model = getUrlParameter(str_url,'model');
	    
        var journal_name=[1,'=',1];
//        alert(journal_name[0]);
        if(active_model=='account.bank.statement'){
        	if($('span.o_form_field').hasClass('journal_name')){
        		journal_name=['journal_id.name', '=', $(".journal_name.o_form_field").text().replace(" (USD)","")];
        	}
        	else if($('select').hasClass('journal_name')){
        		journal_name=['journal_id.name', '=', $("select.journal_name option[value='"+$("select.journal_name").val()+"']").text().replace(" (USD)","")];
        	}
	    }
//        alert(journal_name[0]);
//        console.log(journal_name);
	        var deferred_presets = self.model_presets.query().
	        						filter([['company_id', '=', self.session.company_id],journal_name]).
	        						order_by('-sequence', '-id').all().then(function (data) {
	        							
	        	self.presets = {};
	        	
	            _(data).each(function(datum){
//	            	console.log(datum.journal_id);
//	            	console.log(datum.recon_journal_id);
	            	if(datum.journal_id[0]==datum.recon_journal_id[0] || journal_name[0]!=1){
		                var preset = {
		                    id: datum.id,
		                    name: datum.name,
		                    sequence: datum.sequence,
		                    lines: [{
		                        account_id: datum.account_id,
		                        journal_id: datum.journal_id,
		                        label: datum.label,
		                        amount_type: datum.amount_type,
		                        amount: datum.amount,
		                        tax_id: datum.tax_id,
		                        analytic_account_id: datum.analytic_account_id,
		                    		product_id: datum.product_id,
		                    		partner_id:datum.partner_id,
		                    }]
		                };
		                if (datum.has_second_line) {
		                    preset.lines.push({
		                        account_id: datum.second_account_id,
		                        journal_id: datum.second_journal_id,
		                        label: datum.second_label,
		                        amount_type: datum.second_amount_type,
		                        amount: datum.second_amount,
		                        tax_id: datum.second_tax_id,
		                        analytic_account_id: datum.second_analytic_account_id,
		                        second_product_id: datum.second_product_id,
		                        second_partner_id: datum.second_partner_id,
		                    });
		                }
		                self.presets[datum.id] = preset;
	            	}
	            });
	        });
	        return $.when(deferred_last_update, deferred_presets);
	    },
		
	});
	
	Reconciliation.abstractReconciliationLine.include({
		// Returns an object that can be passed to process_reconciliation()
	    prepareCreatedMoveLinesForPersisting: function(lines) {
	        lines = _.filter(lines, function(line) { return !line.is_tax_line });
	        return _.collect(lines, function(line) {
	            var dict = {
	                account_id: line.account_id,
	                name: line.label,
	                product_id: line.product_id,
	                partner_id: line.partner_id,
	            };
	            // Use amount_before_tax since the amount of the newly created line is adjusted to
	            // reflect tax included in price in account_move_line.create()
	            var amount = line.tax_id ? line.amount_before_tax: line.amount;
	            dict['credit'] = (amount > 0 ? amount : 0);
	            dict['debit'] = (amount < 0 ? -1 * amount : 0);
	            if (line.tax_id) dict['tax_ids'] = [[4, line.tax_id, null]];
	            if (line.analytic_account_id) dict['analytic_account_id'] = line.analytic_account_id;
	            return dict;
	        });
	    },
		
	});
	
	Reconciliation.bankStatementReconciliationLine.include({
		prepareCounterpartAMLDict: function(line) {
	        return {
	            name: line.name,
	            debit: line.debit,
	            credit: line.credit,
	            product_id: line.product_id,
	            counterpart_aml_id: line.id,
	            partner_id: line.partner_id,
	        };
	    },
		
	});
/*	
	return {
	    abstractReconciliation: abstractReconciliation,
	};*/

});