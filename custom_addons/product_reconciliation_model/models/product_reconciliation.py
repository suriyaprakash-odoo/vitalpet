from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare, float_round
from odoo.osv import expression


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"


    @api.model
    def domain_move_lines_for_reconciliation(self, excluded_ids=None, str=False):
        """ Returns the domain which is common to both manual and bank statement reconciliation.

            :param excluded_ids: list of ids of move lines that should not be fetched
            :param str: search string
        """
        context = (self._context or {})
        if excluded_ids is None:
            excluded_ids = []
        domain = []

        if excluded_ids:
            domain = expression.AND([domain, [('id', 'not in', excluded_ids)]])
        if str:
            str_domain = [
                '|', ('move_id.name', 'ilike', str),
                '|', ('account_id.code', 'ilike', str),
                '|', ('account_id.name', 'ilike', str),
                '|', ('move_id.ref', 'ilike', str),
                '|', ('date_maturity', 'like', str),
                '&', ('name', '!=', '/'), ('name', 'ilike', str)
            ]
            try:
                amount = float(str)
                amount_domain = [
                    '|', ('amount_residual', '=', amount),
                    '|', ('amount_residual_currency', '=', amount),
                    '|', ('amount_residual', '=', -amount),
                    '|', ('amount_residual_currency', '=', -amount),
                    '&', ('account_id.internal_type', '=', 'liquidity'),
                    '|', '|', ('debit', '=', amount), ('credit', '=', amount), ('amount_currency', '=', amount),
                ]
                str_domain = expression.OR([str_domain, amount_domain])
            except:
                pass

            # When building a domain for the bank statement reconciliation, if there's no partner
            # and a search string, search also a match in the partner names
            if 'bank_statement_line' in context and not context['bank_statement_line'].partner_id.id:
                str_domain = expression.OR([str_domain, [('partner_id.name', 'ilike', str)]])

            domain = expression.AND([domain, str_domain])
        return domain
class AccountReconcileModel(models.Model):
    _inherit = "account.reconcile.model"
    
    product_id = fields.Many2one('product.product', string='Product')
    second_product_id = fields.Many2one('product.product', string='Second Product')
    partner_id=fields.Many2one('res.partner', string='Partner')
    second_partner_id=fields.Many2one('res.partner', string='Second Partner')


class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement" 

    @api.multi
    def bank_unrecon_statement(self):


        for rec in self:
            rec.button_draft()
            for line in rec.line_ids:
                line.button_cancel_reconciliation()

