from odoo import api, fields, models

class ResCompany(models.Model):
    _inherit = 'res.company'
    
#     experience_company_id = fields.Many2one('res.company',"Company") 
    boarding = fields.Boolean()
    grooming = fields.Boolean()
    day_camp_res = fields.Boolean()
    pre_exam_pts = fields.Integer(default=83)
    post_exam_pts = fields.Integer(default=90)
    survey_visit = fields.Integer()
    tasks_per_week = fields.Integer(default=1)
    survey_temp_id = fields.Many2one('survey.survey',string = "Post Visit Survey Template")
    director_id = fields.Many2one('hr.employee',string = "Medical Director")
    exp_visit_company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id)

class ClientExperienceConfigSettings(models.TransientModel):
    _name = 'client.config.settings'
    _inherit = 'res.config.settings'
    
    exp_visit_company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id)
#     experience_company_id = fields.Many2one('res.company',"Company",related='exp_visit_company_id.experience_company_id')
    boarding = fields.Boolean("Boarding",related='exp_visit_company_id.boarding')
    grooming = fields.Boolean("Grooming",related='exp_visit_company_id.grooming')
    day_camp_res = fields.Boolean("DayCamp",related='exp_visit_company_id.day_camp_res')   
    pre_exam_pts = fields.Integer("Pre Exam Points",related='exp_visit_company_id.pre_exam_pts',default=83)
    post_exam_pts = fields.Integer("Post Exam Points",related='exp_visit_company_id.post_exam_pts',default=90)
    survey_visit = fields.Integer("Post Visit Survey Frequency",related='exp_visit_company_id.survey_visit') 
    tasks_per_week = fields.Integer("Tasks per veterinarian",related='exp_visit_company_id.tasks_per_week',default=1) 
    survey_temp_id = fields.Many2one('survey.survey',string = "Post Visit Survey Template",related='exp_visit_company_id.survey_temp_id')
    director_id = fields.Many2one('hr.employee',string = "Medical Director",related='exp_visit_company_id.director_id')
    email_file = fields.Integer("Email On File",default=10)
    mobile_ph = fields.Integer("Mobile Phone",default=10)
    new_client = fields.Integer("New Client",default=10)
    day_camp = fields.Integer("Day Camp",default=7)
    nail_trim = fields.Integer("Nail Trim",default=10)
    bath = fields.Integer("Bath",default=7)
    anal_gland = fields.Integer("Anal Gland",default=5)
    groomer_sch = fields.Integer("Groomer Scheduled",default=10)
    vaccines = fields.Integer("Vaccines",default=9)
    paracitides = fields.Integer("Paraciticides",default=8)
    blood_work = fields.Integer("Blood Work",default=7)
    dental = fields.Integer("Dental",default=7)
    total = fields.Integer("Total",default=100)
    tpr = fields.Integer("TPR",default=7)
    dental_grade = fields.Integer("Dental Grade Recorded",default=7)
    dental_recom = fields.Integer("Dental Recommendation Made",default=7)
    dental_sch = fields.Integer("Dental Scheduled",default=7)
    int_parasite = fields.Integer("Intestinal Parasite Screen",default=5)
    blood_parasite = fields.Integer("Blood Parasite Screen(Heartworm,etc)",default=5)
    blood_panel = fields.Integer("Medication Blood Panel(Chemistry)",default=7)
    worm_prevent = fields.Integer("Worm Prevention",default=10)
    flea_prevent = fields.Integer("Flea/Tick Prevention",default=5)
    rads = fields.Integer("Rads Recommended",default=10)
    cbc = fields.Integer("Chemistry/CBC Recommended",default=10)
    bcs = fields.Integer("BCS Recorded",default=8)
    work_up = fields.Integer("Senior Workup Offered",default=7)
    estimate = fields.Integer("Estimate Given",default=5)
    total_exam = fields.Integer("Total",default=100)
    bord_sch = fields.Integer("Boarding Scheduled",default=10)
    diet_recom = fields.Integer("Diet Recommendation Offered",default=10)
    card = fields.Integer("Report Card",default=10)
    rem_setup = fields.Integer("Reminders Setup",default=10)
    trt_plan = fields.Integer("Treatment Plan Approved",default=20)
    follw_sch = fields.Integer("Followup Scheduled",default=20)
    call_back = fields.Integer("Callbacks Performed",default=20)
    total_post = fields.Integer("Total",default=100)
    
    @api.model
    def get_default_config_client_experience(self, fields):
        res = {
#             'exp_visit_company_id': self.env['ir.values'].get_default('client.config.settings', 'exp_visit_company_id'),
#             'boarding': self.env['ir.values'].get_default('client.config.settings', 'boarding'),
#             'grooming': self.env['ir.values'].get_default('client.config.settings', 'grooming'),
#             'day_camp_res': self.env['ir.values'].get_default('client.config.settings', 'day_camp_res'),
#             'pre_exam_pts': self.env['ir.values'].get_default('client.config.settings', 'pre_exam_pts'),
#             'post_exam_pts': self.env['ir.values'].get_default('client.config.settings', 'post_exam_pts'),
#             'survey_visit': self.env['ir.values'].get_default('client.config.settings', 'survey_visit'),
            'survey_temp_id': self.env['ir.values'].get_default('client.config.settings', 'survey_temp_id'),
            'email_file': self.env['ir.values'].get_default('client.config.settings', 'email_file'),
            'mobile_ph': self.env['ir.values'].get_default('client.config.settings', 'mobile_ph'),
            'new_client': self.env['ir.values'].get_default('client.config.settings', 'new_client'),
            'day_camp': self.env['ir.values'].get_default('client.config.settings', 'day_camp'),
            'nail_trim': self.env['ir.values'].get_default('client.config.settings', 'nail_trim'),
            'bath': self.env['ir.values'].get_default('client.config.settings', 'bath'),
            'anal_gland': self.env['ir.values'].get_default('client.config.settings', 'anal_gland'),
            'groomer_sch': self.env['ir.values'].get_default('client.config.settings', 'groomer_sch'),
            'vaccines': self.env['ir.values'].get_default('client.config.settings', 'vaccines'),
            'paracitides': self.env['ir.values'].get_default('client.config.settings', 'paracitides'),
            'blood_work': self.env['ir.values'].get_default('client.config.settings', 'blood_work'),
            'dental': self.env['ir.values'].get_default('client.config.settings', 'dental'),
            'total': self.env['ir.values'].get_default('client.config.settings', 'total'),
            'tpr': self.env['ir.values'].get_default('client.config.settings', 'tpr'),
            'dental_grade': self.env['ir.values'].get_default('client.config.settings', 'dental_grade'),
            'dental_recom': self.env['ir.values'].get_default('client.config.settings', 'dental_recom'),
            'dental_sch': self.env['ir.values'].get_default('client.config.settings', 'dental_sch'),
            'int_parasite': self.env['ir.values'].get_default('client.config.settings', 'int_parasite'),
            'blood_parasite': self.env['ir.values'].get_default('client.config.settings', 'blood_parasite'),
            'blood_panel': self.env['ir.values'].get_default('client.config.settings', 'blood_panel'),
            'worm_prevent': self.env['ir.values'].get_default('client.config.settings', 'worm_prevent'),
            'flea_prevent': self.env['ir.values'].get_default('client.config.settings', 'flea_prevent'),
            'rads': self.env['ir.values'].get_default('client.config.settings', 'rads'),
            'cbc': self.env['ir.values'].get_default('client.config.settings', 'cbc'),
            'bcs': self.env['ir.values'].get_default('client.config.settings', 'bcs'),
            'work_up': self.env['ir.values'].get_default('client.config.settings', 'work_up'),
            'estimate': self.env['ir.values'].get_default('client.config.settings', 'estimate'),
            'total_exam': self.env['ir.values'].get_default('client.config.settings', 'total_exam'),
            'bord_sch': self.env['ir.values'].get_default('client.config.settings', 'bord_sch'),
            'diet_recom': self.env['ir.values'].get_default('client.config.settings', 'diet_recom'),
            'card': self.env['ir.values'].get_default('client.config.settings', 'card'),
            'rem_setup': self.env['ir.values'].get_default('client.config.settings', 'rem_setup'),
            'trt_plan': self.env['ir.values'].get_default('client.config.settings', 'trt_plan'),
            'follw_sch': self.env['ir.values'].get_default('client.config.settings', 'follw_sch'),
            'call_back': self.env['ir.values'].get_default('client.config.settings', 'call_back'),
            'total_post': self.env['ir.values'].get_default('client.config.settings', 'total_post'),
              }
        return res
 
    @api.multi
    def set_default_config_client_experience(self):         
        ir_values_obj = self.env['ir.values']
        
