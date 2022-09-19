# -*- coding: utf-8 -*-
import re
import uuid

from odoo import api, fields, models, _


class SignatureItemType(models.Model):
    _inherit = "signature.item.type"

    type = fields.Selection([
        ('signature', "Signature"),
        ('initial', "Initial"),
        ('text', "Text"),
        ('textarea', "Multiline Text"),
        ('boolean', "Boolean"),
        ('float', "Float"),
        ('integer', "Integer"),
        ('selection', "Selection"),
    ], required=True, default='text')

