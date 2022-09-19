# -*- coding: utf-8 -*-
import re
from odoo import api, fields, models, _
from odoo.tools import email_split
from docutils.nodes import description
import odoo.addons.decimal_precision as dp
from odoo.exceptions import ValidationError, UserError
import datetime
import calendar
from datetime import datetime,timedelta

#test

class HrExpense(models.Model):
    _inherit = "hr.expense"
    _description = "Expense"

    unique_import_id = fields.Char()
    source = fields.Selection([('email', 'Email - EML'), ('manual', 'Manual - MNL'), ('import', 'Import - IMP')], string='File Source',
                             readonly=True, default='manual')
#     payment_mode = fields.Selection([("own_account", "Employee (to reimburse)"), ("company_account", "Company"), ("credit_card", "Corporate Card")], default='own_account', states={'done': [('readonly', True)], 'post': [('readonly', True)]}, string="Payment By", track_visibility='onchange')
    payment_mode = fields.Selection([("own_account", "Employee (to reimburse)"), ("credit_card", "Corporate Card")], default='own_account', states={'done': [('readonly', True)], 'post': [('readonly', True)]}, string="Payment By", track_visibility='onchange')
    expense_description = fields.Text('Description', copy=False)
    credit_card_id = fields.Many2one("res.partner", "Credit Card ID")
    product_id = fields.Many2one('product.product', string='Product', readonly=True, states={'draft': [('readonly', False)], 'refused': [('readonly', False)]}, domain=[('can_be_expensed', '=', True)], required=True, track_visibility='onchange')
    unit_amount = fields.Float(string='Unit Price', readonly=True, required=True, states={'draft': [('readonly', False)], 'refused': [('readonly', False)]}, digits=dp.get_precision('Product Price'), track_visibility='onchange')
    quantity = fields.Float(required=True, readonly=True, states={'draft': [('readonly', False)], 'refused': [('readonly', False)]}, digits=dp.get_precision('Product Unit of Measure'), default=1, track_visibility='onchange')
    total_amount = fields.Float(string='Total', store=True, compute='_compute_amount', digits=dp.get_precision('Account'), track_visibility='onchange')
    company_id = fields.Many2one('res.company', string='Company', readonly=True, states={'draft': [('readonly', False)], 'refused': [('readonly', False)]}, default=lambda self: self.env.user.company_id, track_visibility='onchange')
    date = fields.Date(readonly=True, states={'draft': [('readonly', False)], 'refused': [('readonly', False)]}, default=fields.Date.context_today, string="Date", track_visibility='onchange')
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True, readonly=True, states={'draft': [('readonly', False)], 'refused': [('readonly', False)]}, default=lambda self: self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1), track_visibility='onchange',domain="[('company_id', '=', company_id)]")
    account_id = fields.Many2one('account.account', string='Account', readonly=True, store=True, default=lambda self: self.env['ir.property'].get('property_account_expense_categ_id', 'product.category'), track_visibility='onchange')
    attachment_hidden = fields.Float(string="Attachment Hidden",compute='_compute_hidden')
    analytic_account_view = fields.Boolean(string='Analytic Account Aiew')
#     account = fields.Many2one('account.account', 'acc')
# if submited amount is greater then allowed amount employee should submit receipt
#\\-------------inherited onchange----------------
    
    @api.constrains('account_id','company_id')
    def _check_company(self):
        if self.employee_id.company_id != self.company_id or  self.account_id.company_id != self.company_id:
            raise ValidationError(_('Please create the expense from %s') % self.employee_id.company_id.name)


    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.analytic_account_view = self.product_id.require_analytic
        else:
            self.analytic_account_view = False
        if self.payment_mode =="own_account":
            if self.product_id:
                if not self.name:
                    self.name = self.product_id.display_name or ''
                self.unit_amount = self.product_id.price_compute('standard_price')[self.product_id.id]
                self.product_uom_id = self.product_id.uom_id
                self.tax_ids = self.product_id.supplier_taxes_id
                account = self.product_id.product_tmpl_id._get_product_accounts()['expense']
                account_asset_type = self.product_id.categ_id.asset_category_pro_id.account_asset_id
                if account:
                    self.account_id = account
