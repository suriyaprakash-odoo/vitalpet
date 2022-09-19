# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _
import datetime
from time import time,gmtime, strftime
import re

class WeeklyReport(models.Model):
    _name = 'weekly.report'   

    name = fields.Char("name")
    year = fields.Char('Year', required=False, size=4)
    current_company = fields.Many2one('res.company',string="Current company", compute="_compute_current_company", search="_search_current_company")
    quarter = fields.Char('Quarter')
    month = fields.Char('Month')  
    week = fields.Char('Week') 
    fin_week = fields.Many2one('account.fiscal.period.week', 'Fiscal Week')  
    fin_month = fields.Many2one('account.fiscal.period.lines', 'Fiscal Month') 
    fin_year = fields.Many2one('account.fiscal.periods', 'Fiscal Year')
    company_id = fields.Many2one('res.company', 'Company', readonly=True)
    apc = fields.Float('APC', default=0.0,digits=(16,2),group_operator="avg")
    apcvsly = fields.Float('APC vs Last Year', default=0.0,digits=(16,1),group_operator="avg")
    non_medical_pro_serv_per = fields.Float('Non Medical Products and Services %', default=0.0,digits=(16,2),group_operator="avg")
    non_medical_pro_serv = fields.Float('Non Medical Products and Services', default=0.0,digits=(16,2))
    ly_non_medical_pro_serv = fields.Float('LY Non Medical Products and Services', default=0.0,digits=(16,2))
    gross = fields.Float('Gross', default=0.0,digits=(16,2))
    gross_growth = fields.Float('Gross Growth %',group_operator="avg", default=0.0,digits=(16,2))
    deposit = fields.Float('Deposit', default=0.0,digits=(16,2))
    depositgrowth = fields.Float('Deposit Growth %', group_operator="avg",default=0.0,digits=(16,2))
    discount = fields.Float('Discount %',group_operator="avg", default=0.0,digits=(16,2))
    labour_budgettemp = fields.Float('Lbr vs Bgt %', default=0.0,digits=(16,2),group_operator="avg")
    labour_achievedtemp = fields.Float('Labor %', default=0.0,digits=(16,2),group_operator="avg")
    ncint = fields.Float('NClnt',  default=0.0,digits=(16,2))
    ncgrthtempnew = fields.Float('NC Growth %', default=0.0,digits=(16,2),group_operator="avg")
    ncvisittempnew = fields.Float('NC/Visit',default=0.0,digits=(16,2),group_operator="avg")
    nptnts = fields.Float('NPtnts', default=0.0,digits=(16,2))
    visit = fields.Float('Visit', default=0.0,digits=(16,2))
    day_campers = fields.Float('Day Campers', default=0.0,digits=(16,2))
    visitgrowth = fields.Float('Visit Growth %',group_operator="avg",default=0.0,digits=(16,2))
    trans = fields.Float('Trans', default=0.0,digits=(16,2))
    grooming = fields.Float('Grooming', default=0.0,digits=(16,2))
    grooming_growth = fields.Float('Grooming Growth %', group_operator="avg", default=0.0,digits=(16,2))
    brdngoccpncytemp = fields.Float('Boarding Occupancy %',  default=0.0,digits=(16,2),group_operator="avg")
    day_campers_occupance = fields.Float('Day Campers Occupancy %',  default=0.0,digits=(16,2),group_operator="avg")
    dntprophys = fields.Float('DNT Prophys', default=0.0, digits=(16,2))
    lygross = fields.Float('LY Gross', default=0.0,digits=(16,2))
    lydeposit = fields.Float('LY Deposit',  default=0.0,digits=(16,2))
    lyvisit = fields.Float('LY Visit', default=0.0,digits=(16,2))
    lygrooming = fields.Float('LY Grooming',  default=0.0,digits=(16,2))
    lyncint = fields.Float('LY NClnt', default=0.0,digits=(16,2))
    labper = fields.Float('Lab %',default=0.0,digits=(16,2),group_operator="avg")
    clients_gain_loss = fields.Float('Clients-Gain/Lost',default=0.0,digits=(16,2),group_operator="avg")
    annualized_turnover_rate = fields.Float('Annualized Turnover Rate',default=0.0,digits=(16,2),group_operator="avg")
