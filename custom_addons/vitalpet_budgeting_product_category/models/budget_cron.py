from odoo import api, fields, models, _
import time
import datetime
from datetime import date
from datetime import timedelta
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta

def strToDate(dt):
    dt_date = date(int(dt[0 :4]), int(dt[5 :7]), int(dt[8 :10]))
    return dt_date




class BudgetCron(models.Model):
    _name = "budget.cron"
    _description = "Budget Cron"
    _rec_name = 'sch_date'

    child_ids = fields.One2many('budget.cron.lines', 'budget_cron_id', 'Budget to run')
    sch_date = fields.Date('Today', required = True, default=fields.Datetime.now)
    type = fields.Selection([('auto', 'Auto'), ('manual', 'Manual'), ], 'Schedules', required = True, default='auto')
    schedule_for = fields.Selection([('all', 'All'), ('specific', 'Specific'), ], string='Schedule For', required = True, default='all')
    company_ids = fields.Many2many('res.company', 'budget_cron_rel', 'cron_id', 'company_id', string='Company')
    

    # _defaults = {'is_rescheduled' : False, 'sch_date' : , 'type' : 'auto', }

    @api.model
    def create(self, vals):
        cron_obj = self.search([])
        if cron_obj:
            raise UserError(_('Cannot create more than one Cron.'))

        return super(BudgetCron, self).create(vals)

    def update_budget_cron_line(self,cur_obj):
        date_list = []
        current_date = date.today()
        i=0
        inc=0
        for cron_line in cur_obj.child_ids:
            if cron_line.status=='No':
                inc+=1
        if inc==0:
            
            cur_obj.sch_date= current_date + relativedelta(days=1)
                      
            mail_content = "Hi Team, <br>The Budget report sucessfully updated on " +str(current_date)+\
                           ". Please check it<br><br>"+\
                           "<table style='width:100%;border-collapse: collapse;' border='1px'><tr><th>Year</th><th>Month</th><th>Status</th></tr>"
            for cron_line in cur_obj.child_ids:
                mail_content +="<tr><td>"+cron_line.year+"</td><td>"+cron_line.month+"</td><td>"+cron_line.status+"</td></tr>" 
                       
            mail_content +="</table>"          
            main_content = {
                'subject': "Budget Report in Vitalpet",
                'author_id': self.env.user.partner_id.id,
                'body_html': mail_content,
                'email_to': 'mani.jayaraman@pptservices.com,rizwan@pptservices.com,suriyaprakash.subramanian@pptservices.com',
            }            
            self.env['mail.mail'].create(main_content).send()
            
            for cron_line in cur_obj.child_ids:
                cron_line.unlink()
            
            for line in range(0,5):
                date_append = current_date + relativedelta(months=-1*line)
                date_list.append((date_append.month, date_append.year))
                
                self.env['budget.cron.lines'].create({
                    'month':date_append.month,
                    'year':date_append.year,
                    'status':'No',
                    'budget_cron_id':cur_obj.id
                })

    @api.multi
    def cron_budget_calc(self,cron=False):
        company_lst = []
        today = date.today()
        cur_obj = self.search([], limit=1)
        if not cur_obj:
            raise UserError(_('Budget status is not created'))
#             cur_obj = self.create({'sch_date' : today, 'type' : 'manual', 'schedule_for': 'all'})
            
        company_obj = self.env['res.company'].search([])
        if cur_obj.schedule_for == 'all':
            for loop in company_obj:
                company_lst.append(loop.id)

        if cur_obj.schedule_for == 'specific':
            for loop in cur_obj.company_ids:
                company_lst.append(loop.id)
                
        if datetime.datetime.strptime(cur_obj.sch_date, '%Y-%m-%d').date()<today:            
            mail_content = "Hello  Mani, <br>The Budget report is not updated properly on " +str(cur_obj.sch_date)+\
                           ". Please check it<br><br>"+\
                           "<table style='width:100%;border-collapse: collapse;' border='1px'><tr><th>Year</th><th>Month</th><th>Status</th></tr>"
            for cron_line in cur_obj.child_ids:
                mail_content +="<tr><td>"+cron_line.year+"</td><td>"+cron_line.month+"</td><td>"+cron_line.status+"</td></tr>" 
                       
            mail_content +="</table>"          
            main_content = {
                'subject': "Budget is not updated Properly in Vitalpet",
                'author_id': self.env.user.partner_id.id,
                'body_html': mail_content,
                'email_to': 'mani.jayaraman@pptservices.com,rizwan@pptservices.com,suriyaprakash.subramanian@pptservices.com',
            }            
            self.env['mail.mail'].create(main_content).send()
            cur_obj.sch_date=today
            
        if cur_obj.sch_date == str(today):
            i=0
            for cur_obj_line in cur_obj.child_ids:
                budget_line_obj = self.env['budget.cron.lines'].browse(cur_obj_line.id)
                if i==0:
                    if int(budget_line_obj.year) > 2017:
                        if budget_line_obj.status == 'No':
                            now = datetime.datetime.now()
                            budget_line_obj.write({'status' : 'Yes'})
                            budget_line = self.env['budget.category.lines'].budget_calc(budget_line_obj.year,budget_line_obj.month,company_lst)
                            i+=1
        
        self.update_budget_cron_line(cur_obj)

        return True
                        
                      
class BudgetCronLines(models.Model):
    _name = "budget.cron.lines"
    _description = "Budget Cron lines"
    _order= 'year asc, month asc'
    
    budget_cron_id = fields.Many2one('budget.cron', 'Budget Cron ID')
    year = fields.Char('Year', size = 4)
    month = fields.Char('Month', size = 2)
    #status = fields.Selection([('yes','Yes'),('no', 'No')], string='Budget Status')
    status = fields.Char('Budget Status', size = 3)
