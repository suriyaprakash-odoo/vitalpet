import time
import datetime
from operator import itemgetter
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError,UserError
from datetime import datetime,timedelta,date

from bs4 import BeautifulSoup
import re

class account_voucher(models.Model):
    _inherit = 'account.voucher'
    
    x_sales_summary_id = fields.Many2one('sales.summary','Sales Summary Id')
    x_sale_summary_reference_no = fields.Char('Sale Summary Reference',size=128,readonly=True)


    
    @api.multi
    def account_move_get(self):
        res = super(account_voucher, self).account_move_get()
        res['x_sales_summary_id'] = self.x_sales_summary_id.id
        return res

account_voucher()

class account_move(models.Model):
    _inherit = 'account.move'

    x_voucher_id = fields.Many2one('account.voucher', 'Voucher Id')
    x_sale_summary_reference_no = fields.Char('Sale Summary Reference',size=128,readonly=True)
    x_sales_summary_id = fields.Many2one('sales.summary','Sales Summary Id')
    
    def bank_unrecon(self):

        unrecon_obj = self.env['account.bank.statement'].search([('company_id' ,'=' , 67)], limit = 5, offset=0)

        print unrecon_obj
        for rec in unrecon_obj:
            rec.button_draft()
            for line in rec.line_ids:
                print line
                print line.amount
                line.button_cancel_reconciliation()

    
class sales_summary(models.Model):
    _name = 'sales.summary'
    _rec_name = 'sale_summary_seq_no'
    _table = 'sales_summary'
    _inherit = ['mail.thread']
    _order='date desc'


    @api.depends('date')
    def _compute_fiscal_month(self):
        for loop in self:
            if loop.date:
                tid = self.env['account.fiscal.period.lines'].search([('date_start', '<=',loop.date), ('date_end', '>=',loop.date)])
        self.fiscal_period = tid.name

    
                        
    name = fields.Char(string='Name', default = '/')
    state = fields.Selection(
            [('draft', 'Draft'),
             ('valid', 'Valid'),
             ('posted', 'Posted'),
             ('history', 'History')
             ], 'State', readonly=True, size=32, track_visibility='onchange', default="draft",
            help=' * The \'Draft\' status is used when a user is encoding a new and unconfirmed Voucher. \
                                \n* The \'Posted\' status is used when user create voucher,a voucher number is generated and voucher entries are created in account. \
                                \n* The \'History\' status is used for Historical import.')
    company_id  = fields.Many2one('res.company', string='Company', required=True, readonly=True,
                                  states={'draft': [('readonly', False)]} , default=lambda self: self.env.user.company_id.id, track_visibility='onchange')
    date = fields.Date('Date', required=True, readonly=True, states={'draft': [('readonly', False)]}, default=fields.Datetime.now, track_visibility='onchange')
    shift = fields.Selection([('day', 'Day'), ('night', 'Night'), ('healthplan', 'Health Plan'), ('online_pharmacy', 'Online Pharmacy')], string='Shift',
                              required=True, readonly=True, states={'draft': [('readonly', False)]}, default="day", track_visibility='onchange')
    iAdministrative  = fields.Float(string='Administrative', readonly=True, states={'draft': [('readonly', False)]})
    iOfficeVisit = fields.Float('Office Visit', readonly=True, states={'draft': [('readonly', False)]})
    iVaccinations = fields.Float('Vaccinations', readonly=True, states={'draft': [('readonly', False)]})
    iMedicalServices = fields.Float('Medical Services', readonly=True, states={'draft': [('readonly', False)]})
    iDiagnosticTests = fields.Float('Diagnostic Tests', readonly=True, states={'draft': [('readonly', False)]})
    iImaging = fields.Float('Imaging', readonly=True, states={'draft': [('readonly', False)]})
    iAnesthesia  = fields.Float('Anesthesia', readonly=True, states={'draft': [('readonly', False)]})
    iSurgery = fields.Float('Surgery', readonly=True, states={'draft': [('readonly', False)]})
    iDentistry = fields.Float('Dentistry', readonly=True, states={'draft': [('readonly', False)]})
    iNonMedicalServices = fields.Float('Non-Medical Services', readonly=True, states={'draft': [('readonly', False)]})
    iPharmacy = fields.Float('Pharmacy', readonly=True, states={'draft': [('readonly', False)]})
    iPrescriptionDiets = fields.Float('Prescription Diets', readonly=True, states={'draft': [('readonly', False)]})
    iTaxableDiets = fields.Float('Taxable Diets', readonly=True, states={'draft': [('readonly', False)]})
    iRetailSales = fields.Float('Retail Sales', readonly=True, states={'draft': [('readonly', False)]})
    iBoarding = fields.Float('Boarding', readonly=True, states={'draft': [('readonly', False)]})
    iGrooming = fields.Float('Grooming', readonly=True, states={'draft': [('readonly', False)]})
    idaycamp = fields.Float('Day Camp', readonly=True, states={'draft': [('readonly', False)]})
#     iTotal':fields.function(income_calc_func,string='Gross',readonly=True, states={'draft':[('readonly',False)]},store=True,type='float',method=True),

    itotalnew = fields.Float(compute='_income_calc_func', string='Gross', readonly=True, store=True)
    itotalproductionnew = fields.Float(compute='_total_production_calc_func', string='Production', readonly=True, store=True)


    iaSalesTax = fields.Float('Sales Tax (+)', readonly=True, states={'draft': [('readonly', False)]})
    iaReturnsRefunds = fields.Float('Returns or Refunds  (-)', readonly=True, states={'draft': [('readonly', False)]})
    iaCreditsgift = fields.Float('Client Credits or Gift Cards (-)', readonly=True,
                                  states={'draft': [('readonly', False)]})

    iaMiscellaneous = fields.Float('Misc Acct Adjustments (+)', readonly=True,
                                    states={'draft': [('readonly', False)]})
    #iaQBImport = fields.Float('QBImportAdjustments', readonly=True, states={'draft': [('readonly', False)]})
    #iaQBReconcile = fields.Float('QBReconcilingAdjustments', readonly=True,
                                  #states={'draft': [('readonly', False)]})
    iaDiscountsGeneral = fields.Float('Discounts General (-)', readonly=True,
                                       states={'draft': [('readonly', False)]})
    iParasiticides = fields.Float('Parasiticides', readonly=True, states={'draft': [('readonly', False)]})

    iaDiscountsTeamMember = fields.Float('Team Member (-)', readonly=True,
                                          states={'draft': [('readonly', False)]})
    iaDiscountsApprovedSpecials = fields.Float('Approved Specials  (-)', readonly=True,
                                                states={'draft': [('readonly', False)]})
    iaDiscountsHealthPlan = fields.Float('Wellness Plan (-)', readonly=True,
                                          states={'draft': [('readonly', False)]})

    iaDiscountsHealthPlan_pos = fields.Float(compute='_wellness_plan_func', string='Wellness Plan (+)', readonly=True, store=True)
    #iaDiscountsHealthPlan_pos = fields.Float(string='Wellness Plan (+)', store=True)    
    iaDiscountsDiscretionary = fields.Float('Discretionary (-)', readonly=True,
                                             states={'draft': [('readonly', False)]})
    iaDiscountsNewClient = fields.Float('New Client (Discounts)(-)', readonly=True,
                                         states={'draft': [('readonly', False)]})
    iaRescue = fields.Float('Rescue and Partnerships (-)', readonly=True, states={'draft': [('readonly', False)]})
    iaARClientChargesNew = fields.Float('New Accts Receivables (-)', readonly=True,
                                         states={'draft': [('readonly', False)]})
    iaARClientChargesPaydown = fields.Float('Accts Receivable Paydowns (+)', readonly=True,
                                             states={'draft': [('readonly', False)]})
    iaARClientHeldChecksNew = fields.Float('New Held Checks (-)', readonly=True,
                                            states={'draft': [('readonly', False)]})
    iaARClientHeldChecksDeposited = fields.Float('Held Checks Deposited (+)', readonly=True, states={'draft': [('readonly', False)]})
    iaARClientNet = fields.Float(compute='_net_acc_calc_func', string='Net Accounts Receivable Change', readonly=True, store=True)
    ARClientWriteoff = fields.Float('Accts Receivables Writeoffs (-)', readonly=True, states={'draft': [('readonly', False)]})
    iaTotal = fields.Float(compute='_total_adjustment_calc_func', string='Total Adjustments', readonly=True, store=True)
    payment_pay_later = fields.Boolean('Payment "Pay Later or Group Funds"', readonly=True,
                                        states={'draft': [('readonly', False)]}, default=True)
    dCash = fields.Float('Cash', readonly=True, states={'draft': [('readonly', False)]})
    dChecks = fields.Float('Checks', readonly=True, states={'draft': [('readonly', False)]})
    dCashChecks = fields.Float(compute='_total_cash_calc_func', string='Cash and Checks', readonly=True, store=True)
    dVisa = fields.Float('VISA', readonly=True, states={'draft': [('readonly', False)]})
    dMastercard = fields.Float('Mastercard', readonly=True, states={'draft': [('readonly', False)]})
    visa_mastercard = fields.Float(compute='_visa_master_calc_func', string='Visa and Mastercard', readonly=True, store=True)
    dDiscover = fields.Float('Discover', readonly=True, states={'draft': [('readonly', False)]})
    dAMEX = fields.Float('American Express', readonly=True, states={'draft': [('readonly', False)]})
    dDebitCard = fields.Float('Debit Card', readonly=True, states={'draft': [('readonly', False)]})
    dScratchPay = fields.Float('Scratch Pay', readonly=True, states={'draft': [('readonly', False)]})
    dCareCredit = fields.Float('Care Credit', readonly=True, states={'draft': [('readonly', False)]})
    dMerchant = fields.Float(compute='_merchant_deposits_calc_func', string='Merchant Deposits', readonly=True, store=True)
    credit_total = fields.Float(compute='_credit_total_calc_func', string='Credit Total', readonly=True, store=True)
    dTotal = fields.Float(compute='_total_deposite_calc_func', string='Deposit', readonly=True, store=True,)
    mClientsNew = fields.Float('New Clients (Metrics)', readonly=True, states={'draft': [('readonly', False)]}, help="Clients that have never been in our system, medical only")
    mPatientsNew = fields.Float('New Pets', readonly=True, states={'draft': [('readonly', False)]})
    mVisitsBoarding = fields.Float('Pets Boarded', readonly=True, states={'draft': [('readonly', False)]}, help="Total number of pets currently present in boarding, not what was checked in or checked out")
    mVisitsGroooming = fields.Float('Grooming Appointments', readonly=True,
                                     states={'draft': [('readonly', False)]})
    mVisitsPatient = fields.Float('Medical Visits', readonly=True, states={'draft': [('readonly', False)]}, help="Total visits for only Medical purpose")
    mTransactions = fields.Float('No. of Transactions', readonly=True, states={'draft': [('readonly', False)]})
    mDoctorDays = fields.Float('Doctors Scheduled', readonly=True, states={'draft': [('readonly', False)]})
    day_campers = fields.Float('Day Campers', readonly=True,  states={'draft': [('readonly', False)]}, help="Total number of pets currently in camp each day, including pets in boarding that upgraded to DDC Pet Visits")
    newclient = fields.Integer('New Clients (LView)', readonly=True, states={'draft': [('readonly', False)]})
    petvisit = fields.Integer('Pet Visits (LView)', readonly=True, states={'draft': [('readonly', False)]})
    gross_visit = fields.Float(compute="_gross_visit_func", string='APC ($)', readonly=True, states={'draft': [('readonly', False)]})
    clients_visits = fields.Float(compute='_clients_visits_func', string='NC/V %', readonly=True, states={'draft': [('readonly', False)]})
    #                 invisible fields
    period_id = fields.Many2one('account.period', 'Force Period')
    type = fields.Char('type',default="sale")
    ishistory = fields.Boolean('Is History', default=False)

    ihealth_plan_enroll = fields.Float('Wellness Plan Enrollment', readonly=True,
                                        states={'draft': [('readonly', False)]})
    ihealth_plan_due = fields.Float('Wellness Plan Dues', readonly=True, states={'draft': [('readonly', False)]})
    dHealthPlan = fields.Float('Health Plan', readonly=True, states={'draft': [('readonly', False)]})
    mDentalProphy = fields.Float('Dental Prophys', readonly=True, states={'draft': [('readonly', False)]})
    mHealthPlanEnrolls = fields.Float('Wellness Plan Enrollments', readonly=True, states={'draft': [('readonly', False)]})
    sale_summary_seq_no = fields.Char('SEQ', size=128, readonly=True)
    source = fields.Selection([('manual', 'Manual'), ('feed', 'Feed')], 'Source', required=True, readonly=True, states={'draft': [('readonly', False)]}, default='manual')

    idmove_line_ids = fields.One2many('idmove.line', 'incomedep_ref_id', 'ID Move Lines', readonly=True, copy=True)
    remaining_amount = fields.Float(compute='_calc_difference', string='Value Difference', readonly=True, store=True)
    belongs_to_company = fields.Boolean('Belongs to Company')
    days_open = fields.Char(compute='_calc_days_open', string='Opened Till')

    week = fields.Integer(string='Week')
    month = fields.Integer(string='Month')
    year = fields.Integer(string='Year')
    fiscal_period = fields.Char(compute='_compute_fiscal_month', string='Fiscal Period', readonly=True, store=True)

    fiscal_period_id = fields.Many2one('account.fiscal.period.lines', string = 'Fiscal Month', readonly=True, states={'draft': [('readonly', False)]})
    fiscal_quarter = fields.Char(string = 'Fiscal Quarter')
    fiscal_week = fields.Many2one('account.fiscal.period.week', string='Fiscal Week')
    fiscal_year = fields.Char(string = 'Fiscal Year')
    account_fiscal_periods_year = fields.Many2one('account.fiscal.periods',string = "Fiscal Year")

    @api.multi
    def _calc_week(self,date):
        day_start=1
        date=datetime.strptime(str(date), "%Y-%m-%d")+ timedelta(days=day_start)  
        return date.isocalendar()[1]   
            
    @api.multi
    def _calc_month(self,date):
        day_start=1
        date=datetime.strptime(str(date), "%Y-%m-%d")+ timedelta(days=day_start)
        weekNumber = date.isocalendar()[1]
        if weekNumber<=4:
            month=1
        elif weekNumber<=8:
            month=2
        elif weekNumber<=13:
            month=3
        elif weekNumber<=17:
            month=4
        elif weekNumber<=21:
            month=5
        elif weekNumber<=26:
            month=6
        elif weekNumber<=30:
            month=7
        elif weekNumber<=34:
            month=8
        elif weekNumber<=39:
            month=9
        elif weekNumber<=43:
            month=10
        elif weekNumber<=47:
            month=11
        else:
            month=12
         
        return month
    
    @api.multi
    def _calc_year(self,date):
        day_start=1
        date=datetime.strptime(str(date), "%Y-%m-%d")+ timedelta(days=day_start)
        return date.isocalendar()[0]