#         ir_values_obj.sudo().set_default('client.config.settings', "exp_visit_company_id", self.exp_visit_company_id.id, for_all_users=True)               
#         self.env.user.company_id.write({'exp_visit_company_id':self.exp_visit_company_id.id})
        
#         ir_values_obj.sudo().set_default('client.config.settings', "boarding", self.boarding, for_all_users=True)               
#         self.env.user.company_id.write({'boarding':self.boarding})
#         
#         ir_values_obj.sudo().set_default('client.config.settings', "grooming", self.grooming, for_all_users=True)               
#         self.env.user.company_id.write({'grooming':self.grooming})
#         
#         ir_values_obj.sudo().set_default('client.config.settings', "day_camp_res", self.day_camp_res, for_all_users=True)               
#         self.env.user.company_id.write({'day_camp_res':self.day_camp_res})
#         
#         ir_values_obj.sudo().set_default('client.config.settings', "pre_exam_pts", self.pre_exam_pts, for_all_users=True)               
#         self.env.user.company_id.write({'pre_exam_pts':self.pre_exam_pts})
#         
#         ir_values_obj.sudo().set_default('client.config.settings', "post_exam_pts", self.post_exam_pts, for_all_users=True)               
#         self.env.user.company_id.write({'post_exam_pts':self.post_exam_pts})
#         
#         ir_values_obj.sudo().set_default('client.config.settings', "survey_visit", self.survey_visit, for_all_users=True)               
#         self.env.user.company_id.write({'survey_visit':self.survey_visit})
        
        ir_values_obj.sudo().set_default('client.config.settings', "survey_temp_id", self.survey_temp_id.id, for_all_users=True)               
        self.env.user.company_id.write({'survey_temp_id':self.survey_temp_id.id})
        
        ir_values_obj.sudo().set_default('client.config.settings', "email_file", self.email_file, for_all_users=True)               
        self.env.user.company_id.write({'email_file':self.email_file})
        
        ir_values_obj.sudo().set_default('client.config.settings', "mobile_ph", self.mobile_ph, for_all_users=True)               
        self.env.user.company_id.write({'mobile_ph':self.mobile_ph})
        
        ir_values_obj.sudo().set_default('client.config.settings', "new_client", self.new_client, for_all_users=True)               
        self.env.user.company_id.write({'new_client':self.new_client})
        
        ir_values_obj.sudo().set_default('client.config.settings', "day_camp", self.day_camp, for_all_users=True)               
        self.env.user.company_id.write({'day_camp':self.day_camp})
        
        ir_values_obj.sudo().set_default('client.config.settings', "nail_trim", self.nail_trim, for_all_users=True)               
        self.env.user.company_id.write({'nail_trim':self.nail_trim})
        
        ir_values_obj.sudo().set_default('client.config.settings', "bath", self.bath, for_all_users=True)               
        self.env.user.company_id.write({'bath':self.bath})
        
        ir_values_obj.sudo().set_default('client.config.settings', "anal_gland", self.anal_gland, for_all_users=True)               
        self.env.user.company_id.write({'anal_gland':self.anal_gland})
        
        ir_values_obj.sudo().set_default('client.config.settings', "groomer_sch", self.groomer_sch, for_all_users=True)               
        self.env.user.company_id.write({'groomer_sch':self.groomer_sch})
        
        ir_values_obj.sudo().set_default('client.config.settings', "vaccines", self.vaccines, for_all_users=True)               
        self.env.user.company_id.write({'vaccines':self.vaccines})
        
        ir_values_obj.sudo().set_default('client.config.settings', "paracitides", self.paracitides, for_all_users=True)               
        self.env.user.company_id.write({'paracitides':self.paracitides})
        
        ir_values_obj.sudo().set_default('client.config.settings', "blood_work", self.blood_work, for_all_users=True)               
        self.env.user.company_id.write({'blood_work':self.blood_work})
        
        ir_values_obj.sudo().set_default('client.config.settings', "dental", self.dental, for_all_users=True)               
        self.env.user.company_id.write({'dental':self.dental})
        
        ir_values_obj.sudo().set_default('client.config.settings', "total", self.total, for_all_users=True)               
        self.env.user.company_id.write({'total':self.total})
        
        ir_values_obj.sudo().set_default('client.config.settings', "tpr", self.tpr, for_all_users=True)               
        self.env.user.company_id.write({'tpr':self.tpr})
     
        ir_values_obj.sudo().set_default('client.config.settings', "dental_grade", self.dental_grade, for_all_users=True)               
        self.env.user.company_id.write({'dental_grade':self.dental_grade})
        ''
        ir_values_obj.sudo().set_default('client.config.settings', "dental_recom", self.dental_recom, for_all_users=True)               
        self.env.user.company_id.write({'dental_recom':self.dental_recom})
        
        ir_values_obj.sudo().set_default('client.config.settings', "dental_sch", self.dental_sch, for_all_users=True)               
        self.env.user.company_id.write({'dental_sch':self.dental_sch})
        
        ir_values_obj.sudo().set_default('client.config.settings', "int_parasite", self.int_parasite, for_all_users=True)               
        self.env.user.company_id.write({'int_parasite':self.int_parasite})
        
        ir_values_obj.sudo().set_default('client.config.settings', "blood_parasite", self.blood_parasite, for_all_users=True)               
        self.env.user.company_id.write({'blood_parasite':self.blood_parasite})
        
        ir_values_obj.sudo().set_default('client.config.settings', "blood_panel", self.blood_panel, for_all_users=True)               
        self.env.user.company_id.write({'blood_panel':self.blood_panel})
        
        ir_values_obj.sudo().set_default('client.config.settings', "worm_prevent", self.worm_prevent, for_all_users=True)               
        self.env.user.company_id.write({'worm_prevent':self.worm_prevent})
        
        ir_values_obj.sudo().set_default('client.config.settings', "flea_prevent", self.flea_prevent, for_all_users=True)               
        self.env.user.company_id.write({'flea_prevent':self.flea_prevent})
        
        ir_values_obj.sudo().set_default('client.config.settings', "rads", self.rads, for_all_users=True)               
        self.env.user.company_id.write({'rads':self.rads})
        
        ir_values_obj.sudo().set_default('client.config.settings', "cbc", self.cbc, for_all_users=True)               
        self.env.user.company_id.write({'cbc':self.cbc})
        
        ir_values_obj.sudo().set_default('client.config.settings', "bcs", self.bcs, for_all_users=True)               
        self.env.user.company_id.write({'bcs':self.bcs})
        
        ir_values_obj.sudo().set_default('client.config.settings', "work_up", self.work_up, for_all_users=True)               
        self.env.user.company_id.write({'work_up':self.work_up})
        
        ir_values_obj.sudo().set_default('client.config.settings', "estimate", self.estimate, for_all_users=True)               
        self.env.user.company_id.write({'estimate':self.estimate})
        
        ir_values_obj.sudo().set_default('client.config.settings', "total_exam", self.total_exam, for_all_users=True)               
        self.env.user.company_id.write({'total_exam':self.total_exam})
        
        ir_values_obj.sudo().set_default('client.config.settings', "bord_sch", self.bord_sch, for_all_users=True)               
        self.env.user.company_id.write({'bord_sch':self.bord_sch})
        
        ir_values_obj.sudo().set_default('client.config.settings', "diet_recom", self.diet_recom, for_all_users=True)               
        self.env.user.company_id.write({'diet_recom':self.diet_recom})
        
        ir_values_obj.sudo().set_default('client.config.settings', "card", self.card, for_all_users=True)               
        self.env.user.company_id.write({'card':self.card})
        
        ir_values_obj.sudo().set_default('client.config.settings', "rem_setup", self.rem_setup, for_all_users=True)               
        self.env.user.company_id.write({'rem_setup':self.rem_setup})
        
        ir_values_obj.sudo().set_default('client.config.settings', "trt_plan", self.trt_plan, for_all_users=True)               
        self.env.user.company_id.write({'trt_plan':self.trt_plan})
        
        ir_values_obj.sudo().set_default('client.config.settings', "follw_sch", self.follw_sch, for_all_users=True)               
        self.env.user.company_id.write({'follw_sch':self.follw_sch})
        
        ir_values_obj.sudo().set_default('client.config.settings', "call_back", self.call_back, for_all_users=True)               
        self.env.user.company_id.write({'call_back':self.call_back})
        
        ir_values_obj.sudo().set_default('client.config.settings', "total_post", self.total_post, for_all_users=True)               
        self.env.user.company_id.write({'total_post':self.total_post})  
        
    @api.onchange('boarding','grooming','day_camp_res')
    def _compute_pre_exam(self):
        pre_exam_pts=post_exam_pts=100
        if self.boarding == False:
            post_exam_pts-=self.bord_sch
        if self.grooming == False:
            pre_exam_pts-=self.groomer_sch
        if self.day_camp_res == False:
            pre_exam_pts-=self.day_camp
        self.post_exam_pts=post_exam_pts
        self.pre_exam_pts=pre_exam_pts
          
    @api.multi
    def execute(self):
        clint_conf_ids = self.env['client.config.settings'].search([('id','!=',self.id)])
        for client in clint_conf_ids:
            client.unlink()
        return  super(ClientExperienceConfigSettings, self).execute()
    
    
class MypracticeConfigSettings(models.TransientModel):
    _inherit = 'mypractice.config.settings'
    
    medical_director_id = fields.Many2one("hr.employee",string="Medical Director",domain="[('job_seniority_title','ilike','Medical Director'),('company_id','=',company_id)]",related='company_id.director_id')
    