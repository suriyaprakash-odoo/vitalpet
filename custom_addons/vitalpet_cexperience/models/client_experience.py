# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api , _
from datetime import datetime,timedelta
from datetime import date
from odoo.exceptions import UserError, ValidationError
import re
import uuid
from urlparse import urljoin
from odoo.addons.website.models.website import slug


DOCUMENTS = [
    {'doc_name':"Estimate",'count':0},
    {'doc_name':"Medical Record",'count':0},
    {'doc_name':"Invoice",'count':0},
    {'doc_name':"Client Send Home Materials",'count':0}
    ]

class ClientExperience(models.Model):
    _name = "experience.visit"
    _description = 'Experience Visit'
    _inherit = ['mail.thread']
    
    
    @api.model
    def default_get(self, fields):
        res = super(ClientExperience, self).default_get(fields)
        line_ids = []
        vals = ({'doc_name':"Estimate"})
        line_ids.append((0, 0, vals))
#         res.update({'documents_ids': [(0, 0, vals)]})  
        return res
  
    name = fields.Char(compute='_compute_name')
    company_id = fields.Many2one("res.company",string="Company")
    doctor_id = fields.Many2one("hr.employee",string="Doctor",domain="[('job_id','ilike','Veterinarian'),('company_id','=',company_id)]")
    tech_id = fields.Many2one("hr.employee",string="Technician",domain="[('job_id','ilike','Technician'),('company_id','=',company_id)]")
    rec_in_id = fields.Many2one("hr.employee",string="Admitting Receptionist",domain="[('job_id','ilike','Service Coordinator'),('company_id','=',company_id)]")
    rec_out_id = fields.Many2one("hr.employee",string="Check Out Receptionist",domain="[('job_id','ilike','Service Coordinator'),('company_id','=',company_id)]")
    visit_date = fields.Date('Visit Date')
    visit_time = fields.Datetime("Time Of Visit")
    pims_record = fields.Char("Record Number")
    invoice_amount = fields.Monetary("Total Invoice Amount")
    client_name = fields.Char("Client Full Name")
    client_address = fields.Char("Client Address")
    client_email = fields.Char("Client Email Address")
    client_mobile_phone = fields.Char("Client Mobile")
    patient_name = fields.Char("Pet Name")
    patient_age = fields.Integer("Age Of Pets(months)")
    patient_species = fields.Selection([
            ('canine', 'Canine'),
            ('feline', 'Feline'),
            ('others', 'Others'),
                ],string="Species")
    currency_id = fields.Many2one("res.currency",default=lambda self: self.env.user.company_id.currency_id)
    state_bar = fields.Selection([
            ('draft', 'Draft'),
            ('validate', 'Validate'),
                ],default='draft',track_visibility='onchange',string="Status")
    disc_per = fields.Float("Discounts(%)",store = True)
    non_inc_tot = fields.Float("Non Invoiced")
    cron_updated = fields.Boolean("Mail Sent")
    patient_cal = fields.Boolean("")
    board_review = fields.Selection([('yes', 'Board Review'), 
                                ('no', 'No Board Review')
                                  ], string="Board Review",default = "no")
    board_review_track = fields.Selection([('yes', 'Board Review'), 
                                ('no', 'No Board Review')
                                  ], string="Board Review",track_visibility='onchange')
    visit_review_analysis = fields.Integer("Visit Review Analysis",default=1)
    services_active = fields.Boolean("Services Not Invoiced") 
    discount_services_active = fields.Boolean("Discounted Services") 
    cron_board = fields.Boolean("Board Review")
    active = fields.Boolean('Active', default=True)
#     reason_visit_ids_int = fields.Integer("Count Id")

