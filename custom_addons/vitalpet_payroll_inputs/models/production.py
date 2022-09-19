# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, tools, _
import datetime
from odoo.exceptions import ValidationError, UserError


class VitalpetPayrollInputsProduction(models.Model):
    _name = 'vitalpet.payroll.inputs.production'

    def add_times(self, a, b):
        if not a:
            a = '00:00'
        if not b:
            b = '00:00'
        a1, a2 = a.split(":")
        b1, b2 = b.split(":")
        x = int(a1) + int(b1)
        y = int(a2) + int(b2)
        if y >= 60:
            x = x + 1
            y = y - 60
        if len(str(x)) == 1:
            x = "0" + str(x)
        if len(str(y)) == 1:
            y = "0" + str(y)
        return str(x) + ":" + str(y)

    @api.model
    def fetch_production_data(self, context=None):
        period_id = False
        week_type = 'two_weeks';
        filter_production = 'all_production'
        filter_module = 'all'
        total_employee = 1
        current_employee = False
        employee_name = 'All Team Members'
        employee_number = 1
        week_no = 1
        if context:
            if context.get('period_id'):
                period_id = context.get('period_id')
            if context.get('week_type'):
                week_type = context.get('week_type')
            if context.get('week_no'):
                week_no = context.get('week_no')
            if context.get('filter_production'):
                filter_production = context.get('filter_production')
            if context.get('current_employee'):
                current_employee = context.get('current_employee')
                hr_employee = self.env['hr.employee'].sudo().search([('id', '=', current_employee)])
                employee_name = hr_employee.name
            if context.get('employee_number') and filter_production == 'team_member':
                employee_number = context.get('employee_number')
            if context.get('week_no'):
                week_no = context.get('week_no')
            if context.get('filter_module'):
                filter_module = context.get('filter_module')

        today_date = datetime.datetime.today().date()
        result = {}
        dates = []
        periods = []
        values = []
        employee_ids = []
        emp_lst = []
        contract_job_obj = self.env['hr.contract.job']
        contract_job_sr = contract_job_obj.sudo().search([('job_id.company_id', '=', self.env.user.company_id.id), ('contract_id.state', '=', 'open')])
        
        for contract_job in contract_job_sr:
                if contract_job.contract_id.staff_bonus_ids and contract_job.contract_id.employee_id.active == True:
                    emp_lst.append(contract_job.contract_id.employee_id)
        
        if filter_production == 'team_member':
            if not current_employee:
                emp_br = self.env['hr.employee'].search([('id', '=', emp_lst[0].id)])
                current_employee = emp_br.id
                employee_name = emp_br.name
            total_employee = len(emp_lst)
            for employee in emp_lst:
                employee_values = {}
                employee_values['id'] = employee.id
                employee_values['name'] = employee.name
                if employee.active:
                    employee_ids.append(employee_values)
            emp_lst = []
            emp_lst = self.env['hr.employee'].sudo().search([('id', '=', int(current_employee))])
        hr_periods = self.env['hr.period'].search([('company_id', '=', self.env.user.company_id.id),('state', '=', 'open')])
        if period_id:
            select_period = self.env['hr.period'].search([('id', '=', period_id)])
        else:
            select_period = self.env['hr.period'].search([('company_id', '=', self.env.user.company_id.id), ('date_start', '<=', today_date), ('date_stop', '>=', today_date)])
        if not select_period:
            raise ValidationError(_('Payroll Periods not configured for current company.'))
        for period in hr_periods:
            values = {}
            values['id'] = period.id
            values['name'] = period.name
            values['state'] = period.state
            periods.append(values)

        result['payroll_periods'] = periods
        result['current_period'] = select_period.id
        result['current_period_state'] = select_period.state

        if week_type == 'week':
            if week_no == 1:
                from_date = datetime.datetime.strptime(select_period.date_start, "%Y-%m-%d")
                to_date = datetime.datetime.strptime(select_period.date_start, "%Y-%m-%d")
                to_date = to_date + datetime.timedelta(days=6)
            else:
                from_date = datetime.datetime.strptime(select_period.date_start, "%Y-%m-%d")
                to_date = datetime.datetime.strptime(select_period.date_start, "%Y-%m-%d")
                from_date = from_date + datetime.timedelta(days=7)
                to_date = to_date + datetime.timedelta(days=13)

        else:
            from_date = datetime.datetime.strptime(select_period.date_start, "%Y-%m-%d")
            to_date = datetime.datetime.strptime(select_period.date_stop, "%Y-%m-%d")

        # From date will change in every loop, so used date_from variable to stare from date
        date_from = from_date
        # TO date will change in every loop, so used date_from variable to stare to date
        date_to = to_date

        production_values = []
        production_types = self.env['hr.production.type'].search([])
        for production_type in production_types:
            color_code = production_type.color
            if color_code == 1:
                color = "oe_grids_one"
            elif color_code == 2:
                color = "oe_grids_two"
            elif color_code == 3:
                color = "oe_grids_three"
            elif color_code == 4:
                color = "oe_grids_four"
            elif color_code == 5:
                color = "oe_grids_five"
            elif color_code == 6:
                color = "oe_grids_six"
            elif color_code == 7:
                color = "oe_grids_seven"
            elif color_code == 8:
                color = "oe_grids_eight"
            elif color_code == 9:
                color = "oe_grids_nine"
            elif color_code == 10:
                color = "oe_grids_ten"
            elif color_code == 0:
                color = "oe_grids_zero"
            elif color_code > 10:
                color = "oe_grids_default"
            template_values = {}
            has_data = False
            employee_bonus_values = []
            for employee in emp_lst:
                if employee.company_id.id != self.env.user.company_id.id:
                    hr_period = self.env['hr.period'].sudo().search([('company_id', '=', employee.company_id.id),
                                                          ('date_start', '=', select_period.date_start),
                                                          ('date_stop', '=', select_period.date_stop)])
                    select_period = hr_period
                else:
                    if period_id:
                        select_period = self.env['hr.period'].search([('id', '=', period_id)])
                    else:
                        select_period = self.env['hr.period'].search([('company_id', '=', self.env.user.company_id.id), ('date_start', '<=', today_date), ('date_stop', '>=', today_date)])
                bonus_accruals = self.env['bonus.accrual'].sudo().search([('type_id', '=', production_type.id), ('contract_id.employee_id', '=', employee.id), ('job_id.company_id.id', '=', self.env.user.company_id.id)])
                for bonus_accrual in bonus_accruals:
                    has_data = True
                    employee_bonus = {}
                    employee_bonus['name'] = employee.name+'/'+bonus_accrual.job_id.name+'/'+bonus_accrual.production_tag_id.name
                    from_date = date_from
                    to_date = date_to
                    values = []
                    sum_value = 0
                    while (to_date >= from_date):
                        hr_productions = self.env['hr.production'].search([('employee_id', '=', employee.id),
                                                                                    ('period_id', '=', select_period.id)])
                        values_data = {}
                        if hr_productions:
                            hr_production = self.env['hr.production.line'].search([('job_id', '=', bonus_accrual.job_id.id),
                          
                                                                                            ('bonus_id', '=', bonus_accrual.production_tag_id.id),
                                                                                            ('date', '=', from_date),
                                                                                            ('production_line_id', '=', hr_productions.id)])