#                     self.account = account
                elif account_asset_type:
                    self.account_id = account_asset_type
                else:
                    self.account_id = None
        else:
            if self.product_id:
                if not self.name:
                    self.name = self.product_id.display_name or ''
                self.unit_amount = self.unit_amount
                self.product_uom_id = self.product_id.uom_id
                self.tax_ids = self.product_id.supplier_taxes_id
                account = self.product_id.product_tmpl_id._get_product_accounts()['expense']
                account_asset_type = self.product_id.categ_id.asset_category_pro_id.account_asset_id
                
                if account:
                    self.account_id = account
#                     self.account = account
                elif account_asset_type:
                    self.account_id = account_asset_type
                else:
                    self.account_id = None

    @api.multi
    def _compute_hidden(self): 
        for attach in self:
            attach_obj = self.env['ir.values'].search([('name', '=', 'credit_limit_check')])
            attach.attachment_hidden=attach_obj.value_unpickle

    @api.model
    def create(self, values): 
        product = (values.get('product_id'))
        tid = self.env['product.product'].search([('id','=',product)])
        exp_account = tid.product_tmpl_id._get_product_accounts()['expense']
        asset_account = tid.categ_id.asset_category_pro_id.account_asset_id
        if exp_account:
            values.update({'account_id':exp_account.id})
        else:
            values.update({'account_id':asset_account.id})
        
        if (values.get('unit_amount')) == 0.0:
            raise ValidationError(_('Please enter a valid unit price'))
        if values.get('payment_mode') == 'credit_card':
            employee = self.env['hr.employee'].browse(values.get('employee_id'))
            if not employee.credit_card_id:
                raise ValidationError(_('Please assign credit card to employee'))
            else:
                values['credit_card_id'] =  employee.credit_card_id.id
        
        if (values.get('account_id')) == False:
            raise ValidationError(_('Account should not be empty'))

        return super(HrExpense, self).create(values)
    
    @api.multi
    def write(self, vals):
        for line in self:
            if (vals.get('product_id')):
                product = (vals.get('product_id'))
                tid = self.env['product.product'].search([('id','=',product)])
                account = tid.product_tmpl_id._get_product_accounts()['expense']
                asset_account = tid.categ_id.asset_category_pro_id.account_asset_id
                        
                if account:
                    vals.update({'account_id':account.id})
                else:
                    vals.update({'account_id':asset_account.id})
    
            if vals.get('payment_mode') == 'credit_card' or (not vals.get('payment_mode') and line.payment_mode == 'credit_card'):
                employee_id = vals.get('employee_id') or line.employee_id.id
                employee = self.env['hr.employee'].browse(employee_id)
                if not employee.credit_card_id:
                    raise ValidationError(_('Please assign credit card to employee'))
                else:
                    vals['credit_card_id'] =  employee.credit_card_id.id
            else:
                vals['credit_card_id'] =  False
      
        res = super(HrExpense, self).write(vals)
        

        if (vals.get('unit_amount')) == 0.0:
            raise ValidationError(_('Please enter a valid unit price'))
         
        if (vals.get('account_id')) == False:
            raise ValidationError(_('Account should not be empty')) 


        return res