#     PRE-EXAM 
#     reason_visit_ids = fields.Many2many("reason.visit",string="Reason Visit")
    wellness = fields.Boolean("Wellness")
    surgery = fields.Boolean("Surgery")
    sick = fields.Boolean("Sick")
    day_time_emergency = fields.Boolean("Daytime Emergency")
    after_hrs_emergency = fields.Boolean("After Hours Emergency")
    other = fields.Boolean("Other")
    new_client = fields.Boolean("New Client?")
    practice_tour = fields.Boolean(string="Was Practice Tour Performed?")
    records_transfer = fields.Boolean(string="Were Records Transferred?")
    former_practice = fields.Char("Which Practice?")
    surgery_type = fields.Char("Surgery Type")
    presenting_complaint = fields.Char("Presenting Complaint")
    offer_nailtrim = fields.Boolean("Was Nail Trim Performed?")
    offer_promotion = fields.Boolean("Was Current Promotion Booked?")
    offer_daycamp = fields.Boolean("Was At Least 1 Day of Camp Scheduled?")
    offer_daycamp_sett = fields.Boolean(compute='day_camp_settings')
    offer_grooming_sett = fields.Boolean(compute='day_camp_settings')
    offer_bath_accept = fields.Boolean("Was Bath Performed?")
    offer_anal_gland_accept = fields.Boolean("Did Patient Receive Anal Gland Expression?")
    groomer_introduction = fields.Boolean("Was At Least One Grooming Scheduled?")
    compliance_vaccines = fields.Selection([('up to date', 'Up to Date'), 
                                ('overdue', 'Overdue')
                                  ], string="Vaccines")
    offer_vaccines = fields.Boolean(string="Were Vaccines Administered During Visit?")
    compliance_parasiticide = fields.Selection([('up to date', 'Up to Date'), 
                                ('overdue', 'Overdue')
                                  ], string="Paracitides")
    offer_parasiticide = fields.Boolean(string="Were Paracitides Purchased?")
    compliance_diagnostics = fields.Selection([('up to date', 'Up to Date'), 
                                ('overdue', 'Overdue')
                                  ], string="Blood Work")
    offer_diagnostics = fields.Boolean(string="was information provided on bloodwork?")
    compliance_dental_cleaning = fields.Selection([('up to date', 'Up to Date'), 
                                ('overdue', 'Overdue')
                                  ], string="Dental Prophy")
    scheduled_dental = fields.Boolean(string="was dental scheduled during visit?")
    
#    EXAM 
    tpr_compliance = fields.Boolean(string="TPR")
    bcs_recorded = fields.Boolean(string="BCS Recorded")
    physical_exam_recorded = fields.Boolean(string="Full Physical Exam Recorded")
    soap = fields.Boolean(string="SOAP")
    x_ray = fields.Selection([('yes', 'Yes'), 
                                ('no', 'No'),
                                ('not_applicable', 'Not Applicable')], string="X-Ray Performed")
    senior_workup_offered = fields.Selection([('yes', 'Yes'), 
                                ('no', 'No'),
                                ('not_applicable', 'Not Applicable')], string="Senior Workup Offered",default = "not_applicable")
    estimate = fields.Boolean(string="Estimate Given")
    treatment_plan_approved = fields.Boolean(string="Treatment Plan Approved")
    blood_parasite = fields.Boolean(string="Blood Parasite Screen")
    cbc_panel = fields.Boolean(string="CBC Panel")
    chemistry_panel = fields.Boolean(string="Chemistry Panel")
    intestinal_parasite = fields.Boolean(string="Intestinal Parasite Screen")
    dental_grade = fields.Boolean(string="Dental Grade Recorded")
    dental_recom_made = fields.Boolean(string="Dental Recommendation Made")
    dental_sch = fields.Boolean(string="Dental Scheduled")
    rads_recom = fields.Boolean(string="Rads Recommended")
    dental_score = fields.Selection([('no_disease', 'No Disease'), 
                                ('g1', 'G1'),
                                ('g2', 'G2'),
                                ('g3', 'G3'),
                                ('g4', 'G4'),
                                ('g5', 'G5')], string="Dental Score")
    worm_prevention = fields.Boolean(string="Worm Prevention")
    flea_tick_prevention = fields.Boolean(string="Flea/Tick Prevention")
    sub_prescribes = fields.Boolean(string="Were Controlled Substance Prescribed")
    
#    POST-EXAM 
    offer_boarding = fields.Boolean(string="Was At Least 1 Day of Boarding Scheduled?")
    camp_booked = fields.Boolean(string="Was Day Camp Booked?")
    diet_recommended = fields.Boolean(string="Diet Recommendation Offered?")
    report_card_delivered = fields.Boolean(string="Report Card Delivered?")
    followup_reminder_setup = fields.Boolean(string="Follow Up Reminders Setup?")
    grooming_offer = fields.Selection([('yes', 'Yes'), 
                                ('no', 'No'),
                                ('no_offer', 'We Dont Offer Grooming')
                                ], string="Was Grooming Offered")
    app_schedule = fields.Boolean(string="Follow-up Appointment Scheduled")
    app_date = fields.Date("Follow-up Appointment Date")
    callback_performed = fields.Boolean(string="Callbacks Performed")
    callback_id = fields.Many2one("hr.employee",string="Who Performed Callback")
    
#    Discounts and Non Invoiced items
    discounts_ids = fields.One2many('experience.discounts', 'discount_id', string="DISCOUNTS")
    non_invoiced_ids = fields.One2many('experience.noinvoice', 'non_invoiced_id', string="NON INVOICED ITEMS")
    
