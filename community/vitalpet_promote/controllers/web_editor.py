# -*- coding: utf-8 -*-
#Added by ELmehdi Laftouty to allow frontEnd HTML editor in the Backend

import cStringIO
import json
import logging
from PIL import Image, ImageFont, ImageDraw
from odoo import http, tools
from odoo.http import request
from odoo.addons.website.controllers.main import Website

logger = logging.getLogger(__name__)

class Web_Editor(http.Controller):

    #------------------------------------------------------
    # add attachment (images or link)
    #------------------------------------------------------
    @http.route('/web_editor/attachment/jsonadd', type='json', auth='user', methods=['POST'])
    def attach(self, func, upload=None, url=None, disable_optimization=None, **kwargs):
        # the upload argument doesn't allow us to access the files if more than
        # one file is uploaded, as upload references the first file
        # therefore we have to recover the files from the request object
        Attachments = request.env['ir.attachment']  # registry for the attachment table

        uploads = []
        message = None
        if not upload: # no image provided, storing the link and the image name
            name = url.split("/").pop()                       # recover filename
            attachment = Attachments.create({
                'name': name,
                'type': 'url',
                'url': url,
                'public': True,
                'res_model': 'ir.ui.view',
            })
            uploads += attachment.read(['name', 'mimetype', 'checksum', 'url'])
        else:          
            try:
                attachments = request.env['ir.attachment']
                #for c_file in request.httprequest.files.getlist('upload'):
                data = upload.replace('data:image/jpeg;base64,', '')
                try:
                    image = Image.open(cStringIO.StringIO(data.decode('base64')))
                    w, h = image.size
                    if w*h > 42e6: # Nokia Lumia 1020 photo resolution
                        raise ValueError(
                            u"Image size excessive, uploaded images must be smaller "
                            u"than 42 million pixel")
                    if not disable_optimization and image.format in ('PNG', 'JPEG'):
                        data = tools.image_save_for_web(image)
                except IOError, e:
                    print e
                    pass

                attachment = Attachments.create({
                    'name': 'CroppedImage.jpeg',
                    'datas': data.encode('base64'),
                    'datas_fname': 'CroppedImage.jpeg',
                    'public': True,
                    'res_model': 'ir.ui.view',
                })
                attachments += attachment
                uploads += attachments.read(['name', 'mimetype', 'checksum', 'url'])
            except Exception, e:
                logger.exception("Failed to upload image to attachment")
                message = unicode(e)

        return """<script type='text/javascript'>
            window.parent['%s'](%s, %s);
        </script>""" % (func, json.dumps(uploads), json.dumps(message))
        
        
        
class Website(Website):

    
    @http.route(['/website/snippets'], type='json', auth="user", website=True)
    def snippets(self):
        referrer = request.httprequest.referrer
        print referrer
        if referrer and referrer.find('/promote') != -1:
            return request.env['ir.ui.view'].render_template('vitalpet_promote.snippets')
        else:
            return request.env['ir.ui.view'].render_template('website.snippets')
            