#     
 
    @api.multi
    def submit_expenses(self):
        for record in self :            
            if not record.company_id:
                raise ValidationError(_('Please choose company'))
            if record.company_id:
                attachments_id = self.env['ir.attachment'].search([('res_id', '=', record.id)], limit=1)
            if self.env['ir.values'].get_default('hr.expense', 'credit_limit_check') <= record.total_amount and not attachments_id:
                    raise ValidationError(_('Please attach receipt with expense'))
            if not record.employee_id.address_home_id:
                raise ValidationError(_('Please add Home Address for this employee'))

        return super(HrExpense, self).submit_expenses()
    
    def _prepare_move_line(self, line):
        '''
        This function prepares move line of account.move related to an expense
        '''
        if self.payment_mode == 'credit_card':
            partner_id = self.employee_id.credit_card_id.id
        else:
            partner_id = self.employee_id.address_home_id.commercial_partner_id.id
        return {
            'date_maturity': line.get('date_maturity'),
            'partner_id': partner_id,
            'name': line['name'][:64],
            'debit': line['price'] > 0 and line['price'],
            'credit': line['price'] < 0 and -line['price'],
            'account_id': line['account_id'],
            'analytic_line_ids': line.get('analytic_line_ids'),
            'amount_currency': line['price'] > 0 and abs(line.get('amount_currency')) or -abs(line.get('amount_currency')),
            'currency_id': line.get('currency_id'),
            'tax_line_id': line.get('tax_line_id'),
            'tax_ids': line.get('tax_ids'),
            'quantity': line.get('quantity', 1.00),
            'product_id': line.get('product_id'),
            'product_uom_id': line.get('uom_id'),
            'analytic_account_id': line.get('analytic_account_id'),
            'payment_id': line.get('payment_id'),
        }
        
        
   
        
    @api.model
    def message_new(self, msg_dict, custom_values=None):
        if custom_values is None:
            custom_values = {}

        email_address = email_split(msg_dict.get('email_from', False))[0]

        employee = self.env['hr.employee'].search([
            '|',
            ('work_email', 'ilike', email_address),
            ('user_id.email', 'ilike', email_address)
        ], limit=1)

        expense_description = msg_dict.get('subject', '')
        description = msg_dict.get('body', '')

        # Match the first occurence of '[]' in the string and extract the content inside it
        # Example: '[foo] bar (baz)' becomes 'foo'. This is potentially the product code
        # of the product to encode on the expense. If not, take the default product instead
        # which is 'Fixed Cost'
        default_product = self.env.ref('hr_expense.product_product_fixed_cost')
        pattern = '\[([^)]*)\]'
        product_code = re.search(pattern, expense_description)
        if product_code is None:
            product = default_product
        else:
            expense_description = expense_description.replace(product_code.group(), '')
            product = self.env['product.product'].search([('default_code', 'ilike', product_code.group(1))]) or default_product
        account = product.product_tmpl_id._get_product_accounts()['expense']
        if account:
            account_id = account.id
        else:
            account_id = ''

        pattern = '[-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?'
        # Match the last occurence of a float in the string
        # Example: '[foo] 50.3 bar 34.5' becomes '34.5'. This is potentially the price
        # to encode on the expense. If not, take 1.0 instead
        expense_price = re.findall(pattern, expense_description)
        
        # TODO: International formatting
        if not expense_price:
            price = 1.0
        else:
            price = expense_price[-1][0]
            expense_description = expense_description.replace(price, '')
            try:
                price = float(price)
            except ValueError:
                price = 1.0
        print price
        custom_values.update({
            'name': expense_description.strip(),
            'employee_id': employee.id,
            'product_id': product.id,
            'product_uom_id': product.uom_id.id,
#             'description': description,
            'date': datetime.today(),
            'quantity': 1,
            'account_id':account_id,
            'unit_amount': price,
            'company_id': employee.company_id.id,
        })
        return super(HrExpense, self).message_new(msg_dict, custom_values)
      
    @api.onchange('payment_mode')
    def onchange_payment_mode(self):
        if self.payment_mode == 'credit_card':
            emp_rec = self.env["hr.employee"].search([('id', '=', self.employee_id.id)])
            if emp_rec.credit_card_id:
                self.credit_card_id = emp_rec.credit_card_id
            else:
                self.credit_card_id = False
        else:
            self.credit_card_id = False
                    
    @api.onchange('employee_id')
    def onchange_employee_id(self):
        if self.payment_mode == 'credit_card':
            emp_rec = self.env["hr.employee"].search([('id', '=', self.employee_id.id)])
            if emp_rec.credit_card_id:
                self.credit_card_id = emp_rec.credit_card_id
            else:
                self.credit_card_id = False
        else:
            self.credit_card_id = False      