#    DOCUMENTS
    documents_ids = fields.One2many('documents.attachment', 'document_id', string="Documents", default=DOCUMENTS)
    
#   smart buttons
#     view_board = fields.Float()
    pre_exam = fields.Float(compute='_get_points_pre_exam')
    exam_score = fields.Float(compute='_get_points_exam')
    post_exam = fields.Float(compute='_get_points_post_exam')
    visit_score  = fields.Float(compute='_get_sum_visit_score')
    doc_attach = fields.Integer(compute='_doc_attach')
    
#     @api.one
#     def _compute_discounts_percent(self):
#         disc_price_percent = 0.0
#           len_disc = 0
#         for recs in self.discounts_ids:
#             if recs.discount:
#                 len_disc += 1
#                 disc_price_percent += recs.discount
#             self.disc_per = disc_price_percent/len_disc 
#             
#     @api.one
#     def _compute_non_inc_tot(self):
#         disc_non_inc_percent = 0.0
#         len_non_per = 0
#         for recss in self.non_invoiced_ids:
#             if recss.std_price:
#                 len_non_per += 1
#                 disc_non_inc_percent += recss.std_price
#             self.non_inc_tot = disc_non_inc_percent/len_non_per

    @api.multi
    @api.constrains('visit_date','visit_time')
    def date_constrains(self):
        date_now_cons = date.today()
        date_time_cons = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#         date_fin_time_cons=datetime.strptime(str(date_time_cons), '%Y-%m-%d %H:%M:%S').datetime()
        date_fin_cons=datetime.strptime(str(date_now_cons), '%Y-%m-%d').date()
        for rec in self:
            if rec.visit_date > str(date_fin_cons):
                raise ValidationError(_('Sorry, You Have Entered An Incorrect Date...'))
            if rec.visit_time > date_time_cons:
                raise ValidationError(_('Sorry, You Have Entered An Incorrect Date And Time...'))

    @api.constrains('client_email')
    def validate_email(self):
        for obj in self:
            if obj.client_email:
                if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", obj.client_email) == None:
                    raise ValidationError("Please Provide valid Email Address: %s" % obj.client_email)

    @api.one
    def _compute_name(self):
        
        self.name = str(self.company_id.code) + ' - ' + str(self.doctor_id.lastname) + ' - '+ str(self.client_name) + ' - ' +str(self.visit_date)
     
#     @api.one
#     def _board_review(self):
#         if self.state_bar == 'draft':
#             self.board_review = 'no' 
#         if self.state_bar == 'validate':
#             self.board_review = 'yes'
            
#     @api.one
#     def _services_not_invoiced(self):
#         if self.non_invoiced_ids:
#             self.services_active = True
#         else:
#             self.services_active = False
                
    @api.multi
    @api.onchange('discounts_ids')   
    def _onchange_cantidad(self):  
        oncha_dis = 0
        len_oncha_dis = 0
        if not self.discounts_ids:
            self.disc_per = 0
        for val in self.discounts_ids:
            if val.sell_price:
                len_oncha_dis += 1
                oncha_dis +=val.discount
            if len_oncha_dis > 0:
                self.disc_per =  oncha_dis/len_oncha_dis 
            