#                          
                            if hr_production:
                                sum_value += hr_production.amount
                                values_data['amount'] = format(hr_production.amount, '.2f')
                                values_data['employee_id'] = hr_productions.employee_id.id
                                values_data['job_id'] = hr_production.job_id.id
                                values_data['bonus_id'] = hr_production.bonus_id.id
                                values_data['date'] = hr_production.date
                            else:
                                values_data['amount'] = format(0, '.2f')
                                sum_value += 0
                                values_data['employee_id'] = employee.id
                                values_data['job_id'] = bonus_accrual.job_id.id
                                values_data['bonus_id'] = bonus_accrual.production_tag_id.id
                                values_data['date'] = from_date.strftime('%Y-%m-%d')
                        
#                          
                        else:
                            values_data['amount'] = format(0, '.2f')
                            sum_value += 0
                            values_data['employee_id'] = employee.id
                            values_data['job_id'] = bonus_accrual.job_id.id
                            values_data['bonus_id'] = bonus_accrual.production_tag_id.id
                            values_data['date'] = from_date.strftime('%Y-%m-%d')
#                         
                        values.append(values_data)
                        from_date = from_date + datetime.timedelta(days=1)
                    employee_bonus['t_values'] = values
                    employee_bonus['total_values'] = format(sum_value, '.2f')
                    employee_bonus['color_code'] = color
                    employee_bonus_values.append(employee_bonus)
