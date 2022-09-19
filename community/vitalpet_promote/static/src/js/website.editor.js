odoo.define('vitalpet_promote.web_editor', function (require) {
'use strict';

var ajax = require('web.ajax');
var core = require('web.core');
var Widget = require('web.Widget');
var base = require('web_editor.base');
var editor = require('web_editor.editor');
var widget = require('web_editor.widget');
var website = require('website.website');

var QWeb = core.qweb;
var _t = core._t;

ajax.loadXML('/vitalpet_promote/static/src/xml/website.editor.xml', QWeb);

/**
 * Object who contains all method and bind for the top bar, the template is create server side.
 */
widget.MediaDialog.include({
    events: {
        'click .o_form_binary_image_darkroom_modal': 'edit_image',
        'click .crop': function () {
            this.cropper.setDragMode('crop');
        },
        'click .zoomout': function () {
            this.cropper.zoom(0.1);
        },
        'click .zoomin': function () {
            this.cropper.zoom(-0.1);
        },
        'click .move': function () {
            this.cropper.setDragMode('move');
        },
        'click .move_left': function () {
            this.cropper.move(-10, 0);
        },
        'click .move_right': function () {
            this.cropper.move(10, 0);
        },
        'click .move_up': function () {
            this.cropper.move(0, -10);
        },
        'click .move_down': function () {
            this.cropper.move(0, 10);
        },
        'click .rotate_left': function () {
            this.cropper.rotate(-45);
        },
        'click .rotate_right': function () {
            this.cropper.rotate(45);
        },
        'click .scale_x': function () {
            this.cropper.scaleX(this.scale_x_rate);
            this.scale_x_rate = -this.scale_x_rate;
        },
        'click .scale_y': function () {
            this.cropper.scaleY(this.scale_y_rate);
            this.scale_y_rate = -this.scale_y_rate;
        },
        'click .reset_crop': function () {
            this.cropper.reset();
        },
        'click .cropped_download': function () {
            var result = this.cropper.getCroppedCanvas({ maxWidth: 4096, maxHeight: 4096 });
            //this.$('#getCroppedCanvasModal').modal().find('.modal-body').html(result);
            var download = document.getElementById('download');
            download.href = result.toDataURL('image/jpeg');
            download.click();
        },
        'click .cropped_canvas': function () {
        	var self = this;
        	var result = this.cropper.getCroppedCanvas({ maxWidth: 4096, maxHeight: 4096 });
        	var callback = _.uniqueId('func_');
        	ajax.jsonRpc('/web_editor/attachment/jsonadd', 'call', {'func': callback, 'upload': result.toDataURL('image/jpeg')}).then(function (prevented) {
        		if (_.isEmpty(prevented)) {
                    alert('prevented empty');
                    return;
                }

            	var $help_block = self.$('.image-crop').empty();
            	self.imageDialog.start();
            });
        },
        'click .cropped_canvas_2': function () {
        	var result = this.cropper.getCroppedCanvas({ width: 320, height: 180 });
            this.$('#getCroppedCanvasModal').modal().find('.modal-body').html(result);
            var download = document.getElementById('download');
            download.href = result.toDataURL('image/jpeg');
        }
    },
    init: function () {
        this.cropper;
        this.scale_x_rate = -1;
        this.scale_y_rate = -1;
        
        return this._super.apply(this, arguments);
    },
    edit_image: function (e) {
        
    	var $help_block = this.$('.image-crop').empty();
    	var self = this;
        var $a = $(e.target);
        var id = parseInt($a.data('id'), 10);
        var attachment = _.findWhere(this.imageDialog.records, {id: id});
        //alert(attachment.name);

    	var options = {
    		    aspectRatio: NaN,
    		    preview: '.img-preview',
    		    ready: function (e) {
    		      console.log(e.type);
    		    },
    		    cropstart: function (e) {
    		      console.log(e.type, e.detail.action);
    		    },
    		    cropmove: function (e) {
    		      console.log(e.type, e.detail.action);
    		    },
    		    cropend: function (e) {
    		      console.log(e.type, e.detail.action);
    		    },
    		    crop: function (e) {
    		      var data = e.detail;

    		      console.log(e.type);
    		      dataX.value = Math.round(data.x);
    		      dataY.value = Math.round(data.y);
    		      dataHeight.value = Math.round(data.height);
    		      dataWidth.value = Math.round(data.width);
    		      dataRotate.value = typeof data.rotate !== 'undefined' ? data.rotate : '';
    		      dataScaleX.value = typeof data.scaleX !== 'undefined' ? data.scaleX : '';
    		      dataScaleY.value = typeof data.scaleY !== 'undefined' ? data.scaleY : '';
    		    },
    		    zoom: function (e) {
    		      console.log(e.type, e.detail.ratio);
    		    }
    		  };
    
    	$help_block.replaceWith(QWeb.render('vitalpet_promote.dialog.image.existing.crop', {attachment: attachment}));

    	var container = document.querySelector('.img-container');
        var image = container.getElementsByTagName('img').item(0);
        this.cropper = new Cropper(image, options);
    },
});

});