class HrExpenseSheet(models.Model):
    _inherit = "hr.expense.sheet"

    @api.multi
    def _create_expense_task_cron(self):
        company_obj = self.env['res.company']
        company_sr = company_obj.search([('expense', '=', True)])
        for loop in company_sr:
            task_obj = self.env['project.task']
            project_obj = self.env['project.project']
            project_tag = self.env['project.tags']
            project_tag_sr = project_tag.search([('name', '=', 'Expenses')])
            date_today = datetime.now()
            task_todo_sr = self.env['project.task.type'].search([('name', '=', 'To Do')])
            task_complete_sr = self.env['project.task.type'].search([('name', '=', 'Complete')])
            period = self.env['account.fiscal.period.lines'].search([('date_start', '<=', str(date_today)),('date_end', '>=', str(date_today))])
            start = period.date_start
            end = period.date_end
            dt = datetime.strptime(start, '%Y-%m-%d')
            dt_end = datetime.strptime(end, '%Y-%m-%d')
            last_day = calendar.monthrange(dt_end.year, dt_end.month)[-1]
            end_of_month = datetime(year=dt_end.year, month=dt_end.month, day=last_day).date()

            deadline = end_of_month + timedelta(days=5)

            project_sr = project_obj.search([('name', '=', 'My Practice'),('company_id', '=', loop.id)])

            employee_sr = self.env['hr.employee'].search([('user_id', '=', loop.manager_user_id.id)])
            if employee_sr:
                exp_obj = self.env["hr.expense.sheet"]
                name_exp = loop.company_id.code + " -Expense Report- "+ dt.strftime("%m")+ "-" +dt.strftime("%Y")
                if not exp_obj.search([('name','=', name_exp)]):
                    vals = {
                        'name': name_exp,
                        #'employee_id': employee_sr.id,
                        'company_id': loop.id
                    }
                    exp = exp_obj.create(vals)
                
                name_project = loop.code + " -Expense Report- "+ dt.strftime("%m")+ "-" +dt.strftime("%Y")
                project_obj_sr = self.env['project.task'].search([('name','=', name_project)])
                if project_obj_sr:
                    deadline_date = datetime.now()
                    date_start_plus_five = datetime.strptime(project_obj_sr.date_start[:10], '%Y-%m-%d') + timedelta(days=5)
                    date_start_plus_seven = datetime.strptime(project_obj_sr.date_start[:10], '%Y-%m-%d') + timedelta(days=7)
                    date_start_plus_fourteen = datetime.strptime(project_obj_sr.date_start[:10], '%Y-%m-%d') + timedelta(days=14)
                    
                    if project_obj_sr.stage_id != project_obj_sr:
                        
                        if deadline_date > date_start_plus_five and deadline_date <= date_start_plus_seven:
                            task_todo_sr = self.env['project.task.type'].search([('name', '=', 'Overdue < 1 Week')])
                            project_obj_sr.write({'stage_id':task_todo_sr.id})
                        elif deadline_date > date_start_plus_seven and deadline_date <= date_start_plus_fourteen:
                            task_todo_sr = self.env['project.task.type'].search([('name', '=', 'Overdue > 1 Week')])
                            project_obj_sr.write({'stage_id':task_todo_sr.id})
                        elif deadline_date > date_start_plus_fourteen:
                            task_todo_sr = self.env['project.task.type'].search([('name', '=', 'Overdue > 1 Week')])
                            project_obj_sr.write({'stage_id':task_todo_sr.id})

                else:    
                    values = {
                            'name': name_project,
                            'company_id': loop.id,
                            'project_id': project_sr.id,
                            'tag_ids': [(6, 0, [project_tag_sr.id])],
                            'user_id': loop.manager_user_id.id,
                            'mypractice':True,
                            'startdate_date': start,
                            'date_deadline': deadline,
                            'stage_id': task_todo_sr.id
    
                            }
                    task = task_obj.create(values)

        self.expense_task_complete()

        return True

    def expense_task_complete(self):

        exp_obj = self.env['hr.expense.sheet'].search([])
        project_tag = self.env['project.tags']
        project_tag_sr = project_tag.search([('name', '=', 'Expenses')])
        
        company_obj = self.env['res.company'].search([])
        current_month = datetime.today()

        for company in company_obj:
            task_obj = self.env['project.task'].search([('company_id' , '=' , company.id),('tag_ids' , '=' , project_tag_sr.id),('stage_id.name','in',['Overdue < 1 Week','Overdue > 1 Week'])])
            for x in range(12):
                mon = current_month + timedelta(days=(x*-30))
                if exp_obj:
                    i=j=0
                    for rec in exp_obj:
                        for dat in rec.expense_line_ids:
                            if datetime.strptime(dat.date, '%Y-%m-%d').month == mon.month:
                                if company == rec.company_id:
                                    i += 1 
                                    if rec.state == 'post' or rec.state == 'paid' or rec.state == 'cancel':
                                        j +=1 
                    if i == j:
                        for task in task_obj:
                            if datetime.strptime(task.date_start, '%Y-%m-%d %H:%M:%S').month == mon.month:
                                task_complete_sr = self.env['project.task.type'].search([('name', '=', 'Complete')])
                                task.write({'stage_id':task_complete_sr.id})
                                task.completed_date = datetime.now().date()

        return True


    def change_company(self):

        project_tag = self.env['project.tags']
        project_tag_sr = project_tag.search([('name', '=', 'Expenses')])
        exp_obj = self.env['project.task'].search([('tag_ids' , '=' , project_tag_sr.id),('name' , 'like' , 'Expense Report')])
        for exp in exp_obj:
            company_code = exp.name[:3]
            exp.company_id = self.env['res.company'].search([('code' , '=' , company_code)]) 



    def user_role(self):
        user_obj = self.env['res.users']
        officer = user_obj.has_group('hr_expense.group_hr_expense_user')
        manager = user_obj.has_group('hr_expense.group_hr_expense_manager')
        if officer:
            self.role = 'officer'
        if manager:
            self.role = 'manager'

    def approve_expense_sheets(self):
        res=super(HrExpenseSheet, self).approve_expense_sheets()
        if (self.create_uid.id == self.env.user.id) and self.role == 'officer':
            raise UserError(_("You don't have access to approve your own expenses"))
        return res
    
    @api.model
    def _default_journal(self):
        journal_type = 'purchase'
        company_id = False
        if self._context.get('default_company_id'):
            company_id = self._context.get('default_company_id')
        if journal_type:
            journals = self.env['account.journal'].search([('type', '=', journal_type), ('company_id', '=', company_id)])
            if journals:
                return journals[0]
        return self.env['account.journal']
    
                   
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True, readonly=True, states={'submit': [('readonly', False)]}, default=lambda self: self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1),track_visibility='onchange')
    payment_mode = fields.Selection([("own_account", "Employee (to reimburse)"), ("company_account", "Company")], related='expense_line_ids.payment_mode', default='own_account', readonly=True, string="Payment By",track_visibility='onchange')
    company_id = fields.Many2one('res.company', string='Company', readonly=True, states={'submit': [('readonly', False)]}, default=lambda self: self.env.user.company_id,track_visibility='onchange')
    journal_id = fields.Many2one('account.journal', string='Expense Journal', states={'done': [('readonly', True)], 'post': [('readonly', True)]},
        help="The journal used when the expense is done.",track_visibility='onchange', default=_default_journal)
    accounting_date = fields.Date(string="Accounting Date",track_visibility='onchange')
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)      
    role = fields.Char(compute='user_role', string='Role')
           
    @api.multi
    def action_sheet_move_create(self):
        if any(sheet.state != 'approve' for sheet in self):
            raise UserError(_("You can only generate accounting entry for approved expense(s)."))

        if any(not sheet.journal_id for sheet in self):
            raise UserError(_("Expenses must have an expense journal specified to generate accounting entries."))
        print self.mapped('expense_line_ids')
        res = self.mapped('expense_line_ids').action_move_create()

        if not self.accounting_date:
            self.accounting_date = self.account_move_id.date

        if self.payment_mode=='own_account' or self.payment_mode=='credit_card':
            self.write({'state': 'post'})
        else:
            self.write({'state': 'done'})
            
        for line in self.expense_line_ids:
            if line.product_id.asset_category_id:
                vals = {
                        'name': line.name,
                        'code': line.name,
                        'category_id': line.product_id.asset_category_id.id,
                        'value': line.total_amount,
                        'partner_id': line.employee_id.address_home_id.id,
                        'company_id': line.company_id.id,
                        #'currency_id': line.invoice_id.company_currency_id.id,
                        'date': line.date,
                        'method_number':line.product_id.asset_category_id.method_number,
                        'method_period':line.product_id.asset_category_id.method_period,
                        'method':line.product_id.asset_category_id.method,
                        'method_time':line.product_id.asset_category_id.method_time,
                        'prorata':line.product_id.asset_category_id.prorata,
                        }
                if line.product_id.asset_category_id.method_time == 'end' and not line.product_id.asset_category_id.method_end:
                    raise UserError(_('Please update ending date in asset category - %s.') % line.asset_category_id.name)
                if line.product_id.asset_category_id.method_end:
                    vals['method_end'] = line.product_id.asset_category_id.method_end
                asset = self.env['account.asset.asset'].create(vals)

                
        return res
    
    def _get_users_to_subscribe(self, employee=False):        
        users = self.env['res.users']        
        employee = employee or self.employee_id        
        if employee.user_id:                 
            users |= employee.user_id       
        
        #removed below code for avoid multi company conflict