#     @api.model
#     def create(self, vals):
#         vals['week']=self._calc_week(vals['date'])
#         vals['month']=self._calc_month(vals['date'])
#         vals['year']=self._calc_year(vals['date'])
#         inc_dep = super(sales_summary, self).create(vals) 
#         return inc_dep    
    
    @api.multi
    def write(self, vals):
        if 'date' in vals:
            vals['week']=self._calc_week(vals['date'])
            vals['month']=self._calc_month(vals['date'])
            vals['year']=self._calc_year(vals['date'])
            fis_period = self.env['account.fiscal.period.lines'].search([('date_start', '<=',vals['date']), ('date_end', '>=',vals['date'])])
            if fis_period:
                vals['fiscal_period_id'] = fis_period.id
                vals['fiscal_quarter'] = fis_period.quarter
                vals['fiscal_year'] = fis_period.year
                vals['account_fiscal_periods_year'] = fis_period.account_fiscal_period_id.id
            fiscal_wk = self.env['account.fiscal.period.week'].search([('account_fiscal_period_id', '=', fis_period.id),('date_start', '<=',vals['date']), ('date_end', '>=',vals['date'])])
            if fiscal_wk:
                vals['fiscal_week'] = fiscal_wk.id
        inc_dep = super(sales_summary, self).write(vals) 
        return inc_dep
    
    @api.multi
    def _calc_days_open(self):
        for loop in self:
            date_format = "%Y-%m-%d"
            created_date = loop.date
            today = datetime.today()
            date_str = str(today)[:10]
            a = datetime.strptime(str(created_date), date_format)
            b = datetime.strptime(str(date_str), date_format)
            delta = b - a
            loop.days_open = str(delta.days)

#\\-------method to print FY month based on date--------
    @api.multi            
    @api.depends('date')
    def _fiscal_month(self):
        for loop in self:
            if loop.date:
                self.fiscal_period = self.env['account.fiscal.period.lines'].search([('date_start', '<=',loop.date), ('date_end', '>=',loop.date)]).name

    ##-------method to compute Value Difference --------##
    @api.depends('itotalproductionnew','dTotal')
    def _calc_difference(self):
        if self.itotalproductionnew and self.dTotal:
            self.remaining_amount = self.dTotal - self.itotalproductionnew
        else:
            self.remaining_amount = 0.0


    ##-------method to compute Gross Value --------##
    @api.depends('iAdministrative','ihealth_plan_due','ihealth_plan_enroll','iOfficeVisit','iVaccinations','iMedicalServices','iDiagnosticTests','iImaging','iAnesthesia','iSurgery','iDentistry','iNonMedicalServices','iPharmacy','iPrescriptionDiets','iTaxableDiets','iRetailSales','iBoarding','iGrooming','iParasiticides','idaycamp')
    def _income_calc_func(self):
        self.itotalnew = self.iAdministrative + self.ihealth_plan_due +  self.ihealth_plan_enroll + self.iOfficeVisit + self.iVaccinations + self.iMedicalServices + self.iDiagnosticTests + self.iImaging + self.iAnesthesia + self.iSurgery + self.iDentistry + self.iNonMedicalServices + self.iPharmacy + self.iPrescriptionDiets + self.iTaxableDiets + self.iRetailSales + self.iBoarding + self.iGrooming + self.iParasiticides + self.idaycamp
   
    @api.depends('iaDiscountsHealthPlan')
    def _wellness_plan_func(self):
        self.iaDiscountsHealthPlan_pos = self.iaDiscountsHealthPlan


    ##-------method to compute Total Adjustments Value --------##
    @api.depends('iaSalesTax','iaReturnsRefunds','iaCreditsgift','iaMiscellaneous','iaDiscountsGeneral','iaDiscountsTeamMember','iaDiscountsApprovedSpecials','iaDiscountsHealthPlan','iaDiscountsDiscretionary','iaDiscountsNewClient','iaRescue','iaARClientChargesNew','iaARClientChargesPaydown','iaARClientHeldChecksNew','iaARClientHeldChecksDeposited','ARClientWriteoff')
    def _total_adjustment_calc_func(self):
        
        #print self.iaSalesTax - self.iaReturnsRefunds - self.iaCreditsgift + self.iaMiscellaneous - self.iaDiscountsGeneral - self.iaDiscountsTeamMember - self.iaDiscountsApprovedSpecials - self.iaDiscountsHealthPlan + self.iaDiscountsHealthPlan_pos - self.iaDiscountsDiscretionary - self.iaDiscountsNewClient - self.iaRescue - self.iaARClientChargesNew + self.iaARClientChargesPaydown - self.iaARClientHeldChecksNew + self.iaARClientHeldChecksDeposited - self.ARClientWriteoff
        self.iaTotal = self.iaSalesTax - self.iaReturnsRefunds + self.iaCreditsgift + self.iaMiscellaneous - self.iaDiscountsGeneral - self.iaDiscountsTeamMember - self.iaDiscountsApprovedSpecials - self.iaDiscountsHealthPlan - self.iaDiscountsDiscretionary - self.iaDiscountsNewClient - self.iaRescue - self.iaARClientChargesNew + self.iaARClientChargesPaydown - self.iaARClientHeldChecksNew + self.iaARClientHeldChecksDeposited - self.ARClientWriteoff
         
    ##-------method to compute production Value --------##
    @api.depends('itotalnew', 'iaTotal')
    def _total_production_calc_func(self):
        self.itotalproductionnew = self.itotalnew + self.iaTotal

    
   
    ##-------method to compute Net Accounts Receivable Change Value --------##
    @api.depends('iaARClientChargesNew', 'iaARClientChargesPaydown', 'iaARClientHeldChecksNew', 'iaARClientHeldChecksDeposited', 'ARClientWriteoff')    
    def _net_acc_calc_func(self):
        self.iaARClientNet = self.iaARClientChargesNew - self.iaARClientChargesPaydown + self.iaARClientHeldChecksNew - self.iaARClientHeldChecksDeposited + self.ARClientWriteoff 
    
    
    ##-------method to compute Visa and Mastercard Value --------##
    @api.depends('dVisa', 'dMastercard')
    def _visa_master_calc_func(self):
        self.visa_mastercard = self.dVisa + self.dMastercard
    
   
    ##-------method to compute Credit Total Value --------##
    @api.depends('dVisa', 'dMastercard', 'dDiscover', 'dDebitCard', 'dCareCredit', 'dAMEX','dScratchPay')    
    def _credit_total_calc_func(self):
        self.credit_total = self.dVisa + self.dMastercard + self.dDiscover + self.dDebitCard + self.dCareCredit + self.dAMEX + self.dScratchPay
    
   
    ##-------method to compute Merchant Deposit Value --------##
    @api.depends('dVisa', 'dMastercard','dDiscover', 'dDebitCard')    
    def _merchant_deposits_calc_func(self):
        self.dMerchant = self.dVisa + self.dMastercard + self.dDiscover + self.dDebitCard
    
   

    @api.depends('dVisa', 'dMastercard','dDiscover', 'dDebitCard')
    def total_cash_calc(self):
        self.dMerchant = self.dVisa + self.dMastercard + self.dDiscover + self.dDebitCard
        
   
    ##-------method to compute Cash and Checks Value --------##
    @api.depends('dCash', 'dChecks')
    def _total_cash_calc_func(self):
        self.dCashChecks = self.dCash + self.dChecks
    
   
    ##-------method to compute Deposit Value --------##
    @api.depends('dCash','dChecks','dVisa','dMastercard','dDiscover','dDebitCard','dCareCredit','dAMEX','dScratchPay')
    def _total_deposite_calc_func(self):
        for i in self:
            i.dTotal = i.dCash + i.dChecks + i.dVisa + i.dMastercard + i.dDiscover + i.dDebitCard + i.dCareCredit + i.dAMEX+i.dScratchPay

   
    @api.depends('itotalnew', 'mVisitsPatient')
    def _gross_visit_func(self):
        
        for i in self:
            if i.mVisitsPatient != 0:
                i.gross_visit = i.itotalnew / i.mVisitsPatient
            else:
                i.gross_visit = 0
    
   

    @api.depends('mClientsNew', 'mVisitsPatient')
    def _clients_visits_func(self):
       
        for i in self:
            if i.mVisitsPatient != 0:
                i.clients_visits = i.mClientsNew / i.mVisitsPatient * 100
            else:
                i.clients_visits = 0
    

    @api.model
    def update_week_month_year(self):
        for line in self.env['sales.summary'].search([('week','=',False),('date','>=','2017-01-01')]):
            line.week=self._calc_week(line.date)
            line.month=self._calc_month(line.date)
            line.year=self._calc_year(line.date)
            
    @api.model
    def create(self, vals):
        vals['week']=self._calc_week(vals['date'])
        vals['month']=self._calc_month(vals['date'])
        vals['year']=self._calc_year(vals['date'])
        company = vals.get('company_id')
        shift = vals.get('shift')
        date = vals.get('date')
        day_start=1
        fis_period = self.env['account.fiscal.period.lines'].search([('date_start', '<=',vals['date']), ('date_end', '>=',vals['date'])])
        if fis_period:
            vals['fiscal_period_id'] = fis_period.id
            vals['fiscal_quarter'] = fis_period.quarter
            vals['fiscal_year'] = fis_period.year
            vals['account_fiscal_periods_year'] = fis_period.account_fiscal_period_id.id
        fiscal_wk = self.env['account.fiscal.period.week'].search([('account_fiscal_period_id', '=', fis_period.id),('date_start', '<=',vals['date']), ('date_end', '>=',vals['date'])])
        if fiscal_wk:
            vals['fiscal_week'] = fiscal_wk.id

        tid = self.env['sales.summary'].search([('company_id','=',company),('date','=',date),('shift','=',shift)])
        if vals.get('ishistory') == True:
            vals.update({'state':'history'})
        if tid:
            raise ValidationError(('Summary already exist for same Location, Date, Shift.'))
        
        return super(sales_summary, self).create(vals)
    
    @api.multi
    def unlink(self):
        for line in self:
            if line.state == 'posted': 
                raise ValidationError(_('You can\'t delete this summary, since the summary is in Posted state'))
            else:
                task_sr = self.env['project.task'].search([('summary_id', '=', line.id)])
                task_sr.unlink()
            return super(sales_summary, self).unlink()




    ##-------Method will triggers when clicks Set to Draft button in daily summary from and it will convert state to draft 
    ## as well as Cancels all Journal Entries, and Sales receipt if exists against Daily Summary.

    @api.multi
    def set_to_draft(self):
        voucher_obj = self.env['account.voucher']
        voucher_ids = voucher_obj.search([('x_sales_summary_id', '=', self.id)])
        account_move_obj = self.env['account.move']
        move_ids = account_move_obj.search([('x_sales_summary_id', '=', self.id),('x_voucher_id', '=', False)])
        if move_ids:
            move_ids.button_cancel()
            move_ids.unlink()

        if voucher_ids:
            for voucher_id in voucher_ids:
                for move_line_id in voucher_obj.move_id:
                    if move_line_id.reconciled:
                        raise ValidationError("Entry cannot set back to 'Draft' mode, since Journal Entries pertaining to this sales summary has already been reconciled with bank statement.  Kindly unreconcile it manually and then try to reset")
                    else:
                        voucher_obj.move_id.button_cancel()
                voucher_id.cancel_voucher()
        
        line_search = self.env['idmove.line'].search([('incomedep_ref_id', '=', self.id)])
        self.idmove_line_ids.unlink()
        self.state = 'draft'
        return True

   
    @api.multi
    def update_fiscal_period_new(self,company_id,date):
            
        account_fiscal_periods_id=account_fiscal_periods_quarterly=account_fiscal_periods_year=account_fiscal_period_week_id=''
        company = self.env['res.company'].search([('id','=',company_id)])
        account_fiscal_periods = self.env['account.fiscal.periods'].search([('calendar_type', '=', company.calendar_type.id)])
        if account_fiscal_periods:
            period = self.env['account.fiscal.period.lines'].search([('account_fiscal_period_id','in',[a.id for a in account_fiscal_periods]),('date_start', '<=', date),('date_end', '>=', date)])
            if period.closing_date_range == True:
                raise UserError(_('Account Period date is expired so you cannot create a record.'))
            if period:
                account_fiscal_periods_id = period.id
                account_fiscal_periods_quarterly = period.quarter            
                account_fiscal_periods_year = period.account_fiscal_period_id.id          
            
            period_week = self.env['account.fiscal.period.week'].search([('account_fiscal_period_week_id','in',[a.id for a in account_fiscal_periods]),('date_start', '<=', date),('date_end', '>=', date)])
            if period_week:
                account_fiscal_period_week_id = period_week.id
        return [account_fiscal_periods_id,account_fiscal_periods_quarterly,account_fiscal_periods_year,account_fiscal_period_week_id]   
    
                
    @api.multi
    def update_payslip_split(self):                  
        sql_query=''
        for rec in self.env['hr.payslip'].search([('hr_period_id.payroll_split','=',True)]):
            for moves in rec.move_ids:
                result=self.update_fiscal_period_new(moves.company_id.id,moves.date)
                newdate=str(datetime.strptime(moves.date, '%Y-%m-%d')+ timedelta(days=-1))[:10]
                sql_query += "update account_move set date='"+str(newdate)+"' , account_fiscal_periods_id="+str(result[0])+" , account_fiscal_periods_quarterly='"+str(result[1])+"' , account_fiscal_periods_year="+str(result[2])+"  , account_fiscal_period_week_id="+str(result[3])+"  where id="+str(moves.id)+";"
                for line in moves.line_ids:
                    sql_query += "update account_move_line set date='"+str(newdate)+"' , account_fiscal_periods_id="+str(result[0])+" , account_fiscal_periods_quarterly='"+str(result[1])+"' , account_fiscal_periods_year="+str(result[2])+"  , account_fiscal_period_week_id="+str(result[3])+"  where id="+str(line.id)+";"
            
        if sql_query!='':  
            self._cr.execute(sql_query)
                    
    @api.multi
    def split_cheque_payment_entries(self):
        sql_query=''
        
        i=0
        for rec in self.env['account.payment.order'].search([('id','=',346),('state', '=', 'processed'),('payment_mode_id.name', '=', 'E-Check')]):
            for bank_line in rec.bank_line_ids:
                account_numbers=[]
                partner_id=''
                print bank_line.payment_line_ids
                for pay_line in bank_line.payment_line_ids: 
                    print pay_line.bank_line_id.id 
                    partner_id=pay_line.partner_id         
                    if pay_line.acc_number_id:
                        account_numbers.append(pay_line.acc_number_id.id)
                    else:
                        account_numbers.append(False)

                if len(set(account_numbers))>1:    
                    if partner_id:                                
                        for moves in self.env['account.move'].search([('partner_id','=',partner_id.id),('payment_order_id', '=', rec.id)]):
                            for lines in moves.line_ids:
                                 if lines.account_id.id==3825:
                                    amount=0
                                    amount_initial=lines.credit
