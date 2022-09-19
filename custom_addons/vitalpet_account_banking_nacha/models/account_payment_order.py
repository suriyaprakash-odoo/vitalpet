from odoo import api, fields, models, _
from lxml import etree
import base64
import time
import datetime
import re
import pprint
import logging
import random
from odoo.exceptions import UserError


logger = logging.getLogger(__name__)

seq_lst = ['0','1','2','3','4','5','6','7','8','9','A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']


class AccountPaymentMethod(models.Model):
	_inherit = 'account.payment.method'

	@api.multi
	def get_xsd_file_path(self):
		self.ensure_one()
		if self.pain_version in ['NACHA.xml.1.0']:
			path = 'vitalpet_account_banking_nacha/data/%s.xsd'\
				% self.pain_version
			return path
		return super(AccountPaymentMethod, self).get_xsd_file_path()


	pain_version = fields.Selection(selection_add=[('NACHA.xml.1.0', 'NACHA.xml.1.0')])

	
   
class AccountPaymentOrder(models.Model):
	_inherit = "account.payment.order"
	
	# bank_ach = fields.Many2one('ach.payment.config', string='Bank ACH')

	@api.multi
	def generate_pain_nsmap(self):
		self.ensure_one()
		if self.payment_mode_id.name == 'ACH':
			pain_flavor = self.payment_mode_id.payment_method_id.pain_version
			nsmap = {
				'xsi': 'http://www.w3.org/2001/XMLSchema',
			}
			return nsmap


	def get_fileheader(self):
		#payment_order_obj = self.env['account.payment.order'].search([('','','')])

		root_fileheader = etree.Element('FileHeaderRecord')
		RecordTypeCode = etree.Element('RecordTypeCode')
		RecordTypeCode.text = '1'
		root_fileheader.append(RecordTypeCode)

		PriorityCode = etree.Element('PriorityCode')
		PriorityCode.text = '01'
		root_fileheader.append(PriorityCode)

		ImmediateDestination = etree.Element('ImmediateDestination')
		value = self.company_id.initiating_party_issuer
		yourstring = " {0}".format('021000021')
		ImmediateDestination.text = value.rjust(10)
		root_fileheader.append(ImmediateDestination)

		ImmediateOrigin = etree.Element('ImmediateOrigin')
		value = self.company_id.immediate_origin
		ImmediateOrigin.text = value
		root_fileheader.append(ImmediateOrigin)

		FileCreationDate = etree.Element('FileCreationDate')
		date = datetime.datetime.now().strftime("%Y%m%d")
		FileCreationDate.text = str(date)[2:]
		root_fileheader.append(FileCreationDate)

		FileCreationTime = etree.Element('FileCreationTime')
		time = datetime.datetime.now().strftime("%H%M")
		FileCreationTime.text = str(time)
		root_fileheader.append(FileCreationTime)

		FileIdModifier = etree.Element('FileIdModifier')
		seq = random.choice(seq_lst)
		FileIdModifier.text = str(seq)
		root_fileheader.append(FileIdModifier)


		RecordSize = etree.Element('RecordSize')
		RecordSize.text = '094'
		root_fileheader.append(RecordSize)

		BlockingFactor = etree.Element('BlockingFactor')
		BlockingFactor.text = '10'
		root_fileheader.append(BlockingFactor)

		FormatCode = etree.Element('FormatCode')
		FormatCode.text = '1'
		root_fileheader.append(FormatCode)

		ImmediateDestinationName = etree.Element('ImmediateDestinationName')
		maxlength = 23
		value = 'JPMorgan' 
		rem = maxlength - len(value)
		s = '{:<'+str(maxlength)+'}'
		c = s.format(value)
		ImmediateDestinationName.text = c
		root_fileheader.append(ImmediateDestinationName)

		ImmediateOriginName = etree.Element('ImmediateOriginName')
		maxlength = 23
		value = 'TVET OPERATING PLLC' 
		rem = maxlength - len(value)
		s = '{:<'+str(maxlength)+'}'
		c = s.format(value)
		ImmediateOriginName.text = c
		root_fileheader.append(ImmediateOriginName)
 
		ReferenceCode = etree.Element('ReferenceCode')
		maxlength = 8
		value = '' 
		rem = maxlength - len(value)
		s = '{:<'+str(maxlength)+'}'
		c = s.format(value)
		ReferenceCode.text=c
		root_fileheader.append(ReferenceCode)
		self.write({'order_seq':seq})
		return root_fileheader


	def get_filecontrol(self):
		amt = 0.0
		batch_count = 0
		block_count = 0
		hash_sum = 0
