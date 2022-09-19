# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError, UserError
import datetime

class HrContract(models.Model):
    _inherit = 'hr.contract'

    @api.multi
    def contract_page(self,staff=None):
        action_rec = self.env['ir.model.data'].xmlid_to_object('vitalpet_payroll_inputs.action_payroll_input_contract')
        if action_rec:
            return action_rec.id

    @api.multi
    def validate_payroll_contract(self,staff=None):
        contracts=self.env['hr.contract'].search_count([('state','=','pending')])
        if contracts==0:
            employees = self.env['hr.employee'].search([('company_id', '=', self.env.user.company_id.id)])
            employee_append = []
            for employee in employees:
                
                if employee.contracts_count == 0:
                    employee_append.append(employee.name)
            
            if len(employee_append) > 0:
                emm = '\n'
                for i in employee_append:
                    emm += str(i) + '\n'
                raise ValidationError(_('Below employees don\'t have any contract. Please contact HR'+ emm))
                
            action_rec = self.env['ir.model.data'].xmlid_to_object('vitalpet_payroll_inputs.act_hr_employee_holiday_request_new')
            if action_rec:
                return action_rec.id
        else:
            raise ValidationError(_('Please renew pending contracts.'))


class PayrollFinal(models.Model):
    _name = 'payroll.final'

    name = fields.Char('Name', required=True)