#                                         print set(account_numbers)
                                    for account_number in set(account_numbers):
#                                             print account_number 
                                        inc=0
                                        print set(account_numbers), account_number
                                        for account_line in self.env['account.payment.line'].search([('partner_id','=',partner_id.id),('order_id', '=', rec.id),('acc_number_id', '=', account_number)]):
                                            inc+=1
                                            amount+=account_line.amount_currency
                                            if inc==1:
                                                print inc
                                                sql_query+="Update account_move_line set credit="+str(account_line.amount_currency)+" where id="+str(lines.id)+"; "
                                            else: 
                                                print inc 
                                                sql_query+="""
                                                        INSERT INTO account_move_line(
                                                                     create_date, statement_id, journal_id, currency_id, date_maturity, 
                                                                    user_type_id, partner_id, blocked, analytic_account_id, create_uid, 
                                                                    amount_residual, company_id, credit_cash_basis, amount_residual_currency, 
                                                                    debit, ref, account_id, debit_cash_basis, reconciled, tax_exigible, 
                                                                    balance_cash_basis, write_date, date, write_uid, move_id, product_id, 
                                                                    payment_id, company_currency_id, name, invoice_id, full_reconcile_id, 
                                                                    tax_line_id, credit, product_uom_id, amount_currency, balance, 
                                                                    quantity, expected_pay_date, internal_note, next_action_date, 
                                                                    payment_mode_id, partner_bank_id, bank_payment_line_id, account_fiscal_periods_id, 
                                                                    account_fiscal_period_week_id, account_fiscal_periods_quarterly, 
                                                                    custom_calendar, billpay_id, bill_pay, state, account_fiscal_periods_year)
                                                        SELECT  create_date, statement_id, journal_id, currency_id, date_maturity, 
                                                               user_type_id, partner_id, blocked, analytic_account_id, create_uid, 
                                                               amount_residual, company_id, credit_cash_basis, amount_residual_currency, 
                                                               debit, ref, account_id, debit_cash_basis, reconciled, tax_exigible, 
                                                               balance_cash_basis, write_date, date, write_uid, move_id, product_id, 
                                                               payment_id, company_currency_id, name, invoice_id, full_reconcile_id, 
                                                               tax_line_id, """+str(account_line.amount_currency)+""", product_uom_id, amount_currency, balance, 
                                                               quantity, expected_pay_date, internal_note, next_action_date, 
                                                               payment_mode_id, partner_bank_id, bank_payment_line_id, account_fiscal_periods_id, 
                                                               account_fiscal_period_week_id, account_fiscal_periods_quarterly, 
                                                               custom_calendar, billpay_id, bill_pay, state, account_fiscal_periods_year
                                                        FROM account_move_line
                                                        where id="""+str(lines.id)+""";
                                                    """                                                
                                    if round(amount,2)!=round(amount_initial,2):
                                        print amount, amount_initial
                                        raise ValidationError(('Amount not matched'))
                                        
        print i
                    
        if sql_query!='':  
            print sql_query      
#             self._cr.execute(sql_query)  
                       
    @api.multi
    def update_roundoff(self):
        sql_query="""
            update account_move_line set 
            credit=round( CAST(credit as numeric), 2), 
            debit=round( CAST(debit as numeric), 2) ,
            credit_cash_basis=round( CAST(credit_cash_basis as numeric), 2), 
            debit_cash_basis=round( CAST(debit_cash_basis as numeric), 2) , 
            balance_cash_basis=round( CAST(balance_cash_basis as numeric), 2), 
            balance=round( CAST(balance as numeric), 2)  ;
        """

        if sql_query!='':        
            self._cr.execute(sql_query)  
                
    @api.multi
    def update_unearned_income(self):
        sql_query=''
        for rec in self.env['account.move'].search([('ref', 'like', 'Wellness')]):
            for item in rec.line_ids:
                if item.account_id.name=='Retained Earnings':
                    acc=self.env['account.account'].search([('name', 'like', 'Unearned Income'),('company_id','=',item.company_id.id)])
                    sql_query += "update account_move_line set account_id="+str(acc.id)+" where id="+str(item.id)+";"

        if sql_query!='':        
            self._cr.execute(sql_query)  
            
    @api.multi
    def update_reconciled_true(self):
        sql_query=''
        for line in self.env['sales.summary'].search([('company_id', '=', 53),('state', '=', 'posted')]):  
            for rec in self.env['account.move'].search([('x_sales_summary_id', '=', line.id)]):
                for item in rec.line_ids:
                    if item.full_reconcile_id:
                        item.reconciled=True
    @api.multi
    def update_recon_account_date(self):
        sql_query=''
        for line in self.env['sales.summary'].search([('company_id', 'in', [67,75]),('state', '=', 'posted')]):  
            for rec in self.env['account.move'].search([('x_sales_summary_id', '=', line.id)]):
                if rec.statement_line_id:
                    if rec.statement_line_id.date:

                        newdate=datetime.strptime(str(rec.statement_line_id.date), "%Y-%m-%d").date()
                        result=self.update_fiscal_period_new(line.company_id.id,newdate)
                        print rec, newdate
                        sql_query += "update account_move set date='"+str(newdate)+"' , account_fiscal_periods_id="+str(result[0])+" , account_fiscal_periods_quarterly='"+str(result[1])+"' , account_fiscal_periods_year="+str(result[2])+"  , account_fiscal_period_week_id="+str(result[3])+"  where id="+str(rec.id)+";"
                        for item in rec.line_ids:
#                             print item
                            sql_query += "update account_move_line set date='"+str(newdate)+"' , account_fiscal_periods_id="+str(result[0])+" , account_fiscal_periods_quarterly='"+str(result[1])+"' , account_fiscal_periods_year="+str(result[2])+"  , account_fiscal_period_week_id="+str(result[3])+"  where id="+str(item.id)+";"
#                         print "update account_move set create_date='"+str(rec.statement_line_id.create_date)+".000' and write_date='"+str(rec.statement_line_id.write_date)+".000'  where id="+str(rec.id)+";"
                    
        if sql_query!='':        
            self._cr.execute(sql_query)
            
    @api.multi
    def update_full_recon_account_id(self):
        
        sql_query=''