#     compare = fields.Char('Compare')
    
    total_actual_labor_weekly = fields.Float('Actual Labor Weekly',default=0.0,digits=(16,2),group_operator="avg")
    total_revenue_actual = fields.Float('Actual Revenue',default=0.0,digits=(16,2),group_operator="avg")
    
    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        result = super(WeeklyReport, self).read_group(domain, fields, groupby, offset, limit=limit,orderby=orderby,lazy=True)
        res = result
        cusRes=[]
        for re in reversed(res):
            if re['lydeposit'] == 0:
                re['depositgrowth'] == 0.0
            else:
                re['depositgrowth'] = (((re['deposit'] - re['lydeposit'])/re['lydeposit'])*100)
                
            if re['lygross'] == 0:
                re['gross_growth'] == 0.0
            else:
                re['gross_growth'] = (((re['gross'] - re['lygross'])/re['lygross'])*100)
                
            if re['lyncint'] == 0:
                re['ncgrthtempnew'] == 0.0
            else:
                re['ncgrthtempnew'] = (((re['ncint'] - re['lyncint'])/re['lyncint'])*100)
                
            if re['visit'] == 0:
                re['ncvisittempnew'] == 0.0
            else:
                re['ncvisittempnew'] = ((re['ncint']/re['visit'])*100)
                                            
            if re['lyvisit'] == 0:
                re['visitgrowth'] == 0.0
            else:
                re['visitgrowth'] = (((re['visit'] - re['lyvisit'])/re['lyvisit'])*100)
            
            if re['lygrooming'] == 0:
                re['grooming_growth'] == 0.0
            else:
                re['grooming_growth'] = (((re['grooming'] - re['lygrooming'])/re['lygrooming'])*100)

            re['clients_gain_loss'] = (re['visit'] - re['lyvisit'] - re['ncint'])

            if re['total_revenue_actual'] == 0:
                re['labour_achievedtemp'] = 0.0
            else:
                re['labour_achievedtemp'] = (re['total_actual_labor_weekly']/re['total_revenue_actual'])*100

                
            cusRes.append(re)
        return cusRes
