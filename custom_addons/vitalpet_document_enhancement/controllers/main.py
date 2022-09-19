# -*- coding: utf-8 -*-
import base64
import re

from odoo import http, _
from odoo.addons.website_sign.controllers.main import WebsiteSign

class WebsiteSign(WebsiteSign):

    def get_document_qweb_context(self, id, token):
        signature_request = http.request.env['signature.request'].sudo().search([('id', '=', id)])
        if not signature_request:
            if token:
                return http.request.render('website_sign.deleted_sign_request')
            else:
                return http.request.not_found()

        current_request_item = None
        if token:
            current_request_item = signature_request.request_item_ids.filtered(lambda r: r.access_token == token)
            if not current_request_item and signature_request.access_token != token and http.request.env.user.id != signature_request.create_uid.id:
                return http.request.render('website_sign.deleted_sign_request')
        elif signature_request.create_uid.id != http.request.env.user.id:
            return http.request.not_found()

        signature_item_types = http.request.env['signature.item.type'].search_read([])
        if current_request_item:
            for item_type in signature_item_types:
                if item_type['auto_field']:
                    fields = item_type['auto_field'].split('.')
                    auto_field = current_request_item.partner_id
                    for field in fields:
                        if auto_field and field in auto_field:
                            auto_field = auto_field[field]
                        else:
                            auto_field = ""
                            break
                    item_type['auto_field'] = auto_field

        sr_values = http.request.env['signature.item.value'].sudo().search([('signature_request_id', '=', signature_request.id)])
        item_values = {}
        for value in sr_values:
            item_values[value.signature_item_id.id] = value.value

        return {
            'signature_request': signature_request,
            'current_request_item': current_request_item,
            'token': token,
            'nbComments': len(signature_request.message_ids.filtered(lambda m: m.message_type == 'comment')),
            'isPDF': (signature_request.template_id.attachment_id.mimetype.find('pdf') > -1),
            'webimage': re.match('image.*(gif|jpe|jpg|png)', signature_request.template_id.attachment_id.mimetype),
            'hasItems': len(signature_request.template_id.signature_item_ids) > 0,
            'signature_items': signature_request.template_id.signature_item_ids,
            'item_values': item_values,
            'role': current_request_item.role_id.id if current_request_item else 0,
            'readonly': not (current_request_item and current_request_item.state == 'sent'),
            'signature_item_types': signature_item_types,
        }