#         for line in self: 
        for line in self.env['sales.summary'].search([('company_id', 'in', [67,75]),('state', '=', 'posted')]):
            print line 
            care_credit=merc=amex=cash_check=0       
            for rec in self.env['account.move'].search([('x_sales_summary_id', '=', line.id),
                                                        ('journal_id.name', 'like', 'Customer Invoices Journal')]):
                for list in rec.line_ids:
                    if list.ref=='CARE CREDIT' and not list.full_reconcile_id:                        
                        care_credit=list.id
                        
                    if list.ref=='MERCH' and not list.full_reconcile_id:
                        merc=list.id
                    if list.ref=='AMEX' and not list.full_reconcile_id:
                        amex=list.id
                    if list.ref=='CASH&CHECKS' and not list.full_reconcile_id:
                        cash_check=list.id 
                    
            for rec in self.env['account.move'].search([('x_sales_summary_id', '=', line.id),
                                                        ('journal_id.name', 'like', 'Chase Deposit Sweep Journal'),
                                                        ('ref','in',['CARE CREDIT','MERCH','AMEX','CASH&CHECKS'])]):
                try:
                    for list in rec.line_ids:
                        print list.statement_id
                        if rec.ref=='CARE CREDIT' and not list.full_reconcile_id and list.account_id.name=='Account Receivable':
                            if care_credit>0:
                                self.env['account.full.reconcile'].create({
                                    'reconciled_line_ids': [(6, 0, [care_credit,list.id])]
                                    })
                                self.env['account.move.line'].search([('id','=',care_credit)]).reconciled=True
                                list.reconciled=True
                        if rec.ref=='MERCH' and not list.full_reconcile_id and list.account_id.name=='Account Receivable':
                            if merc>0:
                                self.env['account.full.reconcile'].create({
                                    'reconciled_line_ids': [(6, 0, [merc,list.id])]
                                    })
                                self.env['account.move.line'].search([('id','=',merc)]).reconciled=True
                                list.reconciled=True
                        if rec.ref=='AMEX' and not list.full_reconcile_id and list.account_id.name=='Account Receivable':
                            if amex>0:
                                self.env['account.full.reconcile'].create({
                                    'reconciled_line_ids': [(6, 0, [amex,list.id])]
                                    })
                                self.env['account.move.line'].search([('id','=',amex)]).reconciled=True
                                list.reconciled=True
                        if rec.ref=='CASH&CHECKS' and not list.full_reconcile_id and list.account_id.name=='Account Receivable':
                            if cash_check>0:
                                self.env['account.full.reconcile'].create({
                                    'reconciled_line_ids': [(6, 0, [cash_check,list.id])]
                                    })
                                self.env['account.move.line'].search([('id','=',cash_check)]).reconciled=True
                                list.reconciled=True

                except: 
                    raise ValidationError((str(rec)))
            
    @api.multi
    def update_account_id(self):
        
        sql_query=''
        for line in self.env['sales.summary'].search([('company_id', 'in', [67,75]),('state', '=', 'posted')]):        
            for rec in self.env['account.move'].search([('x_sales_summary_id', '=', line.id),('journal_id.name', 'like', 'Customer Invoices Journal')]):
                statement_id=0
                for list in rec.line_ids:
                    if rec.journal_id.id!=list.journal_id.id:
                        
                        print rec.journal_id.id, list.journal_id.id
                        sql_query += "update account_move_line set journal_id="+str(rec.journal_id.id)+" where id="+str(list.id)+";"
        if sql_query!='':        
            self._cr.execute(sql_query)
                        
    @api.multi
    def remove_journal_entries_not_statement(self):        
        sql_query=''
        for line in self.env['sales.summary'].search([('company_id', 'in', [67,75]),('state', '=', 'posted')]):        
            for rec in self.env['account.move'].search([('x_sales_summary_id', '=', line.id),('journal_id.name', 'like', 'Deposit Sweep Journal')]):
                statement_id=0
                i=0
                for list in rec.line_ids:
                    if list.statement_id and not list.full_reconcile_id:
                        statement_id=list.statement_id.id
                    if list.full_reconcile_id:
                        i=1
                if statement_id==0 and i==0:
                    print statement_id
                    rec.button_cancel()
                    rec.unlink()
                             
    @api.multi
    def update_statement_id(self):
        
        sql_query=''
        for line in self.env['sales.summary'].search([('company_id', 'in', [67,75]),('state', '=', 'posted')]):        
            for rec in self.env['account.move'].search([('x_sales_summary_id', '=', line.id),('journal_id.name', 'like', 'Deposit Sweep Journal')]):
                statement_id=0
                for list in rec.line_ids:
                    if list.statement_id:
                        statement_id=list.statement_id.id
                if statement_id>0:
                    for list in rec.line_ids:
                        if not list.statement_id:
                            list.statement_id=statement_id

    @api.multi
    def convert_practices(self):
        
        sql_query=''
        for line in self.env['sales.summary'].search([('company_id', 'in', [67,75]),('state', '=', 'posted')]):
            
            move_id=0
            for rec in self.env['account.move'].search([('x_sales_summary_id', '=', line.id),('journal_id.name', 'like', 'Customer Invoices Journal')]):      
                move_id=rec.id
                for move_line in rec.line_ids:                    
                    if move_line.account_id.name == 'Account Receivable':
                        account_partial_reconciles = self.env['account.partial.reconcile'].search(['|',('credit_move_id', '=',move_line.id),('debit_move_id', '=',move_line.id)])
                        if not account_partial_reconciles:                            
                            sql_query += "Delete from account_move_line where id="+str(move_line.id)+";"
                        else:
                            print line
            if move_id > 0:       
                for rec in self.env['account.move'].search([('x_sales_summary_id', '=', line.id),('journal_id.name', 'like', 'Deposit Sweep Journal')]):                    
                    for move_line in rec.line_ids:
                        if move_line.account_id.name == 'Account Receivable':   
                            print move_line                       
                            sql_query += """
                                INSERT INTO account_move_line (create_date, statement_id, journal_id, currency_id, date_maturity, 
                                    user_type_id, partner_id, blocked, analytic_account_id, create_uid, 
                                    amount_residual, company_id, credit_cash_basis, amount_residual_currency, 
                                    debit, ref, account_id, debit_cash_basis, reconciled, tax_exigible, 
                                    balance_cash_basis, write_date, date, write_uid, move_id, product_id, 
                                    payment_id, company_currency_id, name, invoice_id, full_reconcile_id, 
                                    tax_line_id, credit, product_uom_id, amount_currency, balance, 
                                    quantity, expected_pay_date, internal_note, next_action_date, 
                                    payment_mode_id, partner_bank_id, bank_payment_line_id, account_fiscal_periods_id, 
                                    account_fiscal_period_week_id, account_fiscal_periods_quarterly, 
                                    custom_calendar, billpay_id, bill_pay, state, account_fiscal_periods_year)
                                SELECT create_date, statement_id, journal_id, currency_id, date_maturity, 
                                    user_type_id, partner_id, blocked, analytic_account_id, create_uid, 
                                    amount_residual*-1, company_id, 0.0, amount_residual_currency, 
                                    credit, ref, account_id, debit_cash_basis, reconciled, tax_exigible, 
                                    0.0, write_date, date, write_uid, """+str(move_id)+""", product_id, 
                                    payment_id, company_currency_id, '"""+str(rec.ref)+"""', invoice_id, full_reconcile_id, 
                                    tax_line_id, debit, product_uom_id, amount_currency, balance*-1, 
                                    quantity, expected_pay_date, internal_note, next_action_date, 
                                    payment_mode_id, partner_bank_id, bank_payment_line_id, account_fiscal_periods_id, 
                                    account_fiscal_period_week_id, account_fiscal_periods_quarterly, 
                                    custom_calendar, billpay_id, bill_pay, state, account_fiscal_periods_year
                                FROM account_move_line
                                WHERE id = """+str(move_line.id)+""";
                            """
        if sql_query!='':        
            self._cr.execute(sql_query)        
        return True


    @api.multi
    def compute_overall(self):
        self.convert_practices()
        self.update_statement_id()
        self.remove_journal_entries_not_statement()
        self.update_account_id()
        self.update_full_recon_account_id()
        self.update_recon_account_date()
        
        

    @api.multi
    def compute(self):
        if self.state == 'draft':
            self.env.cr.execute(
                    "SELECT * FROM sales_summary WHERE company_id = %s and date = %s and shift = %s and state=%s",
                    [self.company_id.id, self.date, self.shift, 'posted'])
            fetch_values = self.env.cr.fetchall()
    #                     Date validation
             #---------------------Date validation--------------------------------
            date_now = datetime.now().strftime("%Y-%m-%d")
            selecteddate = time.mktime(time.strptime(self.date, '%Y-%m-%d'))
            todaysdate = time.mktime(time.strptime(date_now, '%Y-%m-%d'))
            days = 60 * 60 * 24
            diffdays = (selecteddate - todaysdate) / days
            hasAttachment = self.env['ir.attachment'].search([('res_model', '=', 'sales.summary'), ('res_id', '=', self.id)])
            
            if diffdays > 15:
                raise ValidationError(("Selected date must be lesser than 15 days away from today's date"))
            
            if (len(fetch_values) >= 1):
                raise ValidationError(('A report has already been submitted for this day. Please contact the corporate office to have it deleted.'))
            
            # ----------To Check Attachment exists or not--------------------------
            if not hasAttachment and self.create_uid and self.source=='manual':
                raise ValidationError(('Please Select an attachment to continue.'))


            #-------List of field names available in Sales Summary Imported data tab ----#

            summary_group_obj = self.env['sale.summary.group']
            summary_config_obj = self.env['sale.summary.config']
            summary_group_search = summary_group_obj.search([])
            
            if summary_group_search:
                inc_summary_group_search = summary_config_obj.sudo().search([('group_code', '=', summary_group_search.id)])
                if inc_summary_group_search:
                    income_fields_list = [i.category_id.name for i in inc_summary_group_search]
                else:
                    raise ValidationError(('No Group is attached with Services.'))
            else:
                raise ValidationError(('No Group is Configured.'))

            for summary in self:
                account_obj = self.env['account.account']
                journal_obj = self.env['account.journal']
                summary.idmove_line_ids.unlink()


                #------- Generating Temporary Journal Entries based on Sales Summary Configuration ---------#

                result = []
                for field in income_fields_list:
                    debit = 0.0
                    credit = 0.0
                    summary_config_search = summary_config_obj.sudo().search([('category_id.name', '=', field)])
                    value_search = self.read([field])[0][field]
                    if summary_config_search and value_search:
                        
                        if value_search > 0 and summary_config_search.debit == 'positive':
                            debit = value_search
                        elif value_search < 0 and summary_config_search.debit == 'negative':
                            debit = abs(value_search)
                        elif value_search > 0 and summary_config_search.credit == 'positive':
                            credit = value_search
                        elif value_search < 0 and summary_config_search.credit == 'negative':
                            credit = abs(value_search)
                            
                        account_sr = account_obj.sudo().search([('name', '=', summary_config_search.account_income_id),('company_id', '=', summary.company_id.id)])
#                         journal = summary.company_id.code+'-'+summary_config_search.journal_id
                        journal = summary_config_search.journal_id
                        journal_sr = journal_obj.sudo().search([('name', 'like', journal),('company_id', '=', summary.company_id.id)])
                        