#     @api.multi
#     @api.onchange('reason_visit_ids')   
#     def _onchange_reason_visit(self):
#         for ids_reason in self.reason_visit_ids:
#             if ids_reason.id == 1:
#                 self.reason_visit_ids_int = ids_reason.id 
                      
            
    @api.multi
    @api.onchange('non_invoiced_ids')   
    def _onchange_non_invoice(self):  
        oncha_dis_non = 0
        len_oncha_dis_non = 0
        if not self.non_invoiced_ids:
            self.non_inc_tot = 0
        for value in self.non_invoiced_ids:
            if value.std_price:
                len_oncha_dis_non += 1
                oncha_dis_non+=value.std_price
            if len_oncha_dis_non >0:
                self.non_inc_tot =  oncha_dis_non/len_oncha_dis_non 
    @api.one
    def day_camp_settings(self): 
        config_id = self.env['client.config.settings'].sudo().search([], order='id desc', limit=1)
        for sett_id in config_id:
            if sett_id.day_camp_res == True:
                self.offer_daycamp_sett = True     
            else:
                self.offer_daycamp_sett = False   
            if sett_id.grooming == True:
                self.offer_grooming_sett = True
            else:
                self.offer_grooming_sett = False  
                
    @api.multi
    @api.onchange('patient_age','patient_species')   
    def _onchange_patient_age(self):             
        if self.patient_age >= 84 and self.patient_species == 'canine':
            self.patient_cal = True
        if self.patient_age < 84  and  self.patient_species == 'canine':
            self.patient_cal = False
        if self.patient_age >= 132 and self.patient_species == 'feline':
            self.patient_cal = True    
        if self.patient_age < 132 and self.patient_species == 'feline':
            self.patient_cal = False       
        if  self.patient_species == 'others':
            self.patient_cal = True    
                
    @api.one
    def _get_points_pre_exam(self):
        
        config_id = self.env['client.config.settings'].sudo().search([], order='id desc', limit=1)
        for res in config_id:
            for rec in self:
                if rec.client_email:
                    amount = res.email_file
                else:
                    amount = 0
                if rec.client_mobile_phone:
                    mob_amt = res.mobile_ph
                else:
                    mob_amt = 0  
                if rec.new_client == True:
                    clt_amt = res.new_client
                else:
                    clt_amt = 0 
                if rec.offer_daycamp and res.day_camp_res:  
                    camp_amt = res.day_camp
                else:
                    camp_amt=0  
                if rec.offer_nailtrim:
                    nail_amt = res.nail_trim
                else:
                    nail_amt = 0  
                if rec.offer_bath_accept:
                    bath_amt = res.bath
                else:
                    bath_amt = 0    
                if rec.offer_anal_gland_accept:
                    anal_amt = res.anal_gland
                else:
                    anal_amt = 0   
                if rec.groomer_introduction and res.grooming == True:
                    grom_amt = res.groomer_sch   
                else:
                    grom_amt = 0 
                if rec.compliance_vaccines:
                    vacc_amt = res.vaccines
                else:
                    vacc_amt = 0  
                if rec.compliance_parasiticide:
                    para_amt = res.paracitides
                else:
                    para_amt = 0     
                if rec.compliance_diagnostics:
                    blood_amt = res.blood_work
                else:
                    blood_amt = 0   
                if rec.compliance_dental_cleaning:
                    dental_amt = res.dental
                else:
                    dental_amt = 0  
                if res.pre_exam_pts:                          
                    rec.pre_exam = "%.2f" % ((amount + mob_amt + clt_amt + camp_amt + nail_amt + bath_amt + anal_amt + grom_amt + vacc_amt + para_amt + blood_amt + dental_amt)/(res.pre_exam_pts*0.1))
                else:
                    rec.pre_exam = "%.2f" % ((amount + mob_amt + clt_amt + camp_amt + nail_amt + bath_amt + anal_amt + grom_amt + vacc_amt + para_amt + blood_amt + dental_amt)/(0.1))
                rec.pre_exam = "%.2f" %((rec.pre_exam*10.0)/20)
    @api.one
    def _get_points_exam(self):
        
        config_exam_id = self.env['client.config.settings'].sudo().search([], order='id desc', limit=1)
        for line in config_exam_id:
            for recs in self:
                if recs.tpr_compliance == True:
                    tpr_amt = line.tpr
                else:
                    tpr_amt = 0
                if recs.dental_grade == True:
                    dent_amt = line.dental_grade
                else:
                    dent_amt = 0  
                if recs.intestinal_parasite == True:
                    int_amt = line.int_parasite
                else:
                    int_amt = 0 
                if recs.blood_parasite == True:
                    blood_amt = line.blood_parasite
                else:
                    blood_amt = 0      
                if recs.chemistry_panel == True:
                    panel_amt = line.blood_panel
                else:
                    panel_amt= 0  
                if recs.worm_prevention == True:
                    worm_amt = line.worm_prevent
                else:
                    worm_amt = 0    
                if recs.flea_tick_prevention == True:
                    flea_amt = line.flea_prevent
                else:
                    flea_amt = 0   
                if recs.cbc_panel == True:
                    cbc_amt = line.cbc
                else:
                    cbc_amt = 0  
                if recs.bcs_recorded == True:
                    bcs_amt = line.bcs
                else:
                    bcs_amt = 0        
                if recs.senior_workup_offered =='yes':
                    work_amt = line.work_up     
                else:
                    work_amt = 0
                if recs.estimate ==True:
                    est_amt = line.estimate
                else:
                    est_amt = 0  
                if recs.dental_recom_made ==True:
                    dent_recom_made_amt = line.dental_recom
                else:
                    dent_recom_made_amt = 0   
                if recs.dental_sch ==True:
                    dent_sch_amt = line.dental_sch
                else:
                    dent_sch_amt = 0 
                if recs.rads_recom ==True:
                    rads_recom_amt = line.rads
                else:
                    rads_recom_amt = 0             
                
                recs.exam_score = "%.2f" % ((tpr_amt +dent_amt+int_amt+blood_amt+panel_amt+worm_amt+flea_amt+cbc_amt+bcs_amt+work_amt+est_amt+dent_recom_made_amt+dent_sch_amt+rads_recom_amt)/100.00)
                recs.exam_score = "%.2f" %((recs.exam_score*100.0)/20)
  
    @api.one
    def _get_points_post_exam(self):
        
        config_post_id = self.env['client.config.settings'].sudo().search([], order='id desc', limit=1)
        for lines in config_post_id:
            for record in self:    
                if record.offer_boarding ==True and lines.boarding == True:
                    brd_sch_amt = lines.bord_sch
                else:
                    brd_sch_amt = 0
                if record.diet_recommended ==True:
                    diet_rec_amt =  lines.diet_recom
                else:
                    diet_rec_amt = 0 
                if record.report_card_delivered ==True:
                    rep_card_amt = lines.card
                else:
                    rep_card_amt = 0 
                if record.followup_reminder_setup ==True:
                    rem_set_amt = lines.rem_setup
                else:
                    rem_set_amt = 0 
                if record.grooming_offer =='yes':
                    grm_off_amt = lines.trt_plan
                else:
                    grm_off_amt = 0 
                if record.app_schedule ==True:
                    app_sch_amt = lines.follw_sch
                else:
                    app_sch_amt = 0 
                if record.callback_performed ==True:
                    callback_amt = lines.call_back
                else:
                    callback_amt = 0    
                if lines.post_exam_pts:
                    record.post_exam = "%.2f" % ((brd_sch_amt+diet_rec_amt+rep_card_amt+rem_set_amt+grm_off_amt+app_sch_amt+callback_amt)/(lines.post_exam_pts*0.1)) 
                else:
                    record.post_exam = "%.2f" % ((brd_sch_amt+diet_rec_amt+rep_card_amt+rem_set_amt+grm_off_amt+app_sch_amt+callback_amt)/(0.1)) 
                record.post_exam = "%.2f" %((record.post_exam*10)/20)
                
                
    @api.one
    def _get_sum_visit_score(self):  
        if self.pre_exam or self.post_exam or self.exam_score:
            self.visit_score = "%.2f" %(self.pre_exam + self.post_exam + self.exam_score)
                      
    @api.one
    def _doc_attach(self):
        amount = 0
        for docs in self.documents_ids:
            if docs.attachment:
                amount +=1
        self.doc_attach = amount    
        
    @api.model   
    def dash_vals(self):
        date_loop = []
        pre_score = []
        exm_score = []
        post_score = []
        ex_score = []
        post_score = []
        graph_discount = []
       
        result = {}
        exp_id = self.env['experience.visit'].search([])
        tot = 0.0
        mob = 0.0
        nail_tr = 0.0
        promo = 0.0
        dental = 0.0
        den_grade = 0.0
        para = 0.0
        int_para =0.0
        esti = 0.0
        sche = 0.0
        callba = 0.0