#         ft_domain = [x for x in domain if "|" not in x]
#         if any("compare" in line for line in ft_domain):            
#             if "week" in groupby:
#                 tid = self.env['account.fiscal.period.week'].search([('date_start', '<=',datetime.datetime.now()), ('date_end', '>=',datetime.datetime.now())]).name
#                 fiscal_weeek = re.split('-',tid)
#                 current_week = str(fiscal_weeek[1])
#                 current_year = datetime.datetime.now().strftime("%Y")
#                 domain = ['|', ['week', '=', str(int(current_year)-1) + '-' + current_week], ['week', '=', current_year + '-' + current_week]]
#             if "month" in groupby:
#                 tid = self.env['account.fiscal.period.lines'].search([('date_start', '<=',datetime.datetime.now()), ('date_end', '>=',datetime.datetime.now())]).name
#                 fiscal_month_year = re.split('-',tid)
#                 fiscal_month = fiscal_month_year[0] 
#                 current_month = str(fiscal_month[1:])
#                 current_year = datetime.datetime.now().strftime("%Y")
#                 domain = ['|', ['month', '=', str(int(current_year)-1) + '-' + current_month], ['month', '=', current_year + '-' + current_month]]
#             if "quarter" in groupby:
#                 tid = self.env['account.fiscal.period.lines'].search([('date_start', '<=',datetime.datetime.now()), ('date_end', '>=',datetime.datetime.now())]).quarter
#                 fiscal_quarter_year = re.split('-',tid)
#                 fiscal_quarter = fiscal_quarter_year[0] 
#                 current_quarter = str(fiscal_quarter[1:])
#                 current_year = datetime.datetime.now().strftime("%Y")
#                 domain = ['|', ['quarter', '=', str(int(current_year)-1) + '-' + current_quarter], ['quarter', '=', current_year + '-' + current_quarter]] 
#             if "year" in groupby:
#                 current_year = datetime.datetime.now().strftime("%Y")
#                 domain = ['|', ['year', '=', str(int(current_year)-1)], ['year', '=', current_year]]       
#         elif any("current_company" in line for line in ft_domain):
#             filter_list = []
#             for idx, val in enumerate(ft_domain):
#                 if val[0]=='current_company':
#                     filter_list.append(ft_domain[idx])
#                     ft_domain.pop(idx)
#             for line_list in range(0,len(ft_domain)-1):
#                 filter_list.append('|')
#             if len(domain) > 1:
#                 domain.pop()
#             domain = (filter_list + ft_domain)
#             
#         return super(WeeklyReport, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)
    
    @api.multi
    @api.depends('year')
    def _get_current_company(self):
        for rec in self:
            rec.current_company = self.env.user.company_id.id
    
    @api.multi
    @api.depends('company_id')
    def _compute_current_company(self):
        for recs in self:
            recs.current_company=self.env.user.company_id.id
            
    @api.multi
    def _search_current_company(self, operator, value):
        recs = self.search([('company_id', '=', self.env.user.company_id.id)])  
        return [('id', 'in', [x.id for x in recs])]    
            
    @api.multi
    def action_create_weekly_report(self):
        current_date=today=datetime.datetime.now().date()
        company_obj = self.env['res.company'].search([('daily_report','=',True)])
        for company in company_obj:
            if company.calendar_type.name:
                type = "Fiscal Calendar"
            else:
                type = "Normal Calendar"
            account_fiscal_periods = self.env['account.fiscal.periods'].search([('calendar_type', '=', company.calendar_type.id)])
            for x in range(0, 30):       
                today = current_date - datetime.timedelta(days=x*7)
                if type == "Fiscal Calendar":    
                    
                    tid_week = self.env['account.fiscal.period.week'].search([('account_fiscal_period_week_id','in',[a.id for a in account_fiscal_periods]),('date_start', '<=', today),('date_end', '>=', today)])
                    tid_period = self.env['account.fiscal.period.lines'].search([('account_fiscal_period_id','in',[a.id for a in account_fiscal_periods]),('date_start', '<=', today),('date_end', '>=', today)])
#                     tid_week = self.env['account.fiscal.period.week'].search([('date_start', '<=',today), ('date_end', '>=',today), ('account_fiscal_period_id.calendar_type', '=',company.calendar_type.id)])
#                     tid_period = self.env['account.fiscal.period.lines'].search([('date_start', '<=',today), ('date_end', '>=',today), ('account_fiscal_period_id.calendar_type', '=',company.calendar_type.id)])
                    current_week = tid_week.name
                    current_week_antr = 'W-0'+tid_week.name.split("-")[1] 
                    current_week_id =  tid_week.id
                    current_year = tid_period.year
                    current_year_id = tid_period.account_fiscal_period_id.id 
                    current_month = tid_period.id
                    qua = tid_period.quarter
                    current_quarter=tid_period.quarter
                else:
                    current_week = 'W-' + today.strftime("%V")
                    current_week_antr = 'W-0' + today.strftime("%V")
                    current_week_id = ''
                    current_year = today.strftime("%Y")
                    current_year_id = ''
                    current_month = ''
                    month = today.strftime("%m")
                    qua=0
                    if month<=3:
                        qua=1
                    elif month<=6:
                        qua=2
                    elif month<=9:
                        qua=3
                    else:
                        qua=4
                    current_quarter="Q"+str(qua)+"-"+str(current_year)
