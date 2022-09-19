# -*- coding: utf-8 -*-

from odoo import fields, models, api
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import except_orm


class promote_settings_source(models.Model):
    _name = 'promote.settings.source'

    name = fields.Char('Name')
    api_url = fields.Char('API URL')
    api_key = fields.Char('Master Account (API Key)')
    account_sid = fields.Char('Account SID')
    auth_token = fields.Char('Auth Token')

class call_summary(models.Model):
    _name = 'call.summary'

    name = fields.Char('Name')
    is_lead = fields.Boolean('Lead')

class score_category(models.Model):
    _name='score.category'

    type = fields.Selection([('1 Appr. Gr.','Appropriate Greeting'), ('2 Cntct Info','Contact Info.'), ('3 Nds Anlys.','Needs Anlysis'), ('4 Prblm. S.','Problem Solving'), ('5 Prtcl','Appointment'), ('6 C. Etqt','Call Etiquette'), ('7 Cl. Call','Closing Call')])
    category_perc = fields.Float('percentage')
    score_per_category = fields.Float('Average Score by Category ( %)', group_operator="avg", default='0.0', store='True') #compute='compute_score_category',
    total_score_id = fields.Many2one('total.score', ondelete='cascade')
    company_id = fields.Many2one('res.company', store=True, string='Practice')

    # @api.one
    # @api.depends('total_score_id.total_score')
    # def compute_score_category(self):
    #     print 'start compute score category', self.type
    #     if self.type=='1 Appr. Gr.':
    #         self.score_per_category = float(self.total_score_id.total_greeting[:-2]) * 100 / 15
    #     if self.type=='2 Cntct Info':
    #         self.score_per_category = float(self.total_score_id.total_contact_info[:-2]) * 100 / 10
    #     if self.type=='3 Nds Anlys.':
    #         self.score_per_category = (float(self.total_score_id.total_needs[:-2]) + float(self.total_score_id.total_problem[:-2])) * 100 / 15
    #     if self.type=='4 Prblm. S.':
    #         self.score_per_category = float(self.total_score_id.total_problem[:-2] ) * 100 / 10
    #     if self.type=='5 Prtcl':
    #         self.score_per_category = float(self.total_score_id.total_protocol[:-2]) * 100 / 25
    #     if self.type=='6 C. Etqt':
    #         self.score_per_category = float(self.total_score_id.total_etiquette[:-2]) * 100 / 20
    #     if self.type=='7 Cl. Call':
    #         self.score_per_category = float(self.total_score_id.total_closure[:-2]) * 100 / 15