#                         if summary.company_id.replacement_account_id:  
# #                             account_sr = account_obj.sudo().search([('name', '=', summary.company_id.replacement_account_id.name),('company_id', '=', summary.company_id.id)])
#                             if summary_config_search.journal_id==summary.company_id.replacement_account_id.journal:
#                                 journal = summary.company_id.code+'-'+summary.company_id.replacement_account_id.journal_use_instead                            
#                                 journal_sr = journal_obj.sudo().search([('name', 'like', journal),('company_id', '=', summary.company_id.id)])
                        if not account_sr:
                             raise ValidationError(("There is no account found for "+ str(summary_config_search.product_id.name)+'.....!'))

                        if not journal_sr:
                             raise ValidationError("There is no journal found in sales summary configuration ")
                        if self.iaSalesTax and summary_config_search.category_id.field_description == 'Sales Tax (+)':    
                            partner = self.company_id.local_tax_partner.id
                        else:
                            partner = summary.company_id.partner_id.id
                        result.append((0, 0, {'name': summary_config_search.category_id.field_description,
                            'product_id': summary_config_search.product_id.id,
                            'account_id': account_sr.id,
                            'partner_id': partner,
                            'company_id': summary.company_id.id,
                            'journal_id': journal_sr.id,
                            'amount_total': value_search, 
                            'debit': debit,
                            'credit': credit,
                            'group_code': summary_config_search.group_code.id,
                            'is_group': summary_config_search.is_group,
                            'service_id': summary_config_search.id
                        }))
                if self.sale_summary_seq_no:
                    sales_seq = self.sale_summary_seq_no
                else:
                    sales_seq = self.env['ir.sequence'].next_by_code('sales.summary')
                summary.write({'remaining_amount': self.remaining_amount, 'idmove_line_ids': result ,'state': 'valid','sale_summary_seq_no':sales_seq})

                approved_value = summary.company_id.ss_roundof

                #----- Validations to check Adjustment Account and Round off values mapped in company or not -------#

                if self.remaining_amount:
                    if not summary.company_id.ss_roundof:
                        raise ValidationError(("Adjustment account - round off is not configured in sales summary company profile."
                                          " Please contact your administrator to configure it"))

                    remind_amount=round(self.remaining_amount, 2)
                    if remind_amount >= 0:
                        if remind_amount > approved_value:
                            raise ValidationError((("Write-off value is more than configured value in company")))
                    else:
                        if remind_amount < -(approved_value):
                            raise ValidationError((("Write-off value is more than configured value in company")))


                    if not summary.company_id.ss_adjustments_id.id:
                        raise ValidationError(
                                         (("Adjustment account is not configured in sales summary' company profile."
                                           " Please contact your administrator to configure it")))


                    #---- Generating Adjustment entries and append into Temporary Journal Entries based on company configuration -------#
                    
                    remaining_round = round(self.remaining_amount,3)
                    
                    if remaining_round <= self.company_id.ss_roundof:
                        debit = 0.0
                        credit=0.0
                        for tem_move_line in self.idmove_line_ids:
                            credit = credit+tem_move_line.credit
                            debit = debit+tem_move_line.debit
                        if credit >= debit:
                            debit=-(remind_amount)
                            credit=0.0
                        else:
                            credit = remind_amount
                            debit = 0.0
                        adjustment_value = {
                            'name': 'Adjustment',
                            'credit': credit,
                            'product_id': '',
                            'debit': debit,
                            'account_id': self.company_id.ss_adjustments_id.id,
                            'company_id': self.company_id.id
                        }
                        self.write({'idmove_line_ids': [(0, 0, adjustment_value)]})
            return True

    @api.multi
    def validate(self):
        summary_group_obj = self.env['sale.summary.group']
        summary_group = summary_group_obj.search([])
        account_obj = self.env['account.account']

        # To fetch Task and Task Stage id against DailySummary
        task_obj = self.env['project.task']
        task_sr = task_obj.search([('summary_id', '=', self.id)])
        task_stage_sr = self.env.ref('vitalpet_mypractice.project_stage_data_4').id


        # to get fiscal period

        #company = self.env['res.company'].search([('id','=',vals.get('company_id'))])

        account_fiscal_periods_id = ''
        account_fiscal_period_week_id = ''
        account_fiscal_periods_quarterly = ''



        account_fiscal_periods = self.env['account.fiscal.periods'].search([('calendar_type', '=', self.company_id.calendar_type.id)])
        if account_fiscal_periods:
            period = self.env['account.fiscal.period.lines'].search([('account_fiscal_period_id','in',[a.id for a in account_fiscal_periods]),('date_start', '<=', self.date),('date_end', '>=', self.date)])
            if period.closing_date_range == True:
                raise UserError(_('Account Period date is expired so you cannot create a record.'))
            if period:
                account_fiscal_periods_id = period.id
                account_fiscal_periods_quarterly = period.quarter
                account_fiscal_year = period.account_fiscal_period_id.id
            else:
                account_fiscal_periods_id = ''
                account_fiscal_periods_quarterly = ''
                account_fiscal_year = ''
                
            period_week = self.env['account.fiscal.period.week'].search([('account_fiscal_period_week_id','in',[a.id for a in account_fiscal_periods]),('date_start', '<=', self.date),('date_end', '>=', self.date)])
            if period_week:
                account_fiscal_period_week_id = period_week.id
            else:
                account_fiscal_period_week_id = ''




        journal_obj = self.env['account.journal']
        if self.state == 'valid':
            payment_fields = ['dCashChecks','dAMEX','dCareCredit','dMerchant','iaDiscountsHealthPlan_pos']
            move_obj = self.env['account.move']
            voucher_obj = self.env['account.voucher']
            summary_config_obj = self.env['sale.summary.config']
            ref = ''
            for summary in self:
                for field in payment_fields:
                    debit = 0.0
                    credit = 0.0
                    voucher_result = {}
                    summary_config_search = summary_config_obj.search([('category_id.name', '=', field)])
                    value_search = self.read([field])[0][field]
                    account_sr = account_obj.sudo().search([('name', '=', summary_config_search.account_income_id),('company_id', '=', summary.company_id.id)])
#                     journal = summary.company_id.code+'-'+summary_config_search.journal_id
                    journal = summary_config_search.journal_id
                    journal_sr = journal_obj.sudo().search([('name', 'like', journal),('company_id', '=', summary.company_id.id)])
                    
#                     if summary.company_id.replacement_account_id:  
#                         if summary_config_search.journal_id==summary.company_id.replacement_account_id.journal:
#                             journal = summary.company_id.code+'-'+summary.company_id.replacement_account_id.journal_use_instead                            
#                             journal_sr = journal_obj.sudo().search([('name', 'like', journal),('company_id', '=', summary.company_id.id)])
#                             
                    
                    if summary_config_search.category_id.name == 'iaDiscountsHealthPlan_pos':
                        reference = summary_config_search.category_id.field_description
                    else:
                        reference = summary_config_search.desc or '/'
                    if not account_sr:
                         raise ValidationError(("There is no account found for "+ str(summary_config_search.product_id.name)+'.....!'))

                    if not journal_sr:
                         raise ValidationError(("There is no journal found in sales summary configuration for "+ str(summary_config_search.category_id.field_description)+'.....!'))

