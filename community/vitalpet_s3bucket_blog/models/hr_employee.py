# -*- coding: utf-8 -*-
import os
import base64
import logging

from odoo import api, fields,models, _
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)

try:
    import boto3
except:
    _logger.debug('boto3 package is required which is not \
    found on your installation')


    
class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    
    image = fields.Binary('Image', attachment=True)
    image_s3_url = fields.Char('S3 URL')
    
        
#     def _get_s3_settings(self, param_name, os_var_name):
#         config_obj = self.env['ir.config_parameter'].sudo()
#         res = config_obj.get_param(param_name)
#         if not res:
#             res = os.environ.get(os_var_name)
#             if res:
#                 config_obj.set_param(param_name, res)
#                 _logger.info('parameter {} has been created from env {}'.format(param_name, os_var_name))
#         return res
#     
#     @api.model
#     def _get_s3_object_url(self, s3, s3_bucket_name, key_name):
#         # bucket_location = s3.meta.client.get_bucket_location(Bucket=s3_bucket_name)
#         # location_constraint = bucket_location.get('LocationConstraint')
#         # domain_part = 's3' + '-' + location_constraint if location_constraint else 's3'
#         object_url = "https://s3-us-west-2.amazonaws.com/{0}/{1}".format(
#             s3_bucket_name,
#             key_name)
#         return object_url
#     
#     @api.model
#     def _get_s3_resource(self):
#         access_key_id = self._get_s3_settings('s3.access_key_id', 'S3_ACCESS_KEY_ID')
#         secret_key = self._get_s3_settings('s3.secret_key', 'S3_SECRET_KEY')
#         bucket_name = self._get_s3_settings('s3.bucket', 'S3_BUCKET')
#     
#         if not access_key_id or not secret_key or not bucket_name:
#             _logger.info(_('Amazon S3 credentials are not defined properly. Attachments won\'t be saved on S3.'))
#             return False
#     
#         s3 = boto3.resource(
#             's3',
#             aws_access_key_id=access_key_id,
#             aws_secret_access_key=secret_key,
#             )
#         bucket = s3.Bucket(bucket_name)
#         if not bucket:
#             s3.create_bucket(Bucket=bucket_name)
#         return s3
#     
#     @api.model
#     def create(self, vals):
#         post = super(HrEmployee, self).create(vals)
#         s3 = self._get_s3_resource()
#         if not s3:
#             _logger.info(_('Amazon S3 source not defined properly. Attachments won\'t be saved on S3.'))
#             return post
#     
#         bucket_name = self._get_s3_settings('s3.bucket', 'S3_BUCKET')
#         if 'image' in vals and post.image:
#             fname = 'staffs%s.jpg' % (post.id)
#             s3.Bucket(bucket_name).put_object(
#                 Key=fname,
#                 Body=base64.b64decode(post.image),
#                 ServerSideEncryption= "AES256"
#                 )
#             post.write({'image_s3_url': self._get_s3_object_url(s3, bucket_name, fname)})
#         return post
#                 
#     @api.multi
#     def write(self, vals):
#         res = super(HrEmployee, self).write(vals)
#         s3 = self._get_s3_resource()
#         if not s3:
#             _logger.info(_('Amazon S3 source not defined properly. Attachments won\'t be saved on S3.'))
#             return res
#         bucket_name = self._get_s3_settings('s3.bucket', 'S3_BUCKET')
#         for post in self:
#             if ('image' in vals and post.image)  and (post.image or  not post.image_s3_url):
#                 fname = 'staffs%s.jpg' % (post.id)
#                 s3.Bucket(bucket_name).put_object(
#                     Key=fname,
#                     Body=post.image and base64.b64decode(post.image) or '',
#                     ServerSideEncryption= "AES256"
#                     )
#                 post.write({'image_s3_url': self._get_s3_object_url(s3, bucket_name, fname)})
#                 
#         return res


class ResCompany(models.Model):
    _inherit = 'res.company'
    
#     @api.multi
#     def get_primary_image(self):
#         obj_data = self.env['promote.post'].sudo()
#         companie = self[0]
#         photo_ids = obj_data.search([('blog_id.name', '=', 'Photos'), 
#                                               ('tags_ids.name', '=', companie.code),
#                                               ('tags_ids.name', '=ilike', 'Primary')])
#         if photo_ids:
#             return photo_ids[0].image_s3_url
#         return ''