class call_scorecard(models.Model):
    _name = 'call.scorecard'

    #score_by_category = fields.One2many('score.category','scorecard_id')#,default= [(0, 0, {'type':'1gr','category_perc':15.0}),(0, 0, {'type':'2ci','category_perc':10.0}),(0, 0, {'type':'3na','category_perc':20.0}),(0, 0, {'type':'5prtcl','category_perc':20.0}),(0, 0, {'type':'6etqt','category_perc':20.0}),(0, 0, {'type':'7cc','category_perc':15.0}),])

    total_score = fields.One2many('total.score', 'scorecard_id', readonly=True, string='Total Score', default= [(0, 0, {'total_greeting':'0 %','total_contact_info':'0 %','total_needs':'0 %','total_problem':'0 %','total_protocol':'0 %','total_etiquette':'0 %','total_closure':'0 %','total_score':'0 %'})],)
    total_score_str = fields.Char('Total Score',compute='compute_totals', store='True')

    phonecall_id = fields.Many2one('crm.phonecall', 'Client Phonecall', ondelete='cascade')
    company_id = fields.Many2one('res.company', store=True, string='Practice', related='phonecall_id.company_id')

    greeting_1 = fields.Selection([('Yes','Yes'), ('no','No')], required=True,string='The Team Member identified themselves to the customer')
    greeting_2 = fields.Selection([('Yes','Yes'), ('no','No')], required=True,string='The Team Member mentioned their company name')
    greeting_3 = fields.Selection([('Yes','Yes'), ('no','No')], required=True,string='The Team Member thanked the customer for calling')

    contact_info_1 = fields.Selection([('Yes','Yes'), ('no','No')], required=True,string='The Team Member asked for the caller’s first and last name')
    contact_info_2 = fields.Selection([('Yes','Yes'), ('no','No')], required=True,string="If existing client, Team Member asked if any of their information has changed. If new client, Team Member attempted to retrieve the caller's telephone number.")
    contact_info_3 = fields.Selection([('Yes','Yes'), ('no','No')], required=True,string='The Team Member attempted to retrieve the caller’s email address')
    contact_info_4 = fields.Selection([('Yes','Yes'), ('no','No')], required=True,default='no',string='The Team Member attempted to retrieve the caller’s home address')

    needs_1 = fields.Selection([('Yes','Yes'), ('no','No')], required=True,string='The Team Member answered the customer’s question correctly')
    needs_2 = fields.Selection([('Yes','Yes'), ('no','No')], required=True,string='The Team Member adequately addressed the caller’s needs')
    needs_3 = fields.Selection([('Yes','Yes'), ('no','No')], required=False,string='The Team Member confirmed that the caller’s needs were met')

    is_problem = fields.Boolean('Problem Encountred')

    problem_solving_1 = fields.Selection([('Yes','Yes'), ('no','No')], string='The Team Member apologized for the issue, inconvenience or cost associated with the problem')
    problem_solving_2 = fields.Selection([('Yes','Yes'), ('no','No')], string='The Team Member took ownership of the problem')
    problem_solving_3 = fields.Selection([('Yes','Yes'), ('no','No')], string='The Team Member asked pertinent questions to accurately diagnose the problem')
    problem_solving_4 = fields.Selection([('Yes','Yes'), ('no','No')], string='The Team Member confirmed that the issue was adequately addressed')

    appointment_1 = fields.Selection([('Yes','Yes'), ('no','No')], required=True,string='The Team Member succeeded in booking an appointment')
    appointment_2 = fields.Selection([('Yes','Yes'), ('no','No')], required=True,string='The Team Member asked the customer to book an appointment')


    protocol_1 = fields.Selection([('Yes','Yes'), ('no','No')], required=True,string='The Team Member attempted to book an appointment when appropriate')
    protocol_2 = fields.Selection([('Yes','Yes'), ('no','No')], required=True,string='The Team Member leveraged upselling and cross-selling opportunities when appropriate')
    protocol_3 = fields.Selection([('Yes','Yes'), ('no','No')], required=True,string='The Team Member highlighted marketing campaigns and promotions when appropriate')

    etiquette_1 = fields.Selection([('Yes','Yes'), ('no','No')], required=True,string='The Team Member received the caller’s permission to place them on hold before doing so')
    etiquette_2 = fields.Selection([('Yes','Yes'), ('no','No')], required=True,string='The Team Member limited the duration of hold time to an appropriate amount')
    etiquette_3 = fields.Selection([('Yes','Yes'), ('no','No')], required=True,string='The Team Member was friendly, polite and professional')
    etiquette_4 = fields.Selection([('Yes','Yes'), ('no','No')], required=True,string='The Team Member avoided long silences during the call')
    etiquette_5 = fields.Selection([('Yes','Yes'), ('no','No')], required=True,string='The Team Member did not interrupt or talk over the customer')
    etiquette_6 = fields.Selection([('Yes','Yes'), ('no','No')], required=True,string='The Team Member remained confident throughout the call')
    etiquette_7 = fields.Selection([('Yes','Yes'), ('no','No')], required=True,string='The Team Member expressed empathy when appropriate')

    closure_1 = fields.Selection([('Yes','Yes'), ('no','No')], required=True,string='The Team Member confirmed that the caller’s needs were met.')
    closure_2 = fields.Selection([('Yes','Yes'), ('no','No')], required=True,string='The Team Member thanked the customer for calling')

    recording_link =fields.Char('Recording Link',help='link to recording',related='phonecall_id.RecordingLink', store=True)

    #compute_total_float = fields.Float('Computed Total (%)', compute='compute_totals',store=True)

    @api.one
    @api.depends('total_score.total_score')
    def compute_totals(self):
        print 'compute totals str triggered'
        if self.total_score.total_score:
            self.total_score_str = self.total_score[0].total_score
        else :
            self.total_score_str = '-'

    @api.multi
    def write(self,vals):
        print 'vals :', vals

        rec = super(call_scorecard, self).write(vals)

        self.phonecall_id.write({'report_date':datetime.today()})

        greeting = self.greeting_1 + self.greeting_2 + self.greeting_3
        contact_info = self.contact_info_1 + self.contact_info_2

        print 'self.appointment_1 :', self.appointment_1
        #appointment = str(self.appointment_1) #+str(self.appointment_1)+ self.protocol_1 + self.protocol_2 + self.protocol_3
        etiquette = self.etiquette_1 + self.etiquette_2 + self.etiquette_3 + self.etiquette_4 + self.etiquette_5 + self.etiquette_6 + self.etiquette_7
        closure = self.closure_1 + self.closure_2

        print 'greeting', greeting
        print 'contact_info', contact_info

        gr_count = greeting.count('Yes') * 5.0
        ci_count = contact_info.count('Yes') * 5.0
        apptmnt_count = str(self.appointment_1).count('Yes') * 25.0 + str(self.appointment_2).count('Yes') * 15.0

        is_prospect = self.phonecall_id.prospect_calls_rate

        ptcl_count = apptmnt_count * is_prospect
        etqt_count = etiquette.count('Yes') * 2.86
        clsr_count = closure.count('Yes')* 7.5
        total_score = gr_count + ci_count + ptcl_count + etqt_count + clsr_count

        if not is_prospect :
            total_score = total_score / 0.6

        self.total_score[0].total_greeting = '%.1f' % ( gr_count) + ' %'
        self.total_score[0].total_contact_info = '%.1f' % ( ci_count) + ' %'
        self.total_score[0].total_protocol = '%.1f' % ( ptcl_count) + ' %'
        self.total_score[0].total_etiquette = '%.1f' % ( etqt_count) + ' %'
        self.total_score[0].total_closure = '%.1f' % ( clsr_count) + ' %'
        self.total_score[0].total_score = '%.1f' % (total_score) + ' %'
        self.total_score[0].total_score_str = str(total_score) + ' %'


        print 'self.score_by_category :', self.total_score[0].score_by_category

        self.total_score[0].score_by_category[0].score_per_category = gr_count * 100 / 15
        self.total_score[0].score_by_category[1].score_per_category = ci_count * 100 / 10
        self.total_score[0].score_by_category[2].score_per_category = ptcl_count * 100 / 40
        self.total_score[0].score_by_category[3].score_per_category = etqt_count * 100 / 20
        self.total_score[0].score_by_category[4].score_per_category = clsr_count * 100 / 15

        for i in range(5):
            self.total_score[0].score_by_category[i].company_id = self.phonecall_id.company_id.id

        #rec['company_id'] = self.phonecall_id.company_id.id
        return rec