#                                     
                template_values['employee_bonus'] = employee_bonus_values
            template_bonus_values = []
            template_bonus = {}
            template_bonus['name'] = production_type.name
            
                
            from_date = date_from
            to_date = date_to
            total_values = []
            sum_tot = 0
            while (to_date >= from_date):
                if filter_production == 'team_member':
            
                    hr_productions = self.env['hr.production'].search([('employee_id', '=', int(current_employee)),
                                                                                 ('period_id', '=', select_period.id)])
                else:
                    hr_productions = self.env['hr.production'].search([('period_id', '=', select_period.id)])
            
                if hr_productions:
                    amount = 0
                    for hr_production in hr_productions:
                        hr_production_line = self.env['hr.production.line'].search([('production_type', '=', production_type.id),
                                                                                    ('job_id.company_id', '=', self.env.user.company_id.id),
                                                                                             ('production_line_id', '=', hr_production.id),
                                                                                             ('date', '=', from_date)])
            
                        for line in hr_production_line:
                            amount += line.amount
                        total_values_data = amount
                else:
                    total_values_data = 0.00
                sum_tot += total_values_data
                total_values.append(format(total_values_data, '.2f'))
                from_date = from_date + datetime.timedelta(days=1)
            template_bonus['t_values'] = total_values
            template_bonus['total_values'] = format(sum_tot, '.2f')
            template_bonus['color_code'] = color
            template_bonus_values.append(template_bonus)
            template_values['template_bonus'] = template_bonus_values
            if has_data:
                production_values.append(template_values)
        result['production_values'] = production_values
# 
        total_template_bonus = {}
        total_template_bonus['name'] = "Total"
        from_date = date_from
        to_date = date_to
        total_values = []
        sum_tot = 0
        while (to_date >= from_date):
            if filter_production == 'team_member':
                hr_productions = self.env['hr.production'].search([('employee_id', '=', int(current_employee)),
                                                                   ('period_id', '=', select_period.id)])
 
            else:
                hr_productions = self.env['hr.production'].search([('period_id', '=', select_period.id)])
 
            if hr_productions:
                amount = 0
                for hr_production in hr_productions:
                    hr_production_line = self.env['hr.production.line'].search([('production_line_id', '=', hr_production.id),
                                                                                         ('date', '=', from_date)])
 
                    for line in hr_production_line:
                        amount += line.amount
                    total_values_data = amount
            else:
                total_values_data = 0.00
            sum_tot += total_values_data
            total_values.append(format(total_values_data, '.2f'))
            from_date = from_date + datetime.timedelta(days=1)
        total_template_bonus['values'] = total_values
        total_template_bonus['total_values'] = format(sum_tot, '.2f')
        total_template_bonus['color_code'] = color
        result['total_production_values'] = total_template_bonus

        from_date = date_from
        to_date = date_to

        while (date_to >= date_from):
            date_new_antr = {}
            date_new_antr['d1'] = date_from.strftime('%a <br />%b %d')
            date_new_antr['d2'] = date_from.strftime('%Y-%m-%d')
            dates.append(date_new_antr)
            date_from = date_from + datetime.timedelta(days=1)
        result['filter_production'] = filter_production
        result['filter_module'] = filter_module
        result['employee_ids'] = employee_ids
        result['total_employee'] = total_employee
        result['current_employee'] = current_employee
        result['employee_name'] = employee_name
        result['employee_number'] = employee_number
        result['dates'] = dates
        result['week_no'] = week_no
        result['week_type'] = week_type
        return result

    def float_time(self, time_value):

        hours, minutes = ([int(x)] for x in str(time_value).split(".", 1))
        if minutes[0] > 60:
            minutes = minutes[0] % 60
            hours = int(hours[0]) + 1
        else:
            minutes = minutes[0]
            hours = hours[0]
        formated_time = str(hours) + ":" + str(minutes)
        return formated_time

    def time_diff(self, a, b):
        a1, a2 = a.split(":")
        b1, b2 = b.split(":")
        x = int(a1) - int(b1)
        y = int(a2) - int(b2)
        if x < 0:
            x = x * -1;
        if y < 0:
            x = x * -1;
        if y >= 60:
            x = x + 1
            y = y - 60
        if len(str(x)) == 1:
            x = "0" + str(x)
        if len(str(y)) == 1:
            y = "0" + str(y)
        return str(x) + ":" + str(y)

