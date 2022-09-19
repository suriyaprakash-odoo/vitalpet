# -*- coding: utf-8 -*-
import logging
import base64
import StringIO
import odoo.addons.decimal_precision as dp

from xml.etree import ElementTree

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError
from odoo.addons.base.res.res_bank import sanitize_account_number

try:
    from ofxparse import OfxParser
    from ofxparse.ofxparse import OfxParserException
    OfxParserClass = OfxParser
except ImportError:
    logging.getLogger(__name__).warning("The ofxparse python library is not installed, ofx import will not work.")
    OfxParser = OfxParserException = None
    OfxParserClass = object


class PatchedOfxParser(OfxParserClass):
    """ This class monkey-patches the ofxparse library in order to fix the following known bug: ',' is a valid
        decimal separator for amounts, as we can encounter in ofx files made by european banks.
    """

    @classmethod
    def decimal_separator_cleanup(cls_, tag):
        if hasattr(tag, "contents"):
            tag.string = tag.contents[0].replace(',', '.')

    @classmethod
    def parseStatement(cls_, stmt_ofx):
        ledger_bal_tag = stmt_ofx.find('ledgerbal')
        if hasattr(ledger_bal_tag, "contents"):
            balamt_tag = ledger_bal_tag.find('balamt')
            cls_.decimal_separator_cleanup(balamt_tag)
        avail_bal_tag = stmt_ofx.find('availbal')
        if hasattr(avail_bal_tag, "contents"):
            balamt_tag = avail_bal_tag.find('balamt')
            cls_.decimal_separator_cleanup(balamt_tag)
        return super(PatchedOfxParser, cls_).parseStatement(stmt_ofx)

    @classmethod
    def parseTransaction(cls_, txn_ofx):
        amt_tag = txn_ofx.find('trnamt')
        cls_.decimal_separator_cleanup(amt_tag)
        return super(PatchedOfxParser, cls_).parseTransaction(txn_ofx)

    @classmethod
    def parseInvestmentPosition(cls_, ofx):
        tag = ofx.find('units')
        cls_.decimal_separator_cleanup(tag)
        tag = ofx.find('unitprice')
        cls_.decimal_separator_cleanup(tag)
        return super(PatchedOfxParser, cls_).parseInvestmentPosition(ofx)

    @classmethod
    def parseInvestmentTransaction(cls_, ofx):
        tag = ofx.find('units')
        cls_.decimal_separator_cleanup(tag)
        tag = ofx.find('unitprice')
        cls_.decimal_separator_cleanup(tag)
        return super(PatchedOfxParser, cls_).parseInvestmentTransaction(ofx)


class ExpenseBankStatementLine(models.TransientModel):
    _name = 'expense.bank.statement.line'
    _description = 'Bank Statement Line'

    bank_statement_line_id = fields.Many2one('expense.bank.statement.import', string = 'BankStatement')

    name = fields.Char(string='Particulars/Description', required=True)
    date = fields.Date(default=fields.Date.context_today, string="Date")
    product_id = fields.Many2one('product.product', string='Product', domain=[('can_be_expensed', '=', True)])
    amount = fields.Float(string='Amount', store=True, digits=dp.get_precision('Account'))
    unique_import_id = fields.Char('Unique bankstatement ID')
    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account')


class ExpenseBankStatementImport(models.TransientModel):
    _name = 'expense.bank.statement.import'
    _description = 'Import Bank Statement'

    name = fields.Char(string = 'Imported Bank Statements', default='Imported Bank Statements')
    data_file = fields.Binary(string='Bank Statement File', help='Get you bank statements in electronic format from your bank and select them here.')
    filename = fields.Char()
    file_binary =fields.Text()
    bank_statement_line_ids = fields.One2many('expense.bank.statement.line', 'bank_statement_line_id', string = 'BankStatement Lines')
    state = fields.Selection([('new', 'New'),
                              ('validated', 'Validated'),
                              ('done', 'Done')], string = 'State', readonly = True, default = 'new')

    validate_message = fields.Text()
    
    # @api.multi
    def create_expense(self):
        self.ensure_one()
        if self.bank_statement_line_ids:
            expense_ids=[]
            # Find employee associated to the user
            employee_id=self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1)
            if not employee_id:
                raise ValidationError(_("Current user is not associated with any employee"))
            # If all the fields are valid create expense
            
            for line in self.bank_statement_line_ids:
                account = line.product_id.product_tmpl_id._get_product_accounts()['expense']
                vals={
                    'name': line.name,
                    'date': line.date,
                    'company_id': self.env.user.company_id.id,
                    'product_id': line.product_id.id,
                    'quantity': 1,
                    'unit_amount': line.amount,
                    'employee_id': employee_id.id,
                    'analytic_account_id': line.analytic_account_id.id,
                    'account_id': account.id,
                    'payment_mode': 'credit_card',
                    'state': 'draft',
                    'unique_import_id': line.unique_import_id,
                    'source': 'import',
                }
                expense_ids.append(self.env['hr.expense'].create(vals).id)