#         pre_ex_pt = 0.0
#         ex_pt = 0.0
#         po_ex_pt = 0.0
        sell_pric = 0.0
        stand_prc = 0.0
        visit_score_avg = 0.0
        visit_score_len = 0.0
        avg_sc_dis = 0.0
        vals_dis_graph = 0.0
        for i in range(10):
            
            avg_sc = 0.0
            
            pre_avg=exm_avg=post_avg= 0.0
            
            date_now = date.today()
            date_t=datetime.strptime(str(date_now), '%Y-%m-%d').date()
            
            final_date = date_t - timedelta(days=i*15)
            date_loop.append(str(final_date))
            
            for lens in self.env['experience.visit'].search([('visit_date','<=',str(final_date)),('visit_date','>=',str(final_date- timedelta(days=14)))]):
#                 date_tim = datetime.strptime(str(lens.visit_date), '%Y-%m-%d').date()
#                 if date_tim <= final_date and date_tim >= final_date- timedelta(days=14):
                avg_sc += 1
                pre_avg += lens.pre_exam
                exm_avg += lens.exam_score
                post_avg += lens.post_exam
#                 if lens.discounts_ids:
#                     avg_sc_dis +=1
                avg_sc_dis = 0
                graph_avg_dis = 0
                vals_dis_graph = 0
                for ren in lens.discounts_ids:
                    if ren.discount:
                        avg_sc_dis +=1
                        vals_dis_graph += ren.discount
                    if avg_sc_dis > 0:
                        graph_avg_dis = vals_dis_graph/avg_sc_dis
                if graph_avg_dis:
                    graph_discount.append(graph_avg_dis)  