class HrHolidays(models.Model):
    _inherit = 'hr.holidays'

    @api.multi
    def leaves_page(self,staff=None):
        
        action_rec = self.env['ir.model.data'].xmlid_to_object('vitalpet_payroll_inputs.act_hr_employee_holiday_request_new')
        if action_rec:
            return action_rec.id

    @api.multi
    def validate_payroll_leaves(self,staff=None):
        leaves=self.env['hr.holidays'].search_count(['|',('state','=','confirm'),('state','=','validate1')])

        if leaves==0:
            action_rec = self.env['ir.model.data'].xmlid_to_object('vitalpet_payroll_inputs.action_payroll_input_timesheets')
            if action_rec:
                return action_rec.id
        else:
            raise ValidationError(_('Please approve all pending leaves'))



    @api.multi
    def timesheet_page(self,staff=None):
        action_rec = self.env['ir.model.data'].xmlid_to_object('vitalpet_payroll_inputs.action_payroll_input_timesheets')
        if action_rec:
            return action_rec.id

    @api.multi
    def production_page(self,payroll_period=None):
        action_rec = self.env['ir.model.data'].xmlid_to_object('vitalpet_payroll_inputs.action_payroll_input_production')
        if action_rec:
            if payroll_period:
                stage_id = self.env['hr.payroll.inputs'].search([("payroll_period","=",payroll_period),("company_id", "=", self.env.user.company_id.id)])
                for line in stage_id:
                    line.stage  = "production"
            return action_rec.id
        
    @api.multi
    def production_page_view(self,payroll_period=None):
        action_rec = self.env['ir.model.data'].xmlid_to_object('vitalpet_payroll_inputs.action_payroll_input_production_new')
        if action_rec:
            if payroll_period:
                stage_id = self.env['hr.payroll.inputs'].search([("payroll_period","=",payroll_period),("company_id", "=", self.env.user.company_id.id)])
                for line in stage_id:
                    line.stage  = "production"
            return action_rec.id

    @api.multi
    def validation_page(self, payroll_period=None):
        # production_reports = self.env["hr.production.line"].search([("company_id", "=", self.env.user.company_id.id), ("status", "=", "non_validate")])
        production_id = self.env['hr.production.tag'].search([("double_validation","=",True)])
        stage_id = self.env['hr.payroll.inputs'].search([("payroll_period","=",payroll_period),("company_id", "=", self.env.user.company_id.id)])
        action_rec = self.env['ir.model.data'].xmlid_to_object('vitalpet_payroll_inputs.act_payroll_final')
        
        flag = self.env['res.users'].has_group('vitalpet_mypractice.group_my_practice_manager')             
        if flag == True:
            action_rec = self.env['ir.model.data'].xmlid_to_object('vitalpet_payroll_inputs.action_payroll_validation')
        else:
            action_rec = self.env['ir.model.data'].xmlid_to_object('vitalpet_payroll_inputs.act_payroll_final')

        production_report = self.env['hr.production.line'].search([('payroll_period.id' , '=' , payroll_period),('status' , '=' , 'validate')])

        emp_list = []
        unique_emp = []
        mail_ids = []

        for employee in production_report:
            emp_list.append(employee.employee_id.id)

        unique_emp = set(emp_list)

        for emp in unique_emp:
            tag_list = []

            employee_id=self.env['hr.employee'].search([('id','=',emp)])
            payroll_period_id=self.env['hr.period'].search([('id','=',payroll_period)])
            now_date = datetime.date.today()
            mail_pool = self.env['mail.mail']
            ir_model_data = self.env['ir.model.data']
            print self.env.user.company_id.name,'!!!!'
            message_to_sent = """
                <div style="line-height: 20px;font-family: 'Lucida Grande', Ubuntu, Arial, Verdana, sans-serif; font-size: 12px; color: rgb(34, 34, 34); background-color: #FFF; ">
                <p>Dear """+str(employee_id.name)+""",</p>
                <p>Please find below your production results at """+str(self.env.user.company_id.name)+""" corresponding to """+payroll_period_id.name+""":</p>

                <table style="margin-top: 10px;font-size: 1.2em;border-collapse: collapse;" border="1px">
                    <tr>
                        <th style="font-weight: 500;padding: 11px 22px;" >Production</th>
                        <th style="font-weight: 500;padding: 11px 22px;" >Amount</th>
                        <th style="font-weight: 500;padding: 11px 22px;" >YTD</th>                  
                    </tr>"""


            for production_list in self.env['hr.production.line'].search([
                                                    ('payroll_period.id' , '=' , payroll_period),
                                                    ('status' , '=' , 'validate'),
                                                    ('employee_id' , '=' , emp)]):
                tag_list.append(production_list.bonus_id.id)

            unique_tag_lists = set(tag_list)
            for unique_tag_list in unique_tag_lists:  

                amount_tag=total=0              
                production_id=production_tag=False
                for line in self.env['hr.production.line'].search([
                                                        ('payroll_period.id' , '=' , payroll_period),
                                                        ('status' , '=' , 'validate'),
                                                        ('employee_id' , '=' , emp),
                                                        ('bonus_id' , '=' , unique_tag_list)]):
                    
                    amount_tag+=line.amount
                    production_tag=line.bonus_id
                    production_id=line.id
                for vals in self.env['hr.production.line'].search([('employee_id' , '=' , emp),
                                                                   ('fin_year' , '=' , line.fin_year.id),
                                                                    ('bonus_id' , '=' , production_tag.id)]):

                    total+=vals.amount
                message_to_sent += """ <tr>
                            <th style="font-weight: 500;padding: 11px 22px;" >"""+str(production_tag.name)+"""</th>
                            <th style="font-weight: 500;padding: 11px 22px;" >"""+str(amount_tag)+"""</th>
                            <th style="font-weight: 500;padding: 11px 22px;" >"""+str(total)+"""</th>
                        </tr>"""

                

            message_to_sent += """</table>

                    If there is any information you would like us to review in regards the above summary, please contact us not later than """+str(now_date)+"""
                    
                    <p>Best Regards,</p>
                    <p>Vitalpet Team</p>
                    </div>
                    """

            if message_to_sent and employee_id.work_email:

                    vals_cont = self.env.context.copy()
                    vals_cont.update({
                                'body_content':message_to_sent 
                                })

                    print vals_cont,"vals_cont"

                    template_id = self.env.ref('vitalpet_production_model.production_validation_notification')
                    if template_id: 
                        template_id.with_context(vals_cont).send_mail(production_id, force_send=True)


        if action_rec:
            if payroll_period:
                if not production_id:
                    for final in stage_id:
                        final.stage = "validate"
                else:
                    for final in stage_id:
                        final.stage = "finalized"

            return action_rec.id


    @api.multi
    def finalized_page(self,payroll_period=None):
        production_reports = self.env["hr.production.line"].search([("company_id", "=", self.env.user.company_id.id),("status","=", "non_validate")])
        if payroll_period:
            hr_work_hours = self.env["hr.work.hours"].search([("company_id", "=", self.env.user.company_id.id), ("status", "=", "non_validate")])
            for hr_work_hour in hr_work_hours:
                    hr_work_hour.write({"status":"validate"})
                
            flag = self.env['res.users'].has_group('vitalpet_mypractice.group_my_practice_manager')             
            if flag == True:
                for production_report in production_reports:
                    production_report.write({"status":"validate"})
                    if self.env['hr.production.line'].search_count([('status','=','non_validate'),('production_line_id','=',production_report.production_line_id.id)]) == 0:
                        production_report.production_line_id.write({'status':'validated'})
                        production_report.production_line_id.write({'state':'validated'})
                
                if payroll_period>0:
                    hr=self.env['hr.period'].search([('id','=',payroll_period)])
                    hr.write({'state':'inputs'})
        action_rec = self.env['ir.model.data'].xmlid_to_object('vitalpet_payroll_inputs.act_payroll_final')

        if action_rec:
            if payroll_period:
                stage_id = self.env['hr.payroll.inputs'].search([("payroll_period","=",payroll_period),("company_id", "=", self.env.user.company_id.id)])
                for line in stage_id:
                    line.stage = "finalized"
            return action_rec.id
