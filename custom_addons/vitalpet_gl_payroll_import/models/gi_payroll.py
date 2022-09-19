from odoo import fields, models, api, _
import datetime
from odoo.exceptions import UserError, RedirectWarning, ValidationError

class GlPayrollImport(models.Model):
    _name = 'gl.payroll.import'
    _rec_name = 'sequence'

    sequence = fields.Char('Sequence', readonly=True, default='New', copy=False)
    name = fields.Char('Name')
    total_record = fields.Integer('Total Record')
    pass_record = fields.Integer('Passed Record')
    issue_record = fields.Integer('Error Record')
    state =  fields.Selection([
            ('draft', 'Draft'),
            ('processing', 'Processing'),
            ('temp_journal', 'Temp Journal'),
            ('validated', 'Validated'),
            ('processed', 'Processed')], 'Status',  default='draft')
    record_ids = fields.One2many('gl.payroll.import.line', 'payroll_import_id', string='Record')
    temp_journal_ids = fields.One2many('temp.move.line', 'import_id' , string='TEMPORARY JE')
    inter_company_balance = fields.Float('InterCompany Balance')

    
    @api.multi
    def reset_draft(self):
        for rec in self:
            move_records = self.env['account.move'].search([('gl_import_id','=',rec.id)])
            for move in move_records:
                move.button_cancel()
                move.unlink()
            for lines in rec.temp_journal_ids:
                lines.unlink()
            rec.state='draft'
            rec.inter_company_balance=0            
            rec.pass_record=0
            
        
    @api.multi
    def open_journal_entries(self):
        return {
                'name':_('Journal Entries'),
                'type':'ir.actions.act_window',
                'domain' : [('gl_import_id.id','=',self.id)],
                'view_type':'form',
                'view_mode':'tree',
                'res_model':'account.move',
                'res_id':self[0].id,
                'view_id':False,
                'views':[(self.env.ref('account.view_move_tree').id or False, 'tree'),(self.env.ref('account.view_move_form').id or False, 'form')],
                'target': 'current',
               }
        
    @api.model
    def create(self, vals):
        if vals.get('sequence',('New'))==('New'):
            vals['sequence']=self.env['ir.sequence'].next_by_code('gl.payroll.import') or ('New')
        return super(GlPayrollImport, self).create(vals)
        
    def unlink(self):
        for rec in self:
            if rec.state!='draft':
                raise UserError(_('Record is not in Draft state.'))
            move_records = self.env['account.move'].search([('gl_import_id','=',rec.id)])
            for move in move_records:
                move.unlink()                
        return super(GlPayrollImport, self).unlink()
        
    @api.multi
    def compute(self):
        self.mapping_error()
        self.account_error()
        self.check_validate()
        self.check_record()
#         if self.issue_record == 0:
#             self.create_temp_journal() 
 
    @api.multi
    def temp_journal(self):
        if self.issue_record == 0 and self.total_record>0:
            self.create_temp_journal()
            balance = 0.00
            for value in self.temp_journal_ids:
                if value.account_id.tag_ids.name in ['Intercompany']:
                    balance +=value.debit-value.credit
            if round(balance,2)>0 or round(balance,2)<0:
                self.inter_company_balance=balance
            else:
                self.inter_company_balance=0                       
            self.state = 'temp_journal' 

    @api.multi
    def mapping_error(self):
        for line in self.record_ids:
            mapping_obj = self.env['gl.payroll.mapping'].search([('job_code','in',[line.job_code,'ALL']),('code_type','=',line.code_type),('code','=',line.code),('code_descr','=',line.code_descr)])
            if not mapping_obj:
                line.reason = 'Mapping Error'
                line.status = 'Error'
            else:
                line.reason = None
                line.status = 'Success'
    @api.multi
    def account_error(self):
        for line in self.record_ids:
            if not line.reason:
                mapping_obj = self.env['gl.payroll.mapping'].search([('job_code','in',[line.job_code,'ALL']),('code_type','=',line.code_type),('code','=',line.code),('code_descr','=',line.code_descr)], limit=1)
#                 debit_account = self.env['account.account'].search([('code','=',mapping_obj.debit_account_number),('name','=',mapping_obj.debit_account_name),('company_id','=',line.company_id.id)])
                if mapping_obj.parent == True:
                    company = 74
                else:
                    company = line.costcenter_code.id
                debit_account = self.env['account.account'].search([('code','=',mapping_obj.debit_account_number),('company_id','=',company)])
                if debit_account:
