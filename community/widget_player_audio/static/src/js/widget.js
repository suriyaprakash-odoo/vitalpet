openerp.widget_player_audio = function (instance) {
        var QWeb = instance.web.qweb;
    instance.web.form.widgets.add('audio', 'instance.web.form.FieldAudio');
    instance.web.form.FieldAudio = instance.web.form.FieldChar.extend({
        template: 'FieldAudio',
        render_value: function () {
            var show_value = this.format_value(this.get('value'), '');
            if (!this.get("effective_readonly")) {
                var $input = this.$el.find('input');
                $input.val(show_value);
                this.$(".oe_form_char_content_edit").html(QWeb.render("playertemaplate", {
                         url:show_value})); 
            } else {
                this.$(".oe_form_char_content").html(QWeb.render("playertemaplate", {
                         url:show_value})); 
            }
        }
    });
 
};