#                 for ren in lens.discounts_ids:
#                     avg_sc_dis +=1
#                     grph_disco += ren.sell_price
#                     grph_avg_dis = grph_disco /avg_sc_dis
#             graph_discount.append(grph_avg_dis)    
            pre_src_avg=exm_src_avg=post_src_avg=0.0
            if avg_sc!=0.0:                
                pre_src_avg = pre_avg/avg_sc 
                exm_src_avg = exm_avg/avg_sc 
                post_src_avg = post_avg/avg_sc
            pre_score.append(pre_src_avg)
            exm_score.append(exm_src_avg)
            post_score.append(post_src_avg)
                    
#                     print"11"
#                     avg_sc += 1
#                     pre_avg += lens.pre_exam
#                     
#                     ex_score.append(lens.exam_score)
#                     post_score.append(lens.post_exam)
#                     grph_disco = 0
#                     for ren in lens.discounts_ids:
#                         grph_disco += ren.sell_price
#                     graph_discount.append(grph_disco)
#                     
#                     pre_src_avg = pre_avg/avg_sc 
#                     pre_score.append(pre_src_avg)
#                     print pre_score,"4"
               
        for rec in exp_id:  
            
            if rec.client_email:
                tot +=1
            if rec.client_mobile_phone:
                mob +=1
            if rec.offer_nailtrim:
                nail_tr +=1   
            if rec.offer_promotion:
                promo +=1 
            if rec.scheduled_dental == True:
                dental +=1 
            if rec.dental_grade == True:
                den_grade +=1  
            if rec.blood_parasite == True:
                para +=1  
            if rec.intestinal_parasite == True:
                int_para +=1 
            if rec.estimate == True:
                esti +=1 
            if rec.app_schedule == True:
                sche +=1
            if rec.callback_performed == True:
                callba +=1