#                     credit_account = self.env['account.account'].search([('code','=',mapping_obj.credit_account_number),('name','=',mapping_obj.credit_account_name),('company_id','=',line.company_id.id)])
                    credit_account = self.env['account.account'].search([('code','=',mapping_obj.credit_account_number),('company_id','=',company)])
                    if credit_account:
                        line.reason = None
                        line.status = 'Success'
                        line.debit_account_id= debit_account.id 
                        line.credit_account_id = credit_account.id 
                        
                        debit_product_obj = mapping_obj.debit_product                      
                        credit_product_obj = mapping_obj.credit_product                        
                        if debit_product_obj:
                            line.debit_product = debit_product_obj.id
                        if credit_product_obj:
                            line.credit_product = credit_product_obj.id
                        line.mapping_based_company_id = company   
                        line.journal_type=mapping_obj.journal_type 
                        if mapping_obj.partner_is_practice:
                            line.partner=line.costcenter_code.partner_id.id
                        else:
                            line.partner=mapping_obj.partner 
                        line.reference=mapping_obj.reference 
                    else:
                        line.reason = 'Credit Account Error'
                        line.status = 'Error'
                else:
                    line.reason = 'Debit Account Error'
                    line.status = 'Error'
                    
    @api.multi
    def check_validate(self):
        i=0
        for line in self.record_ids:
            if line.reason:
                i=1
        if i==0:
            self.state = 'processing'   
    
    @api.multi
    def check_record(self):
        total_record =  len(self.record_ids)
        pass_record = 0
        for line in self.record_ids:
            if not line.reason:
                pass_record+=1
        issue_record = total_record - pass_record
        
        self.total_record = total_record
        self.pass_record = pass_record
        self.issue_record = issue_record


    @api.multi
    def date_period(self,calendar_type,date):
        account_fiscal_periods = self.env['account.fiscal.periods'].search([('calendar_type', '=', calendar_type)])
        if account_fiscal_periods:
            period = self.env['account.fiscal.period.lines'].search([('account_fiscal_period_id','in',[a.id for a in account_fiscal_periods]),('date_start', '<=', date),('date_end', '>=', date)])
            if period:
                return  period.id
        
    @api.multi
    def create_temp_journal(self):
        account_list = []
        for line in self.record_ids:
            credit_product=debit_product=""
            if line.credit_product:
                credit_product=str(line.credit_product.id)
            if line.debit_product:
                debit_product=str(line.debit_product.id)
            partner_def=str(line.partner.id) if line.partner else '0'
            account_list.append(str(line.debit_account_id.id) + '--' + str(line.credit_account_id.id)+'--' +credit_product+'--' +debit_product+"--"+partner_def)
        account_set_list = list(set(account_list))
        date_journal_h= label=journal=company=''
        credit_product_obj=debit_product_obj=date_journal=credit_acc=False
        for account in account_set_list:
            amount = 0.00
            account_split=account.split("--")
            record_ids = self.env['gl.payroll.import.line'].search([
                                        ('payroll_import_id','=',self.id),
                                        ('debit_account_id','=',int(account_split[0])),
                                        ('credit_account_id','=',int(account_split[1])),
                                        ('credit_product','=',int(account_split[2]) if account_split[2]!='' else None),
                                        ('debit_product','=',int(account_split[3]) if account_split[3]!='' else None),
                                        ('partner','=',int(account_split[4]) if int(account_split[4])!=0 else None),
                                        ]);  
                                                
            if record_ids:
                