class crm_phonecall(models.Model):
#     _inherits = {'call.scorecard': "listen_rank"}
    _inherit= 'crm.phonecall'
    _order = 'date_of_call desc'

    date_of_call = fields.Datetime('Date and time of Call')
    duration = fields.Float('Duration', help='Duration in minutes and seconds.', group_operator = 'avg')
    name = fields.Char('Notes', required=False)
    listen_date = fields.Date(string="Listen Date")
    call_summary = fields.Many2one('call.summary', string='Call Summary')
    call_source = fields.Char('Call Source')
    client = fields.Many2one('res.partner', string='Client')
    client_status = fields.Selection([('new','New'), ('current','Current')], 'Client Status')
    company_id = fields.Many2one('res.company', string='Practice')#, store=True, related='agent.company_id')
    agent = fields.Many2one('hr.employee', 'Team Member', domain="[('company_id','=',company_id)]")
    listen_rank = fields.Many2one('call.scorecard', string='Listen & Rank')#, domain=[('greeting_1', '=', 'whatever')])
    total_score = fields.Char('Total Score', store=True, default='-', related='listen_rank.total_score_str')
    total_score_float = fields.Float('Total Score (%)', compute='compute_total_score',group_operator = 'avg',store=True)
    report_date = fields.Datetime(string="Report Date")

    _sql_constraints = [
        ('RecordingLink', 'unique(RecordingLink)', 'One of the recording links you are trying to import already exists.'),
    ]

    DateOfCall=fields.Char('Date of Call',help='Timestamp of end of call in PST')
    CallerId=fields.Char('Caller ID',help='Caller ID of originating caller')
    US_State=fields.Char('State',help='US State of originating caller')
    CallRecipient=fields.Char('Call Recipient',help='Call forwarding number')
    TrackingNumber=fields.Char('Tracking Number',help='Call tracking number')
    CallDuration=fields.Char('Call duration',help='Duration of entire call')
    CallDurationSecs=fields.Char('Call duration in secs',help='Duration Secs of entire call')
    Disposition=fields.Char('Disposition',help='call disposition set by user through the interface')
    RecordingLink=fields.Char('Recording Link',help='link to recording')
    #SubAccountId=fields.Char('Sub Account Id',help='ID of Sub Account, if exists for campaign')
    #GroupId=fields.Char('Group Id',help='ID of Group, if exists for campaign')
    #SubGroupId=fields.Char('SubGroup Id',help='ID of Sub Group, if exists for campaign')
    #IvrKey=fields.Char('Ivr Key',help='IVR key pressed by caller, if campaign uses an IVR')
    #ready = fields.Boolean('Ready', help='Ready to be integrated in the logged calls; if all the VitalPet Audit Variables are filled.')

    @api.one
    def your_function(self):
        logged_calls = self.env['crm.phonecall']
        #for item in self:
            #print 'context :', context
        logged_calls.create({
                "date":self.DateOfCall,
                "listen_date":self.listen_date,
                "call_summary":self.call_summary.id,
                "agent":self.agent.id,
                "call_source":self.RecordingLink,
                "client_status":self.client_status,
                "duration":self.CallDurationSecs,
                            } )
        self.is_pulled = True

    @api.one
    def update_company_id(self):
        if self.TrackingNumber:
            self._cr.execute("select company_id from call_campaign WHERE phone_number_char='%s' LIMIT 1" % (self.TrackingNumber))
            company_id = self.env.cr.fetchone()

            self.company_id = company_id

    @api.multi
    def open_scorecard(self):
        print 'check if call summary is set'
        if not(self.call_summary):
            print 'no call summary'
            raise except_orm('Error', 'Please Set the Call Summary first.')

        print 'listen_rank.id :', self.listen_rank.id


        if self.listen_rank.id:
            listen_rank = self.listen_rank
        else:
            listen_rank = self.env["call.scorecard"].create({
            'greeting_1' : 'no',
            'greeting_2' : 'no',
            'greeting_3' : 'no',

            'contact_info_1' : 'no',
            'contact_info_2' : 'no',
            'contact_info_3' : 'no',
            'contact_info_4' : 'no',

            'needs_1' : 'no',
            'needs_2' : 'no',
            #'needs_3' : 'no',

            'problem_solving_1' : 'no',
            'problem_solving_2' : 'no',
            'problem_solving_3' : 'no',
            'problem_solving_4' : 'no',

            'appointment_1' : 'no',
            'appointment_2' : 'no',
            'protocol_1' : 'no',
            'protocol_2' : 'no',
            'protocol_3' : 'no',

            'etiquette_1' : 'no',
            'etiquette_2' : 'no',
            'etiquette_3' : 'no',
            'etiquette_4' : 'no',
            'etiquette_5' : 'no',
            'etiquette_6' : 'no',
            'etiquette_7' : 'no',

            'closure_1' : 'no',
            'closure_2' : 'no',
            'phonecall_id': self.id,
            'recording_link': self.RecordingLink})


            print 'listen_rank, recording_link :', listen_rank  , self.RecordingLink
            self.listen_rank = listen_rank

        ctx={}
        ctx.update({ 'default_model':'crm.phonecall', 'default_phonecall_id': self.id , 'default_recording_link' : self.RecordingLink,} )

        print 'ctx :' , ctx
        return { 'type': 'ir.actions.act_window',
                'name': 'Call Scorecard',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'call.scorecard',
                'res_id': listen_rank.id,
                #'views': [( %(call_scorecard_form), 'form')],
                #'view_id': call_scorecard_form,
                'target': 'current',
                'context': ctx, }

    @api.one
    @api.depends('total_score')
    def compute_total_score(self):
            try:
                self.total_score_float = self.total_score[:-2]
            except:
                self.total_score_float = 0.0
                self.total_score = '-'
            return False


    #LEADERBOARD FIELDS AND METHODS
    call_month = fields.Char('Call month and Year', readonly=True, compute='compute_call_month',store=True)
    monthly_total_calls = fields.Integer('Monthly Calls', readonly=True, compute='compute_rates',store=True)
    monthly_total_leads = fields.Integer('Monthly Prospect calls', readonly=True, compute='compute_rates',store=True)
    prospect_calls_rate = fields.Float('Monthly Prospect Call Rate', group_operator="avg",readonly=True, compute='compute_rates',store=True)
    appointments_rate = fields.Float('Monthly Appointment Rate', readonly=True,group_operator="avg", compute='compute_rates',store=True)
    missed_opportunities_rate = fields.Float('Monthly Missed Opportunities Rate',group_operator="avg", readonly=True, compute='compute_rates',store=True)

    prospect_calls_sum = fields.Float('Monthly Prospect Call Total', group_operator="sum",readonly=True, compute='compute_rates',store=True)
    appointments_sum = fields.Float('Monthly Appointment Total', readonly=True,group_operator="sum", compute='compute_rates',store=True)
    appointments_perc = fields.Float('Appts (%)', readonly=True,group_operator="avg", compute='compute_rates',store=True)


    cost_prospect_calls = fields.Float('Cost of Prospect Calls ($)', default='0.0',group_operator="sum")

    @api.one
    @api.depends('date_of_call')
    def compute_call_month(self):
        if self.date_of_call:
            date = datetime.strptime(self.date_of_call, DEFAULT_SERVER_DATETIME_FORMAT)

            self.call_month = str(date.strftime('%Y-%m'))

    @api.one
    def compute_appt_rate(self):
        if self.call_summary.is_lead:
            if self.listen_rank.appointment_1=='Yes':
                self.appointments_perc = 100
            else:
                self.appointments_perc = 0
        else:
                self.appointments_perc = 0

    @api.one
    @api.depends('call_month','call_summary','call_summary.is_lead','listen_rank.appointment_1','listen_rank')
    def compute_rates(self):
        print 'triggered compute rates'
        if self.call_summary.is_lead:
                self.prospect_calls_rate = 1
                self.prospect_calls_sum = 1

                if self.listen_rank.appointment_1=='Yes':
                    self.appointments_rate = 1
                    self.appointments_sum = 1
                    self.missed_opportunities_rate = 0.0
                    self.appointments_perc = 100

                else :
                    self.appointments_rate = 0.0
                    self.appointments_sum = 0.0
                    self.missed_opportunities_rate = 1
                    self.appointments_perc = 0

        else :
                self.prospect_calls_rate = 0.0
                self.appointments_rate = 0.0
                self.missed_opportunities_rate = 0.0
                self.appointments_perc = 0