#		if self.payment_line_ids:
		if self.bank_line_ids:
#			length = len(self.payment_line_ids)
			length = len(self.bank_line_ids)
			batch_count = length
			count = length * 4 + 2
			count_len = []
			for x in range(0, count, 10):
				count_len.append(x)
			block_count = int(len(count_len))
			addenda_count = length * 2


#		for loop in self.payment_line_ids:
		for loop in self.bank_line_ids:
			amt = amt + loop.amount_currency
			if not loop.partner_bank_id.bank_id or not loop.partner_bank_id.bank_id.bic:
				raise UserError(_(
                    "ABA/Routing Number is Empty for %s ") % loop.partner_id.name)

			route = loop.partner_bank_id.bank_id.bic
			routing = str(route)[:8]
			hash_sum = hash_sum + int(routing)


		root_filecontrol = etree.Element('FileControlRecord')

		RecordTypeCode = etree.Element('RecordTypeCode')
		RecordTypeCode.text = '9'
		root_filecontrol.append(RecordTypeCode)

		BatchCount = etree.Element('BatchCount')
		maxlength = 6
		s = '{:>0'+str(maxlength)+'}'
		c = s.format(batch_count)
		BatchCount.text = str(c)
		
		root_filecontrol.append(BatchCount)

		BlockCount = etree.Element('BlockCount')
		maxlength = 6
		s = '{:>0'+str(maxlength)+'}'
		c = s.format(block_count)
		BlockCount.text = str(c)
		root_filecontrol.append(BlockCount)

		EntryCount = etree.Element('EntryCount')
		maxlength = 8
		s = '{:>0'+str(maxlength)+'}'
		c = s.format(addenda_count)
		EntryCount.text = str(c)
		root_filecontrol.append(EntryCount)


		EntryHash = etree.Element('EntryHash')
		maxlength=10
		s = '{:>0'+str(maxlength)+'}'
		hash_final = s.format(str(hash_sum))
		EntryHash.text = s.format(str(hash_final))
		root_filecontrol.append(EntryHash)



		TotalDebit = etree.Element('TotalDebit')
		TotalDebit.text = '000000000000'
		root_filecontrol.append(TotalDebit)


		TotalCredit = etree.Element('TotalCredit')
		maxlength=12
		str_amt = int(round(amt*100))
		s = '{:>0'+str(maxlength)+'}'
		amt_final = s.format(str(str_amt))
		TotalCredit.text = s.format(amt_final)
		root_filecontrol.append(TotalCredit)

		Reserved = etree.Element('Reserved')
		maxlength = 39
		value = '' 
		rem = maxlength - len(value)
		s = '{:<'+str(maxlength)+'}'
		c = s.format(value)
		Reserved.text = c
		root_filecontrol.append(Reserved)
		return root_filecontrol


	def get_batchheader(self, payment_line_sr, count):
		batch_dic = {}
