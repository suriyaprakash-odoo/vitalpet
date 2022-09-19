from odoo import api, fields, models, tools, _

class ResPartner(models.Model):    
    _inherit = 'res.partner'

    vendor_payment_mode = fields.Char(related="supplier_payment_mode_id.name",string='Payment Type')


class PartnerBank(models.Model):    
    _inherit = 'res.partner.bank'

    # bank_routing = fields.Char(string='ABA/Routing Number')