#                 print nn,record_ids
                for line in record_ids:
                    company = line.mapping_based_company_id.id
                    amount+=line.namount
                    debit_acc = line.debit_account_id.id
                    credit_acc = line.credit_account_id.id
                    debit_product_obj = line.debit_product                     
                    credit_product_obj = line.credit_product   
                    partner=line.partner.id if line.partner else False                     
    
                    journal = self.env['account.journal'].search([('name','like',line.journal_type),('company_id','=',company)]).id                
                    company_id=line.mapping_based_company_id
                    
                    date_start=self.date_period(company_id.calendar_type.id,line.date_start)
                    date_end=self.date_period(company_id.calendar_type.id,line.date_end)
                    
                    date_journal = line.date_end
                    if date_start==date_end:
                        date_journal_h= ''
                    else:
                        date_journal_h=datetime.datetime.strptime(line.date_start, "%Y-%m-%d") + datetime.timedelta(days=6)
                    
                    label = "Payroll" + '-' + str(date_journal)
                    reference = line.reference
                
                if date_journal_h=='':
                    move_line_1 = {
                        'name': label,
                        'account_id': credit_acc,
                        'debit': 0.0,
                        'credit': amount,
                        'product_id':credit_product_obj.id if credit_product_obj != False else '',
                        'import_id':self.id,
                        'journal_id':journal,
                        'company_id':company,
                        'date_journal':date_journal,
                        'partner':partner
                    }
                    move = self.env['temp.move.line'].create(move_line_1)
                    move_line_2 = {
                        'name': label,
                        'account_id':debit_acc,
                        'credit': 0.0,
                        'debit': amount,
                        'product_id':debit_product_obj.id if debit_product_obj != False else '',
                        'import_id':self.id,
                        'journal_id':journal,
                        'company_id':company,
                        'date_journal':date_journal,
                        'partner':partner
                    }
                    move2 = self.env['temp.move.line'].create(move_line_2)
                    
                else:
                    move_line_1 = {
                        'name': label,
                        'account_id': credit_acc,
                        'debit': 0.0,
                        'credit': amount/2,
                        'product_id':credit_product_obj.id if credit_product_obj != False else '',
                        'import_id':self.id,
                        'journal_id':journal,
                        'company_id':company,
                        'date_journal':date_journal,
                        'partner':partner
                    }
                    move = self.env['temp.move.line'].create(move_line_1)
                    move_line_2 = {
                        'name': label,
                        'account_id':debit_acc ,
                        'credit': 0.0,
                        'debit': amount/2,
                        'product_id':debit_product_obj.id if debit_product_obj != False else '',
                        'import_id':self.id,
                        'journal_id':journal,
                        'company_id':company,
                        'date_journal':date_journal,
                        'partner':partner
                    }
                    move2 = self.env['temp.move.line'].create(move_line_2)
                    move_line_1 = {
                        'name': label,
                        'account_id': credit_acc,
                        'debit': 0.0,
                        'credit': amount/2,
                        'product_id':credit_product_obj.id if credit_product_obj != False else '',
                        'import_id':self.id,
                        'journal_id':journal,
                        'company_id':company,
                        'date_journal':date_journal_h,
                        'partner':partner
                    }
                    move = self.env['temp.move.line'].create(move_line_1)
                    move_line_2 = {
                        'name': label,
                        'account_id':debit_acc ,
                        'credit': 0.0,
                        'debit': amount/2,
                        'product_id':debit_product_obj.id  if debit_product_obj != False else '',
                        'import_id':self.id,
                        'journal_id':journal,
                        'company_id':company,
                        'date_journal':date_journal_h,
                        'partner':partner
                    }
                    move2 = self.env['temp.move.line'].create(move_line_2)
    
    

    def create_temp_journal_partner(self):

        partner_obj = self.env['gl.payroll.import'].search([('state' , 'in' , ['validated'])])

        for record in partner_obj:

            record.temp_journal_ids.unlink()

            record.create_temp_journal()

            

    @api.multi
    def check_intercompany_balance(self):
        
        if self.inter_company_balance > 10 or self.inter_company_balance<-10 :
            return {
                    'name': _('Image'),
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'wizard.intercompany.validate',
                    'view_id': self.env.ref('vitalpet_gl_payroll_import.view_wizard_intercompany_balance').id,
                    'type': 'ir.actions.act_window',
                    'context': self.env.context,
                    'target': 'new'
                }
        else:
            self.create_journal()
          
    @api.multi
    def create_journal(self):
        account_list = []
