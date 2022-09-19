odoo.define('vitalpet_document_enhancement', function(require) {
'use strict';

var core = require('web.core');
var website_sign = require('website_sign.PDFIframe');
var _t = core._t;


website_sign = website_sign.include({

	createSignatureItem: function(type, required, responsible, posX, posY, width, height, value) {
            var self = this;
            var readonly = this.readonlyFields || (responsible > 0 && responsible !== this.role) || !!value;

            var $signatureItem = $(core.qweb.render('vitalpet_document_enhancement.signature_item', {
                editMode: this.editMode,
                readonly: readonly,
                type: type['type'],
                value: value || "",
                placeholder: type['placeholder']
            }));

            return $signatureItem.data({type: type['id'], required: required, responsible: responsible, posx: posX, posy: posY, width: width, height: height})
                                 .data('hasValue', !!value);
        },

	});
});
odoo.define('vitalpet_document_enhancement.Document', function (require) {
	var core = require('web.core');
	var Document = require('website_sign.document_signing').SignableDocument;
	var ajax = require('web.ajax');
    var core = require('web.core');
    var Dialog = require('web.Dialog');
    var Widget = require('web.Widget');
    var PDFIframe = require('website_sign.PDFIframe');
    var session = require('web.session');

    var _t = core._t;

    

    var PublicSignerDialog = Dialog.extend({
        template: "website_sign.public_signer_dialog",
        init: function(parent, requestID, requestToken, options) {
            var self = this;
            options = (options || {});

            options.title = options.title || _t("Final Validation");
            options.size = options.size || "medium";
            if(!options.buttons) {
                options.buttons = [];
                options.buttons.push({text: _t("Validate & Send"), classes: "btn-primary", click: function(e) {
                    var name = this.$inputs.eq(0).val();
                    var mail = this.$inputs.eq(1).val();
                    if(!name || !mail || mail.indexOf('@') < 0) {
                        this.$inputs.eq(0).closest('.form-group').toggleClass('has-error', !name);
                        this.$inputs.eq(1).closest('.form-group').toggleClass('has-error', !mail || mail.indexOf('@') < 0);
                        return false;
                    }

                    ajax.jsonRpc("/sign/send_public/" + this.requestID + '/' + this.requestToken, 'call', {
                        name: name,
                        mail: mail,
                    }).then(function() {
                        self.close();
                        self.sent.resolve();
                    });
                }});
                options.buttons.push({text: _t("Cancel"), close: true});
            }

            this._super(parent, options);

            this.requestID = requestID;
            this.requestToken = requestToken;
            this.sent = $.Deferred();
        },

        open: function(name, mail) {
            var self = this;
            this.opened(function() {
                self.$inputs = self.$('input');
                self.$inputs.eq(0).val(name);
                self.$inputs.eq(1).val(mail);
            });

            return this._super.apply(this, arguments);
        },
    });
    
	var SignableDocument = Document.include({
		signItemDocument: function(e) {
	        var mail = "";
	        this.iframeWidget.$('.o_sign_signature_item').each(function(i, el) {
	            var value = $(el).val();
	            if(value && value.indexOf('@') >= 0) {
	                mail = value;
	            }
	        });
	
	        if(this.$('#o_sign_is_public_user').length > 0) {
	            (new PublicSignerDialog(this, this.requestID, this.requestToken))
	                .open(this.signerName, mail).sent.then(_.bind(_sign, this));
	            
	        } else {
	            _sign.call(this);
	        }
	
	        function _sign() {
	            var signatureValues = {};
	            for(var page in this.iframeWidget.configuration) {
	                for(var i = 0 ; i < this.iframeWidget.configuration[page].length ; i++) {
	                    var $elem = this.iframeWidget.configuration[page][i];
	                    var resp = parseInt($elem.data('responsible')) || 0;
	                    if(resp > 0 && resp !== this.iframeWidget.role) {
	                        continue;
	                    }
	                    
	                    
	                    if($elem.attr('type') == 'checkbox' && $elem.prop('checked') == false) {
	
	                    	value = "not_checked"
	                    }
	                    else {
	                        var value = ($elem.val() && $elem.val().trim())? $elem.val() : false;
	                        if($elem.data('signature')) {
	                            value = $elem.data('signature');
	                        }
	
	                        if(!value) {
	                            if($elem.data('required')) {
	                                this.iframeWidget.checkSignatureItemsCompletion();
	                                Dialog.alert(this, _t("Some fields have still to be completed !"), {title: _t("Warning")});
	                                return;
	                            }
	                            continue;
	                        }
	                    }
	
	                    signatureValues[parseInt($elem.data('item-id'))] = value;
	                }
	            }
	
	            var self = this;
	            ajax.jsonRpc('/sign/sign/' + this.requestID + '/' + this.accessToken, 'call', {
	                signature: signatureValues,
	            }).then(function(success) {
	                if(!success) {
	                    setTimeout(function() { // To be sure this dialog opens after the thank you dialog below
	                        Dialog.alert(self, _t("Sorry, an error occured, please try to fill the document again."), {
	                            title: _t("Error"),
	                            confirm_callback: function() {
	                                window.location.reload();
	                            },
	                        });
	                    }, 500);
	                }
	            });
	            this.iframeWidget.disableItems();
	            setTimeout(function() { window.location.reload()}, 2000);
	        }
	    },
	});

});