#                     if summary_config_search and value_search:
#                         if value_search != 0.0:
#                             # if field == 'dCashChecks':
#                             #     ref = "CASH&CHECKS"
#                             # if field == 'dAMEX':
#                             #     ref = 'AMEX'
#                             # if field == 'dCareCredit':
#                             #     ref = 'CARE CREDIT'
#                             # if field == 'dMerchant':
#                             #     ref = 'MERCH'
#                             # if field == 'dHealthPlan':
#                             #     ref = 'HEALTH PLAN'
#                             if value_search > 0 and summary_config_search.debit == 'positive':
#                                 debit = value_search
#                             elif value_search < 0 and summary_config_search.debit == 'negative':
#                                 debit = abs(value_search)
#                             elif value_search > 0 and summary_config_search.credit == 'positive':
#                                 credit = value_search
#                             elif value_search < 0 and summary_config_search.credit == 'negative':
#                                 credit = abs(value_search)
#                             line_ids = []
#                             line_value = {
#                                     'name': summary_config_search.category_id.field_description,
#                                     'account_id':account_sr.id,
#                                     'partner_id':summary.company_id.partner_id.id,
#                                     'name': summary.name,
#                                     'debit': debit,
#                                     'credit': credit,
#                                     'date': summary.date,
#                                     'date_maturity': summary.date,
#                                     'account_fiscal_periods_year': account_fiscal_year,
#                                     'account_fiscal_periods_id': account_fiscal_periods_id,
#                                     'account_fiscal_period_week_id': account_fiscal_period_week_id,
#                                     'account_fiscal_periods_quarterly': account_fiscal_periods_quarterly,
#                                     }
#                             opp_account_sr = account_obj.sudo().search([('name', '=', summary_config_search.opposite_ac),('company_id', '=', summary.company_id.id)])
#                             opposite_ac = False
#                             if summary_config_search.category_id.name == 'iaDiscountsHealthPlan_pos':
#                                 opp_account_sr = account_obj.sudo().search([('name', '=', 'Account Receivable'),('company_id', '=', summary.company_id.id)])
#                                 opposite_ac = opp_account_sr.id
#                             else:
#                                 opposite_ac = opp_account_sr.id
# 
#                             line_opposite_value = {
#                                     'name': summary_config_search.category_id.field_description,
#                                     'account_id':opp_account_sr.id,
#                                     'partner_id':summary.company_id.partner_id.id,
#                                     'name': summary.name,
#                                     'debit': credit,
#                                     'credit': debit,
#                                     'date': summary.date,
#                                     'date_maturity': summary.date,
#                                     'account_fiscal_periods_year': account_fiscal_year,
#                                     'account_fiscal_periods_id': account_fiscal_periods_id,
#                                     'account_fiscal_period_week_id': account_fiscal_period_week_id,
#                                     'account_fiscal_periods_quarterly': account_fiscal_periods_quarterly,
#                                     }
#                             line_ids.append((0,0,line_value))
#                             line_ids.append((0,0,line_opposite_value))
#                         values = {
#                             'journal_id' : journal_sr.id,
#                             'date' : summary.date,
#                             'ref' : reference,
#                             'company_id' : summary.company_id.id,
#                             'line_ids' : line_ids,
#                             'x_sales_summary_id' : summary.id,
#                             'account_fiscal_periods_year': account_fiscal_year,
#                             'account_fiscal_periods_id': account_fiscal_periods_id,
#                             'account_fiscal_period_week_id': account_fiscal_period_week_id,
#                             'account_fiscal_periods_quarterly': account_fiscal_periods_quarterly,
#                             
#                             }
#                         account_move_id = self.env['account.move'].create(values)
#                         print account_move_id,'-'
#                         account_move_id.post()

                result = []
                line_ids = []
                for line in summary.idmove_line_ids:
                    if not line.is_group:
                        if line.name == 'Sales Tax (+)':
                            partner = self.company_id.local_tax_partner.id
                        else:
                            partner = summary.company_id.partner_id.id    
                        
                        credit_val=debit_val=0
                        
                        if round(line.debit,2)<0 or round(line.credit,2)<0 :
                            debit_val=round(abs(line.credit),2)
                            credit_val=round(abs(line.debit),2)
                        else:
                            debit_val=round(line.debit,2)
                            credit_val=round(line.credit,2)

                        line_value = {
                            'account_id':line.account_id.id,
                            'company_id':line.company_id.id,
                            'product_id':line.product_id.id,
                            'partner_id':partner,
                            'name': summary.name,
                            'debit': debit_val,
                            'credit': credit_val,
                            'date': summary.date,
                            'date_maturity': summary.date,
                            'account_fiscal_periods_year': account_fiscal_year,
                            'account_fiscal_periods_id': account_fiscal_periods_id,
                            'account_fiscal_period_week_id': account_fiscal_period_week_id,
                            'account_fiscal_periods_quarterly': account_fiscal_periods_quarterly,
    
                            }
                        line_ids.append((0,0,line_value))
                opp_idmove_line_id = summary.idmove_line_ids.filtered(lambda s: s.is_group)
                if opp_idmove_line_id:
                    # raise ValidationError(("There is no grouping entry found."))
                    values = {
                        'journal_id' : opp_idmove_line_id.journal_id.id,
                        'date' : summary.date,
                        'ref' : 'Daily Summary - Manual',
                        'company_id' : summary.company_id.id,
                        'line_ids' : line_ids,
                        'x_sales_summary_id' : summary.id,
                        'partner_id': summary.company_id.partner_id.id,
                        'account_fiscal_periods_year': account_fiscal_year,
                        'account_fiscal_periods_id': account_fiscal_periods_id,
                        'account_fiscal_period_week_id': account_fiscal_period_week_id,
                        'account_fiscal_periods_quarterly': account_fiscal_periods_quarterly,
                        }
                    account_move_id = self.env['account.move'].create(values)
                   
                    account_move_id.post()

                    for lines in summary.idmove_line_ids:
                        if not lines.is_group:
                            if lines.credit:
                                if lines.name == 'Adjustment':
                                    result.append((0, 0, {'product_id': '', 
                                    'name': lines.name,
                                    'account_id': summary.company_id.ss_adjustments_id.id,
                                    'quantity': 1,
                                    'price_unit':round(lines.credit,2)
                                    }))
                                else:
                                    result.append((0, 0, {'product_id': lines.product_id.id or '', 
                                        'name': lines.name,
                                        'account_id': lines.account_id.id,
                                        'quantity': 1,
                                        'price_unit': round(lines.credit,2)
                                        }))
                    summary_config_ref = summary_config_obj.search([('is_group', '=', True)])
                    voucher_result1 = {
                    'name': 'Daily Summary',
                    'reference': summary_config_ref.desc or '/',
                    'pay_now': 'pay_now',
                    'journal_id': opp_idmove_line_id.journal_id.id,
                    'account_id': opp_idmove_line_id.account_id.id,
                    'company_id': summary.company_id.id,
                    'date': summary.date,
                    'partner_id': summary.company_id.partner_id.id,
                    'x_sales_summary_id': summary.id,
                    'voucher_type': 'sale',
                    'line_ids': result,
                    'move_id': account_move_id.id
                    }
                    payment_move_id = voucher_obj.create(voucher_result1)
                    account_move_id.write({'x_voucher_id': payment_move_id.id})
                    payment_move_id.proforma_voucher()
                    payment_move_id.write({'state':'posted','number': opp_idmove_line_id.journal_id.sequence_id.with_context(ir_sequence_date=self.date).next_by_id()})
                    self.state = 'posted'
                    
                    # To move task state to completed state against DailySummary  
                    task_sr.write({'stage_id': task_stage_sr, 'completed_date':datetime.now().strftime("%Y-%m-%d")})
                
            return True




    # Open Journals against Summary 
    
    @api.multi    
    def get_open_journal(self,context=None):
        
        ctx = (context or {}).copy()
        voucher_ids=self.env['account.move'].search([('x_sales_summary_id', '=', self.id)])
        return {
            'name': _('Journals'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('x_sales_summary_id', '=', self.id)],
            'context': ctx,
        }
    

    @api.multi
    def action_create_sale_summary(self):
        summary_obj=self.env['sales.summary']
        task_obj = self.env['project.task']
        project_obj = self.env['project.project']
        project_tag = self.env['project.tags']
        project_tag_sr = project_tag.search([('name', '=', 'Daily Summary')])
        # today_dt = datetime.datetime.now().date()
        today_dt= datetime.now() + timedelta(days=-1)
        tomorrow = datetime.now().date()
        yeterday = datetime.now() + timedelta(days=-2)

        tomorrow_dt = str(tomorrow)[:10]
        today_dt_format = str(today_dt)[:10]
        yeterday_dt = str(yeterday)[:10]
        vals={}
        my_practice_obj = self.env['res.company'].search([('daily_report', '=', True),('source', '=', 'manual')])
        if my_practice_obj:
            for line in my_practice_obj:
                project_sr = project_obj.search([('name', '=', 'My Practice'),('company_id', '=', line.id)])
                task_todo_sr = self.env['project.task.type'].search([('name', '=', 'To Do')])
                less_week_st = self.env['project.task.type'].search([('name', '=', 'Overdue < 1 Week')])
                less2week_st = self.env['project.task.type'].search([('name', '=', 'Overdue > 1 Week')])
                # move task to < week
                s = datetime.now() + timedelta(days=-7)
                less_week = str(s)[:10]

                last2week = s + timedelta(days=-7)
                last2week_str = str(last2week)[:10]


                task_sr = task_obj.search([('project_id', '=', project_sr.id),('company_id', '=', line.id), ('stage_id', '=', task_todo_sr.id),('date_deadline', '<=', yeterday_dt), ('date_deadline', '>=', less_week)])
                if task_sr:
                    for loop in task_sr:
                        loop.write({'stage_id':less_week_st.id})
 
 
                task2week_sr = task_obj.search([('project_id', '=', project_sr.id),('company_id', '=', line.id), ('stage_id', '=', less_week_st.id),('date_deadline', '<=', less_week), ('date_deadline', '>=', last2week_str)])
                if task2week_sr:
                    for loop in task2week_sr:
                        loop.write({'stage_id':less2week_st.id})
                
                now = str(today_dt.strftime("%A"))
                    
                shift_dic = {
                            'Sunday': line.sunday_shift, 'Monday': line.monday_shift, 'Tuesday': line.tuesday_shift, 
                            'Wednesday':line.wednesday_shift, 'Thursday': line.thursday_shift, 'Friday':line.friday_shift ,
                            'Saturday': line.saturday_shift
                            }

                name_summary = str(line.code)+" -Daily Report "+str(today_dt_format)+" Day"
                project_obj_sr = self.env['project.task'].search([('name','=', name_summary)])
                if project_obj_sr:
                    deadline_date = datetime.now()
                    date_start_plus_two = datetime.strptime(project_obj_sr.date_start[:10], '%Y-%m-%d') + timedelta(days=2)
                    
                    if deadline_date > date_start_plus_two:
                        task_todo_sr = self.env['project.task.type'].search([('name', '=', 'Overdue < 1 Week')])
                        project_obj_sr.write({'stage_id':task_todo_sr.id})
                elif line.Wednesday and now == 'Wednesday' or line.Thursday and now == 'Thursday' or  line.Friday and now == 'Friday' or line.Saturday and now == 'Saturday' or line.Sunday and now == 'Sunday' or line.Monday and now == 'Monday' or line.Tuesday and now == 'Tuesday':
                    if shift_dic[now] == "0": 
                        vals = {  
                                'company_id': line.id,
                                'date':today_dt_format,
                                'shift': 'day',
                                'source': line.source,
                               }
                        sales_summary_count = self.env['sales.summary'].search_count([('date','=', today_dt_format),('shift','=', 'day'),('company_id','=', line.id)])
                        if sales_summary_count==0:
                            sum_id=summary_obj.create(vals)
                            vals_task = {
                                    'name': name_summary,
                                    'project_id': project_sr.id,
                                    'startdate_date': today_dt,
                                    'summary_id' : sum_id.id,
                                    'date_deadline': today_dt,
                                    'company_id': line.id,
                                    'tag_ids': [(6, 0, [project_tag_sr.id])],
                                    'stage_id': task_todo_sr.id,
                                    'user_id': line.manager_user_id.id,
                                    'mypractice': True
                                }
                            task_obj.create(vals_task)
                        
                        
                    elif shift_dic[now] == "1": 
                        vals = {  
                                'company_id': line.id,
                                'date': today_dt_format,
                                'shift': 'night',
                                'source': line.source,
                               }
                        sales_summary_count = self.env['sales.summary'].search_count([('date','=', today_dt_format),('shift','=', 'night'),('company_id','=', line.id)])
                        if sales_summary_count==0:
                            sum_id=summary_obj.create(vals)
                            vals_task = {
                                    'name': str(line.code)+" -Daily Report "+str(today_dt_format)+" Night",
                                    'project_id': project_sr.id,
                                    'startdate_date': today_dt,
                                    'summary_id' : sum_id.id,
                                    'company_id': line.id,
                                    'date_deadline': today_dt,
                                    'tag_ids': [(6, 0, [project_tag_sr.id])],
                                    'stage_id': task_todo_sr.id,
                                    'user_id': line.manager_user_id.id,
                                    'mypractice': True
                                }
                            task_obj.create(vals_task)
                        
                    else:
                        vals = {  
                            'company_id': line.id,
                            'date': today_dt_format,
                            'shift': 'day',
                            'source': line.source,
                           }     
                        sales_summary_count = self.env['sales.summary'].search_count([('date','=', today_dt_format),('shift','=', 'day'),('company_id','=', line.id)])
                        if sales_summary_count==0:               
                            sum_id = summary_obj.create(vals)
                            vals_task = {
                                    'name': str(line.code)+" -Daily Report "+str(today_dt_format)+" Day",
                                    'summary_id' : sum_id.id,
                                    'startdate_date': today_dt,
                                    'project_id': project_sr.id,
                                    'company_id': line.id,
                                    'date_deadline': today_dt,
                                    'tag_ids': [(6, 0, [project_tag_sr.id])],
                                    'stage_id': task_todo_sr.id,
                                    'user_id': line.manager_user_id.id,
                                    'mypractice': True
                                }
                            task_obj.create(vals_task)
                        vals = {  
                            'company_id': line.id,
                            'date': today_dt_format,
                            'shift': 'night',
                            'source': line.source,
                           }    
                        sales_summary_count = self.env['sales.summary'].search_count([('date','=', today_dt_format),('shift','=', 'night'),('company_id','=', line.id)])
                        if sales_summary_count==0:                   
                            sum_id = summary_obj.create(vals)   
                            vals_task = {
                                    'name': str(line.code)+" -Daily Report "+str(today_dt_format)+" Night",
                                    'summary_id' : sum_id.id,
                                    'startdate_date': today_dt,
                                    'project_id': project_sr.id,
                                    'company_id': line.id,
                                    'date_deadline': today_dt,
                                    'tag_ids': [(6, 0, [project_tag_sr.id])],
                                    'stage_id': task_todo_sr.id,
                                    'user_id': line.manager_user_id.id,
                                    'mypractice': True
                                
                                }
                            task_obj.create(vals_task)       
        self.daily_report_overdue_complete     
        return True

    @api.multi
    def action_sale_summary_feed(self):
        feed_obj = self.env['sales.summary'].search([('date', '=', (datetime.now() + timedelta(days=-2))),('source', '=', 'feed'),('state','in',['draft','valid'])])
        for line in feed_obj:
            print line.date
            if line.remaining_amount >= 0:
                if not line.remaining_amount > line.company_id.ss_roundof:
                    line.compute()
                    line.validate()
            else:
                if not line.remaining_amount < -(line.company_id.ss_roundof):
                    line.compute()
                    line.validate()        
        return True

    @api.multi
    def daily_report_overdue_complete(self):
        task_complete_sr = self.env['project.task.type'].search([('name', '=', 'Complete')])
        task_overdue_one = self.env['project.task.type'].search([('name', '=', 'Overdue > 1 Week')])
        task_overdue_less_one = self.env['project.task.type'].search([('name', '=', 'Overdue < 1 Week')])
        task_cancel_obj = self.env['project.task.type'].search([('name', '=', 'Cancelled')])
        project_tag_sr = self.env['project.tags'].search([('name', '=', 'Daily Summary')])
        task_summary_obj = self.env['project.task'].search([('mypractice','=',True),('stage_id','in',(task_overdue_one.id,task_overdue_less_one.id)),('tag_ids','=',project_tag_sr.id)])
        for summary_task in task_summary_obj:
            if summary_task.summary_id:
                if summary_task.summary_id.state == 'posted':
                    summary_task.write({'stage_id':task_complete_sr.id})
        daily_summary_obj = self.env['project.task'].search([('mypractice','=',True),('stage_id','=',task_overdue_one.id),('tag_ids','=',project_tag_sr.id)])
        for summary in daily_summary_obj:
            if not summary.summary_id:
                summary.write({'stage_id':task_cancel_obj.id})
                summary.completed_date = datetime.now().date()


    @api.multi
    def action_update_fiscal_je(self):
        sql_query='update hr_employee set birth_country=null;update hr_employee_onboarding set birth_country=null;'
        if sql_query!='':
            self._cr.execute(sql_query)
#         expense_sheets = self.env['hr.expense.sheet'].search([('state','=', 'post'),('id','in',[449,438,439,420,407,406,401,397,396,390,385,379,373,370,391,376,347,337,336,327,313,309,307,304,302,422,319,300,285,280,275,270,262,254,251,228,248,182,340,321,265,253,214,211,209,188,184,175,161,158,69,51,250,210,163,139,56,46,45,43,37,152,61,60,41])])
#         print expense_sheets
        
#         sql_query=""
#         for expense_sheet in expense_sheets:
#             i=0
#             for move in expense_sheet.account_move_id:
#                 for line in move.line_ids:
#                     print line
#                     if not line.partner_id:
#                         print expense_sheet
#                         print ''
#                         if expense_sheet.employee_id.credit_card_id:
#                             print expense_sheet.employee_id
#                             sql_query +="update account_move set partner_id = "+str(expense_sheet.employee_id.credit_card_id.id)+" where id = "+str(move.id)+";"
#                             sql_query +="update account_move_line set partner_id = "+str(expense_sheet.employee_id.credit_card_id.id)+" where id = "+str(line.id)+";"
#     #                         line.partsner_id = expense_sheet.employee_id.credit_card_id.id
#                             print line.move_id
#                             print line
# #         sql_query ="""update account_asset_category set method_end = NULL where id = 2749"""
#         if sql_query!='':
#             self._cr.execute(sql_query)
#         
        
#         for lines in self.env['gl.payroll.mapping'].search([]):    
#             lines.credit_product=lines.credit_product_id.id
#             lines.debit_product=lines.debit_product_id.id
#         for lines in self.env['gl.payroll.mapping'].search([]):    
#             credit_pro_nil = self.env['product.product'].search([('name' , 'ilike' , lines.credit_product)])
#             if credit_pro_nil:
#                 lines.credit_product_id=credit_pro_nil.id
#             debit_pro_nil = self.env['product.product'].search([('name' , 'ilike' , lines.debit_product)])
#             if debit_pro_nil:
#                 lines.debit_product_id=debit_pro_nil.id
                 