#         if self.inter_company_balance > 10 or self.inter_company_balance<-10 :
#             raise UserError(_('Payroll cannot be validated because Intercompany Balance exceeds $10.00'))
        for line in self.record_ids:
            credit_product=debit_product=""
            if line.credit_product:
                credit_product=str(line.credit_product.id)
            if line.debit_product:
                debit_product=str(line.debit_product.id)
                
            partner_def=str(line.partner.id) if line.partner else '0'
            account_list.append(str(line.debit_account_id.id) + '--' + str(line.credit_account_id.id)+'--' +credit_product+'--' +debit_product+"--"+partner_def)            
        account_set_list = list(set(account_list))
        date_journal_h= label=journal=company=''
        credit_product_obj=debit_product_obj=date_journal=credit_acc=False
        countn=1
        for account in account_set_list:
            countn+=1
            amount = 0.00
            account_split=account.split("--")
            record_ids = self.env['gl.payroll.import.line'].search([
                                        ('payroll_import_id','=',self.id),
                                        ('debit_account_id','=',int(account_split[0])),
                                        ('credit_account_id','=',int(account_split[1])),
                                        ('credit_product','=',int(account_split[2]) if account_split[2]!='' else None),
                                        ('debit_product','=',int(account_split[3]) if account_split[3]!='' else None),
                                        ('partner','=',int(account_split[4]) if int(account_split[4])!=0 else None),
                                        ]);  
                                                
            if record_ids:                
                for line in record_ids:
                    company = line.mapping_based_company_id.id
                    amount+=line.namount
                    
                    debit_acc = line.debit_account_id.id
                    credit_acc = line.credit_account_id.id
                    debit_product_obj = line.debit_product                     
                    credit_product_obj = line.credit_product
                    partner=line.partner.id if line.partner else False
                    
                    journal = self.env['account.journal'].search([('name','like',line.journal_type),('company_id','=',company)]).id                
                    company_id=line.mapping_based_company_id
                    
                    date_start=self.date_period(company_id.calendar_type.id,line.date_start)
                    date_end=self.date_period(company_id.calendar_type.id,line.date_end)
                    
                    date_journal = line.date_end
                    if date_start==date_end:
                        date_journal_h= ''
                    else:
                        date_journal_h=datetime.datetime.strptime(line.date_start, "%Y-%m-%d") + datetime.timedelta(days=6)
                    
                    label = "Payroll" + '-' + str(date_journal)
                    reference = line.reference                    
                    description = self.sequence
       
                    
                if date_journal_h=='':
                    move_line_1 = {
                        'name': label,
                        'account_id': credit_acc,
                        'debit': 0.0 if amount>0 else amount*-1,
                        'credit': amount if amount>0 else 0.0,
                        'product_id':credit_product_obj.id if credit_product_obj != False else '',
                        'partner_id':partner
                    }
                    move_line_2 = {
                        'name': label,
                        'account_id':debit_acc ,
                        'credit': 0.0 if amount>0 else amount*-1,
                        'debit': amount if amount>0 else 0.0,
                        'product_id':debit_product_obj.id if debit_product_obj != False else '',
                        'partner_id':partner
                    }
                    move_vals = {
                        'date': date_journal or False,
                        'journal_id': journal,
                        'ref':reference,
                        'line_ids': [(0, 0, move_line_1), (0, 0, move_line_2)],
                        'gl_import_id':self.id,
                        'description':description,
                    }
                    move = self.env['account.move'].create(move_vals)   
                else:
                    move_line_1 = {
                        'name': label,
                        'account_id': credit_acc,
                        'debit': 0.0 if amount>0 else (amount/2)*-1,
                        'credit': amount/2 if amount>0 else 0.0,
                        'product_id':credit_product_obj.id if credit_product_obj != False else '',
                        'partner_id':partner
                    }
                    move_line_2 = {
                        'name': label,
                        'account_id':debit_acc ,
                        'credit': 0.0 if amount>0 else (amount/2)*-1,
                        'debit': amount/2 if amount>0 else 0.0,
                        'product_id':debit_product_obj.id if debit_product_obj != False else '',
                        'partner_id':partner
                    }
                    move_vals = {
                        'date': date_journal or False,
                        'journal_id': journal,
                        'ref':reference,
                        'line_ids': [(0, 0, move_line_1), (0, 0, move_line_2)],
                        'gl_import_id':self.id,
                        'description':description,
                    }
                    move = self.env['account.move'].create(move_vals)  
                    move_line_1 = {
                        'name': label,
                        'account_id': credit_acc,
                        'debit': 0.0 if amount>0 else (amount/2)*-1,
                        'credit': amount/2 if amount>0 else 0.0,
                        'product_id':credit_product_obj.id if credit_product_obj != False else '',
                        'partner_id':partner
                    }
                    move_line_2 = {
                        'name': label,
                        'account_id':debit_acc ,
                        'credit': 0.0 if amount>0 else (amount/2)*-1,
                        'debit': amount/2 if amount>0 else 0.0,
                        'product_id':debit_product_obj.id if debit_product_obj != False else '',
                        'partner_id':partner
                    }
                    move_vals = {
                        'date': date_journal_h or False,
                        'journal_id': journal,
                        'ref':reference,
                        'line_ids': [(0, 0, move_line_1), (0, 0, move_line_2)],
                        'gl_import_id':self.id,
                        'description':description,
                    }
                    move = self.env['account.move'].create(move_vals)  
        self.state = 'validated' 

class TempMoveLine(models.Model):
    _name = 'temp.move.line'
    
    name = fields.Char(required=True, string="Label")
    account_id = fields.Many2one('account.account', string='Account', required=True, index=True,
        ondelete="cascade")      
    date_journal = fields.Date(string='Date')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    partner = fields.Many2one('res.partner','Partner')
    debit = fields.Float(default=0.0, string='Debit')
    credit = fields.Float(default=0.0, string='Credit')
    import_id = fields.Many2one('gl.payroll.import', string='Import Ref')
    journal_id = fields.Many2one('account.journal', string='Journal')    
    company_id = fields.Many2one('res.company', string='Company')
    
        