#                 week_format=str(current_year)+"-"+str(current_week)
#                 month_format=str(current_year)+"-"+str(current_month)
                # print week_format,qua
                report_obj = self.env['weekly.report'].search_count([('fin_week','=',current_week_id),('fin_year','=',current_year_id),('company_id','=',company.id)])
                if report_obj>0:
                    report_obj = self.env['weekly.report'].search([('fin_week','=',current_week_id),('fin_year','=',current_year_id),('company_id','=',company.id)])
                else:  
                    report_obj=self.env['weekly.report'].create({
                            'week': current_week,
                            'fin_week':current_week_id,
                            'year': current_year,
                            'fin_year': current_year_id,   
                            'company_id': company.id,                  
                            'fin_month': current_month,  
                            'quarter':current_quarter,                
                        })
                for rec in report_obj:                      
                    week=current_week
                    gross=deposit=ncint=nptnts=visit=day_campers=trans=grooming=boarding=dntprophs=boarding=boardoccupancy=non_medical_services=retail_sales=day_camp=0
                    sale_obj = self.env['sales.summary'].search([('fiscal_week.name','in',[current_week,current_week_antr]),('fiscal_year','=',rec.year),('company_id','=',company.id)])
                    print sale_obj                    
                    if sale_obj:
                        for record in sale_obj:
                            gross+=record.itotalnew
                            deposit+=record.dTotal
                            ncint+=record.mClientsNew
                            nptnts+=record.mPatientsNew
                            visit+=record.mVisitsPatient
                            day_campers+=record.day_campers
                            trans+=record.mTransactions
                            grooming+=record.iGrooming
                            boarding+=record.iBoarding
                            dntprophs+=record.mDentalProphy
                            boardoccupancy+=record.mVisitsBoarding
                            non_medical_services+=record.iNonMedicalServices
                            retail_sales+=record.iRetailSales
                            day_camp+=record.idaycamp
                        
                        lgross=ldeposit=lncint=lvisit=lnon_medical_services=lgrooming=lboarding=ldaycamp=lretail_sales=0
                        ly_records=self.env['sales.summary'].search([('fiscal_week.name','in',[current_week,current_week_antr]),('fiscal_year','=',(int(rec.year)-1)),('company_id','=',company.id)])
                        print ly_records
                        print sale_obj
                        for ly_record in ly_records:
                            lgross+=ly_record.itotalnew
                            ldeposit+=ly_record.dTotal
                            lncint+=ly_record.mClientsNew
                            lvisit+=ly_record.mVisitsPatient
                            lgrooming+=ly_record.iGrooming
                            lnon_medical_services+=ly_record.iNonMedicalServices
                            lboarding+=ly_record.iBoarding
                            ldaycamp+=ly_record.idaycamp
                            lretail_sales+=ly_record.iRetailSales
                        
                        print lgrooming,'-!-',lnon_medical_services,'-!-',lboarding,'-!-',ldaycamp,'-!-',lretail_sales

                        if visit>0:
                            rec.apc=(gross-(day_camp+grooming+non_medical_services+boarding+retail_sales))/visit                            
                        rec.gross=gross

                        if lvisit>0 and visit>0:
                            
                            rec.apcvsly=((((gross-(day_camp+grooming+non_medical_services+boarding+retail_sales))/visit)-((lgross-(lgrooming+lnon_medical_services+lboarding+ldaycamp+lretail_sales))/lvisit))/((lgross-(lgrooming+lnon_medical_services+lboarding+ldaycamp+lretail_sales))/lvisit))*100
                        rec.gross=gross


                        
                        rec.trans=trans
                        rec.grooming=grooming
                        
                        rec.dntprophys=dntprophs
                        rec.lygross=lgross
                        rec.lyvisit=lvisit
                        rec.lygrooming=lgrooming
                        rec.lyncint=lncint
                        rec.lydeposit=ldeposit
                        
                        rec.non_medical_pro_serv = day_camp+rec.grooming+non_medical_services+boarding+retail_sales

                        rec.ly_non_medical_pro_serv = lgrooming+lnon_medical_services+lboarding+ldaycamp+lretail_sales

