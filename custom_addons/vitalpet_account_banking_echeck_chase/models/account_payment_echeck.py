from odoo import api, fields, models, _
import xlsxwriter
from lxml import etree
import base64
import time
import datetime
import csv
import logging
import re
from odoo.exceptions import UserError
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class AccountPaymentMethod(models.Model):
	_inherit = 'account.payment.method'

	@api.multi
	def get_xsd_file_path(self):
		self.ensure_one()
		if self.pain_version in ['echeck.chase.1.0']:
			path = 'vitalpet_account_banking_echeck_chase/data/%s.xsd'\
				% self.pain_version
			return path
		return super(AccountPaymentMethod, self).get_xsd_file_path()


	pain_version = fields.Selection(selection_add=[('echeck.chase.1.0', 'echeck.chase.1.0')])



class AccountPaymentLine(models.Model):
    _inherit = 'account.payment.line'

    check_number = fields.Char('Check Number')
	
   
class AccountPaymentOrder(models.Model):
	_inherit = "account.payment.order"

	#echeck_acc = fields.Many2one('echeck.payment.config', string='E-Check Account')

	def get_echeckfileheader(self):
		root_fileheader = etree.Element('FileHeaderRecord')
		RecordIdentifier = etree.Element('RecordIdentifier')
		RecordIdentifier.text = 'FILHDR'
		root_fileheader.append(RecordIdentifier)

		FileDestination = etree.Element('FileDestination')
		FileDestination.text = 'PWS'
		root_fileheader.append(FileDestination)

		CustomerId = etree.Element('CustomerId')
		CustomerId.text = ''
		root_fileheader.append(CustomerId)

		TransactionDate = etree.Element('TransactionDate')
		date = datetime.datetime.now().strftime("%m/%d/%Y")
		TransactionDate.text = str(date)
		root_fileheader.append(TransactionDate)

		TransactionTime = etree.Element('TransactionTime')
		time = datetime.datetime.now().strftime("%H%M")
		TransactionTime.text = str(time)
		root_fileheader.append(TransactionTime)
		return root_fileheader



	def get_filetrailer(self, number_record):
		root_filetrailer = etree.Element('FileTrailerRecord')
		RecordIdentifier = etree.Element('RecordIdentifier')
		RecordIdentifier.text = 'FILTRL'
		root_filetrailer.append(RecordIdentifier)

		NumberofRecords = etree.Element('NumberofRecords')		
		NumberofRecords.text = str(number_record).rjust(6,'0')
		root_filetrailer.append(NumberofRecords)

		return root_filetrailer


	def get_echeck_batchheader(self, vendor, check_seq,inv_account_number="empty"):
		batch_dic = {}
		payment_line_obj = self.env['account.payment.line']
		vendor_br = self.env['res.partner'].browse(vendor)
		if inv_account_number != "empty":
			payment_line_sr = payment_line_obj.search([('partner_id', '=', vendor), ('order_id', '=', self.id), ('invoice_id.acc_number_id', '=', inv_account_number)])
		else:
			payment_line_sr = payment_line_obj.search([('partner_id', '=', vendor), ('order_id', '=', self.id)])		
			
					



		tot_amt = 0.0
		for loop in payment_line_sr:
			# if payment_line_sr.invoice_id:
			tot_amt = tot_amt + loop.amount_currency

			loop.check_number = check_seq


		lst_batch = []
		#check_no = 0000001
		################################# for Entry Detail ###################################

		# for Payment Header ############	

		root_paymentheader = etree.Element('PaymentHeaderRecord')

		RecordIdentifier = etree.Element('RecordIdentifier')
		RecordIdentifier.text = 'PMTHDR'
		root_paymentheader.append(RecordIdentifier)

		CourierCode = etree.Element('CourierCode')
		courier_code = self.payment_mode_id.payment_method_id.courier_code
		CourierCode.text = courier_code or 'UPSOVN'
		root_paymentheader.append(CourierCode)

		FormCode = etree.Element('FormCode')
		FormCode.text = 'AP6V'
		root_paymentheader.append(FormCode)

		PaymentDate = etree.Element('PaymentDate')
		date = datetime.datetime.now().strftime("%m/%d/%Y")
		PaymentDate.text = str(date)
		root_paymentheader.append(PaymentDate)

		PaymentAmount = etree.Element('PaymentAmount')
		PaymentAmount.text = str("%.2f" % tot_amt)
		root_paymentheader.append(PaymentAmount)

		AccountNumber = etree.Element('AccountNumber')
		account_no = self.company_partner_bank_id.acc_number
		AccountNumber.text = str(account_no)
		root_paymentheader.append(AccountNumber)

		CheckNumber = etree.Element('CheckNumber')
		CheckNumber.text = str(check_seq)
		root_paymentheader.append(CheckNumber)

		lst_batch.append(root_paymentheader)
		batch_dic['PaymentHeaderRecord'] = lst_batch


		#Payee Name Record

		root_payeename = etree.Element('PayeeNameRecord')

		RecordIdentifier = etree.Element('RecordIdentifier')
		RecordIdentifier.text = 'PAYENM'
		root_payeename.append(RecordIdentifier)


		pattern = re.compile(r',')
            
		if vendor_br.name and pattern.findall(vendor_br.name):
		    raise UserError(_(
		        "Remove comma from %s") % vendor_br.name)
		if vendor_br.street and pattern.findall(vendor_br.street):
		    raise UserError(_(
		        "Remove comma from %s street") % vendor_br.name)
		if vendor_br.street2 and pattern.findall(vendor_br.street2):
		    raise UserError(_(
		        "Remove comma from %s street2") % vendor_br.name)

		PayeeName1 = etree.Element('PayeeName1')
		PayeeName1.text = vendor_br.name
		root_payeename.append(PayeeName1)


		PayeeName2 = etree.Element('PayeeName2')
		PayeeName2.text = ''
		root_payeename.append(PayeeName2)

		VendorNumber = etree.Element('VendorNumber')
		VendorNumber.text = vendor_br.ref
		root_payeename.append(VendorNumber)


		lst_batch.append(root_payeename)
		batch_dic['PayeeNameRecord'] = lst_batch


		# Payee Address Record

		root_payeeaddress = etree.Element('PayeeAddressRecord')

		RecordIdentifier = etree.Element('RecordIdentifier')
		RecordIdentifier.text = 'PYEADD'
		root_payeeaddress.append(RecordIdentifier)

		PayeeAddress1 = etree.Element('PayeeAddress1')
		PayeeAddress1.text = vendor_br.street or ''
		root_payeeaddress.append(PayeeAddress1)

		PayeeAddress2 = etree.Element('PayeeAddress2')
		PayeeAddress2.text = vendor_br.street2 or ''
		root_payeeaddress.append(PayeeAddress2)	

		lst_batch.append(root_payeeaddress)
		batch_dic['PayeeAddressRecord'] = lst_batch


		# Additional Payee Address Record


		root_addpayeeaddress = etree.Element('AdditionalPayeeAddressRecord')

		RecordIdentifier = etree.Element('RecordIdentifier')
		RecordIdentifier.text = 'ADDPYE'
		root_addpayeeaddress.append(RecordIdentifier)

		PayeeAddress3 = etree.Element('PayeeAddress3')
		PayeeAddress3.text = ''
		root_addpayeeaddress.append(PayeeAddress3)

		PayeeAddress2 = etree.Element('PayeeAddress4')
		PayeeAddress2.text = ''
		root_addpayeeaddress.append(PayeeAddress2)

		lst_batch.append(root_addpayeeaddress)
		batch_dic['PayeeAddressRecord'] = lst_batch



		# Payee Postal Record

		root_payeepostal = etree.Element('PayeePostalRecord')

		RecordIdentifier = etree.Element('RecordIdentifier')
		RecordIdentifier.text = 'PYEPOS'
		root_payeepostal.append(RecordIdentifier)

		PayeeCity = etree.Element('PayeeCity')
		PayeeCity.text = vendor_br.city or ''
		root_payeepostal.append(PayeeCity)

		PayeeState = etree.Element('PayeeState')
		PayeeState.text = vendor_br.state_id.code or ''
		root_payeepostal.append(PayeeState)

		PayeeZip = etree.Element('PayeeZip')
		PayeeZip.text = vendor_br.zip or ''
		root_payeepostal.append(PayeeZip)

		PayeeCountry = etree.Element('PayeeCountry')
		PayeeCountry.text = vendor_br.country_id.code or ''
		root_payeepostal.append(PayeeCountry)

		lst_batch.append(root_payeepostal)
		batch_dic['PayeePostalRecord'] = lst_batch


		# Remittance Detail Record

		root_remittance = etree.Element('Remittance')
		remittance_dic = {}
		remittance_lst = []
		for loop in payment_line_sr:
			invoice_obj = self.env['account.invoice']
			inv_sr = invoice_obj.search([('number', '=', loop.move_line_id.move_id.name)])	

			root_remittancetype = etree.Element('RemittanceType')

			RecordIdentifier = etree.Element('RecordIdentifier')
			RecordIdentifier.text = 'RMTDTL'
			root_remittancetype.append(RecordIdentifier)

			InvoiceNumber = etree.Element('InvoiceNumber')
			if inv_sr.invoice_number:
				InvoiceNumber.text = inv_sr.invoice_number
			else:
				InvoiceNumber.text = inv_sr.number

			root_remittancetype.append(InvoiceNumber)

			Description = etree.Element('Description')
			if inv_sr.acc_number_id:
				Description.text = inv_sr.acc_number_id.account_number
			elif inv_sr.reference:
				if len(inv_sr.reference) <= 30:
					Description.text = inv_sr.reference
				else:
					Description.text = loop.communication
			else:
				Description.text = inv_sr.number
			root_remittancetype.append(Description)

			InvoiceDate = etree.Element('InvoiceDate')
			inv_date = datetime.datetime.strptime(str(inv_sr.date_invoice), '%Y-%m-%d').strftime('%m/%d/%Y')
			#date = datetime.datetime.now().strftime("%m/%d/%Y")
			#TransactionDate.text = str(date)[2:]
			InvoiceDate.text = str(inv_date)
			root_remittancetype.append(InvoiceDate)

			NetAmount = etree.Element('NetAmount')
			NetAmount.text = str("%.2f" % loop.amount_company_currency)

			root_remittancetype.append(NetAmount)


			GrossAmount = etree.Element('GrossAmount')
			GrossAmount.text = str("%.2f" % loop.amount_company_currency)
			root_remittancetype.append(GrossAmount)

			DiscountAmount = etree.Element('DiscountAmount')
			DiscountAmount.text = str("%.2f" % 0.00)
			root_remittancetype.append(DiscountAmount)

			remittance_lst.append(root_remittancetype)
			remittance_dic['RemittanceType'] = remittance_lst

			lst_batch.append(root_remittancetype)
			batch_dic['RemittanceType'] = lst_batch
			# count = count+1

			batch_dic = {}
		return lst_batch



	@api.multi
	def finalize_echeck_file_creation(self, xml_root, gen_args):
		if self.payment_mode_id.name == "E-Check":
			xml_string = etree.tostring(
				xml_root, pretty_print=True, encoding='UTF-8',
				xml_declaration=True)
			logger.debug(
				"Generated SEPA XML file in format %s below"
				% gen_args['pain_flavor'])
			logger.debug(xml_string)
			self._validate_xml(xml_string, gen_args)

			filename = '%s%s.xml' % (gen_args['file_prefix'], self.name)
			return (xml_string, filename)




	@api.multi
	def generate_echeck_payment_file(self):
		if self.payment_mode_id.name == "E-Check":
			xsd_file = self.payment_method_id.get_xsd_file_path()
			gen_args = {
			'convert_to_ascii': self.payment_method_id.convert_to_ascii,
			'file_prefix': 'echeck_',
			'pain_flavor': 'echeck.chase.1.0',
			'pain_xsd_file': xsd_file,
			}
			echeck_fileheader = self.get_echeckfileheader()
			trans_len = len(self.payment_line_ids)
			lst = []
			vendor_lst =[] 
			vendor_lst_count=[]
			account_numbers = []

			for loop in self.payment_line_ids:
				# account_number = False
				# if loop.invoice_id:
				# 	if loop.invoice_id.acc_number_id:
				# 		account_numbers.append(loop.invoice_id.acc_number_id.id)
				# 		account_number = loop.invoice_id.acc_number_id.id
				# 	else:
				# 		account_numbers.append(account_number)
				# else:
				# 	account_numbers.append(account_number)
				# print account_number
				# print account_numbers
				# if account_number not in account_numbers:
				# 	print account_number,"asdasdas"
				# 	unique_lst.append(loop.partner_id.id)

				# # if loop.invoice_id:
				# # 	if loop.invoice_id.acc_number_id:
				# # 		account_numbers.append(loop.invoice_id.acc_number_id.id)
				# # if loop.invoice_id.acc_number_id.id not in 

				lst.append(loop)
									
				vendor_lst.append(loop.partner_id.id)
				vendor_acc = str(loop.partner_id.id)+"-"+str(loop.acc_number_id.id)
				vendor_lst_count.append(vendor_acc)
			unique_lst = set(vendor_lst)
			unique_lst_count = set(vendor_lst_count)
			print len(unique_lst)
			print len(unique_lst_count)

			unique_lst = list(unique_lst)
			unique_lst_count = list(unique_lst_count)
			root_echeck = etree.Element('Document')
			root_echeck.append(echeck_fileheader)
			number_of_record = len(unique_lst_count)*5 + trans_len + 2
			echeck_filetrailer = self.get_filetrailer(number_of_record)
			payment_group = etree.Element('Payment')
			count = 1
			for batch_loop in unique_lst:
				check_seq = self.env['ir.sequence'].next_by_code('e_check')
				if self.payment_mode_id.name=='E-Check':
					payment_line_obj = self.env['account.payment.line']
					vendor_br = self.env['res.partner'].browse(batch_loop)
					payment_lines = payment_line_obj.search([('partner_id', '=', batch_loop), ('order_id', '=', self.id)])
					inv_account_numbers = []
					for payment_line in payment_lines:
						inv_account_number = False
						if payment_line.invoice_id:
							if payment_line.invoice_id.acc_number_id:
								inv_account_number = payment_line.invoice_id.acc_number_id.id
						inv_account_numbers.append(inv_account_number)
											
					unique_inv_account_number = set(inv_account_numbers)
					find_account=0
					for inv_account_number in unique_inv_account_number:
						if find_account>0:
							check_seq = self.env['ir.sequence'].next_by_code('e_check')
						find_account+=1
						batch = self.get_echeck_batchheader(batch_loop, check_seq, inv_account_number)
						count = count + 1
						for loop in batch:
							payment_group.append(loop)
				else:
					batch = self.get_echeck_batchheader(batch_loop, check_seq, "empty")
					count = count + 1
					for loop in batch:
						payment_group.append(loop)

					
			root_echeck.append(payment_group)
			root_echeck.append(echeck_filetrailer)
