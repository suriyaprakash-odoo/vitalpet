import datetime
from odoo import fields, models, api, _
from odoo.tools.translate import _
from odoo.exceptions import UserError, RedirectWarning, ValidationError
import calendar
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from odoo.tools import float_compare, float_is_zero

class account_asset_asset(models.Model):
    _inherit = "account.asset.asset"
    
    @api.model
    def _date_journal(self):
        todayDate = date.today()
        if todayDate.day:
            todayDate = date.today().replace(day=15)
        return todayDate
   
    asset_area = fields.Selection([('attic', 'Attic'),('breakroom', 'Breakroom'),('doctors_office', 'Doctors Office'),('lab', 'Lab'),('exam_room', 'Exam Room'),('kernal', 'Kennel/Grooming'),('lobby', 'Lobby'),('managers_office', 'Managers Office'),('conference_room', 'Conference Room'),('outside', 'Outside'),('pharmacy', 'Pharmacy'),('reception', 'Reception'),('storage_closet', 'Storage Closet'),('treatment_area', 'Treatment Area'),('mobile_use', 'Mobile Use')],'Area')
    manufacturer = fields.Char('Manufacturer')
    model = fields.Char('Model')
    part_number = fields.Char('Part Number')
    serial_number = fields.Char('Serial Number')
    item_warranty = fields.Selection([('Yes', 'Yes'),('No', 'No'),('factory', 'Factory'),('qrtly_maintenance_agreement', 'Qrtly Maintenance agreement')],'Service Contract or Warranty')
    warranty_lengths = fields.Char('Contract/Warranty Length (Months)')
    service_contract_number = fields.Char('Service Contract Number')
    support_link = fields.Char('Support Link')
    suport_phone = fields.Char('Support Phone Number')
    software_key = fields.Char('OS/Software Key')
    mac_address = fields.Char('MAC Address')
    licenses_count = fields.Char('Number of Licenses')
    os = fields.Selection([('android', 'Android'),('apple', 'Apple'),('linux', 'Linux'),('thin_client', 'Thin Client'),('windows_vista', 'Windows Vista'),('windows_xp', 'Windows XP'),('windows_7', 'Windows 7'),('windows_8', 'Windows 8'),('windows_server_2003', 'Windows Server 2003'),('windows_server_2008', 'Windows Server 2008'),('windows_server_2012', 'Windows Server 2012')],'Operating System ')
    cpu_speed = fields.Char('CPU Speed (Ghz)')
    cpu_cores =  fields.Selection([('1', '1'),('2', '2'),('3', '3'),('4', '4'),('5', '5'),('6', '6'),('7', '7'),('8', '8')],'CPU Cores')
    memory = fields.Selection([('greater_than_500', '<500 MB'),('500_to_1', '500MB - 1GB'),('1_to_2', '1GB-2GB'),('2_to_3', '2GB-3GB'),('2_to_3', '3GB-4GB'),('greater_than_4', '>4GB')],'Memory')
    hard_drive_size = fields.Char('Hard Drive Size (GB)')
    admin_uname = fields.Char('Administrator Username')
    admin_pwd = fields.Char('Administrator Password')
    bill_id = fields.Char('Bill Id')
    journal_date = fields.Date('Journal Date', required=True, default=_date_journal)
    
    @api.multi
    def compute_depreciation_board(self):
        self.ensure_one()

        posted_depreciation_line_ids = self.depreciation_line_ids.filtered(lambda x: x.move_check).sorted(key=lambda l: l.depreciation_date)
        unposted_depreciation_line_ids = self.depreciation_line_ids.filtered(lambda x: not x.move_check)

        # Remove old unposted depreciation lines. We cannot use unlink() with One2many field
        commands = [(2, line_id.id, False) for line_id in unposted_depreciation_line_ids]

        if self.value_residual != 0.0:
            amount_to_depr = residual_amount = self.value_residual
            if self.prorata:
                # if we already have some previous validated entries, starting date is last entry + method perio
                if posted_depreciation_line_ids and posted_depreciation_line_ids[-1].depreciation_date:
                    last_depreciation_date = datetime.strptime(posted_depreciation_line_ids[-1].depreciation_date, DF).date()
                    depreciation_date = last_depreciation_date + relativedelta(months=+self.method_period)
                else:
                    depreciation_date = datetime.strptime(self._get_last_depreciation_date()[self.id], DF).date()
            else:
                # depreciation_date = 1st of January of purchase year if annual valuation, 1st of
                # purchase month in other cases
                if self.method_period >= 12:
                    asset_date = datetime.strptime(self.date[:4] + '-01-01', DF).date()
                    journal_date = datetime.strptime(self.journal_date[:4] + '-01-01', DF).date()
                else:
                    asset_date = datetime.strptime(self.date[:7] + '-01', DF).date()
                    journal_date = datetime.strptime(self.journal_date[:7] + '-01', DF).date()
                # if we already have some previous validated entries, starting date isn't 1st January but last entry + method period
                if posted_depreciation_line_ids and posted_depreciation_line_ids[-1].depreciation_date:
                    last_depreciation_date = datetime.strptime(posted_depreciation_line_ids[-1].depreciation_date, DF).date()
                    depreciation_date = last_depreciation_date + relativedelta(months=+self.method_period)
                else:
                    depreciation_date = asset_date
            day = depreciation_date.day
            month = depreciation_date.month
            year = depreciation_date.year
            total_days = (year % 4) and 365 or 366

            undone_dotation_number = self._compute_board_undone_dotation_nb(depreciation_date, total_days)
            
            date_journal = datetime.strptime(self.journal_date, DF).date()

            if self.state=='open':
                i=0
                for deprication in self.depreciation_line_ids:
                    if deprication.move_check:
                        if date_journal<=datetime.strptime(deprication.journal_date, DF).date():
                            i=1
                            date_journal=datetime.strptime(deprication.journal_date, DF).date()
                if i==1:
                    date_journal = date_journal + relativedelta(months=+self.method_period)
            for x in range(len(posted_depreciation_line_ids), undone_dotation_number):
                sequence = x + 1
                amount = self._compute_board_amount(sequence, residual_amount, amount_to_depr, undone_dotation_number, posted_depreciation_line_ids, total_days, depreciation_date)
                amount = self.currency_id.round(amount)
                if float_is_zero(amount, precision_rounding=self.currency_id.rounding):
                    continue
                residual_amount -= amount
                vals = {
                    'amount': amount,
                    'asset_id': self.id,
                    'sequence': sequence,
                    'name': (self.code or '') + '/' + str(sequence),
                    'remaining_value': residual_amount,
                    'depreciated_value': self.value - (self.salvage_value + residual_amount),
                    'depreciation_date': depreciation_date.strftime(DF),
                    'journal_date': date_journal,
                }
                commands.append((0, False, vals))
                # Considering Depr. Period as months
                depreciation_date = date(year, month, day) + relativedelta(months=+self.method_period)
                day = depreciation_date.day
                month = depreciation_date.month
                year = depreciation_date.year
                date_journal = date_journal + relativedelta(months=+self.method_period)
        
        self.write({'depreciation_line_ids': commands})
        return True

    @api.model
    def create(self,vals):
        catagory_id=self.env['account.asset.category'].browse(vals['category_id'])        
        if catagory_id.company_id.id != vals['company_id']:           
            raise UserError(_('Access Denied!'),(('Asset Category belongs to the same company.')))
        return super(account_asset_asset, self).create(vals)

    @api.multi
    def write(self, vals):
        
        category_id = self.env['account.asset.category'].browse(vals.get('category_id'))
        if vals.has_key('company_id'):
            if category_id.company_id.id != vals.get('company_id'):               
                raise UserError(_('Access Denied!'),(('Asset Category belongs to the same company.')))
        
        return super(account_asset_asset, self).write(vals)


    def process_depreciation(self):
        depreciation = self.env['account.asset.depreciation.line']
        account_asset = self.env['account.asset.asset']
