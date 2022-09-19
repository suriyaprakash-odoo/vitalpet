# -*- coding: utf-8 -*-
import re
import base64
import StringIO
from odoo import api, fields, models, _
from pyPdf import PdfFileReader, PdfFileWriter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from odoo.exceptions import ValidationError

class SignatureRequestItem(models.Model):
    _inherit = "signature.request.item"
    
    
    @api.multi
    def sign(self, signature):
        self.ensure_one()
        if not isinstance(signature, dict):
            self.signature = signature
        else:
            SignatureItemValue = self.env['signature.item.value']
            request = self.signature_request_id

            signerItems = request.template_id.signature_item_ids.filtered(lambda r: not r.responsible_id or r.responsible_id.id == self.role_id.id)
            autorizedIDs = set(signerItems.mapped('id'))
            requiredIDs = set(signerItems.filtered('required').mapped('id'))

            itemIDs = set(map(lambda k: int(k), signature.keys()))
            if not (itemIDs <= autorizedIDs and requiredIDs <= itemIDs): # Security check
                return False
            
            for itemId in signature:               
                item_value = SignatureItemValue.search([('signature_item_id', '=', int(itemId)), ('signature_request_id', '=', request.id)])
                if not item_value:
                    request_item = self.env['signature.item'].browse(int(itemId))
                    print signature[itemId]
                    if request_item.related_field and request_item.field_id and signature[itemId] != 'not_checked':
                        model_name = request_item.responsible_id.model_id.model
                        if model_name == 'hr.employee':
                            find_rec_id = self.env[model_name].search([('address_home_id', '=', self.partner_id.id)])
                            
                        elif model_name == 'res.partner':
                            find_rec_id = self.env[model_name].search([('id', '=', self.partner_id.id)])
                            
                        else:
                            find_rec_id = self.env[model_name].search([('partner_id', '=', self.partner_id.id)])
                        
                        if len(find_rec_id) == 1:
                            if request_item.field_id.relation:
                                rel_model_name = request_item.field_id.relation
                                if rel_model_name:
                                    if request_item.map_to:
                                        rec_id = self.env[rel_model_name].search([('name', '=', request_item.map_to)])
                                    else:
                                        rec_id = self.env[rel_model_name].search([('name', '=', signature[itemId])])
                                    record_value = rec_id.id
                            else:
                                if request_item.map_to:
                                    record_value = request_item.map_to
                                else:
                                    record_value = signature[itemId]
                            if request_item.field_id.name == 'supplier_payment_mode_id':
                                ir_property = self.env['ir.property'].search([('name', '=', 'supplier_payment_mode_id'),
                                                                ('fields_id', '=', request_item.field_id.id),
                                                                ('res_id', '=', request_item.field_id.model_id.model+','+str(find_rec_id.id)),
                                                                ('company_id', '=', 74),
                                                                ])
                                if ir_property:
                                    ir_property.write({'value_reference':'account.payment.mode'+","+str(record_value)})
                                
                                else:
                                    values = {
                                        'name':'supplier_payment_mode_id',
                                        'fields_id':request_item.field_id.id,
                                        'res_id':request_item.field_id.model_id.model+','+str(find_rec_id.id),
                                        'value_reference':'account.payment.mode'+","+str(record_value),
                                        'company_id':74,
                                        'type':'many2one'                                    
                                        }
                                    self.env['ir.property'].create(values)
                            else:
                                find_rec_id.write({request_item.field_id.name:record_value}) 
                        else:
                            raise ValidationError(("Error occured. Contact administrator"))
                            
                                
                    if signature[itemId] != 'not_checked':
                        item_value = SignatureItemValue.create({'signature_item_id': int(itemId), 'signature_request_id': request.id, 'value': signature[itemId]})
                        if item_value.signature_item_id.type_id.type == 'signature':
                            self.signature = signature[itemId][signature[itemId].find(',')+1:]            
        return True
    
    
class SignatureItemParty(models.Model):
    _inherit = "signature.item.party"
    
    model_id = fields.Many2one('ir.model',string='Related Model')