#             if rec.pre_exam:
#                 pre_ex_pt += rec.pre_exam   
#             if rec.exam_score:
#                 ex_pt += rec.exam_score 
#             if rec.post_exam:
#                 po_ex_pt += rec.post_exam  
            for temp in rec.discounts_ids:
                sell_pric += temp.sell_price  
            for invc in rec.non_invoiced_ids:
                stand_prc += invc.std_price
            if rec.visit_score:
                visit_score_len +=1
                visit_score_avg += rec.visit_score
            if visit_score_len > 0:   
                visit_score_dash = (visit_score_avg/visit_score_len)
            if visit_score_len == 0:
                visit_score_dash = 0   
        
        survey_input_id = self.env['survey.user_input'].search([]) 
        
        clicks_len = 0.0
        overall_rec = 0.0
        open_len = 0.0
        reply_len = 0.0
        no_of_click = 0.0
        no_of_open = 0.0
        no_of_reply = 0.0
        for survey_in_id in survey_input_id:  
            if survey_in_id.exp_id:
                overall_rec += 1
                if survey_in_id.state == 'new':
                    clicks_len +=1
                click_val = clicks_len
                no_of_click = (click_val/overall_rec)*100
                if survey_in_id.state == 'skip':
                    open_len +=1
                open_val = open_len  
                no_of_open = (open_val/overall_rec)*100
                if survey_in_id.state == 'done':  
                    reply_len += 1
                reply_val = reply_len 
                no_of_reply = (reply_val/overall_rec)*100   
                
        if len(exp_id) > 0:                
            rec_tot = tot/len(exp_id)
            mob_tot = mob/len(exp_id)
            nail_tot = nail_tr/len(exp_id)
            promo_tot = promo/len(exp_id)
            dent_tot = dental/len(exp_id)
            dent_grade_tot = den_grade/len(exp_id)
            para_tot = para/len(exp_id)
            int_para_tot = int_para/len(exp_id)
            esti_tot = esti/len(exp_id)
            sche_tot = sche/len(exp_id)
            callba_tot = callba/len(exp_id)
            pre_ex_pt_tot = (rec_tot + mob_tot + nail_tot + promo_tot + dent_tot)/5
            ex_pt_tot = (dent_grade_tot + para_tot + int_para_tot +esti_tot)/4
            po_ex_pt_tot = (sche_tot + callba_tot)/2
        
            result['rec_tot'] = "%.2f" % (rec_tot*100)
            result['mob_tot'] = "%.2f" %(mob_tot*100)
            result['nail_tot'] = "%.2f" %(nail_tot*100)
            result['promo_tot'] = "%.2f" %(promo_tot*100)
            result['dent_tot'] = "%.2f" %(dent_tot*100)
            result['dent_grade_tot'] = "%.2f" %(dent_grade_tot*100)
            result['para_tot'] = "%.2f" %(para_tot*100)
            result['int_para_tot'] = "%.2f" %(int_para_tot*100)
            result['esti_tot'] = "%.2f" %(esti_tot*100)
            result['sche_tot'] = "%.2f" %(sche_tot*100)
            result['callba_tot'] = "%.2f" %(callba_tot*100)
            result['pre_ex_pt_tot'] = "%.2f" %(pre_ex_pt_tot*100)
            result['ex_pt_tot'] = "%.2f" %(ex_pt_tot*100)
            result['po_ex_pt_tot'] = "%.2f" %(po_ex_pt_tot*100)
            result['sell_pric'] = "%.2f" %(sell_pric)
            result['stand_prc'] = "%.2f" %(stand_prc)
            result['vist_src_avg'] = "%.2f" %(visit_score_dash)
            result['date_loop']= date_loop
            result['pre_score']= pre_score
            result['ex_score']= exm_score
            result['post_score']= post_score
            result['no_of_click']= "%.2f" %(no_of_click)
            result['no_of_open']= "%.2f" %(no_of_open)
            result['no_of_reply']= "%.2f" %(no_of_reply)
            result['graph_dis']= graph_discount
        else:
            result['rec_tot'] = 0.0
            result['mob_tot'] = 0.0
            result['nail_tot'] = 0.0
            result['promo_tot'] = 0.0
            result['dent_tot'] = 0.0
            result['dent_grade_tot'] = 0.0
            result['para_tot'] = 0.0
            result['int_para_tot'] = 0.0
            result['esti_tot'] = 0.0
            result['sche_tot'] = 0.0
            result['callba_tot'] = 0.0
            result['pre_ex_pt_tot'] = 0.0
            result['ex_pt_tot'] = 0.0
            result['po_ex_pt_tot'] = 0.0
            result['sell_pric'] = 0.0
            result['stand_prc'] = 0.0
            result['vist_src_avg'] = 0.0
            result['no_of_click']= 0.0
            result['no_of_open']= 0.0
            result['no_of_reply']= 0.0
            date_not_res = date_loop
            pre_not_res = [0]
            ex_not_res = [0]
            post_not_res = [0]
            graph_dis_not = [0]
            result['date_loop'] = date_not_res 
            result['pre_score'] = pre_not_res 
            result['ex_score'] = ex_not_res
            result['post_score'] = post_not_res
            result['graph_dis'] = graph_dis_not
        if not result:
            date_not_res = date_loop
            pre_not_res = [0]
            ex_not_res = [0]
            post_not_res = [0]
            graph_dis_not = [0]
            result['date_loop'] = date_not_res 
            result['pre_score'] = pre_not_res 
            result['ex_score'] = ex_not_res
            result['post_score'] = post_not_res
            result['graph_dis'] = graph_dis_not    
            
        if not result['graph_dis']:
            graph_dis_not = [0]
            result['graph_dis'] = graph_dis_not  
                  
        return result
    
     
    def action_view_board(self):
        if self.board_review == 'yes':
            self.board_review = 'no'
            self.board_review_track = 'no'
            
        elif not self.company_id.director_id.name:
            raise UserError(_("There is no Medical Director for this record."))    
            
        elif self.board_review == 'no':   
            self.board_review = 'yes'
            self.board_review_track = 'yes'
         
    def set_draft(self):
        self.write({
        'state_bar': 'draft',
        }) 
        
    def validate(self):
        self.write({
        'state_bar': 'validate',
        })           
    
    @api.multi
    @api.onchange('non_invoiced_ids')   
    def _onchange_non_invoiced_ids(self):
        if self.non_invoiced_ids:
            self.services_active = True
        else:
            self.services_active = False  
            
    @api.multi
    @api.onchange('discounts_ids')   
    def _onchange_discounts_ids(self):
        if self.discounts_ids:
            self.discount_services_active = True
        else:
            self.discount_services_active = False             
     
    @api.model
    def visit_review_mail_send_cron(self):
        review_id = self.env['client.config.settings'].sudo().search([], order='id desc', limit=1)
        exp_visit_id = self.env['experience.visit'].search([])
        val_id = 0
        for exp_id in exp_visit_id:
            val_id +=1
            if exp_id.cron_updated == False:
                if review_id.survey_visit > 0:
                    if (val_id % review_id.survey_visit) == 0:
                        token = uuid.uuid4().__str__()
                        if review_id.survey_temp_id.id:
                            self.env['survey.user_input'].create({
                            'survey_id': review_id.survey_temp_id.id or False,
                            'public': 'email_public_link',
                            'date_create': fields.Datetime.now(),
                            'type': 'link',
                            'state': 'new',
                            'token': token,
                            'email': exp_id.client_email,
                            'exp_id' : exp_id.id
                            }) 
                            self.env.cr.execute("select survey_id,token from survey_user_input where exp_id="+str(exp_id.id))
                            results = self.env.cr.dictfetchall()
        
                            for record in results:
                                survey = self.env['survey.survey'].search([('id' , '=' , record['survey_id'])])
        
                                base_url = '/' if self.env.context.get('relative_url') else self.env['ir.config_parameter'].get_param('web.base.url')
                                public_url = urljoin(base_url, "survey/start/%s" % (slug(survey)))
                                benifits_survey_info = public_url+"/"+record['token']  
                                
                            template_id = self.env.ref('vitalpet_cexperience.visit_review_mail_template')
                            if template_id:
                                template_id.with_context(survey_info = benifits_survey_info).send_mail(exp_id.id, force_send=True)
                            exp_id.cron_updated = True     
            
            if exp_id.board_review =='yes':
                if exp_id.cron_board == False:
                    if exp_id.company_id.director_id:
                            template_director_id = self.env.ref('vitalpet_cexperience.medical_director_mail_template')