# 		payment_line_obj = self.env['account.payment.line']
		payment_line_obj = self.env['bank.payment.line']
		lst_batch = []
		batch_count = 0000001
		
		###### for Batch Header ######
		root_batchheader = etree.Element('BatchHeaderRecord')

		RecordTypeCode = etree.Element('RecordTypeCode')
		RecordTypeCode.text = '5'
		root_batchheader.append(RecordTypeCode)

		ServiceClassCode = etree.Element('ServiceClassCode')
		ServiceClassCode.text = '200'
		root_batchheader.append(ServiceClassCode)

		CompanyName = etree.Element('CompanyName')
		maxlength = 16
		value = 'TVET OPERATING' 
		rem = maxlength - len(value)
		s = '{:<'+str(maxlength)+'}'
		c = s.format(value)
		CompanyName.text = c
		root_batchheader.append(CompanyName)

		CompanyDiscretionaryData = etree.Element('CompanyDiscretionaryData')
		maxlength = 20
		value = '' 
		rem = maxlength - len(value)
		s = '{:<'+str(maxlength)+'}'
		c = s.format(value)
		CompanyDiscretionaryData.text = c
		root_batchheader.append(CompanyDiscretionaryData)

		CompanyIdentification = etree.Element('CompanyIdentification')
		value = self.company_id.initiating_party_identifier
		CompanyIdentification.text = value
		root_batchheader.append(CompanyIdentification)

		StandardEntryClassCode = etree.Element('StandardEntryClassCode')
		StandardEntryClassCode.text = 'CCD'
		root_batchheader.append(StandardEntryClassCode)


		CompanyEntryDescription = etree.Element('CompanyEntryDescription')
		CompanyEntryDescription.text = 'Vendor Pmt'
		root_batchheader.append(CompanyEntryDescription)

		CompanyDescriptiveDate = etree.Element('CompanyDescriptiveDate')
		date = datetime.datetime.now().strftime("%b %d").upper()
		CompanyDescriptiveDate.text = str(date)
		root_batchheader.append(CompanyDescriptiveDate)


		EffectiveEntryDate = etree.Element('EffectiveEntryDate')
		tomorrow = datetime.date.today() + datetime.timedelta(days=1)
		date = tomorrow.strftime("%Y%m%d")
		EffectiveEntryDate.text = str(date)[2:]
		root_batchheader.append(EffectiveEntryDate)

		SettlementDate = etree.Element('SettlementDate')
		SettlementDate.text = '   '
		root_batchheader.append(SettlementDate)


		OriginStatusCode = etree.Element('OriginStatusCode')
		OriginStatusCode.text = '1'
		root_batchheader.append(OriginStatusCode)

		OriginDFIIdentification = etree.Element('OriginDFIIdentification')
		string = self.company_id.immediate_origin
		value = string[1:-1]
		OriginDFIIdentification.text = value
		root_batchheader.append(OriginDFIIdentification)

		BatchNumber = etree.Element('BatchNumber')
		maxlength=7
		trace = str(count)
		s = '{:>0'+str(maxlength)+'}'
		BatchNumber.text = s.format(trace)
		root_batchheader.append(BatchNumber)
		lst_batch.append(root_batchheader)
		batch_dic['batch_header'] = lst_batch
		#batch_count = batch_count + 1
		dic = {}
		lst_entrydetail = []    
		tracenumber = 0000001
		addenda_count = 0000001
		################################# for Entry Detail ###################################
		for pmt_line_loop in payment_line_sr:
			root_entrydetail = etree.Element('CCDEntryDetailRecord')

			RecordTypeCode = etree.Element('RecordTypeCode')
			RecordTypeCode.text = '6'
			root_entrydetail.append(RecordTypeCode)

			TransactionCode = etree.Element('TransactionCode')
			TransactionCode.text = '22'
			root_entrydetail.append(TransactionCode)

			ReceivingDFIIdentification = etree.Element('ReceivingDFIIdentification')
			maxlength = 8
			route = payment_line_sr.partner_bank_id.bank_id.bic
			routing = str(route)[:8]
			ReceivingDFIIdentification.text = str(routing)
			root_entrydetail.append(ReceivingDFIIdentification)

			CheckDigit = etree.Element('CheckDigit')
			maxlength = 1
			route = payment_line_sr.partner_bank_id.bank_id.bic
			routing = str(route)[-1]
			CheckDigit.text = routing
			root_entrydetail.append(CheckDigit)

			DFIAccountNumber = etree.Element('DFIAccountNumber')
			maxlength = 17
			value = payment_line_sr.partner_bank_id.acc_number
			rem = maxlength - len(value)
			s = '{:<'+str(maxlength)+'}'
			c = s.format(value)
			DFIAccountNumber.text = c
			root_entrydetail.append(DFIAccountNumber)

			Amount = etree.Element('Amount')
			digitlength = 10
			amt = pmt_line_loop.amount_currency
			str_amt = int(round(amt*100))
			s = '{:>0'+str(digitlength)+'}'
			amt_final = s.format(str(str_amt))
			Amount.text = amt_final
			root_entrydetail.append(Amount)


			IdentificationNumber = etree.Element('IdentificationNumber')
			maxlength = 15
			value = pmt_line_loop.name 
			rem = maxlength - len(value)
			s = '{:<'+str(maxlength)+'}'
			c = s.format(value)
			IdentificationNumber.text = c
			root_entrydetail.append(IdentificationNumber)

			IndividualName = etree.Element('IndividualName')
			maxlength = 22
			value = pmt_line_loop.partner_id.name 
			rem = maxlength - len(value)
			s = '{:<'+str(maxlength)+'}'
			c = s.format(value)
			IndividualName.text = c
			root_entrydetail.append(IndividualName)


			DiscretionaryData = etree.Element('DiscretionaryData')
			DiscretionaryData.text = '  '
			root_entrydetail.append(DiscretionaryData)

			AddendaRecordIndicator = etree.Element('AddendaRecordIndicator')
			AddendaRecordIndicator.text = '1'
			root_entrydetail.append(AddendaRecordIndicator)


			TraceNumber = etree.Element('TraceNumber')
			maxlength=7
			trace = str(tracenumber)
			s = '{:>0'+str(maxlength)+'}'
			s.format(trace)
			string = self.company_id.immediate_origin
			value = string[1:-1]
			TraceNumber.text =  value+s.format(trace)
			root_entrydetail.append(TraceNumber)
			lst_batch.append(root_entrydetail)
			batch_dic['entry_detail'] = lst_batch
			tracenumber = tracenumber+1
			

			root_addenda = etree.Element('CommonAddendaRecord')

			RecordTypeCode = etree.Element('RecordTypeCode')
			RecordTypeCode.text = '7'
			root_addenda.append(RecordTypeCode)

			AddendaTypeCode = etree.Element('AddendaTypeCode')
			AddendaTypeCode.text = '05'
			root_addenda.append(AddendaTypeCode)

			PaymentRelatedInfo = etree.Element('PaymentRelatedInfo')
			maxlength = 80
			pmt = 'RMR*PO*'+str(pmt_line_loop.communication)+'\\'
			if len(pmt)>80:
				pmt=pmt[:75]
			value = pmt 
			rem = maxlength - len(value)
			s = '{:<'+str(maxlength)+'}'
			c = s.format(value)
			PaymentRelatedInfo.text = c
			root_addenda.append(PaymentRelatedInfo)

			AddendaSequenceNumber = etree.Element('AddendaSequenceNumber')
			AddendaSequenceNumber.text = '0001'
			root_addenda.append(AddendaSequenceNumber)

			EntryDetailSequenceNumber = etree.Element('EntryDetailSequenceNumber')
			maxlength=7
			trace = str(addenda_count)
			s = '{:>0'+str(maxlength)+'}'
			c = s.format(trace)
			EntryDetailSequenceNumber.text = c
			root_addenda.append(EntryDetailSequenceNumber)
			addenda_count = addenda_count+1
			#lst_addenda.append(root_addenda)
			lst_batch.append(root_addenda)
			batch_dic['addenda'] = lst_batch
			#lst_entrydetail.append(batch_dic)


		####################### for Batch Control ################### 

		root_batchcontrol = etree.Element('BatchControlRecord')

		RecordTypeCode = etree.Element('RecordTypeCode')
		RecordTypeCode.text = '8'
		root_batchcontrol.append(RecordTypeCode)

		ServiceClassCode = etree.Element('ServiceClassCode')
		ServiceClassCode.text = '200'
		root_batchcontrol.append(ServiceClassCode)

		EntryCount = etree.Element('EntryCount')
		maxlength = 6
		value = 2
		s = '{:>0'+str(maxlength)+'}'
		c = s.format(value)
		EntryCount.text = c
		root_batchcontrol.append(EntryCount)

		EntryHash = etree.Element('EntryHash')
		maxlength = 10
		route = payment_line_sr.partner_bank_id.bank_id.bic
		routing = str(route)[:8]
		s = '{:>0'+str(maxlength)+'}'
		EntryHash.text = s.format(routing)
		root_batchcontrol.append(EntryHash)

		TotalDebit = etree.Element('TotalDebit')
		maxlength=12
		TotalDebit.text = s.format('000000000000')
		root_batchcontrol.append(TotalDebit)

		TotalCredit = etree.Element('TotalCredit')
		maxlength=12
		amt = pmt_line_loop.amount_currency
		str_amt = int(round(amt*100))
		s = '{:>0'+str(maxlength)+'}'
		amt_final = s.format(str(str_amt))
		TotalCredit.text = s.format(amt_final)
		root_batchcontrol.append(TotalCredit)


		CompanyIdentification = etree.Element('CompanyIdentification')
		CompanyIdentification.text = '9722708002'
		root_batchcontrol.append(CompanyIdentification)



		MessageAuthenticationCode = etree.Element('MessageAuthenticationCode')
		maxlength = 19
		value = '' 
		rem = maxlength - len(value)
		s = '{:<'+str(maxlength)+'}'
		c = s.format(value)
		MessageAuthenticationCode.text =c
		root_batchcontrol.append(MessageAuthenticationCode)


		Reserved = etree.Element('Reserved')
		maxlength = 6
		value = '' 
		rem = maxlength - len(value)
		s = '{:<'+str(maxlength)+'}'
		c = s.format(value)
		Reserved.text = c
		root_batchcontrol.append(Reserved)

		OriginDFIIdentification = etree.Element('OriginDFIIdentification')
		OriginDFIIdentification.text = '77585108'
		root_batchcontrol.append(OriginDFIIdentification)


		BatchNumber = etree.Element('BatchNumber')
		maxlength=7
		trace = str(count)
		s = '{:>0'+str(maxlength)+'}'
		BatchNumber.text = s.format(trace)
		root_batchcontrol.append(BatchNumber)
		lst_batch.append(root_batchcontrol)
		batch_dic['batch_control'] = lst_batch
		batch_dic = {}
		return lst_batch


	@api.multi
	def finalize_sepa_file_creation(self, xml_root, gen_args):
		if self.payment_method_id.code != 'ach_chase_transfer':
			return super(AccountPaymentOrder, self).finalize_sepa_file_creation()
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
	def generate_payment_file(self):
		if self.payment_method_id.code != 'ach_chase_transfer':
			return super(AccountPaymentOrder, self).generate_payment_file()
		xsd_file = self.payment_method_id.get_xsd_file_path()
		gen_args = {
		'convert_to_ascii': self.payment_method_id.convert_to_ascii,
		'file_prefix': 'sct_',
		'pain_flavor': 'pain_nacha',
		'pain_xsd_file': xsd_file,
		}
		filecontrol = self.get_filecontrol()
		fileheader = self.get_fileheader()
#		trans_len = len(self.payment_line_ids)
		trans_len = len(self.bank_line_ids)
		lst = []
		vendor_lst = []
#		for loop in self.payment_line_ids:
		for loop in self.bank_line_ids:
			lst.append(loop)
			vendor_lst.append(loop.partner_id.id)
			unique_lst = set(vendor_lst)
		unique_lst = list(unique_lst)
		len_unique_lst = len(unique_lst)
		nsmap = self.generate_pain_nsmap()
		attrib = self.generate_pain_attrib()
		root = etree.Element('Document',nsmap=nsmap, attrib=attrib)
		root.append(fileheader)
		batch_group = etree.Element('Batch')
		count = 1
#		for batch_loop in self.payment_line_ids:
		for batch_loop in self.bank_line_ids:
			batch = self.get_batchheader(batch_loop, count)
			count = count + 1
			for loop in batch:
				batch_group.append(loop)
		root.append(batch_group)
		root.append(filecontrol)
		return self.finalize_sepa_file_creation(root, gen_args)



	@api.multi
	def open2generated(self):
		self.ensure_one()
		if self.payment_method_id.code != 'ach_chase_transfer':
			return super(AccountPaymentOrder, self).open2generated()
		payment_file_str, filename = self.generate_payment_file()
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