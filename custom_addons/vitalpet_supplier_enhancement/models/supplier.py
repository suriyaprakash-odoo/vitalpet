from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError
import base64
import re
from socket import gethostname, gethostbyname 
from urllib2 import urlopen

class AccountNumber(models.Model):
    _name = "account.number"
    _order = "company_id asc, account_number asc"

#\----method to concatenate fields from Accounts numbers------    
    @api.multi
    @api.depends('account_number', 'company_id')
    def name_get(self):
        result = []
        for item in self:
            if item.company_id:
                name = item.company_id.code + "-" + item.account_number
            else:
                name = item.account_number
                
            result.append((item.id, name))
        return result
    
    company_id = fields.Many2one('res.company', string='Company')
    account_number = fields.Char(string='Account Number' , size=30)
    vendor_id = fields.Many2one('res.partner')
#\--------------To get unique account number-----------
    _sql_constraints = [
        ('account_number', 'unique (1=1)', 'Account Number already exists !')
    ]


class ResBank(models.Model):
        
    _inherit = 'res.bank'
    
    @api.multi
    @api.constrains('bic')
    def check_bic_length(self):
        for bank in self:
            if bank.bic and len(bank.bic) not in (8, 9, 11):
                raise ValidationError(_(
                    "A valid BIC contains 8,9 or 11 characters. The BIC '%s' "
                    "contains %d characters, so it is not valid.")
                    % (bank.bic, len(bank.bic)))


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    bank_account_type = fields.Char(string="Bank Type")

    _sql_constraints = [
        ('unique_number', 'unique(sanitized_acc_number, company_id, partner_id, bank_id, active)', 'Account Number must be unique'),
    ]

    # @api.multi
    # @api.constrains('acc_number','bank_id')
    # def _check_month(self):
    #     bank_count = self.env['res.partner.bank'].search_count([('acc_number','=',self.acc_number),('bank_id','=',self.bank_id.id),('active','=',True)])
    #     print bank_count,'--'
    #     if bank_count>=1:
    #         raise ValidationError(_('Account Number must be unique.'))


class Partner(models.Model): 
    _inherit = "res.partner"
    
    street = fields.Char(size=35)
    is_1099 = fields.Boolean(string="Is 1099")
    is_cron = fields.Boolean(string="Is Cron")
    w9_form = fields.Many2one('signature.request', string="W9 Form")
    bank_name = fields.Char(string="Bank Name", track_visibility='onchange')
    bank_routing = fields.Char(string="Bank Routing", track_visibility='onchange')
    bank_account = fields.Char(string="Bank Account", track_visibility='onchange')
    bank_account_type = fields.Char(string="Bank Type", track_visibility='onchange')
    ach_form = fields.Many2one('signature.request', string="ACH Form")
    account_number_ids = fields.One2many('account.number', 'vendor_id', string='Account Number')
    encrypt_value = fields.Boolean(string="Encrypted", default=False)