# Get list of running assets
        now = datetime.datetime.now()
        account_asset_ids = account_asset.search([('state', '=', 'open')])
        if account_asset_ids:
            for account_asset_id in account_asset_ids:
# Get account asset values
                depreciation_ids = depreciation.search([('depreciation_date', '<=', now.strftime("%m-%d-%Y")),('asset_id', '=', account_asset_id), ('move_check', '=', False)])
                try:
# Call base method from account_asset module
                    depreciation.create_move(depreciation_ids)
                except Exception as e:
                    print "Exception Occured:" + str(e)
        return True

account_asset_asset()


class UpdateJournalDate(models.TransientModel):
    _name = 'update.journal'

    journal_update = fields.Date('Journal Date', required=True, default=fields.Datetime.now)

    @api.multi
    def confirm(self):
        context = dict(self._context)
       
        context['journal_update'] = self.journal_update or False  

        rows = self.env['account.asset.asset'].browse(self.env.context.get('active_ids'))
        for rec in  rows:

            if rec.journal_date:                   
                return {
                    'name': ('Journal Date Existing'),
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'update.date',
                    'view_id': self.env.ref('vitalpet_custom_asset.journal_date_warning_form').id,
                    'type': 'ir.actions.act_window',
                    'context': context,
                    'target': 'new'
                }
            else:
                rec.write({'journal_date':self.journal_update})

        return True