#         for lines in self.env['gl.payroll.mapping'].search([]):    
#             credit_pro_nil = self.env['product.product'].search([('name' , 'ilike' , lines.credit_product)])
#             if not credit_pro_nil:
#                 raise UserError("Please Enter a valid Credit Product --"+str(lines.debit_product))
#             debitt_pro_nil = self.env['product.product'].search([('name' , 'ilike' , lines.debit_product)])
#             if not debitt_pro_nil:
#                 raise UserError("Please Enter a valid Debit Product --"+str(lines.debit_product))
#         payment_orders = self.env['account.payment.order'].search([('payment_mode_id','=',4),('state','=','processed')])
#         for payment_order in payment_orders:
#             for rec in payment_order.move_ids:
#                 sql_query = ''
#                 # if rec.date != payment_order.date_generated:
#                 newdate = payment_order.date_generated
#                 result=self.update_fiscal_period_new(self.env.user.company_id.id,newdate)
#                 print rec, newdate
#                 sql_query += "update account_move set date='"+str(newdate)+"' , account_fiscal_periods_id="+str(result[0])+" , account_fiscal_periods_quarterly='"+str(result[1])+"' , account_fiscal_periods_year="+str(result[2])+"  , account_fiscal_period_week_id="+str(result[3])+"  where id="+str(rec.id)+";"
#                 for item in rec.line_ids:
# #                             print item
#                     sql_query += "update account_move_line set date='"+str(newdate)+"' , date_maturity='"+str(newdate)+"' , account_fiscal_periods_id="+str(result[0])+" , account_fiscal_periods_quarterly='"+str(result[1])+"' , account_fiscal_periods_year="+str(result[2])+"  , account_fiscal_period_week_id="+str(result[3])+"  where id="+str(item.id)+";"
#                 if sql_query!='':        
#                     self._cr.execute(sql_query)
#                     self._cr.commit()
#         sql_query ="""delete from budget_consolidate_monthly where name='Revenue' and type!='revenue'"""
#         self._cr.execute(sql_query)
#         assets = self.env['account.asset.depreciation.line'].search([('move_id','!=', False)])

#         print assets
#         for asset_Line in assets:
#             print asset_Line
#             print  asset_Line.move_id.line_ids
#             for move_line in asset_Line.move_id.line_ids:
#                 print move_line.debit
#                 print move_line.product_id

#                 if move_line.debit > 0.0 and not move_line.product_id:
#                     move_line.product_id = asset_Line.asset_id.category_id.product_id.id


                         
        #             partner.write({'is_cron': True})
        
        
#         payment_orders = self.env['account.payment.order'].search([('payment_mode_id','=',4),('state','=','processed')])
#         for payment_order in payment_orders:
#             for rec in payment_order.move_ids:
#                 sql_query = ''
#                 # if rec.date != payment_order.date_generated:
#                 newdate = payment_order.date_generated
#                 result=self.update_fiscal_period_new(self.env.user.company_id.id,newdate)
#                 print rec, newdate
#                 sql_query += "update account_move set date='"+str(newdate)+"' , account_fiscal_periods_id="+str(result[0])+" , account_fiscal_periods_quarterly='"+str(result[1])+"' , account_fiscal_periods_year="+str(result[2])+"  , account_fiscal_period_week_id="+str(result[3])+"  where id="+str(rec.id)+";"
#                 for item in rec.line_ids:
# #                             print item
#                     sql_query += "update account_move_line set date='"+str(newdate)+"' , date_maturity='"+str(newdate)+"' , account_fiscal_periods_id="+str(result[0])+" , account_fiscal_periods_quarterly='"+str(result[1])+"' , account_fiscal_periods_year="+str(result[2])+"  , account_fiscal_period_week_id="+str(result[3])+"  where id="+str(item.id)+";"
#                 if sql_query!='':        
#                     self._cr.execute(sql_query)
#                     self._cr.commit()
                    
#         payment_orders = self.env['account.payment.order'].search([('payment_mode_id','=',4),('state','=','processed'),('is_cron','=', False)],limit = 5, order = "id asc")
#         print payment_orders
#         i = 0
#         for payment_order in payment_orders:
#             i+=1
#             try:
#                 print payment_order
#                 print i
#                 print "action cancel"
#                 payment_order.action_cancel()
#                 print "cancel2draft"
#                 payment_order.cancel2draft()
#                 print "draft2open"

#                 payment_order.draft2open()
#                 print "payment_processed"

#                 payment_order.payment_processed()

        # payment_orders = self.env['account.payment.order'].search([('payment_mode_id','=',4),('state','=','processed'),('is_cron','=', False)],limit = 5, order = "id asc")
        # print payment_orders
        # i = 0
        # for payment_order in payment_orders:
        #     i+=1
        #     try:
        #         print payment_order
        #         print i
        #         print "action cancel"
        #         payment_order.action_cancel()
        #         print "cancel2draft"
        #         payment_order.cancel2draft()
        #         print "draft2open"

        #         payment_order.draft2open()
        #         print "payment_processed"

        #         payment_order.payment_processed()

        #         payment_order.is_cron = True
        #         self.env._cr.commit()
        #     except:
        #         print payment_order
        #         print "error in payment order"+str(payment_order.id)


        # sql_query = "update res_partner a set ach_form = (select signature_request_id from signature_request_item where partner_id = a.id and state = 'completed' order by id desc limit 1 ) where a.ach_form is NULL"
        # self._cr.execute(sql_query)
        # self._cr.commit()

        # sql_query2 = "update res_partner a set ach_form = (select signature_request_id from signature_request_item where partner_id = a.id order by id desc limit 1 ) where a.ach_form is NULL"
        # self._cr.execute(sql_query2)
        # self._cr.commit()


#         sql_query = "delete from res_partner_bank where bank_id is null and id not in (select bank_account_id from account_journal where bank_account_id is not null) and id not in (select partner_bank_id from account_payment_line where partner_bank_id is not null)"
#         self._cr.execute(sql_query)
#         self._cr.commit()
# 
# 
# 
#         daily_partner = self.env['res.partner'].search([('bank_routing','!=', '')])
#         for daily in daily_partner:
#             for partner in daily:
#                 if partner.bank_routing:
#                     res_bank = self.env['res.bank'].search([('bic', '=', partner.bank_routing)])
#                     if res_bank:
#                         partner.bank_name = res_bank.name
#                     else:
#                         if partner.bank_name:
#                             res_bank = self.env['res.bank'].create({
#                                 'name': partner.bank_name,
#                                 'bic':partner.bank_routing
#                                 }) 
#                         else:
#                             res_bank = self.env['res.bank'].create({
#                                 'name': 'undefined bank name' + ":" + partner.bank_routing,
#                                 'bic':partner.bank_routing
#                                 }) 
#                         
#                         partner.bank_name = res_bank.name
#                     if partner.bank_account:
#                         update_bank = self.env['res.partner.bank'].search([('acc_number', '=', partner.bank_account)])
#                         print update_bank
#                         if not update_bank:
#                             self.env['res.partner.bank'].create({
#                                 'acc_number':partner.bank_account,
#                                 'bank_id':res_bank.id,
#                                 'partner_id':partner.id,
#                                 'company_id':partner.company_id.id
#                                 })
#                         update_bank = self.env['res.partner.bank'].search([('acc_number', '=', partner.bank_account),('bank_id', '=', False)])
#                         print partner.name
#                         if update_bank:
#                             update_bank.bank_id = res_bank.id

        

    @api.multi
    def action_update_fiscal(self):
        invoice_obj = self.env['account.invoice'].search([('id','in',[45726])])
        if invoice_obj:
            for account_move in invoice_obj:
                move_id = account_move.move_id.id
                move_obj = self.env['account.move'].search([('id','=',move_id)])
                sql_query3 = """DELETE FROM account_invoice where id = %s"""
                params3 = (account_move.id,)
                self._cr.execute(sql_query3, params3)  
                for line_id in move_obj.line_ids:
                    account_partial_reconciles = self.env['account.partial.reconcile'].search(['|',('credit_move_id', '=',line_id.id),('debit_move_id', '=',line_id.id)])
                    for account_partial_reconcile in account_partial_reconciles:
                        sql_query1 = """DELETE FROM account_partial_reconcile where credit_move_id = %s or debit_move_id = %s"""
                        params1 = (account_partial_reconcile.id,)
                        self._cr.execute(sql_query1, params1)
                    account_payment_lines = self.env['account.payment.line'].search([('move_line_id', '=', line_id.id)])
                    for account_payment_line in account_payment_lines:
                        sql_query2 = """DELETE FROM account_payment_line where id = %s"""
                        params2 = (account_payment_line.id,)
                        self._cr.execute(sql_query2, params2)
                for line_id in move_obj:
                    sql_query3 = """DELETE FROM account_move where id = %s"""
                    params3 = (line_id.id,)
                    self._cr.execute(sql_query3, params3)
   
                
        return True
    
        
    @api.multi
    def bills_status_change(self):
        i=j=k=0
        invoice_ids=self.env['account.invoice'].search([('billpay_id','=',None),('state','in',['open']),('company_id','!=',74)])
        print 12321, len(invoice_ids), invoice_ids
        
        for invoice in invoice_ids:  
            if invoice.move_id:        
                for line in invoice.move_id.line_ids: 
                    if line.account_id.name=='Accounts Payable' and  line.billpay_id:
                        i+=1
                        if line.billpay_id.state=='paid':
                            j+=1
                            payment_lines=self.env['account.payment.line'].search([('invoice_id','=',invoice.id),('order_id.state','not in',['processed'])])
                            if payment_lines:
                                for order in payment_lines:   
                                    k+=1
                                    order.unlink()
                            self._cr.execute("update account_invoice set state='paid' where id="+str(invoice.id))
                            
                    elif line.account_id.name=='Accounts Payable':
                        i+=1
                        payment_lines=self.env['account.payment.line'].search([('communication','=',invoice.reference),('order_id.state','not in',['processed'])])
                        for order in payment_lines:
                                k+=1
                                order.unlink()
                        
                        self._cr.execute("update account_invoice set state='paid' where id="+str(invoice.id))

#                     if line.account_id.name=='Accounts Payable' and line.billpay_id:
#                         print line.billpay_id.state,'--'
#                         if line.billpay_id.state=='paid':
#                             payment_lines=self.env['account.payment.line'].search([('communication','=',invoice.reference),('order_id.state','not in',['processed','cancel'])])
#                             for order in payment_lines:    
#                                                           
#                                 print order, len(payment_lines), order.order_id.state
# #                                 if len(payment_lines)>1:                            
# #                                     print invoice, invoice.move_id, line, line.billpay_id
# #                                 i+=1
#                                 print i
#                                 order.unlink()
#                             invoice.state='paid'
#                       
#                     elif line.account_id.name=='Accounts Payable' and not line.billpay_id:
#                         payment_lines=self.env['account.payment.line'].search([('communication','=',invoice.reference),('order_id.state','not in',['processed','cancel'])])
#                         for order in payment_lines:    
#                                                           
#                                 print order, len(payment_lines), order.order_id.state
# #                                 if len(payment_lines)>1:                            
# #                                     print invoice, invoice.move_id, line, line.billpay_id
#                                 i+=1
#                                 print i
#                                 order.unlink()
                         
        print i,j,k
        
    @api.multi
    def remove_production_date_missed(self):
        