#         if employee.parent_id:         #         if employee.parent_id:
#             users |= employee.parent_id.user_id        +#             user_ids.append(employee.parent_id.user_id.id)
#         if employee.department_id and employee.department_id.manager_id and employee.parent_id != employee.department_id.manager_id:         #         if employee.department_id and employee.department_id.manager_id and employee.parent_id != employee.department_id.manager_id:
#             users |= employee.department_id.manager_id.user_id        +#             user_ids.append(employee.department_id.manager_id.user_id.id)
        return users
    

         
class CreditcardInfo(models.Model):
    _name = "creditcard.info"

    name = fields.Char(string='Card Number')#view_type=form&model=hr.expense&action=377&menu_id=274
    card_type = fields.Char(string='Card Type')


class Employee(models.Model):
    _inherit = "hr.employee"

    credit_card_id = fields.Many2one('res.partner', string='Corporate Credit Card')

#     @api.model
#     def create(self, vals):
#         res=super(Employee, self).create(vals)
#         
#         if vals.get('credit_card_id'):           
#             emp_rec = self.env["res.partner"].search([('id', '=',vals.get('credit_card_id'))]) 
#             emp_rec.write({
#                 'assigned_to_id': res.id,
#                 })
#         
#         return res
#     
#     @api.multi
#     def write(self, vals): 
#         if vals.get('credit_card_id'):     
#             emp_rec = self.env["res.partner"].search([('id', '=',vals.get('credit_card_id'))]) 
#             emp_rec.write({
#                 'assigned_to_id': self.id,
#                 })
#         else:
#             emp_rec = self.env["res.partner"].search([('id', '=',self.credit_card_id.id)]) 
#             emp_rec.write({
#                 'assigned_to_id': False,
#                 })
#             
#         res=super(Employee, self).write(vals)        
#         return res