class GlPayrollImportLine(models.Model):
    _name = 'gl.payroll.import.line'
    _order = 'reason asc' 
    
    payroll_import_id = fields.Many2one('gl.payroll.import', 'Payroll Import Ref')
    row_num = fields.Integer('Row Number')
    department_code = fields.Char('Department Code')
    gl_account_no = fields.Char('GL Account No.')
    company_id  = fields.Char(string='Company')
    department = fields.Char('Department')
    costcenter_code = fields.Many2one('res.company','Costcenter Code')
    costcenter_descr = fields.Char('Costcenterdescr')
    job_code = fields.Char('Job Code')
    job_title = fields.Char('Job Title')
    code_type = fields.Char('Code Type')
    code = fields.Char('Code')
    code_descr = fields.Char('Codedescr')  
    namount = fields.Float('NAmount')
    date_start = fields.Date('Date Start')
    date_end = fields.Date('Date End')
    processed = fields.Boolean('Processed')
    status = fields.Char('Status', readonly=True)
    reason = fields.Char('Reason', readonly=True)
    
    debit_account_id= fields.Many2one('account.account','Debit Account') 
    credit_account_id = fields.Many2one('account.account','Credit Account')
    debit_product = fields.Many2one('product.product','Debit Product')
    credit_product = fields.Many2one('product.product','Credit Product')
    journal_type = fields.Char('Journal Type')
    partner = fields.Many2one('res.partner','Partner')
    mapping_based_company_id=fields.Many2one('res.company','Mapping based company')
    reference = fields.Char('Reference')
    
class GlPayrollMapping(models.Model):
    _name = 'gl.payroll.mapping'
    _inherit = ['mail.thread']
    _rec_name = 'sequence'

    sequence = fields.Char('Sequence', readonly=True, default='New', copy=False)
    parent = fields.Boolean('Parent')
    group_code = fields.Boolean('Group Code')    
    job_code = fields.Char('Job Code',track_visibility='onchange')
    code_type = fields.Char('Code Type',track_visibility='onchange')
    code = fields.Char('Code',track_visibility='onchange')
    code_descr = fields.Char('Codedescr ',track_visibility='onchange')
    debit_account_number= fields.Char('Debit Account Number',track_visibility='onchange')    
    debit_account_name = fields.Char('Debit Account Name')
    debit_product = fields.Many2one('product.product','Debit Product', required=True)
    credit_product = fields.Many2one('product.product','Credit Product', required=True)
#     debit_product_id = fields.Many2one('product.product',' ', required=True)
#     credit_product_id = fields.Many2one('product.product',' ', required=True)
    credit_account_number = fields.Char('Credit Account Number',track_visibility='onchange')
    credit_account_name = fields.Char('Credit Account Name')
    journal_type = fields.Char('Journal Type')
    partner_is_practice = fields.Boolean('Partner Practice')
    partner = fields.Many2one('res.partner','Partner')
    reference = fields.Char('Reference')
    
    @api.model
    def create(self, vals):
        if vals.get('sequence',('New'))==('New'):
            vals['sequence']=self.env['ir.sequence'].next_by_code('gl.payroll.mapping') or ('New')

        if vals.get('debit_account_name'):
            debit_acc_nil = self.env['account.account'].search([('name' , 'ilike' , vals.get('debit_account_name'))])
            if not debit_acc_nil:
                raise UserError("Please Enter a valid Debit Account Name")

        if vals.get('credit_account_name'):
            credit_acc_nil = self.env['account.account'].search([('name' , 'ilike' , vals.get('credit_account_name'))])
            if not credit_acc_nil:
                raise UserError("Please Enter a valid Credit Account Name")

        return super(GlPayrollMapping, self).create(vals)


    @api.multi
    def write(self, vals):

        if vals.get('debit_account_name'):
            debit_acc_nil = self.env['account.account'].search([('name' , 'ilike' , vals.get('debit_account_name'))])
            if not debit_acc_nil:
                raise UserError("Please Enter a valid Debit Account Name")

        if vals.get('credit_account_name'):
            credit_acc_nil = self.env['account.account'].search([('name' , 'ilike' , vals.get('credit_account_name'))])
            if not credit_acc_nil:
                raise UserError("Please Enter a valid Credit Account Name")


        return super(GlPayrollMapping, self).write(vals)
    
class AccountMove(models.Model):
    _inherit = "account.move"

    gl_import_id = fields.Many2one('gl.payroll.import', string='GL Import Ref')