class SignatureRequestTemplate(models.Model):
    _inherit = "signature.request.template"
    
    encrypt = fields.Boolean(string="Encrypted?")
    document_tag = fields.Many2many('document.tag',string="Document Tag")
    related_template = fields.Many2one('document.template',string="Related Form Template")

#     @api.onchange('related_template')
#     def onchange_related_template(self):
#         print self.signature_item_ids
#         self_id = False
#         
#         if self.signature_item_ids:
#             self_id = self.signature_item_ids[0].template_id
#         print self_id
#         if self_id:
#             adjustment_value = {
#                 'type_id': 1,
#                 'page': 1,
#                 'posX': 0.001,
#                 'posX': 0.002,
#                 'width': 0.150,
#                 'height':0.150,
#             }
#             res = self.write({'signature_item_ids': [(6, 0, adjustment_value)]})
#             print res
#             res.unlink()
# #         return res
#         return {}

    
    
    
class SignatureItem(models.Model):
    _inherit = "signature.item"
    
    model_id = fields.Integer(related='responsible_id.model_id.id')
    field_id = fields.Many2one('ir.model.fields',string="Field ID")
    map_to = fields.Char(string="Map To")
    related_field = fields.Many2one('document.template.lines',string="Related Field")
    
    @api.onchange('related_field')
    def onchange_required(self):
        self.required =  self.related_field.is_required
    
    
    @api.onchange('related_field')
    def onchange_related_field(self):   
        res = {'domain': {
        'related_field': "[('id', '=', False)]",
        }}
        if self.template_id.related_template and self.template_id.related_template.document_template_ids:
            jrl_ids = self.template_id.related_template.document_template_ids.ids
            res['domain']['related_field'] = "[('id', 'in', %s)]" % jrl_ids
        return res
    
class SignatureRequest(models.Model):
    _inherit = "signature.request"       
    
    def generate_completed_document(self):
        if len(self.template_id.signature_item_ids) <= 0:
            self.completed_document = self.template_id.attachment_id.datas
            return

        old_pdf = PdfFileReader(StringIO.StringIO(base64.b64decode(self.template_id.attachment_id.datas)))
        box = old_pdf.getPage(0).mediaBox
        height = int(box.getUpperRight_y())
        font = "Helvetica"

        normalFontSize = height*0.015

        packet = StringIO.StringIO()
        can = canvas.Canvas(packet)
        itemsByPage = self.template_id.signature_item_ids.getByPage()
        SignatureItemValue = self.env['signature.item.value']
        for p in range(0, old_pdf.getNumPages()):
            if (p+1) not in itemsByPage:
                can.showPage()
                continue

            items = itemsByPage[p+1]
            for item in items:
                value = SignatureItemValue.search([('signature_item_id', '=', item.id), ('signature_request_id', '=', self.id)], limit=1)
                if not value or not value.value:
                    continue

                value = value.value
                box = old_pdf.getPage(p).mediaBox
                width = int(box.getUpperRight_x())
                height = int(box.getUpperRight_y())

                if item.type_id.type == "text":
                    can.setFont(font, int(height*item.height*0.8))
                    can.drawString(width*item.posX, height*(1-item.posY-item.height*0.9), value)

                elif item.type_id.type == "textarea":
                    can.setFont(font, int(normalFontSize*0.8))
                    lines = value.split('\n')
                    y = height*(1-item.posY)
                    for line in lines:
                        y -= normalFontSize*0.9
                        can.drawString(width*item.posX, y, line)
                        y -= normalFontSize*0.1

                elif item.type_id.type == "signature" or item.type_id.type == "initial":
                    img = base64.b64decode(value[value.find(',')+1:])
                    can.drawImage(ImageReader(StringIO.StringIO(img)), width*item.posX, height*(1-item.posY-item.height), width*item.width, height*item.height, 'auto', True)

            can.showPage()

        can.save()

        item_pdf = PdfFileReader(packet)
        new_pdf = PdfFileWriter()

        for p in range(0, old_pdf.getNumPages()):
            page = old_pdf.getPage(p)
            page.mergePage(item_pdf.getPage(p))
            new_pdf.addPage(page)

        output = StringIO.StringIO()
        new_pdf.write(output)
        self.completed_document = base64.b64encode(output.getvalue())
        output.close()