class HrExpenseMyReceipt(models.Model):
    _name = "hrexpense.myreceipt"
    
    name = fields.Char('Name')
    attachment = fields.Binary('Image')
    sender = fields.Char('Sender')
    subject = fields.Char('Subject')
    employee_id = fields.Many2one('hr.employee', string='Employee')
    company_id = fields.Many2one('res.company', string='Company')
    mimetype = fields.Char()
    submit_date = fields.Datetime(string = 'Submit Date', readonly = True, default = lambda self: fields.datetime.now())
    state = fields.Selection([('open', 'Open'), ('processed', 'processed'), ], string = 'Status',
                         copy = False, index = True, default = 'open')
# class ResCompany(models.Model):
#     _inherit = 'res.company'
#     credit_limit = fields.Float(string = 'Expense Limit', store = True, digits = dp.get_precision('Account'),
#                                 required = True)

    @api.multi
    def action_add_to_expenses(self):
        active_ids=[]
        context = dict(self._context)
        employee_id = False
        for receipt in self:
            active_ids.append(receipt.id)
            employee_id = receipt.employee_id.id
            receipt_id = receipt.id
        
        
        

        context['active_ids'] = active_ids
        context['default_employee_id'] = employee_id
        context['default_receipt_id'] = receipt_id
        return {
            'name': _('Add to Expenses'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'add.expenses',
            'view_id': self.env.ref('vitalpet_expense.add_expenses_view_form').id,
            'type': 'ir.actions.act_window',
            'context': context,
            'target': 'new'
        }