#                             if template_director_id:
#                                 template_director_id.send_mail(exp_id.id, force_send=True)
#                                 exp_id.cron_board = True
                                
        current_date =  date.today()  
        start_date_id = self.env['hr.period'].search([('date_start' , '=' , current_date)])
        for start_id in start_date_id:
            if start_id:
                company_user_id = self.env['res.users'].search([])
                for company_user in company_user_id:
                    template_remainder_id = self.env.ref('vitalpet_cexperience.medical_director_remainder_mail_template')
#                     if template_remainder_id:
#                         template_remainder_id.send_mail(company_user.id, force_send=True)
                        

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        """
            Override read_group to calculate the sum of the non-stored fields that depend on the user context
        """
        res_cal = super(ClientExperience, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)
        
        for lines in res_cal:
            if '__domain' in lines:
                recs_id = self.env['experience.visit'].search(lines['__domain'])
                recs_id_len = self.env['experience.visit'].search_count(lines['__domain'])
                rec_pre =rec_ex =rec_post=rec_visit= 0
                if recs_id:
                    if 'pre_exam' in fields:
                        rec_pre= sum(recs_id.mapped('pre_exam'))
                    if recs_id_len > 0: 
                        lines['pre_exam'] = rec_pre/recs_id_len
                    if 'exam_score' in fields:
                        rec_ex = sum(recs_id.mapped('exam_score'))  
                    if recs_id_len > 0:
                        lines['exam_score'] = rec_ex/recs_id_len      
                    if 'post_exam' in fields:
                        rec_post = sum(recs_id.mapped('post_exam'))
                    if recs_id_len > 0:
                        lines['post_exam'] = rec_post/recs_id_len      
                    if 'visit_score' in fields:
                        rec_visit = sum(recs_id.mapped('visit_score'))    
                    if recs_id_len > 0:
                        lines['visit_score'] = rec_visit/recs_id_len            
        return res_cal                        
                            
class ReasonVisit(models.Model):
    _name = "reason.visit"  
    
    name = fields.Char("Reason")
    
class DiscountsItems(models.Model):
    _name = "experience.discounts"  
    
    discount_id = fields.Many2one("experience.visit")    
    service = fields.Char("Service")
    std_price = fields.Float("Standard Price")
    sell_price = fields.Float("Selling Price")
    discount = fields.Float("Discounts(%)",compute='_compute_discounts_calc')
    discount_percent = fields.Char("Discounts(%)",compute='_compute_discounts_calc')
    currency_id = fields.Many2one("res.currency",default=lambda self: self.env.user.company_id.currency_id)

    
    @api.one
    @api.depends('sell_price')
    def _compute_discounts_calc(self):
        disc_per_calc = 0
        for percen in self.discount_id.discounts_ids:
            if percen.sell_price:
                if percen.std_price:
                    pric = (percen.sell_price - percen.std_price)/percen.std_price
                    disc_per_calc = pric*100
            percen.discount = "%.2f" %(disc_per_calc)
            percen.discount = abs(percen.discount)
            percen.discount_percent = str(percen.discount)+"%"
            
     
class InvoicedItems(models.Model):
    _name = "experience.noinvoice"  
    
    non_invoiced_id = fields.Many2one("experience.visit")    
    service = fields.Char("Service", required=True)
    std_price = fields.Float("Standard Price")
    
class DocumentAttachment(models.Model):
    _name = "documents.attachment"  
    
    document_id = fields.Many2one("experience.visit")    
    doc_name = fields.Char("Document Name")
    attachment = fields.Binary("Attachment")
    count = fields.Integer("Count",compute='_compute_count')
    
    @api.one
    def _compute_count(self):
        for counts in self.document_id.documents_ids:
            if counts.attachment:
                counts.count = 1
            else:
                counts.count = 0    
                