class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line" 

    def get_move_lines_for_reconciliation(self, excluded_ids=None, str=False, offset=0, limit=None, additional_domain=None, overlook_partner=False):
        """ Return account.move.line records which can be used for bank statement reconciliation.

            :param excluded_ids:
            :param str:
            :param offset:
            :param limit:
            :param additional_domain:
            :param overlook_partner:
        """
        # Blue lines = payment on bank account not assigned to a statement yet
        reconciliation_aml_accounts = [self.journal_id.default_credit_account_id.id, self.journal_id.default_debit_account_id.id]
        domain_reconciliation = ['&', '&', ('statement_id', '=', False), ('account_id', 'in', reconciliation_aml_accounts), ('payment_id','<>', False)]

        # Black lines = unreconciled & (not linked to a payment or open balance created by statement
        domain_matching = [('reconciled', '=', False)]
        if self.partner_id.id or overlook_partner:
            domain_matching = expression.AND([domain_matching, [('account_id.internal_type', 'in', ['payable', 'receivable'])]])
        else:
            # TODO : find out what use case this permits (match a check payment, registered on a journal whose account type is other instead of liquidity)
            domain_matching = expression.AND([domain_matching, [('account_id.reconcile', '=', True)]])

        # Let's add what applies to both
        domain = expression.OR([domain_reconciliation, domain_matching])
        if self.partner_id.id and not overlook_partner:
            domain = expression.AND([domain, [('partner_id', '=', self.partner_id.id)]])

        # Domain factorized for all reconciliation use cases
        ctx = dict(self._context or {})
        ctx['bank_statement_line'] = self
        generic_domain = self.env['account.move.line'].with_context(ctx).domain_move_lines_for_reconciliation(excluded_ids=excluded_ids, str=str)
        domain = expression.AND([domain, generic_domain])

        # Domain from caller
        if additional_domain is None:
            additional_domain = []
        else:
            additional_domain = expression.normalize_domain(additional_domain)
        domain = expression.AND([domain, additional_domain])
        domain = expression.AND([domain, [('company_id', '=', self.env.user.company_id.id)]])
        print domain
        return self.env['account.move.line'].search(domain, offset=offset, limit=limit, order="date_maturity asc, id asc")

    def _get_common_sql_query(self, overlook_partner = False, excluded_ids = None, split = False):
        acc_type = "acc.internal_type IN ('payable', 'receivable')" if (self.partner_id or overlook_partner) else "acc.reconcile = true"
        select_clause = "SELECT aml.id "
        from_clause = "FROM account_move_line aml JOIN account_account acc ON acc.id = aml.account_id "
        where_clause = """WHERE aml.company_id = %(company_id)s  
                                AND (
                                        (aml.statement_id IS NULL AND aml.account_id IN %(account_payable_receivable)s) 
                                    OR 
                                        ("""+acc_type+""" AND aml.reconciled = false)
                                    )"""
        where_clause = where_clause + ' AND aml.partner_id = %(partner_id)s' if self.partner_id else where_clause
        where_clause = where_clause + ' AND aml.id NOT IN %(excluded_ids)s' if excluded_ids else where_clause
        if split:
            return select_clause, from_clause, where_clause
        return select_clause + from_clause + where_clause
     
    def process_reconciliation(self, counterpart_aml_dicts=None, payment_aml_rec=None, new_aml_dicts=None):
        """ Match statement lines with existing payments (eg. checks) and/or payables/receivables (eg. invoices and refunds) and/or new move lines (eg. write-offs).
            If any new journal item needs to be created (via new_aml_dicts or counterpart_aml_dicts), a new journal entry will be created and will contain those
            items, as well as a journal item for the bank statement line.
            Finally, mark the statement line as reconciled by putting the matched moves ids in the column journal_entry_ids.

            :param self: browse collection of records that are supposed to have no accounting entries already linked.
            :param (list of dicts) counterpart_aml_dicts: move lines to create to reconcile with existing payables/receivables.
                The expected keys are :
                - 'name'
                - 'debit'
                - 'credit'
                - 'move_line'
                    # The move line to reconcile (partially if specified debit/credit is lower than move line's credit/debit)

            :param (list of recordsets) payment_aml_rec: recordset move lines representing existing payments (which are already fully reconciled)

            :param (list of dicts) new_aml_dicts: move lines to create. The expected keys are :
                - 'name'
                - 'debit'
                - 'credit'
                - 'account_id'
                - (optional) 'tax_ids'
                - (optional) Other account.move.line fields like analytic_account_id or analytics_id

            :returns: The journal entries with which the transaction was matched. If there was at least an entry in counterpart_aml_dicts or new_aml_dicts, this list contains
                the move created by the reconciliation, containing entries for the statement.line (1), the counterpart move lines (0..*) and the new move lines (0..*).
        """
        counterpart_aml_dicts = counterpart_aml_dicts or []
        payment_aml_rec = payment_aml_rec or self.env['account.move.line']
        new_aml_dicts = new_aml_dicts or []

        aml_obj = self.env['account.move.line']

        company_currency = self.journal_id.company_id.currency_id
        statement_currency = self.journal_id.currency_id or company_currency
        st_line_currency = self.currency_id or statement_currency

        counterpart_moves = self.env['account.move']

        # Check and prepare received data
        print payment_aml_rec
        for rec in payment_aml_rec:
            print payment_aml_rec
            print rec
            print rec.statement_id
        print any(rec.statement_id for rec in payment_aml_rec)
        if any(rec.statement_id for rec in payment_aml_rec):
            print "first"
            raise UserError(_('A selected move line was already reconciled.'))
        for aml_dict in counterpart_aml_dicts:
            if aml_dict['move_line'].reconciled:
                raise UserError(_('A selected move line was already reconciled.'))
            if isinstance(aml_dict['move_line'], (int, long)):
                aml_dict['move_line'] = aml_obj.browse(aml_dict['move_line'])
        for aml_dict in (counterpart_aml_dicts + new_aml_dicts):
            if aml_dict.get('tax_ids') and aml_dict['tax_ids'] and isinstance(aml_dict['tax_ids'][0], (int, long)):
                # Transform the value in the format required for One2many and Many2many fields
                aml_dict['tax_ids'] = map(lambda id: (4, id, None), aml_dict['tax_ids'])

        # Fully reconciled moves are just linked to the bank statement
        total = self.amount
        for aml_rec in payment_aml_rec:
            total -= aml_rec.debit-aml_rec.credit
            aml_rec.write({'statement_id': self.statement_id.id})
            aml_rec.move_id.write({'statement_line_id': self.id})
            counterpart_moves = (counterpart_moves | aml_rec.move_id)

        # Create move line(s). Either matching an existing journal entry (eg. invoice), in which
        # case we reconcile the existing and the new move lines together, or being a write-off.
        if counterpart_aml_dicts or new_aml_dicts:
            st_line_currency = self.currency_id or statement_currency
            st_line_currency_rate = self.currency_id and (self.amount_currency / self.amount) or False

            # Create the move
            self.sequence = self.statement_id.line_ids.ids.index(self.id) + 1
            move_vals = self._prepare_reconciliation_move(self.statement_id.name)
            move = self.env['account.move'].create(move_vals)
            counterpart_moves = (counterpart_moves | move)

            # Create The payment
            payment = False
            if abs(total)>0.00001:
                partner_id = self.partner_id and self.partner_id.id or False
                partner_type = False
                if partner_id:
                    if total < 0:
                        partner_type = 'supplier'
                    else:
                        partner_type = 'customer'

                payment_methods = (total>0) and self.journal_id.inbound_payment_method_ids or self.journal_id.outbound_payment_method_ids
                currency = self.journal_id.currency_id or self.company_id.currency_id
                payment = self.env['account.payment'].create({
                    'payment_method_id': payment_methods and payment_methods[0].id or False,
                    'payment_type': total >0 and 'inbound' or 'outbound',
                    'partner_id': self.partner_id and self.partner_id.id or False,
                    'partner_type': partner_type,
                    'journal_id': self.statement_id.journal_id.id,
                    'payment_date': self.date,
                    'state': 'reconciled',
                    'currency_id': currency.id,
                    'amount': abs(total),
                    'communication': self.name or '',
                    'name': self.statement_id.name,
                })

            # Complete dicts to create both counterpart move lines and write-offs
            to_create = (counterpart_aml_dicts + new_aml_dicts)
            ctx = dict(self._context, date=self.date)
            for aml_dict in to_create:
                aml_dict['move_id'] = move.id
                print aml_dict
                if self.partner_id:
                    aml_dict['partner_id'] = self.partner_id.id
                else:
                    if aml_dict.get('partner_id'):
                        aml_dict['partner_id'] = aml_dict['partner_id']
                aml_dict['statement_id'] = self.statement_id.id
                if st_line_currency.id != company_currency.id:
                    aml_dict['amount_currency'] = aml_dict['debit'] - aml_dict['credit']
                    aml_dict['currency_id'] = st_line_currency.id
                    if self.currency_id and statement_currency.id == company_currency.id and st_line_currency_rate:
                        # Statement is in company currency but the transaction is in foreign currency
                        aml_dict['debit'] = company_currency.round(aml_dict['debit'] / st_line_currency_rate)
                        aml_dict['credit'] = company_currency.round(aml_dict['credit'] / st_line_currency_rate)
                    elif self.currency_id and st_line_currency_rate:
                        # Statement is in foreign currency and the transaction is in another one
                        aml_dict['debit'] = statement_currency.with_context(ctx).compute(aml_dict['debit'] / st_line_currency_rate, company_currency)
                        aml_dict['credit'] = statement_currency.with_context(ctx).compute(aml_dict['credit'] / st_line_currency_rate, company_currency)
                    else:
                        # Statement is in foreign currency and no extra currency is given for the transaction
                        aml_dict['debit'] = st_line_currency.with_context(ctx).compute(aml_dict['debit'], company_currency)
                        aml_dict['credit'] = st_line_currency.with_context(ctx).compute(aml_dict['credit'], company_currency)
                elif statement_currency.id != company_currency.id:
                    # Statement is in foreign currency but the transaction is in company currency
                    prorata_factor = (aml_dict['debit'] - aml_dict['credit']) / self.amount_currency
                    aml_dict['amount_currency'] = prorata_factor * self.amount
                    aml_dict['currency_id'] = statement_currency.id

            # Create write-offs
            # When we register a payment on an invoice, the write-off line contains the amount
            # currency if all related invoices have the same currency. We apply the same logic in
            # the manual reconciliation.
            counterpart_aml = self.env['account.move.line']
            for aml_dict in counterpart_aml_dicts:
                counterpart_aml |= aml_dict.get('move_line', self.env['account.move.line'])
            new_aml_currency = False
            if counterpart_aml\
                    and len(counterpart_aml.mapped('currency_id')) == 1\
                    and counterpart_aml[0].currency_id\
                    and counterpart_aml[0].currency_id != company_currency:
                new_aml_currency = counterpart_aml[0].currency_id
            for aml_dict in new_aml_dicts:
                aml_dict['payment_id'] = payment and payment.id or False
                if new_aml_currency and not aml_dict.get('currency_id'):
                    aml_dict['currency_id'] = new_aml_currency.id
                    aml_dict['amount_currency'] = company_currency.with_context(ctx).compute(aml_dict['debit'] - aml_dict['credit'], new_aml_currency)
                aml_obj.with_context(check_move_validity=False, apply_taxes=True).create(aml_dict)

            # Create counterpart move lines and reconcile them
            for aml_dict in counterpart_aml_dicts:
                if aml_dict['move_line'].partner_id.id:
                    aml_dict['partner_id'] = aml_dict['move_line'].partner_id.id
                aml_dict['account_id'] = aml_dict['move_line'].account_id.id
                aml_dict['payment_id'] = payment and payment.id or False

                counterpart_move_line = aml_dict.pop('move_line')
                if counterpart_move_line.currency_id and counterpart_move_line.currency_id != company_currency and not aml_dict.get('currency_id'):
                    aml_dict['currency_id'] = counterpart_move_line.currency_id.id
                    aml_dict['amount_currency'] = company_currency.with_context(ctx).compute(aml_dict['debit'] - aml_dict['credit'], counterpart_move_line.currency_id)
                new_aml = aml_obj.with_context(check_move_validity=False).create(aml_dict)

                (new_aml | counterpart_move_line).reconcile()

            # Create the move line for the statement line using the bank statement line as the remaining amount
            # This leaves out the amount already reconciled and avoids rounding errors from currency conversion
            st_line_amount = -sum([x.balance for x in move.line_ids])
            aml_dict = self._prepare_reconciliation_move_line(move, st_line_amount)
            aml_dict['payment_id'] = payment and payment.id or False
            aml_obj.with_context(check_move_validity=False).create(aml_dict)

            move.post()
            #record the move name on the statement line to be able to retrieve it in case of unreconciliation
            self.write({'move_name': move.name})
            payment.write({'payment_reference': move.name})