# Change file imported state
            if expense_ids:
                self.state='done'
                return {
                    'name': _('My Expense'),
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'res_model': 'hr.expense',
                    'type': 'ir.actions.act_window',
                    'domain': [('id', 'in', expense_ids)], }


    # @api.multi
    def validate_statement(self):
        self.ensure_one()
        if self.data_file:
            if self.bank_statement_line_ids:
                employee_ids = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)])
                if not employee_ids :
                    raise ValidationError(_("Current user is not associated with any of existing employee"))
                if employee_ids:
                    count=0
                    for line in employee_ids:
                        count+=1
                    if count >1:
                        raise ValidationError(_("Multiple employee are associated with this user."))
                # Check for empty field
                for line in self.bank_statement_line_ids:
                    if not line.name:
                        raise ValidationError(_("Could not find description"))
                    if not line.product_id:
                        raise ValidationError(_("Could not find product"))
                    account = line.product_id.product_tmpl_id._get_product_accounts()['expense']
                    asset_account = line.product_id.categ_id.asset_category_pro_id.account_asset_id
                    if not account and not asset_account:
                        raise ValidationError(_("Could not find expense or asset account for  "+line.product_id.name))
                    if not line.date:
                        raise ValidationError(_("Could not find date"))
                    if self.env['hr.expense'].search([('unique_import_id', '=', line.unique_import_id)]):
                        raise ValidationError(_("Transaction "+line.name+" already imported"))
                # If all the fields are valid move state
                self.state = 'validated'
            else:
                raise ValidationError(_("Could not find bank statements"))
    
   

    # @api.multi
    @api.onchange('data_file')
    def import_file(self):
        self.ensure_one()
        # If new file is updated reset stage to follow initial process
        self.state = 'new'
        if self.data_file:
            self.file_binary = self.data_file
            # check file extension
            if self.filename:
                file_extension=self.filename.split(".")[-1].lower()
                if file_extension not in ['ofx', 'qfx']:
                    raise ValidationError(_("Please import .OFX or .QFX files."))

            # Let the appropriate implementation module parse the file and return the required data
            # The active_id is passed in context in case an implementation module requires information about the wizard state (see QIF)
            currency_code, account_number, stmts_vals = self.with_context()._parse_file(base64.b64decode(self.data_file))
            # Check raw data
            self._check_parsed_data(stmts_vals)
            # Prepare statement data to be used for bank statements creation
            stmts_vals = self._complete_stmts_vals(stmts_vals, account_number)
            # Create the expense bank statements line items
            bank_statements = self._compute_bank_statements(stmts_vals)
            # Now that the import worked out, set it as the bank_statements_source of the journal
            self.bank_statement_line_ids = bank_statements

    def _check_ofx(self, data_file):
        if data_file.startswith("OFXHEADER"):
            #v1 OFX
            return True
        try:
            #v2 OFX
            return "<ofx>" in data_file.lower()
        except ElementTree.ParseError:
            return False

    def _parse_file(self, data_file):
        if not self._check_ofx(data_file):
            return super(ExpenseBankStatementImport, self)._parse_file(data_file)
        if OfxParser is None:
            raise ValidationError(_("The library 'ofxparse' is missing, OFX import cannot proceed."))

        ofx = PatchedOfxParser.parse(StringIO.StringIO(data_file))
        vals_bank_statement = []
        account_lst = set()
        currency_lst = set()
        for account in ofx.accounts:
            account_lst.add(account.number)
            currency_lst.add(account.statement.currency)
            transactions = []
            total_amt = 0.00
            for transaction in account.statement.transactions:
                if transaction.amount !=0:
                    amount = 0.00
                    # Since ofxparse doesn't provide account numbers, we'll have to find res.partner and res.partner.bank here
                    # (normal behaviour is to provide 'account_number', which the generic module uses to find partner/bank)
                    bank_account_id = partner_id = False
                    partner_bank = self.env['res.partner.bank'].search([('partner_id.name', '=', transaction.payee)], limit=1)
                    if partner_bank:
                        bank_account_id = partner_bank.id
                        partner_id = partner_bank.partner_id.id
                    if transaction.amount < 0:
                        amount=-transaction.amount
                    else:
                        amount = transaction.amount
                    vals_line = {
                        'date': transaction.date,
                        'name': transaction.payee + (transaction.memo and ': ' + transaction.memo or ''),
                        'ref': transaction.id,
                        'amount': amount,
                        'unique_import_id': transaction.id,
                        'bank_account_id': bank_account_id,
                        'partner_id': partner_id,
                        'sequence': len(transactions) + 1,
                    }
                    total_amt += float(transaction.amount)
                    transactions.append(vals_line)

            vals_bank_statement.append({
                'transactions': transactions,
                # WARNING: the provided ledger balance is not necessarily the ending balance of the statement
                # see https://github.com/odoo/odoo/issues/3003
                'balance_start': float(account.statement.balance) - total_amt,
                'balance_end_real': account.statement.balance,
            })

        if account_lst and len(account_lst) == 1:
            account_lst = account_lst.pop()
            currency_lst = currency_lst.pop()
        else:
            account_lst = None
            currency_lst = None

        return currency_lst, account_lst, vals_bank_statement

    def _check_parsed_data(self, stmts_vals):
        """ Basic and structural verifications """
        if len(stmts_vals) == 0:
            raise ValidationError(_('This file doesn\'t contain any statement.'))

        no_st_line = True
        for vals in stmts_vals:
            if vals['transactions'] and len(vals['transactions']) > 0:
                no_st_line = False
                break
        if no_st_line:
            raise ValidationError(_('This file doesn\'t contain any transaction.'))

    def _complete_stmts_vals(self, stmts_vals, account_number):
        for st_vals in stmts_vals:
            if not st_vals.get('reference'):
                st_vals['reference'] = self.filename
            if st_vals.get('number'):
                #build the full name like BNK/2016/00135 by just giving the number '135'
                # st_vals['name'] = journal.sequence_id.with_context(ir_sequence_date=st_vals.get('date')).get_next_char(st_vals['number'])