#     supplier_payment_mode_id = fields.Many2one(
#         'account.payment.mode', string='Supplier Payment Mode',
#         company_dependent=True,
#         track_visibility='onchange',
#         domain=[('payment_type', '=', 'outbound')],
#         help="Select the default payment mode for this supplier.")
    creating_user_id = fields.Many2one('res.users', 'Responsible',compute="_compute_creating_user_id")
    ip_address = fields.Char('IP Address',compute="_compute_ip_address" )
    
    @api.depends()
    def _compute_ip_address(self):
        for recs in self:
            recs.ip_address=gethostbyname(gethostname()) +" Public :"+urlopen('http://ip.42.pl/raw').read()
            
    @api.depends()
    def _compute_creating_user_id(self):
        for recs in self:
            recs.creating_user_id=self.env.user.id 
            
    
    @api.multi
    def send_w9_signup_link(self):
        print self, "partner"
        if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", self.email) != None:
            template_sr = self.env['ir.values'].search([('name', '=', 'w9_template_link_id')])        
            if not template_sr:            
                raise ValidationError(_('W9 link is empty. Please paste the link in configuration to send the mail'))  
            else:        
                temp_id = template_sr.value_unpickle           
                template_id = self.env['signature.request.template'].search([('id', '=', int(temp_id))])
            
            if template_id:
                signature_template = self.env["signature.request.template"].search([("id", "=", template_id.id)])
                reference = signature_template.attachment_id.name
                request_item = self.env["signature.item"].search([('template_id', '=', template_id.id)])
                if request_item:
                    for req in request_item:
                        if not req.responsible_id.id == 1:
                            raise ValidationError(_('Responsible ID for the template is not set for Customer'))
                else:
                    raise ValidationError(_('Responsible ID for the template is not set for Customer'))
            request_id = self.env["signature.request"].initialize_new(template_id.id, [{"partner_id":self.id, "role":1}], followers=[], reference=reference, subject="", message="", send=True)
            self.message_post(body=_('ACH link sent to %s. <a href=# data-oe-model=signature.request data-oe-id=%d>Click to view document</a>') % (self.email, request_id.get('id')))
            self.w9_form = request_id.id
        
    @api.multi
    def send_ach_signup_link(self,ctxt=None,payment_send=None):

        comapny_obj = self.env['res.company'].search([('name','=','TVET Operating PLLC')])
        i=0
        if comapny_obj.send_message == True:            
            for payment in comapny_obj.payment_mode_ids:
                if self.supplier_payment_mode_id.id == payment.id:
                    i=1
        if payment_send == None:
                i=1
        if i==1:
            if self.email:
                if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", self.email) != None:
                    template_sr = self.env['ir.values'].search([('name', '=', 'ach_template_link_id')])        
                    if not template_sr:            
                        raise ValidationError(_('ACH link is empty. Please paste the link in configuration to send the mail'))  
                    else:        
                        temp_id = template_sr.value_unpickle           
                        template_id = self.env['signature.request.template'].search([('id', '=', int(temp_id))])
                    if template_id:
                        signature_template = self.env["signature.request.template"].search([("id", "=", template_id.id)])
                        reference = signature_template.attachment_id.name
                        request_item = self.env["signature.item"].search([('template_id', '=', template_id.id)])
                        if request_item:
                            for req in request_item:
                                if not req.responsible_id.id == 1:
                                    raise ValidationError(_('Responsible ID for the template is not set for Customer'))
                        else:
                            raise ValidationError(_('Responsible ID for the template is not set for Customer'))
                        access_action = self.with_context(force_website=True).get_access_action()
                        print access_action,'access_action'
                       
                        request_id = self.env["signature.request"].initialize_new(template_id.id, [{"partner_id": self.id, "role": 1}], followers=[], reference=reference, subject="", message="", send=True)
                        self.message_post(body=_('ACH link sent to %s. <a href=# data-oe-model=signature.request data-oe-id=%d>Click to view document</a>') % (self.email, request_id.get('id')))
                        self.ach_form = request_id.get('id')


    
    def _post_messages_line_items(self, line, i, line_id):
        if line_id:   
            
            message_id = self.message_post(body=_('Default message'))
            if message_id:
                if line.has_key('supplier_payment_mode_id'): 
                    self._add_post_message_values(message_id, 'supplier_payment_mode_id', 'supplier_payment_mode_id', self.supplier_payment_mode_id.name, self.get_id_name('res.partner', line['supplier_payment_mode_id']))
                    self.message_post(body=_('Line item  %s updated .') % (i + 1))
        else:
            message_new_id = self.message_post(body=_('Line item  %s created .') % (i + 1))
            if line.has_key('supplier_payment_mode_id'): 
                self._add_post_message_values(message_new_id, 'supplier_payment_mode_id', 'supplier_payment_mode_id', '', self.get_id_name('res.partner', line['supplier_payment_mode_id']))
        
            self.message_post(body=_('Line item  %s created .') % (i + 1))
                
    def _add_post_message_values(self, message_id, field, field_desc, old_value_char, new_value_char):
        vals = {}
        vals['field'] = field
        vals['field_desc'] = field_desc
        vals['mail_message_id'] = message_id.id
        vals['new_value_char'] = new_value_char
        vals['old_value_char'] = old_value_char
        self.env['mail.tracking.value'].create(vals)
      
    @api.model
    def create(self, vals):
        if vals.get('vat'):
            vals['vat'] = base64.b64encode(vals.get('vat'))

        vals['encrypt_value'] = True
        if vals.get('country_id'):
            if self.env['res.country'].search([('id', '=', vals.get('country_id'))]).name == 'United States':
                if vals.get('zip'):
                    if len(vals.get('zip')) > 10:
                        raise ValidationError(_('Enter a valid Zip code'))
        res = super(Partner, self).create(vals)
        return res
        
    @api.multi
    def write(self, vals):
        for rec in self:
            if rec.encrypt_value == True:
                if vals.get('vat'):
                    vals['vat'] = base64.b64encode(vals.get('vat'))
                    
            if vals.get('bank_routing') or vals.get('bank_account'):
                vals['is_cron'] = False
        res = super(Partner, self).write(vals) 
    
        if vals.get('city'):
            if self.env['res.company'].search([('partner_id.name', '=', self.name)]):
                template_id = self.env.ref('vitalpet_supplier_enhancement.example_email_template')
                if not template_id:            
                    raise ValidationError(_('Please configure email template'))  
                else:        
                    if template_id:
                        template_id.send_mail(self.ids[0], force_send=True)
        return res
        
    @api.multi
    def encrpyt_decrypt_values(self):
        for rec in self:
            if rec.encrypt_value:
                rec.encrypt_value = False
                if rec.vat:
                    rec.vat = base64.b64decode(rec.vat)
            else:
                rec.encrypt_value = True
                if rec.vat:
                    rec.vat = rec.vat
        return True
    
    @api.multi
    def encrpyt_decrypt_all_cron(self):
        partner_count = self.env['res.partner'].search_count([('is_1099','=', True),('encrypt_value','=', False)])
        daily_partner = self.env['res.partner'].search([('is_1099','=', True)])
        
        print partner_count
        if partner_count>0:
            for rec in daily_partner:
                if rec.encrypt_value:
                    rec.encrypt_value = False
                    if rec.vat:
                        rec.vat = base64.b64decode(rec.vat)
        else:
            for rec in self:
                if not rec.encrypt_value:
                    rec.encrypt_value = True
                    if rec.vat:
                        rec.vat = rec.vat
            
        return True

    def update_is_cron_field(self):
        partner_obj = self.env['res.partner'].search([('id' , 'in' , [44575,44480])])

        for partner in partner_obj:
            partner.is_cron = True
        
    @api.multi
    def cron_daily_partner(self):
        daily_partner = self.env['res.partner'].search([('is_cron','=', False)])
        for daily in daily_partner:
            for partner in daily:
                if partner.bank_routing:
                    res_bank = self.env['res.bank'].search([('bic', '=', partner.bank_routing)],limit=1)
                    if res_bank:
                        partner.bank_name = res_bank.name
                    else:
                        if partner.bank_name:
                            res_bank = self.env['res.bank'].create({
                                'name': partner.bank_name,
                                'bic':partner.bank_routing,
                                }) 
                        else:
                            res_bank = self.env['res.bank'].create({
                                'name': 'undefined bank name' + ":" + partner.bank_routing,
                                'bic':partner.bank_routing
                                }) 
                        
                        partner.bank_name = res_bank.name

                    if partner.bank_account:                        

                        print partner.name
                        
                        existing_bank_new = self.env['res.partner.bank'].search([('partner_id','=',partner.id)])

                        if existing_bank_new:
                            i=0
                            for existing_bank in existing_bank_new:
                                if existing_bank.acc_number == partner.bank_account:
                                    i+=1
                                    print 'same bank'
                                    update_bank_others = self.env['res.partner.bank'].search([('acc_number', '=', partner.bank_account),('partner_id', '!=', partner.id),('active','=',True)])
                                    
                                    if update_bank_others:
                                        print 'other partner'  
                                        update_bank_others.status_active=False                  
                                        update_bank_others.active = False
                                        
                                        update_bank = self.env['res.partner.bank'].search([('acc_number', '=', partner.bank_account),('partner_id', '=', partner.id)])      
                                   
                                        if not update_bank:
                                            print 'no active bank'
                                            update_bank_false = self.env['res.partner.bank'].search([('acc_number', '=', partner.bank_account),('partner_id', '=', partner.id),('active','=',False)])  
                                            
                                            if update_bank_false:
                                                print 'if bank false'
                                                update_bank_false.status_active=True
                                                update_bank_false.active=True
    
                                            else:
                                                print 'bank create'
                                                self.env['res.partner.bank'].create({
                                                    'acc_number':partner.bank_account,
                                                    'bank_id':res_bank.id,
                                                    'partner_id':partner.id,
                                                    'company_id':partner.company_id.id,
                                                    'bank_account_type':partner.bank_account_type,
                                                    'status_active':True
                                                    })
                            if i==0:
                                print 'different bank'
                                for existing_bank in existing_bank_new:
                                    existing_bank.status_active=False
                                    existing_bank.active=False

                                self.env['res.partner.bank'].create({
                                    'acc_number':partner.bank_account,
                                    'bank_id':res_bank.id,
                                    'partner_id':partner.id,
                                    'company_id':partner.company_id.id,
                                    'bank_account_type':partner.bank_account_type,
                                    'status_active':True
                                    })
                        else:
                            update_bank_others = self.env['res.partner.bank'].search([('acc_number', '=', partner.bank_account),('partner_id', '!=', partner.id),('active','=',True)])
                                
                            if update_bank_others:
                                print 'other partner'  
                                update_bank_others.status_active=False                  
                                update_bank_others.active = False
                                print 'new create'
                                self.env['res.partner.bank'].create({
                                    'acc_number':partner.bank_account,
                                    'bank_id':res_bank.id,
                                    'partner_id':partner.id,
                                    'company_id':partner.company_id.id,
                                    'bank_account_type':partner.bank_account_type,
                                    'status_active':True
                                    })
                            else:
                                self.env['res.partner.bank'].create({
                                    'acc_number':partner.bank_account,
                                    'bank_id':res_bank.id,
                                    'partner_id':partner.id,
                                    'company_id':partner.company_id.id,
                                    'bank_account_type':partner.bank_account_type,
                                    'status_active':True
                                    })
                            
                        
                         
                    partner.write({'is_cron': True})
        
