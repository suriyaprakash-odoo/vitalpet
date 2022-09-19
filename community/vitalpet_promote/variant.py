# -*- coding: utf-8 -*-

from odoo import fields, models, api
import operator


class hr_employee2(models.Model):
    _inherit = 'hr.employee'
    _order = 'avg desc'

    prospect_calls = fields.Integer('Prospect Calls', readonly=True, compute='compute_prospect_calls', store=True)
    all_calls = fields.Integer('All Calls', readonly=True, compute='compute_prospect_calls', store=True)
    avg_score = fields.Char('Score', readonly=True, compute='compute_prospect_calls', store=True)
    cost_prospect_calls = fields.Float('Cost of Prospect Calls ($)', default='0.0',group_operator="sum")
    appointments_set = fields.Integer('Appointments Set', readonly=True, compute='compute_appointments_set', store=True)
    avg_call_duration = fields.Float('Average Call Duration', default='0',group_operator="avg", compute='compute_avg_duration',store=True)
    #company_rank = fields.Integer('Company Rank', readonly=True, compute='compute_ranking', group_operator="avg")
    #clinic_rank = fields.Integer('Clinic Rank', readonly=True, compute='compute_ranking')

    phonecalls = fields.One2many('crm.phonecall', 'agent', readonly=True, string='Phone Calls')
    avg = fields.Float('Average Score', compute='compute_prospect_calls',group_operator="avg", readonly=True, store=True)

    @api.one
    @api.depends('phonecalls.duration')
    def compute_avg_duration(self):
        duration=0
        for phonecall in self.phonecalls:
            duration += phonecall.duration
        if self.phonecalls:
            self.avg_call_duration = (duration / len(self.phonecalls)) if self.phonecalls else 0.0

    @api.one
    @api.depends('phonecalls','phonecalls.total_score','phonecalls.listen_rank','phonecalls.agent','phonecalls.call_summary','phonecalls.call_summary.is_lead')
    def compute_prospect_calls(self):
        self.all_calls = len(self.phonecalls)

        pr_calls = 0
        for phonecall in self.phonecalls:
            if phonecall.call_summary.is_lead:
                pr_calls +=  1
            print pr_calls, self.id, ': prospect calls'
        self.prospect_calls = pr_calls


        sum_score=0.0

        for phonecall in self.phonecalls:
            print 'phonecall_id :', phonecall
            if phonecall.listen_rank.total_score :
                sum_score += float(str(phonecall.listen_rank.total_score[0].total_score)[:-2])
        if self.all_calls:
            avg_score = sum_score / self.all_calls
        else :
            avg_score = 0.0
        self.avg = avg_score
        self.avg_score = str(avg_score) + ' %'



    @api.multi
    def compute_ranking(self):
        res={}
        clinic_rank = {}
        rank = 1 #len(self.ids)

        for employee in self.browse(self.ids):
            res[employee.id] = employee.avg

        sorted_dict = sorted(res.items(), key=operator.itemgetter(1),reverse=True)

        print 'sorted_dict :', sorted_dict

        for key in sorted_dict :
            employee = self.browse(key[0])

            employee.company_rank = rank
            rank += 1
            try :
                clinic_rank[employee.company_id.id] += 1
            except :
                clinic_rank[employee.company_id.id] = 1

            employee.clinic_rank = clinic_rank[employee.company_id.id]

    @api.one
    @api.depends('phonecalls.listen_rank.appointment_1', 'phonecalls.agent')
    def compute_appointments_set(self):
        prtcl = ''
        for phonecall in self.phonecalls:
            if phonecall.listen_rank:
                prtcl +=  str(phonecall.listen_rank.appointment_1)
        self.appointments_set = prtcl.count('Yes')

# class prospect_rate(models.Model):
#     _name = 'prospect_rate'
#
#     company_id = fields.Many2one('res.company', string='Clinic')
#     prospects = fields.Integer('Number of leads', compute='compute_prospect_rate')
#     calls = fields.Integer('Number of Total Calls', compute='compute_prospect_rate')

class res_company(models.Model):
    _inherit = 'res.company'

    prospect_calls = fields.Integer('Prospect Calls', readonly=True, compute='compute_prospect_calls', store=True)
    all_calls = fields.Integer('All Calls', readonly=True, compute='compute_prospect_calls', store=True)
    employee_ids = fields.One2many('hr.employee', 'company_id')
    call_ids = fields.One2many('crm.phonecall', 'company_id')
    user_ids = fields.One2many('res.users', 'company_id')
    appointments_set = fields.Integer('Appointments Set', readonly=True, compute='compute_appointments_set', store=True)
    missed_opportunities = fields.Integer('Missed Opportunities', readonly=True, compute='compute_appointments_set', store=True)

    @api.one
    #@api.depends('child_ids.prospect_calls','child_ids.all_calls','employee_ids.all_calls', 'employee_ids.prospect_calls')
    @api.depends('child_ids.prospect_calls','child_ids.all_calls','call_ids','call_ids.call_summary', 'call_ids.call_summary.is_lead')
    def compute_prospect_calls(self):
        pr_calls = all_calls = 0
        for company in self.child_ids:
            pr_calls += company.prospect_calls
            all_calls += company.all_calls
        for phonecall in self.call_ids:
            if phonecall.call_summary.is_lead:
                pr_calls +=  1
            all_calls += 1
        self.all_calls = all_calls
        self.prospect_calls = pr_calls

    @api.one
    @api.depends('child_ids.appointments_set','call_ids.appointments_sum','prospect_calls')
    def compute_appointments_set(self):
        apts_set = 0
        for company in self.child_ids:
            apts_set += company.appointments_set
        for calls in self.call_ids:
            apts_set += calls.appointments_sum
        self.appointments_set = apts_set
        self.missed_opportunities = self.prospect_calls - self.appointments_set

#     @api.one
#     @api.depends('appointments_set','prospect_calls')
#     def compute_missed_opportunities(self):
#         self.missed_opportunities = self.prospect_calls - self.appointments_set


#Code coming from calls.py

class call_campaign(models.Model):
    _name = 'call.campaign'

    #api_wizard_id = fields.Many2one('api.wizard')
    campaign_name = fields.Char('Campaign name', required=True)
    company_id = fields.Many2one('res.company', 'Company')
    provider_id = fields.Many2one('promote.settings.source', 'Provider')
    enable_inb_calls = fields.Boolean('Inbound Calls', default=True)
    enable_sms = fields.Boolean('SMS', default=True)
    phone_number_char = fields.Char('Phone Number (10 digits)',size=10, required=True )
    forward_number_char = fields.Char('Forward Number (10 digits)', size=10)
    call_frequency = fields.Integer('Inbound Call Freq')
    trunk_ID = fields.Char('Trunk ID')

    @api.multi
    @api.onchange('company_id', 'phone_number_char' )
    def onchange_company_id(self):
        print 'triggered onchange company id for calls'
        calls = self.env['crm.phonecall'].search([('TrackingNumber','=',self.phone_number_char)])

        if calls:
            print 'if', calls
            for call in calls:
                call.write({'company_id' : int(self.company_id.id)})
        else:
            print 'else calls not found', calls