#fixme: Show journal sequence
                st_vals['name'] = 'Show journal sequence'
                del(st_vals['number'])
            for line_vals in st_vals['transactions']:
                unique_import_id = line_vals.get('unique_import_id')
                if unique_import_id:
                    sanitized_account_number = sanitize_account_number(account_number)
                    line_vals['unique_import_id'] = (sanitized_account_number and sanitized_account_number + '-' or '') + '-' + unique_import_id

                if not line_vals.get('bank_account_id'):
                    # Find the partner and his bank expense or create the bank expense. The partner selected during the
                    # reconciliation process will be linked to the bank when the statement is closed.
                    partner_id = False
                    bank_account_id = False
                    identifying_string = line_vals.get('account_number')
                    if identifying_string:
# Get partner and his bank in vetzip
                        partner_bank = self.env['res.partner.bank'].search([('acc_number', '=', identifying_string)], limit=1)
                        if partner_bank:
                            bank_account_id = partner_bank.id
                            partner_id = partner_bank.partner_id.id
                    line_vals['partner_id'] = partner_id
                    line_vals['bank_account_id'] = bank_account_id

        return stmts_vals


    def _compute_bank_statements(self, stmts_vals):
        """ Create new bank statements from imported values, filtering out already imported transactions, and returns data used by the reconciliation widget """
        HrExpense = self.env['hr.expense']
        # Filter out already imported transactions and create statements
#         for st_vals in stmts_vals:
#             for line_vals in st_vals['transactions']:
#                 print line_vals['name']
#                 if 'unique_import_id' in line_vals and bool(HrExpense.sudo().search([('unique_import_id', '=', line_vals['unique_import_id'])], limit=1)):
#                     raise ValidationError(_('Transaction '+line_vals['name']+' already imported.'))

        for st_vals in stmts_vals :
            # Create the satement
            bank_statements = [(0, 0, line) for line in st_vals['transactions']]
        return bank_statements
