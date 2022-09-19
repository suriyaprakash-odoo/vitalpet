from odoo import api, fields, models

# Class used to store configuration data. It is related to billpay.config.settings
class ResCompany(models.Model):
    _inherit = 'res.company'
    
    name = fields.Char(default='Billpay')
    incoming_fax = fields.Char()
    auto_post_bills = fields.Boolean()
    force_create_invoice = fields.Boolean()
    bill_approval_amount = fields.Integer(default="500")
    po_required_amount = fields.Integer(default="500")
    reverse_app_amt = fields.Integer(default="500")
    cancel_app_amt = fields.Integer(default="500")
    email_box = fields.Boolean()
    fax_box = fields.Boolean()
    ach_template_link = fields.Char("ACH Template Link")
    w9_template_link = fields.Char("W9 Template Link")
    
    billpay_processing_company = fields.Many2one('res.company', 'Parent Bill Pay Processing Company', default=lambda self: self.env.user.company_id)

    
    allowed_companies = fields.Many2many('res.company', 'billpay_allowed_companies_rel', 'src_id', 'dest_id', string='Allowed Companies')
    child_intercompany_account = fields.Many2one('account.account.tag','Child Intercompany Tag')
    intercompany_expense_account = fields.Many2one('account.account', 'Parent Intercompany Expense Account')
    standard_ap_account = fields.Many2one('account.account', 'Standard AP Account')
    standard_ar_account = fields.Many2one('account.account', 'Standard AR Account')
    billpayment_journal = fields.Many2one('account.journal', 'Parent Bill Payment Journal')
    child_payable_tag = fields.Many2one('account.account.tag', 'Child Payable Tag')
    child_receivable_tag = fields.Many2one('account.account.tag', 'Child Receivable Tag')
    intercompany_id_prefix = fields.Char('Intercompany ID Prefix', require=True)
    
    send_message = fields.Boolean('Send signup message to each manual pay vendor upon every payment')
    payment_signup_message = fields.Text('Electronic Payments Signup Message')
    payment_mode_ids = fields.Many2many("account.payment.mode",string="Payment Modes to Include")
    
    
    child_billpay_journal = fields.Many2one('account.journal', 'Child Billpay Journal')
    
# Configuration settings page fields.
class BillpayConfigSettings(models.TransientModel):
    _name = 'billpay.config.settings'
    _inherit = 'res.config.settings'
    


    # Company ID used to store all related data in this model
    billpay_processing_company = fields.Many2one('res.company', 'Parent Bill Pay Processing Company', default=lambda self: self.env.user.company_id)

    incoming_fax = fields.Char(related='billpay_processing_company.incoming_fax')
    auto_post_bills = fields.Boolean(related='billpay_processing_company.auto_post_bills')
    force_create_invoice = fields.Boolean(related='billpay_processing_company.force_create_invoice')
    bill_approval_amount = fields.Integer(related='billpay_processing_company.bill_approval_amount')
    po_required_amount = fields.Integer(related='billpay_processing_company.po_required_amount')
    reverse_app_amt = fields.Integer(related='billpay_processing_company.reverse_app_amt')
    cancel_app_amt = fields.Integer(related='billpay_processing_company.cancel_app_amt')
    allowed_companies = fields.Many2many('res.company', related='billpay_processing_company.allowed_companies')
    child_intercompany_account = fields.Many2one(related='billpay_processing_company.child_intercompany_account')
    
    intercompany_expense_account = fields.Many2one('account.account', related='billpay_processing_company.intercompany_expense_account')
    standard_ap_account = fields.Many2one('account.account', related='billpay_processing_company.standard_ap_account')
    standard_ar_account = fields.Many2one('account.account', related='billpay_processing_company.standard_ar_account')
    billpayment_journal = fields.Many2one('account.journal', related='billpay_processing_company.billpayment_journal')
    intercompany_id_prefix = fields.Char(related='billpay_processing_company.intercompany_id_prefix')
    send_message = fields.Boolean(related='billpay_processing_company.send_message')
    payment_signup_message = fields.Text(related='billpay_processing_company.payment_signup_message')
    alias_prefix = fields.Char('Default Alias Name for Expenses')  # Used to store alias email id
    alias_domain = fields.Char('Alias Domain', readonly=True, default=lambda self: self.env["ir.config_parameter"].get_param("mail.catchall.domain"))
    
    fax_prefix = fields.Char('Fax Mail Alias', default='message@inbound.efax.com')

    child_payable_tag = fields.Many2one('account.account.tag',related='billpay_processing_company.child_payable_tag', string='Child Payable Tag')
    child_receivable_tag = fields.Many2one('account.account.tag', related='billpay_processing_company.child_receivable_tag',string='Child Receivable Tag')
    email_box = fields.Boolean(related='billpay_processing_company.email_box')
    fax_box = fields.Boolean(related='billpay_processing_company.fax_box')
    payment_mode_ids = fields.Many2many("account.payment.mode",string="Payment Modes to Include", related='billpay_processing_company.payment_mode_ids')
    ach_template_link_id = fields.Many2one('signature.request.template',string="ACH Template Link",domain=[('archived','=',False)])
    w9_template_link_id = fields.Many2one('signature.request.template',string="W9 Template Link",domain=[('archived','=',False)])
    
    # Used to store alias domain.
#     Get and set default used to store in mail_alias table
    @api.model
    def get_default_alias_prefix(self, fields):
        alias_name = self.env.ref('vitalpet_bill_pay.mail_alias_billpay').alias_name
        ach = self.env['ir.values'].get_default('billpay.bills', 'ach_template_link_id')
        w9 = self.env['ir.values'].get_default('billpay.bills', 'w9_template_link_id')
        return {'alias_prefix': alias_name,'ach_template_link_id': ach,'w9_template_link_id':w9}

    @api.multi
    def set_default_alias_prefix(self):
        for record in self:
            self.env.ref('vitalpet_bill_pay.mail_alias_billpay').write({'alias_name': record.alias_prefix})
            ir_values_obj = self.env['ir.values']
            if record.ach_template_link_id:
                ir_values_obj.sudo().set_default('billpay.bills', "ach_template_link_id", record.ach_template_link_id.id, for_all_users=True)
            if record.w9_template_link_id:
                ir_values_obj.sudo().set_default('billpay.bills', "w9_template_link_id", record.w9_template_link_id.id, for_all_users=True)
            
    @api.multi
    def set_default_child_payable_receivable_tag(self):
        if self.child_payable_tag:
            payable_view_id = self.env.ref('vitalpet_bill_pay.action_account_payable')
            if payable_view_id:
                payable_view_id.write({'domain': "[('account_id.tag_ids', 'in', ["+ str(self.child_payable_tag.id) +"]), ('billpay_id', '=', None), ('credit', '>', 0)]"})
                
        if self.child_receivable_tag:
            receivable_view_id = self.env.ref('vitalpet_bill_pay.action_account_receivable')
            if receivable_view_id:
                receivable_view_id.write({'domain': "[('account_id.tag_ids', 'in', ["+ str(self.child_receivable_tag.id) +"]), ('billpay_id', '=', None)]"})
                
 
