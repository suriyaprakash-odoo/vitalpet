from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AccountPaymentMode(models.Model):
    _inherit = 'account.payment.mode'

    group_vendor_account = fields.Boolean(string="Group Transaction by Vendor and Account in Payment Orders")
    allow_back_date = fields.Boolean(string="Allow Back Date")



    @api.constrains('group_vendor_account','group_lines')
    def _check_group_options(self):
        if self.group_vendor_account and self.group_lines:
            raise ValidationError(_('User can select only one group option'))


class BankPaymentLine(models.Model):
	_inherit = 'bank.payment.line'

	@api.model
	def account_same_fields_payment_line_and_bank_payment_line(self):
		res = super(BankPaymentLine, self).same_fields_payment_line_and_bank_payment_line()
		res.append('acc_number_id')
		return res
		




