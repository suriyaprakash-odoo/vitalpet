# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

class PopupImage(models.TransientModel):

    _name = "popup.image.wizard"
    _description = "Popup image while clicking image in billpay"
    
    attachment = fields.Binary()