#         self._cr.execute("""delete from hr_production_line hpl 
#             WHERE  hpl.date not between (select (select date_start from hr_period hr where hr.id=hp.period_id ) from hr_production hp where hp.id=hpl.production_line_id )
#             AND    (select (select date_stop from hr_period hr where hr.id=hp.period_id ) from hr_production hp where hp.id=hpl.production_line_id )
#             """)
        self._cr.execute("""update hr_contract_line_log set is_approved=true """)
      
    @api.multi
    def jounal_entry_fiscal_entry_error(self):        
        self.env.cr.execute("""select id from account_invoice  where 
(account_fiscal_periods_id=374  and date not between '2017-01-01' and '2017-01-28')
or (account_fiscal_periods_id=375  and date not between '2017-01-29' and '2017-02-25')
or (account_fiscal_periods_id=376  and date not between '2017-02-26' and '2017-04-01')
or (account_fiscal_periods_id=377  and date not between '2017-04-02' and '2017-04-29')
or (account_fiscal_periods_id=378  and date not between '2017-04-30' and '2017-05-27')
or (account_fiscal_periods_id=379  and date not between '2017-05-28' and '2017-07-01')
or (account_fiscal_periods_id=380  and date not between '2017-07-02' and '2017-07-29')
or (account_fiscal_periods_id=381  and date not between '2017-07-30' and '2017-08-26')
or (account_fiscal_periods_id=382  and date not between '2017-08-27' and '2017-09-30')
or (account_fiscal_periods_id=383  and date not between '2017-10-01' and '2017-10-28')
or (account_fiscal_periods_id=384  and date not between '2017-10-29' and '2017-11-25')
or (account_fiscal_periods_id=385  and date not between '2017-11-26' and '2017-12-30')
or (account_fiscal_periods_id=794 and date not between '2017-12-31' and '2018-01-27')
or (account_fiscal_periods_id=795 and date not between '2018-01-28' and '2018-02-24')
or (account_fiscal_periods_id=796 and date not between '2018-02-25' and '2018-03-31')
or (account_fiscal_periods_id=797 and date not between '2018-04-01' and '2018-04-28')
or (account_fiscal_periods_id=798 and date not between '2018-04-29' and '2018-05-26')
or (account_fiscal_periods_id=799 and date not between '2018-05-27' and '2018-06-30')
or (account_fiscal_periods_id=800 and date not between '2018-07-01' and '2018-07-28')
or (account_fiscal_periods_id=801 and date not between '2018-07-29' and '2018-08-25')
or (account_fiscal_periods_id=802 and date not between '2018-08-26' and '2018-09-29')
or (account_fiscal_periods_id=803 and date not between '2018-09-30' and '2018-10-27')
or (account_fiscal_periods_id=804 and date not between '2018-10-28' and '2018-11-24')
or (account_fiscal_periods_id=805 and date not between '2018-11-25' and '2018-12-29')
or (account_fiscal_periods_id=805 and date not between '2018-11-25' and '2018-12-29')
or (account_fiscal_periods_id=805 and date not between '2018-11-25' and '2018-12-29')
or (account_fiscal_periods_id=805 and date not between '2018-11-25' and '2018-12-29')
or (account_fiscal_periods_id=1478 and date not between '2018-12-30' and '2019-01-26')
or (account_fiscal_periods_id=1479 and date not between '2019-01-27' and '2019-02-23')
or (account_fiscal_periods_id=1480 and date not between '2019-02-24' and '2019-03-30')
or (account_fiscal_periods_id=1481 and date not between '2019-03-31' and '2019-04-27')
or (account_fiscal_periods_id=1482 and date not between '2019-04-28' and '2019-05-25')
or (account_fiscal_periods_id=1483 and date not between '2019-05-26' and '2019-06-29')
or (account_fiscal_periods_id=1484 and date not between '2019-06-30' and '2019-07-27')
or (account_fiscal_periods_id=1485 and date not between '2019-07-28' and '2019-08-24')
or (account_fiscal_periods_id=1486 and date not between '2019-08-25' and '2019-09-28')
or (account_fiscal_periods_id=1487 and date not between '2019-09-29' and '2019-10-26')
or (account_fiscal_periods_id=1488 and date not between '2019-10-27' and '2019-11-23')
or (account_fiscal_periods_id=1489 and date not between '2019-11-24' and '2019-12-28')""")
        fetch_values = self.env.cr.fetchall()
        
        for row in fetch_values:
            rec=self.env['account.invoice'].search([('id', '=', row[0])])
            if rec:
                company = self.env['res.company'].search([('id','=',rec.company_id.id)])
                account_fiscal_periods = self.env['account.fiscal.periods'].search([('calendar_type', '=', rec.company_id.calendar_type.id)])
                if account_fiscal_periods:
                    period = self.env['account.fiscal.period.lines'].search([('account_fiscal_period_id','in',[a.id for a in account_fiscal_periods]),('date_start', '<=', rec.date),('date_end', '>=', rec.date)])
                    if period.closing_date_range == True:
                        raise UserError(_('Account Period date is expired so you cannot create a record.'))
                    if period:
                        account_fiscal_periods_id = period
                        account_fiscal_periods_quarterly = period.quarter
                        account_fiscal_periods_year = period.account_fiscal_period_id                    
                        self._cr.execute("""
                            update account_invoice set 
                            account_fiscal_periods_id="""+str(account_fiscal_periods_id.id)+""",
                            account_fiscal_periods_quarterly="""+str(account_fiscal_periods_quarterly)+""",
                            account_fiscal_periods_year="""+str(account_fiscal_periods_year.id)+"""
                            where id="""+str(row[0])+"""                
                        """)
                        
                    period_week = self.env['account.fiscal.period.week'].search([('account_fiscal_period_week_id','in',[a.id for a in account_fiscal_periods]),('date_start', '<=', rec.date),('date_end', '>=', rec.date)])
                    if period_week:
                        account_fiscal_period_week_id = period_week.id
                        self._cr.execute("""
                            update account_invoice set
                            account_fiscal_period_week_id="""+str(account_fiscal_period_week_id.id)+""" 
                            where id="""+str(row[0])+"""                
                        """)
                    
                    self._cr.commit()
                    
#                 
#             
#             rec=self.env['account.move'].search([('id', '=', row[0])])
#             print row[0]
#             company = self.env['res.company'].search([('id','=',rec.company_id.id)])
#             account_fiscal_periods = self.env['account.fiscal.periods'].search([('calendar_type', '=', company.calendar_type.id)])
#             if account_fiscal_periods:
#                 period = self.env['account.fiscal.period.lines'].search([('account_fiscal_period_id','in',[a.id for a in account_fiscal_periods]),('date_start', '<=', rec.date),('date_end', '>=', rec.date)])
#                 if period.closing_date_range == True:
#                     raise UserError(_('Account Period date is expired so you cannot create a record.'))
#                 if period:
#                     rec.account_fiscal_periods_id = period.id
#                     rec.account_fiscal_periods_quarterly = period.quarter
#                     rec.account_fiscal_periods_year = period.account_fiscal_period_id.id                    
#                      
#                 period_week = self.env['account.fiscal.period.week'].search([('account_fiscal_period_week_id','in',[a.id for a in account_fiscal_periods]),('date_start', '<=', rec.date),('date_end', '>=', rec.date)])
#                 if period_week:
#                     rec.account_fiscal_period_week_id = period_week.id
         
        
    def bank_unrecon(self):

        unrecon_obj = self.env['account.bank.statement.line'].search([('statement_id' ,'=' , 710)])
        
        print unrecon_obj
        for rec in unrecon_obj:
            print rec
            rec.button_cancel_reconciliation()
        
        
    @api.multi    
    def sales_summary_change(self):

        move_lines = self.env['account.move.line'].search([
                                                            ('journal_id.name' ,'ilike' , '%Chase Deposit Sweep Journal%'),
                                                            ('ref' ,'not ilike' , '%2018%'),
                                                            ('ref' ,'not ilike' , '%2019%'),
                                                            ('account_id.name' ,'ilike', '%Deposit Sweep%'),
                                                            ('company_id' ,'>', 72)
                                                            ])
        
        i=j=0
        print move_lines
        for move_line in move_lines:
            if move_line.move_id.x_sales_summary_id:
                ar=self.env['account.move.line'].search([('move_id' ,'=' , move_line.move_id.id),('id' ,'!=' , move_line.id)])
                print ar
                if ar:                
                    if ar.full_reconcile_id:
                        print ar.full_reconcile_id
                        for rows in ar.full_reconcile_id.reconciled_line_ids:
                            if rows.id!=ar.id:
                                j+=1
                                if rows.balance==move_line.balance:
                                    i+=1
                                    rows.statement_id=move_line.statement_id.id                                    
                                    move_line.statement_id=False
                                  
                        print ar.full_reconcile_id
                        ar.full_reconcile_id.unlink()
                   
                   
    @api.multi
    def sales_summary_remove(self):
        move_lines = self.env['account.move.line'].search([('journal_id.name' ,'ilike' , '%Chase Deposit Sweep Journal%'),
                                                            ('ref' ,'not ilike' , '%2018%'),
                                                            ('ref' ,'not ilike' , '%2019%'),
                                                            ('account_id.name' ,'ilike'  , '%Deposit Sweep%')
                                                            ])
        print move_lines
        
        for move_ids in move_lines:
            if move_ids:
                print move_ids
                self._cr.execute("""update account_move_line set reconciled='f' where move_id="""+str(move_ids.move_id.id))
                move_ids.move_id.button_cancel()
                move_ids.move_id.unlink()
                self._cr.commit()
                  
    @api.multi
    def sales_summary_statement_remove(self):
        move_lines = self.env['account.move.line'].search([
                                                            ('journal_id.name' ,'ilike' , '%Customer Invoices Journal%'),
                                                            ('account_id.name' ,'ilike'  , '%Account Receivable%'),
                                                            ('statement_id' ,'!='  , None),
                                                            ('move_id.x_sales_summary_id' ,'!='  , None),
                                                            ('move_id.account_fiscal_periods_id.name','in',['M01-2018','M02-2018','M03-2018'])
                                                            ])
        print len(move_lines)
        i=0
        for move_ids in move_lines:
            lines=self.env['account.bank.statement.line'].search(['|', ('amount','=',move_ids.debit), ('amount','=',move_ids.debit),('statement_id','=',move_ids.statement_id.id)])
            if lines:
                j=0
                for new_lines in lines:
                    if len(new_lines.journal_entry_ids)>=1:            
                        j+=1                
                if j==0:
                    move_ids.move_id.statement_id=False 
                    move_ids.move_id.button_cancel()
                    move_ids.move_id.post()  
            else:
                i+=1
                move_ids.statement_id=False
                move_ids.move_id.button_cancel()
                move_ids.move_id.post()
                    
        print len(move_lines), i, j
        
    @api.multi
    def sales_summary_statement_remove_2(self):
        move_lines = self.env['account.move.line'].search([
                                                            ('journal_id.name' ,'ilike' , '%Customer Invoices Journal%'),
                                                            ('account_id.name' ,'ilike'  , '%Account Receivable%'),
                                                            ('statement_id' ,'!='  , None),
                                                            ('move_id.x_sales_summary_id' ,'!='  , None),
                                                            ('company_id' ,'not in'  , [54,66,53,57]),
                                                            ('move_id.account_fiscal_periods_id.name','in',['M01-2018','M02-2018','M03-2018'])
                                                          ])
        print len(move_lines)
        i=0
        for move_ids in move_lines:
            print(move_ids)
            lines=self.env['account.bank.statement.line'].search(['|', ('amount','=',move_ids.debit), ('amount','=',move_ids.debit),('statement_id','=',move_ids.statement_id.id)])
            print lines
            if lines:
                j=0
                for new_lines in lines:
                    if len(new_lines.journal_entry_ids)>=1:            
                        j+=1                
                if j==0:
                    i+=1
                    move_ids.move_id.statement_id=False 
                    move_ids.move_id.button_cancel()
                    move_ids.move_id.post()  
            else:
                i+=1
                move_ids.statement_id=False
                move_ids.move_id.button_cancel()
                move_ids.move_id.post()
        print i
                         
                          
    @api.multi
    def sales_summary_statement_remove_test(self):
        move_lines = self.env['account.move'].search([
#                                                             ('account_id.name' ,'ilike'  , '%Account Receivable%'),                                                            
                                                            ('journal_id.name' ,'ilike' , '%Customer Invoices Journal%'),
# #                                                             ('statement_id' ,'!='  , None),
                                                            ('date' ,'>='  , '2018-01-22'),
                                                            ('x_sales_summary_id' ,'!='  , None),
                                                            ('company_id' ,'in'  , [68,78,132,70,71,73,72,75,76]),
#                                                             ('company_id' ,'not in'  , [56,60,61,63,62,64,65,67,127,68,78,132,70,71,73,72,75,76]),
                                                            ('account_fiscal_periods_id.name','in',['M01-2018','M02-2018','M03-2018'])
                                                            ])

        print len(move_lines)
#         for move_ids in move_lines:
#             move_ids.button_cancel()
#             move_ids.post()
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
                    for pay_line in self.env['account.move'].search([('payment_order_id','=',pay_order.id),('partner_id','=',int(list3[i]))]):
    
                        if float("%.2f" % round(pay_line.amount,2))==float(list2[i]):
                            n=0
                            for line in pay_line.line_ids:
                                if line.account_id.name != 'Accounts Payable' and n==0:
                                    print line.account_id.name,'!!!'
                                    if line.ref:
                                        if "CHECK" not in line.move_id.ref: 
                                            n+=1
                                            line.ref = pay_order.name+' - CHECK '+str(int(row))
                                            line.move_id.ref=pay_order.name+' - CHECK '+str(int(row))
                                    else:                                        
                                        if "CHECK" not in line.move_id.ref: 
                                            n+=1
                                            line.ref = 'CHECK '+str(int(row))
                                            line.move_id.ref=pay_order.name+' - CHECK '+str(int(row))
                    i+=1
                    
    @api.multi
    def biweeklychange(self):        
        self.env.cr.execute("""update hr_production_line a  set 
    payroll_period=(select b.id from hr_period b 
                where a.company_id=b.company_id and  b.date_start<=a.date and b.date_stop>=a.date)
    where a.date>='2017-12-31'""")
        self._cr.commit()
        
class res_company(models.Model):
    _inherit = 'res.company'
    
    
    code = fields.Char('Company Code', required=True)