#                         if lnon_medical_services>0 or lgrooming>0 or lboarding>0 or ldaycamp>0 or lretail_sales>0:
#                             rec.non_medical_pro_serv_per=(((day_camp+grooming+non_medical_services+boarding+retail_sales)-(lgrooming+lnon_medical_services+lboarding+ldaycamp+lretail_sales))/(lgrooming+lnon_medical_services+lboarding+ldaycamp+lretail_sales))*100
                        if rec.ly_non_medical_pro_serv > 0:
                            rec.non_medical_pro_serv_per = (rec.non_medical_pro_serv - rec.ly_non_medical_pro_serv)/rec.ly_non_medical_pro_serv

                        if lgross>0:
                            rec.gross_growth=((gross-lgross)/lgross)*100
                        rec.deposit = deposit
                        if ldeposit>0:
                            rec.depositgrowth = ((deposit-ldeposit)/ldeposit)*100
                        if rec.gross>0:
                            rec.discount=((rec.gross-rec.deposit)/rec.gross)*100
                        rec.ncint=ncint
                        if lncint>0:
                            rec.ncgrthtempnew=((rec.ncint-lncint)/lncint)*100
                        if visit>0:
                            rec.ncvisittempnew=(rec.ncint/visit)*100
                        rec.nptnts=nptnts
                        rec.visit=visit
                        rec.day_campers=day_campers
                        if lvisit>0:
                            rec.visitgrowth=((visit-lvisit)/lvisit)*100
                        if lgrooming>0:
                            rec.grooming_growth=((grooming-lgrooming)/lgrooming)*100
                        rec.clients_gain_loss=visit-lvisit-ncint
                       
                        if rec.company_id.total_capacity>0:
                            rec.brdngoccpncytemp=(boardoccupancy/((rec.company_id.total_capacity)*7))*100

                        if rec.company_id.total_day_camp_capacity>0:
                            rec.day_campers_occupance = (day_campers/((rec.company_id.total_day_camp_capacity)*5))*100

                        termination_count = self.env['hr.employee'].search_count([('active','=',False),('termination_date','>=',datetime.datetime.strptime(str(tid_week.date_end),'%Y-%m-%d').date() - datetime.timedelta(days=90)),('termination_date','<=',datetime.datetime.strptime(str(tid_week.date_end),'%Y-%m-%d').date()),('company_id','=',company.id)])
                        employee_count = self.env['hr.employee'].search_count([('active','=',True),('company_id','=',company.id)])
                        
                        rec.annualized_turnover_rate = (float(termination_count)/float(employee_count))*4

                    labor_obj = self.env['actual.labor.weekly'].search([('fin_week','=',current_week_id),('fin_year','=',current_year_id),('company_id','=',company.id)])
                    labour=actual_budget=total_actual_labor_weekly=total_revenue_actual=0    
                    if labor_obj:
                        for record in labor_obj:
                            actual_budget+=record.labor_budget_per
                            labour+=record.actual_labor_per
                            total_actual_labor_weekly+=record.actual_labor_weekly
                            total_revenue_actual+=record.revenue_actual

                        rec.labour_achievedtemp=labour
                        if actual_budget>0:
                            rec.labour_budgettemp=((actual_budget-labour)/actual_budget)*100
                            rec.total_actual_labor_weekly=total_actual_labor_weekly
                            rec.total_revenue_actual=total_revenue_actual

                    lab_per_obj = self.env['sales.summary'].search([('fiscal_week.name','in',[current_week,current_week_antr]),('fiscal_year','=',rec.year),('company_id','=',company.id)])
                    deposit_total=diagnostic_total=0
                    if lab_per_obj:
                        for record in lab_per_obj:
                            deposit_total += record.dTotal
                            diagnostic_total += record.iDiagnosticTests
                        
                        if deposit_total > 0:
                            rec.labper = (diagnostic_total/deposit_total)*100