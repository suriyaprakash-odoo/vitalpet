from odoo import api, fields, models, _
from datetime import datetime
import base64
import xlwt
import csv
from odoo.tools import html2plaintext
import platform
from odoo.http import request
from urlparse import urljoin
import pandas as pd
from io import StringIO

class DemographicsFileWizard(models.TransientModel):
    _name = "demographics.file.wizard"


    date_from = fields.Date("From Date")
    date_to = fields.Date("To Date")
    specific_date = fields.Date("Specefic Date")
    today_date = fields.Boolean("Only Today")
    xl_file = fields.Binary(" Download File")
    xl_name = fields.Char("File name")
    select_all = fields.Boolean("Select all")
    date_type = fields.Selection([
        ('range', 'Date Range'),
        ('specific', 'Specefic Date'),
        ('today', 'Today'),
    ],default = 'range' , string='Date Type')


    @api.multi
    def generate_xl_report(self):
        
        list=[]
        workbook = xlwt.Workbook()
        # if self.select_all:
        #     user_ids = self.env['res.users'].search([('is_salesperson', '=', True)])
        # else:
        #     user_ids = self.user_ids
        # for user in user_ids:
        sheet = workbook.add_sheet('Demographics Report', cell_overwrite_ok=True)
        sheet.show_grid = False
        sheet.col(1).width = 256 * 25
        sheet.col(2).width = 256 * 25
        sheet.col(3).width = 256 * 25
        sheet.col(4).width = 256 * 25
        sheet.col(5).width = 256 * 25

        # style0 = xlwt.easyxf('font: name Century Gothic, height 300,bold True;align: horiz center;pattern:pattern solid;', num_format_str='YYYY-MM-DD')
        # style00 = xlwt.easyxf('font: name Century Gothic, colour white, bold True;pattern:pattern solid;border:top_color gray40, bottom_color gray40, right_color gray40, left_color gray40,'
        #                       'left thin,right thin,top thin,bottom thin;align: vert top;', num_format_str='#,##0.00')
        style01 = xlwt.easyxf('font: name Times New Roman,color-index black ; border:top_color gray40,bottom_color gray40,right_color gray40,left_color gray40,left thin,right thin,top thin,bottom thin;')
        style02 = xlwt.easyxf('font: name Times New Roman,color-index black ; border:top_color gray40,bottom_color gray40,right_color gray40,left_color gray40,left thin,right thin,top thin,bottom thin;')
        # style03 = xlwt.easyxf('font: name Century Gothic; pattern:pattern solid;border:top_color gray40, bottom_color gray40, right_color gray40, left_color gray40,left thin,right thin,top thin,bottom thin;align: vert top; align:wrap on;', num_format_str='#,##0.00')
        # style04 = xlwt.easyxf('font: name Century Gothic; pattern:pattern solid;border:top_color gray40, bottom_color gray40, right_color gray40, left_color gray40,left thin,right thin,top thin,bottom thin;align: vert top; align:wrap on;', num_format_str='"$"#,##0.00')

        # sheet.write_merge(1, 2, 1, 5, 'DEMOGRAPHIC REPORT ' + '(' + str(datetime.today().date()) + ')', style0)

        lines = self.env['hr.employee'].search([('create_date', '<=', self.date_to),('create_date', '>=', self.date_from)])
        n=0
        n+=0
        sheet.write(n, 0,'EECode', style01)
        sheet.write(n, 1,'Social Security Number', style01)
        sheet.write(n, 2,'Clock Sequence #', style01)
        sheet.write(n, 3,'Last Name', style01)
        sheet.write(n, 4,'First Name', style01)
        sheet.write(n, 5,'Middle Name', style01)
        sheet.write(n, 6,'Street Address', style01)
        sheet.write(n, 7,'City', style01)
        sheet.write(n, 8,'State', style01)
        sheet.write(n, 9,'Zipcode', style01)
        sheet.write(n, 10,'Home Phone#', style01)
        sheet.write(n, 11,'E-Mail Address', style01)
        sheet.write(n, 12,'Gender', style01)
        sheet.write(n, 13,'Marital Status', style01)
        sheet.write(n, 14,'Birth Date', style01)
        sheet.write(n, 15,'Ethnic Background', style01)
        sheet.write(n, 16,'Employee Status', style01)
        sheet.write(n, 17,'Hire Date', style01)
        sheet.write(n, 18,'Termination Date', style01)
        sheet.write(n, 19,'Employee Type', style01)
        sheet.write(n, 20,'DOL Status', style01)
        sheet.write(n, 21,'Position', style01)
        sheet.write(n, 22,'EEOC Class', style01)
        sheet.write(n, 23,'Home Department', style01)
        sheet.write(n, 24,'Pay Type', style01)
        sheet.write(n, 25,'Pay Frequency', style01)
        sheet.write(n, 26,'Salary Amount', style01)
        sheet.write(n, 27,'Rate_1', style01)
        sheet.write(n, 28,'Rate_2', style01)
        sheet.write(n, 29,'Rate_3', style01)
        sheet.write(n, 30,'Rate_4', style01)
        sheet.write(n, 31,'Rate_5', style01)
        sheet.write(n, 32,'Enrolled in Retirement Plan', style01)
        sheet.write(n, 33,'Workers Compensation Code', style01)
        sheet.write(n, 34,'Hire Act Field', style01)
        sheet.write(n, 35,'Tax Profile Description', style01)
        sheet.write(n, 36,'Live State', style01)
        sheet.write(n, 37,'Work State', style01)
        sheet.write(n, 38,'SUI State', style01)
        sheet.write(n, 39,'Federal Filing Status', style01)
        sheet.write(n, 40,'Federal # Exemptions', style01)
        sheet.write(n, 41,'Federal Additional $', style01)
        sheet.write(n, 42,'Federal Additional %', style01)
        sheet.write(n, 43,'Block Federal Tax', style01)
        sheet.write(n, 44,'Live State Filing Status', style01)
        sheet.write(n, 45,'Live State # Exemptions', style01)
        sheet.write(n, 46,'Live State Exempt Amount', style01)
        sheet.write(n, 47,'Live State Estimated Deductions', style01)
        sheet.write(n, 48,'Live State Additional $', style01)
        sheet.write(n, 49,'Live State Additional %', style01)
        sheet.write(n, 50,'Block Live State Tax', style01)
        sheet.write(n, 51,'Work State Filing Status', style01)
        sheet.write(n, 52,'Work State # Exemptions', style01)
        sheet.write(n, 53,'Work State Exempt Amount', style01)
        sheet.write(n, 54,'Work State Estimated Deductions', style01)
        sheet.write(n, 55,'Work State Additional $', style01)
        sheet.write(n, 56,'Work State Additional %', style01)
        sheet.write(n, 57,'Block Work State Tax', style01)
        sheet.write(n, 58,'EIC Filing Status', style01)
        sheet.write(n, 59,'Employee Local Tax Code 1', style01)
        sheet.write(n, 60,'Employee Local Tax Code 2', style01)
        sheet.write(n, 61,'Employee Local Tax Code 3', style01)
        sheet.write(n, 62,'Employee Local Tax Code 4', style01)
        sheet.write(n, 63,'Employee Local Tax Code 5', style01)
        sheet.write(n, 64,'Employee Local Tax Code 6', style01)
        sheet.write(n, 65,'Employ(er) Local Tax Code 1', style01)
        sheet.write(n, 66,'Employ(er) Local Tax Code 2', style01)
        sheet.write(n, 67,'Employ(er) Local Tax Code 3', style01)
        sheet.write(n, 68,'Employ(er) Local Tax Code 4', style01)
        sheet.write(n, 69,'Employ(er) Local Tax Code 5', style01)
        sheet.write(n, 70,'Employ(er) Local Tax Code 6', style01)
        sheet.write(n, 71,'Net Direct Deposit Enabled', style01)
        sheet.write(n, 72,'Net Direct Deposit Routing Code', style01)
        sheet.write(n, 73,'Net Direct Deposit Account Code', style01)
        sheet.write(n, 74,'Net Direct Deposit Account Type', style01)
        sheet.write(n, 75,'Direct Deposit Distributions Enabled', style01)
        sheet.write(n, 76,'Direct Deposit Distribution 1 Routing Code', style01)
        sheet.write(n, 77,'Direct Deposit Distribution 1 Account Code', style01)
        sheet.write(n, 78,'Direct Deposit Distribution 1 Account Type', style01)
        sheet.write(n, 79,'Direct Deposit Distribution 1 Amount', style01)
        sheet.write(n, 80,'Direct Deposit Distribution 1 Percentage', style01)
        sheet.write(n, 81,'Direct Deposit Distribution 2 Routing Code', style01)
        sheet.write(n, 82,'Direct Deposit Distribution 2 Account Code', style01)
        sheet.write(n, 83,'Direct Deposit Distribution 2 Account Type', style01)
        sheet.write(n, 84,'Direct Deposit Distribution 2 Amount', style01)
        sheet.write(n, 85,'Direct Deposit Distribution 2 Percentage', style01)
        sheet.write(n, 86,'Direct Deposit Distribution 3 Routing Code', style01)
        sheet.write(n, 87,'Direct Deposit Distribution 3 Account Code', style01)
        sheet.write(n, 88,'Direct Deposit Distribution 3 Account Type', style01)
        sheet.write(n, 89,'Direct Deposit Distribution 3 Amount', style01)
        sheet.write(n, 90,'Direct Deposit Distribution 3 Percentage', style01)
        sheet.write(n, 91,'Direct Deposit Distribution 4 Routing Code', style01)
        sheet.write(n, 92,'Direct Deposit Distribution 4 Account Code', style01)
        sheet.write(n, 93,'Direct Deposit Distribution 4 Account Type', style01)
        sheet.write(n, 94,'Direct Deposit Distribution 4 Amount', style01)
        sheet.write(n, 95,'Direct Deposit Distribution 4 Percentage', style01)
        sheet.write(n, 96,'Custom Text Field 01', style01)
        sheet.write(n, 97,'Custom Text Field 02', style01)
        sheet.write(n, 98,'Custom Text Field 03', style01)
        sheet.write(n, 99,'Custom Text Field 04', style01)
        sheet.write(n, 100,'Custom Text Field 05', style01)
        sheet.write(n, 101,'Custom Text Field 06', style01)
        sheet.write(n, 102,'Custom Text Field 07', style01)
        sheet.write(n, 103,'Custom Text Field 08', style01)
        sheet.write(n, 104,'Custom Text Field 09', style01)
        sheet.write(n, 105,'Custom Text Field 10', style01)
        sheet.write(n, 106,'Custom Text Field 11', style01)
        sheet.write(n, 107,'Custom Text Field 12', style01)
        sheet.write(n, 108,'Custom Text Field 13', style01)
        sheet.write(n, 109,'Custom Text Field 14', style01)
        sheet.write(n, 110,'New Hire Flag', style01)
        sheet.write(n, 111,'Exempt Status', style01)
        sheet.write(n, 112,'Labor Allocation Defaults', style01)
        sheet.write(n, 113,'WorkAddressID', style01)
        sheet.write(n, 114,'PA PSD Code', style01)
        sheet.write(n, 115,'Default Payroll Profile', style01)
        sheet.write(n, 116,'Ohio Lives-in Local', style01)
        sheet.write(n, 117,'Ohio Works-in Local', style01)
        sheet.write(n, 118,'Salary Entry Method', style01)
        sheet.write(n, 119,'Processing Scheduling', style01)

        n += 2;
        if self.date_type == 'specific':
            employee_obj = request.env['hr.employee'].sudo().search([('hire_date' , '=' , self.specific_date)])
        if self.date_type == 'range':
            employee_obj = request.env['hr.employee'].sudo().search([('hire_date', '<=', self.date_to),('hire_date', '>=', self.date_from)])
        if self.date_type == 'today':
        	if self.today_date:
        		employee_obj = request.env['hr.employee'].sudo().search([('hire_date' , '=' , datetime.today().date())])
        	
        	
        if employee_obj:            
            
            for employee in employee_obj:

                gender = marital = exempt_status = id_no = default_payroll_profile = routing = emp_fname = emp_mname = emp_lname = ''

                if employee.firstname:
                    emp_fname = employee.firstname.upper()

                if employee.middlename:
                    emp_mname = employee.middlename.upper()

                if employee.lastname:
                    emp_lname = employee.lastname.upper()

                if employee.encrypt_value == True:
                    if employee.identification_id:
                        id_no = base64.b64decode(employee.identification_id)
                        id_num = id_no.replace('-','',2)

                else:
                    if employee.identification_id:
                        id_no = employee.identification_id
                        id_num = id_no.replace('-','',2)

                if employee.address_home_id.street2:
                    address = str(employee.address_home_id.street)+','+str(employee.address_home_id.street2) 
                else:
                    address = employee.address_home_id.street

                if employee.address_id.state_id.code == 'AR':
                    default_payroll_profile = '0QJ26'

                elif employee.address_id.state_id.code == 'NY':
                    default_payroll_profile = '0QJ28'

                elif employee.address_id.state_id.code == 'LA':
                    default_payroll_profile = '0QJ27'

                else:
                    default_payroll_profile = '0QJ29'

                if employee.address_home_id.bank_routing or employee.address_home_id.bank_account or employee.address_home_id.bank_account_type:
                    routing = 'T'
                else:
                    routing = 'F'

                if employee.employment_status.name == 'Full Time Employee' and employee.job_id.job_template.name == 'Veterinary Technician':
                    pay_class = 'PC3'
                elif employee.employment_status.name == 'Full Time Employee' and employee.job_id.job_template.name != 'Veterinary Technician':
                    pay_class = 'PC2'
                else:
                    pay_class = 'PC1'


            	if employee.employment_status.name == 'Full Time Employee':
                    dol_status = 'FT'
                if employee.employment_status.name == 'Part Time Employee':
                    dol_status = 'PT'

                if employee.overtime_pay == 'exempt':
                    exempt_status = 'T'
                else:
                    exempt_status = 'F'

                if employee.gender == 'male':
                    gender = 'M'
                if employee.gender == 'female':
                    gender = 'F'

                if employee.marital == 'single':
                    marital = 'S'
                if employee.marital == 'married':
                    marital = 'M'
                if employee.marital == 'divorced':
                    marital = 'D'
                if employee.marital == 'widower':
                    marital = 'W'

                # position_obj = self.env['external.hr.mapping'].search([('job_id' , '=' , employee.job_id.id),('seniority_id' , '=' , employee.job_seniority_title.id),('active' , '=' , True)],limit=1)
                position_obj = self.env['external.hr.mapping'].search([('job_id' , '=' , employee.job_id.id),('seniority_id' , '=' , employee.job_seniority_title.id)],limit=1)
            	
                if employee.contract_id:

                    # if employee.contract_id.salary_computation_method == 'yearly':

                    if employee.contract_id.salary_computation_method == 'yearly' or employee.contract_id.salary_computation_method == 'monthly':
                        dept_code = 200
                    else:
                        dept_code = 100

                    salary = salary_hourly = ''
                    if employee.contract_id.salary_computation_method == 'yearly' or employee.contract_id.salary_computation_method == 'monthly':
                        salary = employee.contract_id.wage
                    else:
                        # rate1 = rate2 = rate3 = rate4 = rate5 = ''
                        ss = [line.hourly_rate for line in employee.contract_id.contract_job_ids if line.is_main_job == True]
                        salary_hourly = ss[0]
                #         dd = [line.hourly_rate for line in employee.contract_id.contract_job_ids if line.is_main_job != True]
                #         i=1
                #         for x in range(len(dd)):
                #             if i == 1:
                #                 rate1 = dd[i-1]
                #             if i == 2:
                #                 rate2 = dd[i-1]
                #             if i == 3:
	            			# 	rate3 = dd[i-1]
	            			# if i == 4:
	            			# 	rate4 = dd[i-1]
	            			# if i == 5:
	            			# 	rate5 = dd[i-1]
	            			# i += 1 

                        
	            		# for rec in employee.contract_id.contract_job_ids:
	            		# 	x=0
	            		# 	if rec.is_main_job:
	            		# 		salary = rec.hourly_rate


            	onboarding_obj = self.env['hr.employee.onboarding'].search([('employee_id' , '=' , employee.id)])

                i = 0
                sheet.write(n - 1, 0, employee.employee_id or '', style02)
                sheet.write(n - 1, 1, id_num or '', style02)
                sheet.write(n - 1, 2, employee.time_clock or '', style02)
                sheet.write(n - 1, 3, emp_lname or '', style02)
                sheet.write(n - 1, 4, emp_fname or '', style02)
                sheet.write(n - 1, 5, emp_mname or '', style02)
                sheet.write(n - 1, 6, address or '', style02)
                sheet.write(n - 1, 7, employee.address_home_id.city or '', style02)
                sheet.write(n - 1, 8, employee.address_home_id.state_id.code or '', style02)
                sheet.write(n - 1, 9, employee.address_home_id.zip or '', style02)
                sheet.write(n - 1, 10, employee.address_home_id.phone or '', style02)
                sheet.write(n - 1, 11, employee.address_home_id.email or '', style02)
                sheet.write(n - 1, 12, gender or '', style02)
                sheet.write(n - 1, 13, marital or '', style02)
                sheet.write(n - 1, 14, employee.birthday or '', style02)
                sheet.write(n - 1, 15, '', style02)
                sheet.write(n - 1, 16, 'A', style02)
                sheet.write(n - 1, 17, employee.hire_date or '', style02)
                sheet.write(n - 1, 18, '', style02)
                sheet.write(n - 1, 19, 'W2', style02)
                sheet.write(n - 1, 20, dol_status or'', style02)
                sheet.write(n - 1, 21, position_obj.external_job_id or '', style02)
                sheet.write(n - 1, 22, '', style02)
                sheet.write(n - 1, 23, dept_code or '', style02)
                sheet.write(n - 1, 24, 'H', style02)
                sheet.write(n - 1, 25, 'B', style02)
                sheet.write(n - 1, 26, salary or '0', style02)
                sheet.write(n - 1, 27, salary_hourly or '0', style02)
                sheet.write(n - 1, 28, '', style02)
                sheet.write(n - 1, 29, '', style02)
                sheet.write(n - 1, 30, '', style02)
                sheet.write(n - 1, 31, '', style02)
                sheet.write(n - 1, 32, '', style02)
                sheet.write(n - 1, 33, '00000000', style02)
                sheet.write(n - 1, 34, '', style02)
                sheet.write(n - 1, 35, '', style02)
                sheet.write(n - 1, 36, employee.address_home_id.state_id.code or '', style02)
                sheet.write(n - 1, 37, employee.address_home_id.state_id.code or '', style02)
                sheet.write(n - 1, 38, employee.address_home_id.state_id.code or '', style02)
                sheet.write(n - 1, 39, employee.filing_staus or '', style02)
                sheet.write(n - 1, 40, employee.children or '0', style02)
                sheet.write(n - 1, 42, '', style02)
                sheet.write(n - 1, 41, '', style02)
                sheet.write(n - 1, 43, '', style02)
                sheet.write(n - 1, 44, employee.filing_staus or '', style02)
                sheet.write(n - 1, 45, employee.children or '0', style02)
                sheet.write(n - 1, 46, '', style02)
                sheet.write(n - 1, 47, '', style02)
                sheet.write(n - 1, 48, '', style02)
                sheet.write(n - 1, 49, '', style02)
                sheet.write(n - 1, 50, '', style02)
                sheet.write(n - 1, 51, employee.filing_staus or '', style02)
                sheet.write(n - 1, 52, employee.children or '0', style02)
                sheet.write(n - 1, 53, '', style02)
                sheet.write(n - 1, 54, '', style02)
                sheet.write(n - 1, 55, '', style02)
                sheet.write(n - 1, 56, '', style02)
                sheet.write(n - 1, 57, '', style02)
                sheet.write(n - 1, 58, '', style02)
                sheet.write(n - 1, 59, '', style02)
                sheet.write(n - 1, 60, '', style02)
                sheet.write(n - 1, 61, '', style02)
                sheet.write(n - 1, 62, '', style02)
                sheet.write(n - 1, 63, '', style02)
                sheet.write(n - 1, 64, '', style02)
                sheet.write(n - 1, 65, '', style02)
                sheet.write(n - 1, 66, '', style02)
                sheet.write(n - 1, 67, '', style02)
                sheet.write(n - 1, 68, '', style02)
                sheet.write(n - 1, 69, '', style02)
                sheet.write(n - 1, 70, '', style02)
                sheet.write(n - 1, 71, routing or '', style02)
                sheet.write(n - 1, 72, employee.address_home_id.bank_routing or '', style02)
                sheet.write(n - 1, 73, employee.address_home_id.bank_account or '', style02)
                sheet.write(n - 1, 74, employee.address_home_id.bank_account_type or '', style02)
                sheet.write(n - 1, 75, '', style02)
                sheet.write(n - 1, 76, '', style02)
                sheet.write(n - 1, 77, '', style02)
                sheet.write(n - 1, 78, '', style02)
                sheet.write(n - 1, 79, '', style02)
                sheet.write(n - 1, 80, '', style02)
                sheet.write(n - 1, 81, '', style02)
                sheet.write(n - 1, 82, '', style02)
                sheet.write(n - 1, 83, '', style02)
                sheet.write(n - 1, 84, '', style02)
                sheet.write(n - 1, 85, '', style02)
                sheet.write(n - 1, 86, '', style02)
                sheet.write(n - 1, 87, '', style02)
                sheet.write(n - 1, 88, '', style02)
                sheet.write(n - 1, 89, '', style02)
                sheet.write(n - 1, 90, '', style02)
                sheet.write(n - 1, 91, '', style02)
                sheet.write(n - 1, 92, '', style02)
                sheet.write(n - 1, 93, '', style02)
                sheet.write(n - 1, 94, '', style02)
                sheet.write(n - 1, 95, '', style02)
                sheet.write(n - 1, 96, '', style02)
                sheet.write(n - 1, 97, '', style02)
                sheet.write(n - 1, 98, '', style02)
                sheet.write(n - 1, 99, '', style02)
                sheet.write(n - 1, 100, '', style02)
                sheet.write(n - 1, 101, '', style02)
                sheet.write(n - 1, 102, '', style02)
                sheet.write(n - 1, 103, '', style02)
                sheet.write(n - 1, 104, '', style02)
                sheet.write(n - 1, 105, '', style02)
                sheet.write(n - 1, 106, '', style02)
                sheet.write(n - 1, 107, '', style02)
                sheet.write(n - 1, 108, '', style02)
                sheet.write(n - 1, 109, '', style02)
                sheet.write(n - 1, 110, '1', style02)
                sheet.write(n - 1, 111, exempt_status or '', style02)
                sheet.write(n - 1, 112, '', style02)
                sheet.write(n - 1, 113, '', style02)
                sheet.write(n - 1, 114, '', style02)
                sheet.write(n - 1, 115, default_payroll_profile or '', style02)
                sheet.write(n - 1, 116, '', style02)
                sheet.write(n - 1, 117, '', style02)
                sheet.write(n - 1, 118, '', style02)
                sheet.write(n - 1, 119, '2569', style02)

                n += 1
          
        if platform.system() == 'Linux':
                filename = ('/tmp/Demographics Report-' + str(datetime.today().date()) + '.xls')
                filename1='Demographics Report-' + str(datetime.today().date()) + '.xls'
        else:
           filename = ('Demographics Report-' + str(datetime.today().date()) + '.xls')
           filename1='Demographics Report-' + str(datetime.today().date()) + '.xls'
        # filename = ('Pipeline Report - ' + str(datetime.today().date()) + '.xls')
        workbook.save(filename)
        fp = open(filename, "rb")
        file_data = fp.read()
        out = base64.encodestring(file_data)

        data_xls = pd.read_excel(filename, 'Demographics Report', index_col=None)
        data_xls.to_csv('/tmp/Demographics Report.csv', encoding='utf-8')
 
        csv_name='Demographics Report-' + str(datetime.today().date()) + '.csv'
        
        csv_file = open('/tmp/Demographics Report.csv', "rb")
        file_data_csv = csv_file.read()
        out_csv = base64.encodestring(file_data_csv)
        
        attach_vals = {
            'xl_file' :out_csv,
            'xl_name':csv_name,
            'select_all': self.select_all,
        }


        act_id = self.env['demographics.file.wizard'].create(attach_vals)
        

        return {
            'name': _('Demographics Report'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'demographics.file.wizard',
            'target': 'new',
            'res_id':act_id.id,
            }
