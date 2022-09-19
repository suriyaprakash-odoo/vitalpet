from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

class DocumentTag(models.Model):
    _name = "document.tag"
    
    name = fields.Char(string="Tag")
    
    
class DocumentForm(models.Model):
    _name = "document.form"
    
    name = fields.Char(string="Type")
    
class DocumentTemplateLines(models.Model):
    _name = "document.template.lines"
    
    _rec_name = 'field_name'
    
    field_name = fields.Char(string="Field Name")
    field_type = fields.Many2one('signature.item.type',string="Field Type")
    display_name = fields.Char(string="Display Name")
    description = fields.Text(string="Description")
    parameter = fields.Char(string="Parameter")
    sequence = fields.Char(string="Sequence")
    is_required = fields.Boolean(string="Is Required")
    document_template_id = fields.Many2one('document.template','Form', required="True")

       
    
    
    
class DocumentTemplate(models.Model):
    _name = "document.template"
    
    name = fields.Char(string="Name")
    template_type = fields.Many2one('document.form',string="Type")
    state = fields.Many2one('res.country.state',string="State")
    country_id = fields.Many2one('res.country',string="Country")
    external_id = fields.Char(string='External ID')
    alternate_code = fields.Char(string='Alternate Code')
    sequence = fields.Char(string='Sequence')
    description = fields.Text(string='Description')
    document_template_ids = fields.One2many('document.template.lines','document_template_id',string="Lines")
#\\ To change the country based on state
    @api.onchange('state')
    def onchange_state(self):
        for line in self:
            line.country_id = line.state.country_id.id