#         elif self.move_name:
#             raise UserError(_('Operation not allowed. Since your statement line already received a number, you cannot reconcile it entirely with existing journal entries otherwise it would make a gap in the numbering. You should book an entry and make a regular revert of it in case you want to cancel it.'))
        counterpart_moves.assert_balanced()
        return counterpart_moves

    @api.multi
    def button_cancel_reconciliation(self):
        moves_to_cancel = self.env['account.move']
        payment_to_unreconcile = self.env['account.payment']
        payment_to_cancel = self.env['account.payment']
        for st_line in self:
            moves_to_unbind = st_line.journal_entry_ids
            for move in st_line.journal_entry_ids:
                for line in move.line_ids:
                    payment_to_unreconcile |= line.payment_id
                    if st_line.move_name and line.payment_id.payment_reference == st_line.move_name:
                        #there can be several moves linked to a statement line but maximum one created by the line itself
                        moves_to_cancel |= move
                        payment_to_cancel |= line.payment_id
                        # st_line.move_name = ''

            moves_to_unbind = moves_to_unbind - moves_to_cancel

            if moves_to_unbind:
                moves_to_unbind.write({'statement_line_id': False})
                for move in moves_to_unbind:
                    move.line_ids.filtered(lambda x: x.statement_id == st_line.statement_id).write({'statement_id': False})

        payment_to_unreconcile = payment_to_unreconcile - payment_to_cancel
        if payment_to_unreconcile:
            payment_to_unreconcile.unreconcile()

        if moves_to_cancel:
            for move in moves_to_cancel:
                move.line_ids.remove_move_reconcile()
            moves_to_cancel.button_cancel()
            moves_to_cancel.unlink()
        if payment_to_cancel:
            payment_to_cancel.unlink()

  
