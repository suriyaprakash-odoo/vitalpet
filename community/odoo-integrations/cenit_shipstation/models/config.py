# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010, 2014 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import logging

from openerp import models, fields, api


_logger = logging.getLogger(__name__)

COLLECTION_NAME = "shipstation"
COLLECTION_VERSION = "1.0.0"
COLLECTION_PARAMS = {
    'Shipstation API Key':'key',
    'Shipstation API Secret':'secret',
    'Shipstation Store':'store_id',
}

class CenitIntegrationSettings(models.TransientModel):
    _name = "cenit.shipstation.settings"
    _inherit = 'res.config.settings'

    ############################################################################
    # Pull Parameters
    ############################################################################
    key = fields.Char('Shipstation API Key')
    secret = fields.Char('Shipstation API Secret')
    store_id = fields.Char('Shipstation Store')

    ############################################################################
    # Default Getters
    ############################################################################
    def get_default_key(self, context):
        key = self.env['ir.config_parameter'].get_param(
            'odoo_cenit.shipstation.key', default=None
        )
        return {'key': key or ''}

    def get_default_secret(self, context):
        secret = self.env['ir.config_parameter'].get_param(
            'odoo_cenit.shipstation.secret', default=None
        )
        return {'secret': secret or ''}

    def get_default_store_id(self, context):
        store_id = self.env['ir.config_parameter'].get_param(
            'odoo_cenit.shipstation.store_id', default=None
        )
        return {'store_id': store_id or ''}


    ############################################################################
    # Default Setters
    ############################################################################
    def set_key(self):
        config_parameters = self.env['ir.config_parameter']
        for record in self.browse(self.ids):
            config_parameters.set_param (
                'odoo_cenit.shipstation.key', record.key or ''
            )

    def set_secret(self):
        config_parameters = self.env['ir.config_parameter']
        for record in self.browse(self.ids):
            config_parameters.set_param (
                'odoo_cenit.shipstation.secret', record.secret or ''
            )

    def set_store_id(self):
        config_parameters = self.env['ir.config_parameter']
        for record in self.browse(self.ids):
            config_parameters.set_param (
                'odoo_cenit.shipstation.store_id', record.store_id or ''
            )


    ############################################################################
    # Actions
    ############################################################################
    def execute(self):
        rc = super(CenitIntegrationSettings, self).execute()

        if not self.env.context.get('install', False):
            return rc

        objs = self.browse(self.ids)
        if not objs:
            return rc
        obj = objs[0]

        installer = self.env['cenit.collection.installer']
        data = installer.get_collection_data(
            COLLECTION_NAME,
            version = COLLECTION_VERSION
        )

        params = {}
        for p in data.get('pull_parameters'):
            k = p['label']
            id_ = p.get('id')
            value = getattr(obj,COLLECTION_PARAMS.get(k))
            params.update ({id_: value})

        installer.pull_shared_collection(data.get('id'), params=params)
        installer.install_common_data(data['data'])

        return rc
