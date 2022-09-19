# -*- coding: utf-8 -*-

from odoo import fields, models, api
from datetime import datetime

class total_score(models.Model):
    _name = 'total.score'

    score_by_category = fields.One2many('score.category','total_score_id',default= [(0, 0, {'type':'1 Appr. Gr.','category_perc':15.0}),(0, 0, {'type':'2 Cntct Info','category_perc':10.0}),(0, 0, {'type':'5 Prtcl','category_perc':20.0}),(0, 0, {'type':'6 C. Etqt','category_perc':20.0}),(0, 0, {'type':'7 Cl. Call','category_perc':15.0}),])

    scorecard_id = fields.Many2one('call.scorecard', 'Call Scorecard', ondelete='cascade')

    total_greeting = fields.Char('Greeting', compute='compute_totals',store='True')#,compute='_compute_total_greeting')
    total_contact_info = fields.Char('Contact Info', compute='compute_totals',store='True')
    total_needs = fields.Char('Needs Analysis', compute='compute_totals',store='True')
    total_problem = fields.Char('Problem Solving', compute='compute_totals',store='True')
    total_protocol = fields.Char('Appointment', compute='compute_totals',store='True')
    total_etiquette = fields.Char('Call Etiquette', compute='compute_totals',store='True')
    total_closure = fields.Char('Closure', compute='compute_totals',store='True')
    total_score = fields.Char('Total Score', compute='compute_totals',store='True')


    @api.one
    # @api.depends('scorecard_id.greeting_1','scorecard_id.greeting_2','scorecard_id.greeting_3',
    # 'scorecard_id.contact_info_1','scorecard_id.contact_info_2',
    # 'scorecard_id.appointment_1','scorecard_id.appointment_2',
    # 'scorecard_id.etiquette_1', 'scorecard_id.etiquette_2', 'scorecard_id.etiquette_3' ,'scorecard_id.etiquette_4' ,'scorecard_id.etiquette_5' ,'scorecard_id.etiquette_6', 'scorecard_id.etiquette_7' ,
    # 'scorecard_id.closure_1', 'scorecard_id.closure_2')
    def compute_totals(self):

        greeting = self.scorecard_id.greeting_1 + self.scorecard_id.greeting_2 + self.scorecard_id.greeting_3
        contact_info = self.scorecard_id.contact_info_1 + self.scorecard_id.contact_info_2 #+ self.scorecard_id.contact_info_3 + self.scorecard_id.contact_info_4
        #needs = self.scorecard_id.needs_1 + self.scorecard_id.needs_2 #+ self.scorecard_id.needs_3
        #problem_solving = self.scorecard_id.problem_solving_1 + self.scorecard_id.problem_solving_2 + self.scorecard_id.problem_solving_3 + self.scorecard_id.problem_solving_4

        print 'self.scorecard_id.appointment_1 :', self.scorecard_id.appointment_1
        appointment = str(self.scorecard_id.appointment_1) #+str(self.scorecard_id.appointment_1)+ self.scorecard_id.protocol_1 + self.scorecard_id.protocol_2 + self.scorecard_id.protocol_3
        etiquette = self.scorecard_id.etiquette_1 + self.scorecard_id.etiquette_2 + self.scorecard_id.etiquette_3 + self.scorecard_id.etiquette_4 + self.scorecard_id.etiquette_5 + self.scorecard_id.etiquette_6 + self.scorecard_id.etiquette_7
        closure = self.scorecard_id.closure_1 + self.scorecard_id.closure_2

        print 'greeting', greeting
        print 'contact_info', contact_info

        gr_count = greeting.count('Yes') * 5.0
        ci_count = contact_info.count('Yes') * 5.0
        apptmnt_count = str(self.scorecard_id.appointment_1).count('Yes') * 25.0 + str(self.scorecard_id.appointment_2).count('Yes') * 15.0

        is_prospect = self.scorecard_id.phonecall_id.prospect_calls_rate

        ptcl_count = apptmnt_count * is_prospect
        etqt_count = etiquette.count('Yes') * 2.86
        clsr_count = closure.count('Yes')* 7.5
        total_score = gr_count + ci_count + ptcl_count + etqt_count + clsr_count

        if not is_prospect :
            total_score = total_score / 0.6

        self.total_greeting = '%.1f' % ( gr_count) + ' %'
        self.total_contact_info = '%.1f' % ( ci_count) + ' %'
        #self.total_needs = '%.1f' % ( nds_count) + ' %'
        #self.total_problem = '%.1f' % ( ps_count) + ' %'
        self.total_protocol = '%.1f' % ( ptcl_count) + ' %'
        self.total_etiquette = '%.1f' % ( etqt_count) + ' %'
        self.total_closure = '%.1f' % ( clsr_count) + ' %'
        self.total_score = '%.1f' % (total_score) + ' %'



        self.scorecard_id.total_score_str = str(total_score) + ' %'

        self.scorecard_id.company_id = self.scorecard_id.phonecall_id.company_id.id
        self.scorecard_id.phonecall_id.write({'report_date':datetime.today()})

        print 'self.score_by_category :', self.score_by_category

#         try:
        self.score_by_category[0].score_per_category = gr_count * 100 / 15
        self.score_by_category[1].score_per_category = ci_count * 100 / 10
        #self.score_by_category[2].score_per_category = (nds_count + ps_count) * 100 / 15
        self.score_by_category[2].score_per_category = ptcl_count * 100 / 40
        self.score_by_category[3].score_per_category = etqt_count * 100 / 20
        self.score_by_category[4].score_per_category = clsr_count * 100 / 15

        for i in range(5):
            self.score_by_category[i].company_id = self.scorecard_id.phonecall_id.company_id.id

#     self.total_score[0].total_score = self.total_score[0].total_greeting + self.total_score[0].total_contact_info + self.total_score[0].total_needs + self.total_score[0].total_problem_solving + self.total_score[0].total_protocol + self.total_score[0].total_etiquette +self.total_score[0].total_closure
#         if self.scorecard_id.is_problem :
#             try :
#                 self.score_by_category[6].score_per_category = ps_count * 100 / 10
#                 print 'before write '
#             except:
#                 self.write({ 'score_by_category' :[(0, 0, {'type':'4 Prblm. S.','score_per_category': ps_count * 100 / 10,'category_perc':10.0})]})
#             print 'After write '
        #raise except_orm(('Done !'),_('Your total Score is %s/100.') % (total_score))
        return True