# 			return False
			return self.finalize_echeck_file_creation(root_echeck, gen_args)



	@api.multi
	def open2generated(self):
		self.ensure_one()
		if self.payment_method_id.code != 'echeck_chase_transfer':
			return super(AccountPaymentOrder, self).open2generated()
		payment_file_str, filename = self.generate_echeck_payment_file()
		action = {}
		if payment_file_str and filename:
			attachment = self.env['ir.attachment'].create({
				'res_model': 'account.payment.order',
				'res_id': self.id,
				'name': filename,
				'datas': payment_file_str.encode('base64'),
				'datas_fname': filename,
				})
			simplified_form_view = self.env.ref(
				'account_payment_order.view_attachment_simplified_form')
			action = {
				'name': _('Payment File'),
				'view_mode': 'form',
				'view_id': simplified_form_view.id,
				'res_model': 'ir.attachment',
				'type': 'ir.actions.act_window',
				'target': 'current',
				'res_id': attachment.id,
				}
			self.write({
				'date_generated': fields.Date.context_today(self),
				'state': 'generated',
				'generated_user_id': self._uid,
				})
			return action


	@api.multi
	def update_check_number(self):
		for pay_order in self.env['account.payment.order'].search([('payment_mode_id.name','=','E-Check'),('state','=','processed')]):
			attachment_obj = self.env['ir.attachment'].search([('res_id','=',pay_order.id),('res_model','=','account.payment.order')],limit=1, order="id desc")

			attachment_path = attachment_obj._full_path(attachment_obj.store_fname)

			with open(attachment_path, 'r') as fileObj:
				soup = BeautifulSoup(fileObj.read(), 'xml')
				sub_node = soup.children
				list1=[]
				list2=[]
				list3=[]
				for payment in sub_node:				
						for payment_cheque in payment.find_all('CheckNumber'):
							list1.append(payment_cheque.text)

						for payment_list in payment.find_all('PaymentAmount'):
							list2.append(payment_list.text)

						for payment_list in payment.find_all('VendorNumber'):
							list3.append(payment_list.text)
				i=0
				for row in list1:
					# print pay_order.id,'--!!',list3[i],'!!--',list2[i]
					for pay_line in self.env['account.move'].search([('id','=',235214),('payment_order_id','=',pay_order.id),('partner_id','=',int(list3[i]))]):
						
						if float("%.2f" % round(pay_line.amount,2))==float(list2[i]):
							print 1111
							for line in pay_line.line_ids:
								#print line.account_id.name,'!!!!!'
								if line.account_id.name != 'Accounts Payable':
									print line.account_id.name,'!!!'
									if line.ref:
										line.name = line.ref
										line.ref = line.name+' - CHECK '+str(int(row))
									else:
										line.name = ''
										line.ref = 'CHECK '+str(int(row))
					i+=1


		# print '---',attachment_obj,'---'

	# def gen_echeck(self):
	# 	echeck_fileheader = self.get_echeckfileheader()
	# 	echeck_filetrailer = self.get_filetrailer()
	# 	trans_len = len(self.payment_line_ids)
	# 	lst = []
	# 	vendor_lst = []
	# 	for loop in self.payment_line_ids:
	# 		lst.append(loop)
	# 		vendor_lst.append(loop.partner_id.id)
	# 		unique_lst = set(vendor_lst)
	# 	unique_lst = list(unique_lst)
	# 	len_unique_lst = len(unique_lst)
	# 	root_echeck = etree.Element('Document')
	# 	root_echeck.append(echeck_fileheader)
	# 	#s = zip(*[iter(lst)]*3)
	# 	count = 1
	# 	for batch_loop in unique_lst:
	# 		batch = self.get_echeck_batchheader(batch_loop, count)
	# 		count = count + 1
	# 		for loop in batch:
	# 			root_echeck.append(loop)
	# 	#root.append(filecontrol)
	# 	root_echeck.append(echeck_filetrailer)
	# 	final = etree.tostring(root_echeck, pretty_print=True, xml_declaration=True, encoding="UTF-8")
	# 	attachment = self.env['ir.attachment'].create({
	# 			'res_model': 'account.payment.order',
	# 			'res_id': self.id,
	# 			'name': 'echeck.xml',
	# 			'datas': final.encode('base64'),
	# 			'datas_fname': 'echeck.xml',
	# 			})
	# 	return True
