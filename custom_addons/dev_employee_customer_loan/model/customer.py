# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 Devintelle Software Solutions (<http://devintellecs.com>).
#
##############################################################################

from odoo import fields, models, api, _
from email.utils import formataddr
from odoo.exceptions import UserError, ValidationError

class Partner(models.Model):
    _inherit = 'res.partner'

    partner_id=fields.Many2one('res.partner')
#    partner_employee_ids = fields.One2many('partner.employer', 'partner_id')
#    partner_existing_loan_ids = fields.One2many('existing.loan', 'partner_id')
#    partner_guarantor_ids = fields.One2many('partner.guarantor', 'partner_id')
    partner_property_ids = fields.One2many('partner.property', 'partner_id','Partner')

    type = fields.Selection(
        [('contact', 'Applicant Contact'),
         ('invoice', 'Other Contact Address'),
         ('delivery', 'Guarantor Address'),
         ('other', 'Mortgage Property Address'),], string='Address Type',
        default='contact',
        help="Used to select automatically the right address according to the context in sales and purchases documents.")

    # address_type=fields.Selection([('mortgage','Mortgage Property Address'),('Guarantor','Guarantor Address'),('other','Other Contact')], string = 'Address Type')
    first_name=fields.Char('First Name',size=32,required=True)
    last_name=fields.Char('Last Name',size=32,required=True)
#    chinese_first_name=fields.Char('Chinese First Name',size=32)
#    chinese_last_name=fields.Char('Chinese Last Name',size=32)
#    chinese_address=fields.Text('Chinese Address')
    customer_1=fields.Char('Customer 1',size=32,required=True)
    customer_2=fields.Char('Customer 2',size=32)
    mobile_1=fields.Char('Mobile 1')
    mobile_2=fields.Char('Mobile 2')
#    dob=fields.Date('Date of birth')
#    id_no=fields.Char('ID / Passport no.')
    loan_ids = fields.One2many('partner.loan', 'partner_id')

    @api.model
    def create(self, vals):
        if self._context.get('g_id'):
            vals.update({'type': 'delivery', 'parent_id': self._context.get('partner_id')})
            if not self._context.get('partner_id'):
                raise UserError("Please Save the Main Customer record first")
        elif self._context.get('p_id'):
            vals.update({'type': 'other', 'parent_id': self._context.get('partner_id')})
            if not self._context.get('partner_id'):
                raise UserError("Please Save the Main Customer record first")
        return super(Partner, self).create(vals)
        
    @api.multi
    def write(self, vals):
        name = ''
        if vals.get('first_name'):
            name = vals.get('first_name')
        else:
            name = self.first_name
            
        if vals.get('last_name'):
            name = name +' ' + vals.get('last_name')
        else:
            name = name +' ' + self.last_name
        vals['name'] = name
        return super(Partner, self).write(vals)
        
    @api.depends('is_company', 'name', 'parent_id.name', 'type', 'company_name')
    def _compute_display_name(self):
        res = super(Partner, self)._compute_display_name()
        for partner in self:
            partner.display_name = partner.name
        





#class PartnerEmployer(models.Model):
#    _name = 'partner.employer'

#    partner_id=fields.Many2one('res.partner')
#    name=fields.Char('Name of employer',size=32)
#    address=fields.Text('Address of Employer')
#    contact_number=fields.Char('Tel no. of employer', default='')
#    title=fields.Char('Title')
#    income=fields.Float('Monthly Income')
#    servicing_year=fields.Integer('Servicing Year')

#class ExistingLoan(models.Model):
#    _name = 'existing.loan'

#    partner_id=fields.Many2one('res.partner')
#    existing_loan_company=fields.Char('Existing Loan Company')
#    outstanding_loan_amount=fields.Float('Outstanding Loan Amount')
#    monthly_installment=fields.Float('Monthly installment')
#    remaining_terms=fields.Integer('Remaining terms')
#    attachment=fields.Binary('Attach File')
#    att_name = fields.Char('Attchment Name')


#class GuarantorInformation(models.Model):
#    _name = 'partner.guarantor'

#    @api.model
#    def default_get(self, fields_list):
#        res = super(GuarantorInformation, self).default_get(fields_list)
#        res.update({'partner_id': self._context.get('partner_id') or False})
#        return res

#    partner_id=fields.Many2one('res.partner','Customer')
#    guarantor_id=fields.Many2one('res.partner','Guarantor')
#    relation=fields.Char('Relationship with customer')
#    attachment_ids = fields.One2many('partner.attachment', 'guarantor_id', 'Attachment')



class PropertyInformation(models.Model):
    _name = 'partner.property'

    @api.model
    def default_get(self, fields_list):
        res = super(PropertyInformation, self).default_get(fields_list)
        res.update({'partner_id': self._context.get('partner_id') or False})
        return res

    partner_id=fields.Many2one('res.partner','Customer')
    property_id = fields.Many2one('res.partner', 'Property')

    address=fields.Text('Address')
    age=fields.Float('Property Age')
    value_company=fields.Char('Valuation company')
    value_date=fields.Date('Valuation Date')
    value_amount=fields.Float('Property Valuation Amount')
    existing_mortgage_bank=fields.Char('Existing Mortgage bank')
    outstanding_amount=fields.Float('Outstanding loan amount')
    monthly_installment=fields.Float('Monthly Installment')
    remaining_terms=fields.Integer('Remaining terms')

    attachment_ids=fields.One2many('partner.attachment','property_id','Attachment')

class PartnerAttachment(models.Model):
    _name = "partner.attachment"

    att_name = fields.Binary('Attachment')
    name = fields.Char('Attachment')
    guarantor_id = fields.Many2one('partner.guarantor', 'Gurantor')
    property_id = fields.Many2one('partner.property', 'Property')


