#     def _prepare_reconciliation_move_line(self, move, amount):
#         """ Prepare the dict of values to create the move line from a statement line.
#    
#             :param recordset move: the account.move to link the move line
#             :param float amount: the amount of transaction that wasn't already reconciled
#         """
#         company_currency = self.journal_id.company_id.currency_id
#         statement_currency = self.journal_id.currency_id or company_currency
#         st_line_currency = self.currency_id or statement_currency
#    
#         amount_currency = False
#         if statement_currency != company_currency or st_line_currency != company_currency:
#             # First get the ratio total mount / amount not already reconciled
#             if statement_currency == company_currency:
#                 total_amount = self.amount
#             elif st_line_currency == company_currency:
#                 total_amount = self.amount_currency
#             else:
#                 total_amount = statement_currency.with_context({'date': self.date}).compute(self.amount, company_currency, round=False)
#             if float_compare(total_amount, amount, precision_digits=company_currency.rounding) == 0:
#                 ratio = 1.0
#             else:
#                 ratio = total_amount / amount
#             # Then use it to adjust the statement.line field that correspond to the move.line amount_currency
#             if statement_currency != company_currency:
#                 amount_currency = self.amount * ratio
#             elif st_line_currency != company_currency:
#                 amount_currency = self.amount_currency * ratio
#         print self.env.context,'context'
#         account_reconcile = self.env['account.reconcile.model'].search([('name', 'ilike', self._context.get('name'))], limit=1)
#         print account_reconcile.product_id.name,'account_reconcile'
#         product_temp_id = self.env['product.template'].search([('name', '=', account_reconcile.product_id.name)], limit=1) 
#         print self.name
#         return {
#             'name': self.name,
#             'move_id': move.id,
#             'partner_id': self.partner_id and self.partner_id.id or False,
#             'account_id': amount >= 0 \
#                 and self.statement_id.journal_id.default_credit_account_id.id \
#                 or self.statement_id.journal_id.default_debit_account_id.id,
#             'credit': amount < 0 and -amount or 0.0,
#             'debit': amount > 0 and amount or 0.0,
#             'statement_id': self.statement_id.id,
#             'currency_id': statement_currency != company_currency and statement_currency.id or (st_line_currency != company_currency and st_line_currency.id or False),
#             'amount_currency': amount_currency,
#             'product_id':product_temp_id.id,
#                  
#         }
#            
#                  
#     def process_reconciliation(self, counterpart_aml_dicts=None, payment_aml_rec=None, new_aml_dicts=None):
#         """ Match statement lines with existing payments (eg. checks) and/or payables/receivables (eg. invoices and refunds) and/or new move lines (eg. write-offs).
#             If any new journal item needs to be created (via new_aml_dicts or counterpart_aml_dicts), a new journal entry will be created and will contain those
#             items, as well as a journal item for the bank statement line.
#             Finally, mark the statement line as reconciled by putting the matched moves ids in the column journal_entry_ids.
#    
#             :param self: browse collection of records that are supposed to have no accounting entries already linked.
#             :param (list of dicts) counterpart_aml_dicts: move lines to create to reconcile with existing payables/receivables.
#                 The expected keys are :
#                 - 'name'
#                 - 'debit'
#                 - 'credit'
#                 - 'move_line'
#                     # The move line to reconcile (partially if specified debit/credit is lower than move line's credit/debit)
#    
#             :param (list of recordsets) payment_aml_rec: recordset move lines representing existing payments (which are already fully reconciled)
#    
#             :param (list of dicts) new_aml_dicts: move lines to create. The expected keys are :
#                 - 'name'
#                 - 'debit'
#                 - 'credit'
#                 - 'account_id'
#                 - (optional) 'tax_ids'
#                 - (optional) Other account.move.line fields like analytic_account_id or analytics_id
#    
#             :returns: The journal entries with which the transaction was matched. If there was at least an entry in counterpart_aml_dicts or new_aml_dicts, this list contains
#                 the move created by the reconciliation, containing entries for the statement.line (1), the counterpart move lines (0..*) and the new move lines (0..*).
#         """
#         print 'coming'
#         context = dict(self.env.context or {})
#         print new_aml_dicts
#         name = ''
#         for record in new_aml_dicts:
#             if record['name']:
#                 name=record['name']
#                 break
#         context['name'] = name
#            
#    
#         counterpart_aml_dicts = counterpart_aml_dicts or []
#         payment_aml_rec = payment_aml_rec or self.env['account.move.line']
#         new_aml_dicts = new_aml_dicts or []
#    
#         aml_obj = self.env['account.move.line']
#    
#         company_currency = self.journal_id.company_id.currency_id
#         statement_currency = self.journal_id.currency_id or company_currency
#         st_line_currency = self.currency_id or statement_currency
#    
#         counterpart_moves = self.env['account.move']
#    
#         # Check and prepare received data
#         if any(rec.statement_id for rec in payment_aml_rec):
#             raise UserError(_('A selected move line was already reconciled.'))
#         for aml_dict in counterpart_aml_dicts:
#             if aml_dict['move_line'].reconciled:
#                 raise UserError(_('A selected move line was already reconciled.'))
#             if isinstance(aml_dict['move_line'], (int, long)):
#                 aml_dict['move_line'] = aml_obj.browse(aml_dict['move_line'])
#         for aml_dict in (counterpart_aml_dicts + new_aml_dicts):
#             if aml_dict.get('tax_ids') and aml_dict['tax_ids'] and isinstance(aml_dict['tax_ids'][0], (int, long)):
#                 # Transform the value in the format required for One2many and Many2many fields
#                 aml_dict['tax_ids'] = map(lambda id: (4, id, None), aml_dict['tax_ids'])
#    
#         # Fully reconciled moves are just linked to the bank statement
#         total = self.amount
#         for aml_rec in payment_aml_rec:
#             total -= aml_rec.debit-aml_rec.credit
#             aml_rec.write({'statement_id': self.statement_id.id})
#             aml_rec.move_id.write({'statement_line_id': self.id})
#             counterpart_moves = (counterpart_moves | aml_rec.move_id)
#    
#         # Create move line(s). Either matching an existing journal entry (eg. invoice), in which
#         # case we reconcile the existing and the new move lines together, or being a write-off.
#         if counterpart_aml_dicts or new_aml_dicts:
#             st_line_currency = self.currency_id or statement_currency
#             st_line_currency_rate = self.currency_id and (self.amount_currency / self.amount) or False
#    
#             # Create the move
#             self.sequence = self.statement_id.line_ids.ids.index(self.id) + 1
#             move_vals = self._prepare_reconciliation_move(self.statement_id.name)
#             move = self.env['account.move'].create(move_vals)
#             counterpart_moves = (counterpart_moves | move)
#    
#             # Create The payment
#             payment = False
#             if abs(total)>0.00001:
#                 partner_id = self.partner_id and self.partner_id.id or False
#                 partner_type = False
#                 if partner_id:
#                     if total < 0:
#                         partner_type = 'supplier'
#                     else:
#                         partner_type = 'customer'
#    
#                 payment_methods = (total>0) and self.journal_id.inbound_payment_method_ids or self.journal_id.outbound_payment_method_ids
#                 currency = self.journal_id.currency_id or self.company_id.currency_id
#                 payment = self.env['account.payment'].create({
#                     'payment_method_id': payment_methods and payment_methods[0].id or False,
#                     'payment_type': total >0 and 'inbound' or 'outbound',
#                     'partner_id': self.partner_id and self.partner_id.id or False,
#                     'partner_type': partner_type,
#                     'journal_id': self.statement_id.journal_id.id,
#                     'payment_date': self.date,
#                     'state': 'reconciled',
#                     'currency_id': currency.id,
#                     'amount': abs(total),
#                     'communication': self.name or '',
#                     'name': self.statement_id.name,
#                 })
#    
#             # Complete dicts to create both counterpart move lines and write-offs
#             to_create = (counterpart_aml_dicts + new_aml_dicts)
#             ctx = dict(self._context, date=self.date)
#             for aml_dict in to_create:
#                 aml_dict['move_id'] = move.id
#                 aml_dict['partner_id'] = self.partner_id.id
#                 aml_dict['statement_id'] = self.statement_id.id
#                 if st_line_currency.id != company_currency.id:
#                     aml_dict['amount_currency'] = aml_dict['debit'] - aml_dict['credit']
#                     aml_dict['currency_id'] = st_line_currency.id
#                     if self.currency_id and statement_currency.id == company_currency.id and st_line_currency_rate:
#                         # Statement is in company currency but the transaction is in foreign currency
#                         aml_dict['debit'] = company_currency.round(aml_dict['debit'] / st_line_currency_rate)
#                         aml_dict['credit'] = company_currency.round(aml_dict['credit'] / st_line_currency_rate)
#                     elif self.currency_id and st_line_currency_rate:
#                         # Statement is in foreign currency and the transaction is in another one
#                         aml_dict['debit'] = statement_currency.with_context(ctx).compute(aml_dict['debit'] / st_line_currency_rate, company_currency)
#                         aml_dict['credit'] = statement_currency.with_context(ctx).compute(aml_dict['credit'] / st_line_currency_rate, company_currency)
#                     else:
#                         # Statement is in foreign currency and no extra currency is given for the transaction
#                         aml_dict['debit'] = st_line_currency.with_context(ctx).compute(aml_dict['debit'], company_currency)
#                         aml_dict['credit'] = st_line_currency.with_context(ctx).compute(aml_dict['credit'], company_currency)
#                 elif statement_currency.id != company_currency.id:
#                     # Statement is in foreign currency but the transaction is in company currency
#                     prorata_factor = (aml_dict['debit'] - aml_dict['credit']) / self.amount_currency
#                     aml_dict['amount_currency'] = prorata_factor * self.amount
#                     aml_dict['currency_id'] = statement_currency.id
#    
#             # Create write-offs
#             # When we register a payment on an invoice, the write-off line contains the amount
#             # currency if all related invoices have the same currency. We apply the same logic in
#             # the manual reconciliation.
#             counterpart_aml = self.env['account.move.line']
#             for aml_dict in counterpart_aml_dicts:
#                 counterpart_aml |= aml_dict.get('move_line', self.env['account.move.line'])
#             new_aml_currency = False
#             if counterpart_aml\
#                     and len(counterpart_aml.mapped('currency_id')) == 1\
#                     and counterpart_aml[0].currency_id\
#                     and counterpart_aml[0].currency_id != company_currency:
#                 new_aml_currency = counterpart_aml[0].currency_id
#             for aml_dict in new_aml_dicts:
#                 aml_dict['payment_id'] = payment and payment.id or False
#                 if new_aml_currency and not aml_dict.get('currency_id'):
#                     aml_dict['currency_id'] = new_aml_currency.id
#                     aml_dict['amount_currency'] = company_currency.with_context(ctx).compute(aml_dict['debit'] - aml_dict['credit'], new_aml_currency)
#                 aml_obj.with_context(check_move_validity=False, apply_taxes=True).create(aml_dict)
#    
#             # Create counterpart move lines and reconcile them
#             for aml_dict in counterpart_aml_dicts:
#                 if aml_dict['move_line'].partner_id.id:
#                     aml_dict['partner_id'] = aml_dict['move_line'].partner_id.id
#                 aml_dict['account_id'] = aml_dict['move_line'].account_id.id
#                 aml_dict['payment_id'] = payment and payment.id or False
#    
#                 counterpart_move_line = aml_dict.pop('move_line')
#                 if counterpart_move_line.currency_id and counterpart_move_line.currency_id != company_currency and not aml_dict.get('currency_id'):
#                     aml_dict['currency_id'] = counterpart_move_line.currency_id.id
#                     aml_dict['amount_currency'] = company_currency.with_context(ctx).compute(aml_dict['debit'] - aml_dict['credit'], counterpart_move_line.currency_id)
#                 new_aml = aml_obj.with_context(check_move_validity=False).create(aml_dict)
#    
#                 (new_aml | counterpart_move_line).reconcile()
#    
#             # Create the move line for the statement line using the bank statement line as the remaining amount
#             # This leaves out the amount already reconciled and avoids rounding errors from currency conversion
#             st_line_amount = -sum([x.balance for x in move.line_ids])
#             print name
#             context = dict(self.env.context or {})
#             context['name'] = name
#             aml_dict = self.with_context(context)._prepare_reconciliation_move_line(move, st_line_amount)
#             aml_dict['payment_id'] = payment and payment.id or False
#             aml_obj.with_context(check_move_validity=False).create(aml_dict)
#    
#             move.post()
#             #record the move name on the statement line to be able to retrieve it in case of unreconciliation
#             self.write({'move_name': move.name})
#             payment.write({'payment_reference': move.name})
#         elif self.move_name:
#             raise UserError(_('Operation not allowed. Since your statement line already received a number, you cannot reconcile it entirely with existing journal entries otherwise it would make a gap in the numbering. You should book an entry and make a regular revert of it in case you want to cancel it.'))
#         counterpart_moves.assert_balanced()
#         return counterpart_moves

