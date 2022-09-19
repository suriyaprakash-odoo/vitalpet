from odoo import fields, models, api, _


class ResPartnerBank(models.Model):
    _inherit = "res.partner.bank"

    
    active = fields.Boolean('Active', default=True)

    @api.model
    def create(self, vals):
        if vals.get('partner_id'):
            res_partner_banks = self.env['res.partner.bank'].search([('partner_id','=', vals.get('partner_id'))])
            for rec in res_partner_banks:
                #ONly one account should be in active
                rec.active = False
        return super(ResPartnerBank, self).create(vals)

    @api.multi
    def write(self, vals):
        if vals.get('active') == True:
            if vals.get('partner_id'):
                res_partner_banks = self.env['res.partner.bank'].search([('partner_id','=', vals.get('partner_id')), ('id', '!=', self.id)])
            else:
                res_partner_banks = self.env['res.partner.bank'].search([('partner_id','=', self.partner_id.id),('id', '!=', self.id)])
            for rec in res_partner_banks:
                rec.active = False
        return super(ResPartnerBank, self).write(vals)



    # @api.multi
    # def write(self, vals):
    #     if vals.get('partner_id'):
    #         res_partner_banks = self.env['res.partner.bank'].search([('partner_id','=', vals.get('partner_id'))])
    #         for rec in res_partner_banks:
    #             rec.active = False
    #     return super(ResPartnerBank, self).create(vals)



        
