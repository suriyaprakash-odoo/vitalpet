# -*- coding: utf-8 -*-
import hashlib

from odoo.tools.safe_eval import safe_eval
from odoo import models, fields, api, exceptions, _


class S3Settings(models.TransientModel):
    _name = 's3.config.settings'
    _inherit = 'res.config.settings'

    s3_bucket = fields.Char(string='S3 bucket name', help="i.e. 'attachmentbucket'")
    s3_access_key_id = fields.Char(string='S3 access key id')
    s3_secret_key = fields.Char(string='S3 secret key')
    s3_condition = fields.Char(string='S3 condition',
                               help="""Specify valid odoo search domain here,
                               i.e. [('res_model', 'in', ['product.image'])].
                               According to this only data of model product.image will be sored on S3""")
    
    @api.multi
    def get_default_all(self, fields):
        s3_bucket = self.env["ir.config_parameter"].get_param("s3.bucket", default='')
        s3_access_key_id = self.env["ir.config_parameter"].get_param("s3.access_key_id", default='')
        s3_secret_key = self.env["ir.config_parameter"].get_param("s3.secret_key", default='')
        s3_condition = self.env["ir.config_parameter"].get_param("s3.condition", default='')

        return dict(
            s3_bucket=s3_bucket,
            s3_access_key_id=s3_access_key_id,
            s3_secret_key=s3_secret_key,
            s3_condition=s3_condition
        )

    # s3_bucket
    @api.multi
    def set_s3_bucket(self):
        self.env['ir.config_parameter'].set_param("s3.bucket",
                                                  self.s3_bucket or '',
                                                  groups=['base.group_system'])

    # s3_access_key_id
    @api.multi
    def set_s3_access_key_id(self):
        self.env['ir.config_parameter'].set_param("s3.access_key_id",
                                                  self.s3_access_key_id or '',
                                                  groups=['base.group_system'])

    # s3_secret_key
    @api.multi
    def set_s3_secret_key(self):
        self.env['ir.config_parameter'].set_param("s3.secret_key",
                                                  self.s3_secret_key or '',
                                                  groups=['base.group_system'])

    # s3_condition
    @api.multi
    def set_s3_condition(self):
        self.env['ir.config_parameter'].set_param("s3.condition",
                                                  self.s3_condition or '',
                                                  groups=['base.group_system'])

    def upload_existing(self):
        condition = self.s3_condition and safe_eval(self.s3_condition, mode="eval") or []
        domain = [('type', '!=', 'url'), ('id', '!=', 0)] + condition
        attachments = self.env['ir.attachment'].search(domain)
        print 'domain: ', domain
        print 'attachments: ', attachments
        attachments = attachments._filter_protected_attachments()

        if attachments:

            s3 = self.env['ir.attachment']._get_s3_resource()

            if not s3:
                raise exceptions.MissingError(_("Some of the S3 connection credentials are missing.\n Don't forget to click the ``[Apply]`` button after any changes you've made"))

            for attach in attachments:
                value = attach.datas
                bin_data = value and value.decode('base64') or ''
                fname = hashlib.sha1(bin_data).hexdigest()

                bucket_name = self.s3_bucket

                try:
                    s3.Bucket(bucket_name).put_object(
                        Key=fname,
                        Body=bin_data,
                        ACL='public-read',
                        ContentType=attach.mimetype,
                        )
                except Exception, e:
                    raise exceptions.UserError(e.message)

                vals = {
                    'file_size': len(bin_data),
                    'checksum': attach._compute_checksum(bin_data),
                    'index_content': attach._index(bin_data, attach.datas_fname, attach.mimetype),
                    'store_fname': fname,
                    'db_datas': False,
                    'type': 'url',
                    'url': attach._get_s3_object_url(s3, bucket_name, fname),
                }
                attach.write(vals)