class UpdateJournalWarning(models.TransientModel):
    _name = 'update.date' 
    
    def continue_to_new_journal_entry(self):        
            journal_update = self.env.context.get('journal_update')      
            

            rows = self.env['account.asset.asset'].browse(self.env.context.get('active_ids'))
            for rec in  rows:
                rec.write({'journal_date':journal_update})
    

class account_asset_category(models.Model):
    _inherit = 'account.asset.category'
    
    assinged = fields.Boolean('Assigned')
    
account_asset_category()

class account_asset_depreciation_line(models.Model):
    _inherit = 'account.asset.depreciation.line'

   
    company_id = fields.Many2one('res.company', 'Company')
    journal_date = fields.Date('Journal Date')

    @api.multi
    def create_move(self, post_move=True):
        created_moves = self.env['account.move']
        for line in self:
            category_id = line.asset_id.category_id
            depreciation_date = self.env.context.get('journal_date') or line.journal_date or fields.Date.context_today(self)
            company_currency = line.asset_id.company_id.currency_id
            current_currency = line.asset_id.currency_id
            amount = current_currency.compute(line.amount, company_currency)
            sign = (category_id.journal_id.type == 'purchase' or category_id.journal_id.type == 'sale' and 1) or -1
            asset_name = line.asset_id.name + ' (%s/%s)' % (line.sequence, len(line.asset_id.depreciation_line_ids))
            prec = self.env['decimal.precision'].precision_get('Account')
            move_line_1 = {
                'name': asset_name,
                'account_id': category_id.account_depreciation_id.id,
                'debit': 0.0 if float_compare(amount, 0.0, precision_digits=prec) > 0 else -amount,
                'credit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0,
                'journal_id': category_id.journal_id.id,
                'partner_id': line.asset_id.partner_id.id,
                'analytic_account_id': category_id.account_analytic_id.id if category_id.type == 'sale' else False,
                'currency_id': company_currency != current_currency and current_currency.id or False,
                'amount_currency': company_currency != current_currency and - sign * line.amount or 0.0,
            }
            move_line_2 = {
                'name': asset_name,
                'account_id': category_id.account_depreciation_expense_id.id,
                'credit': 0.0 if float_compare(amount, 0.0, precision_digits=prec) > 0 else -amount,
                'debit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0,
                'journal_id': category_id.journal_id.id,
                'partner_id': line.asset_id.partner_id.id,
                'product_id': category_id.product_id.id if category_id.product_id.id else False,
                'analytic_account_id': category_id.account_analytic_id.id if category_id.type == 'purchase' else False,
                'currency_id': company_currency != current_currency and current_currency.id or False,
                'amount_currency': company_currency != current_currency and sign * line.amount or 0.0,
            }
            
            move_vals = {
                'ref': line.asset_id.code,
                'date': depreciation_date or False,
                'journal_id': category_id.journal_id.id,
                'line_ids': [(0, 0, move_line_1), (0, 0, move_line_2)],
            }
            move = self.env['account.move'].create(move_vals)
            line.write({'move_id': move.id, 'move_check': True})
            created_moves |= move

        if post_move and created_moves:
            created_moves.filtered(lambda m: any(m.asset_depreciation_ids.mapped('asset_id.category_id.open_asset'))).post()
        return [x.id for x in created_moves]

    
    def show_journal(self):
        cur_obj = self.browse()
        return {
            'name': _('Journal Entries'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.move',
            'res_id': cur_obj.move_id.id,
            'type': 'ir.actions.act_window',
        }

account_asset_depreciation_line()

# class asset_depreciation_manual_wizard(models.TransientModel):
#     _name = "asset.depreciation.manual.wizard"
#     _description = "asset.depreciation.manual.wizard"

#     @api.model
#     def _get_default_company(self):
#         print 'sow==========='
#         res = self.env['res.users'].browse().company_id.id,
#         print res,'res--------'
#         return res  

#     # _defaults = {
#     #     'company_id': lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, c).company_id.id,
#     #     'type': 'draft',
#     # }

#     type = fields.Selection([('draft', 'View Draft'),('run', 'Run Depreciation')], 'Deprication Type', required=True,default='draft')
#     company_id = fields.Many2one('res.company', 'Company', required=True,default=_get_default_company)       
   
#     def asset_compute(self):
       
#         depreciation_ids = []
#         processed_depreciation_ids = []
#         data = self.browse()
#         print self.company_id.id,'its comp==='
#         if self.company_id:          
#             company_id = self.env['res.users'].search([('company_id', '=', self.company_id.id)]) 
#             print company_id.id,'comp--'

#         if self.company_id.id != company_id:
#             print 'yes---not equal--is not thr'
#             raise UserError(_('Chosen company is not equal to current company.'))


#         depreciation = self.env['account.asset.depreciation.line']
#         account_asset = self.env['account.asset.asset']
# # Get list of running assets
#         now = datetime.datetime.now()
#         account_asset_ids = account_asset.search([('company_id', '=', data.company_id.id), ('state', '=', 'open')])
#         if account_asset_ids:
#             if data.type == 'run':
#                 for account_asset_id in account_asset_ids:
# # Get account asset values
#                     if account_asset_id:
#                         print "Fetching all depreciation"
#                         depreciation_ids = depreciation.search([('depreciation_date', '<=', now.strftime("%m-%d-%Y")),
#                                                                          ('asset_id', '=', account_asset_id),
#                                                                          ('move_check', '=', False)],)
#                         for line in depreciation_ids:
#                             processed_depreciation_ids.append(line)
#                 try:
# # Call base method from account_asset module
#                     depreciation.create_move(processed_depreciation_ids)
#                 except Exception as e:
                    
#                     raise UserError(_('Asset Info!'),
#                                          _('Exception Occured: "%s".'))
#             else:
#                 for account_asset_id in account_asset_ids:
# # Get account asset values
#                     if account_asset_id:
#                         print "Fetching all depreciation"
#                         depreciation_ids = depreciation.search(
#                                                                [('asset_id', '=', account_asset_id),
#                                                                 ('move_check', '=', False)])
#                         for line in depreciation_ids:
#                             processed_depreciation_ids.append(line)
# # Open depreciation line items which is posted manualy now
#             if processed_depreciation_ids:
#                 domain = [('id', 'in', processed_depreciation_ids)]
#                 return {
#                     'type': 'ir.actions.act_window',
#                     'name': _('Assets Depreciation'),
#                     'view_type': 'form',
#                     'view_mode': 'tree,form',
#                     'domain': domain,
#                     'res_model': 'account.asset.depreciation.line',
#                     'nodestroy': True,
#                 }

#             else:
                
#                 raise UserError(_('Asset Info'), (('Current day assets depreciation line not available.')))
#         else:
            
#             raise UserError(_('Asset Info'), (('Processing assets not available for the company.')))

# asset_depreciation_manual_wizard()