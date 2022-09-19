from odoo import fields, models, api, _

import pytz
import datetime



@api.model
def _tz_get(self):
    # put POSIX 'Etc/*' entries at the end to avoid confusing users - see bug 1086728
    return [(tz, tz) for tz in sorted(pytz.all_timezones, key=lambda tz: tz if not tz.startswith('Etc/') else '_')]

class ResCompany(models.Model):
    _name = "res.company"
    _inherit = ['res.company','mail.thread']
    
    name = fields.Char("Company",track_visibility='onchange')
    active_state = fields.Boolean("Active State",track_visibility='onchange')
    yelp_account = fields.Char("Yelp Account",track_visibility='onchange')
    facebook_account = fields.Char("Facebook Account",track_visibility='onchange')
    youtube_account = fields.Char("Youtube Account",track_visibility='onchange')
    appointment_request_url = fields.Char("Appointment Request URL",track_visibility='onchange')
    download_app_url = fields.Char("Download App URL",track_visibility='onchange')
    rewards_program = fields.Text("Rewards Program",track_visibility='onchange')
    existing_website = fields.Char("Existing Website",track_visibility='onchange')
    online_pharmacy = fields.Char("Online Pharmacy",track_visibility='onchange')
    about_us = fields.Text("About Us",track_visibility='onchange')
    after_hours_contact = fields.Char("After Hours Contact Info",track_visibility='onchange')
    region = fields.Char("Region",track_visibility='onchange')
    map_link = fields.Char("Map Link",track_visibility='onchange')
    hours_of_operation = fields.Text("Hours of operation",track_visibility='onchange')
    zipcode = fields.Char("Near By zipcode",track_visibility='onchange')
    birdeye_account = fields.Char("Birdeye Account",track_visibility='onchange')
    
    website_publish = fields.Boolean('Publish On Website', default=True,track_visibility='onchange')
    aaha_certified = fields.Boolean('AAHA Certified',track_visibility='onchange')
    upload_logo = fields.Binary("Upload Logo",track_visibility='onchange')
    camp_name = fields.Char("Form Heading",track_visibility='onchange')
    form_active = fields.Boolean("Form Active",track_visibility='onchange')
    camp_line_ids = fields.One2many('website.camp.values','camp_line_id',string="Camp",track_visibility='onchange')
    camera_name = fields.Char("Camera Heading",track_visibility='onchange')
    camera_active = fields.Boolean("Camera Active",track_visibility='onchange')
    camera_line_ids = fields.One2many('website.camera.values','camera_line_id',string="Pets Play",track_visibility='onchange')
    active = fields.Boolean('Active',default=True,track_visibility='onchange')
    location_url = fields.Char('Location URL',track_visibility='onchange')
    form_line_ids = fields.One2many('website.form.heading','company_id',string="Form Heading",track_visibility='onchange')
    business_hour_ids = fields.One2many('website.business.hour','company_id',string="Business Hours",track_visibility='onchange')
    time_zone = fields.Selection(_tz_get, string='Timezone', default=lambda self: self._context.get('tz'),track_visibility='onchange')
    tz_offset = fields.Char(compute='_compute_tz_offset', string='Timezone offset', invisible=True,track_visibility='onchange')
    slack_channel = fields.Char(string='Slack Channel',track_visibility='onchange')
    online_booking = fields.Boolean(string='Accepts Online Booking?',track_visibility='onchange')
    widget_code = fields.Text(string='Online Booking Widget Code',track_visibility='onchange')
    chat_allowed = fields.Boolean(string='Chat Allowed?',track_visibility='onchange')
    title_meta_seo_ids = fields.One2many('website.title.meta.seo','company_id',string="Title And Meta For SEO",track_visibility='onchange')
    
    @api.depends('time_zone')
    def _compute_tz_offset(self):
        for c in self:
            c.tz_offset = datetime.datetime.now(pytz.timezone(c.time_zone or 'GMT')).strftime('%z')

    @api.onchange('form_active')
    def onchange_form(self):
        for line in self.camp_line_ids:
            line.status = self.form_active
            
    @api.onchange('camera_active')
    def onchange_camera(self):
        for line in self.camera_line_ids:
            line.status = self.camera_active
            
    @api.multi
    def toggle_website_publish(self):
        for rec in self:
            if rec.website_publish:
                rec.website_publish = False
            else:
                rec.website_publish = True
        


class WebsiteTitleMetaSeo(models.Model):
    _name = "website.title.meta.seo"
    
    company_id = fields.Many2one('res.company')
    category = fields.Char('Category')
    title_tag = fields.Char('Title Tag')
    meta_description = fields.Text('Meta Description')
    
    
class WebsiteBusinessHour(models.Model):
    _name = "website.business.hour"
    
    company_id = fields.Many2one('res.company')
    day_of_week= fields.Selection([('Monday', 'Monday'),('Tuesday', 'Tuesday'),
                                   ('Wednesday', 'Wednesday'),('Thursday', 'Thursday'),
                                   ('Friday', 'Friday'),('Saturday', 'Saturday'),
                                   ('Sunday', 'Sunday'),], string='Day')
    from_time = fields.Float('From')
    to_time = fields.Float('To')
    
            
class WebsiteFormHeader(models.Model):
    _name = "website.form.heading"
    
    company_id = fields.Many2one('res.company')
    name= fields.Char('Name')
    status = fields.Boolean('Active', default=True)
    sequence = fields.Integer('Sequence')
    camp_line_ids = fields.One2many('website.camp.values','form_line_id',string="Camp")
    
class WebsiteCampValues(models.Model):
    _name = "website.camp.values"
    
    camp_line_id = fields.Many2one('res.company')
    form_line_id = fields.Many2one('website.form.heading')
    name= fields.Char('Name')
    link = fields.Char('Link')
    status = fields.Boolean('Active', default=True)
    sequence = fields.Integer('Sequence')
    
class WebsiteCameraValues(models.Model):
    _name = "website.camera.values"
    
    camera_line_id = fields.Many2one('res.company')
    name= fields.Char('Name')
    link = fields.Char('Link')
    status = fields.Boolean('Active', default=True)
    access_code= fields.Char('Access Code')
    
class ConfirmPublish(models.TransientModel):
    _name = 'confirm.publish'
    
    @api.multi
    def confirm_company_publish(self):
        print 111111111111
        print self._context.get('active_ids'),'----------'
        current_obj = self.env['res.company'].search([('id' , '=' , self._context.get('active_ids')[0])]) 
        current_obj.toggle_website_publish()
    

        
class HrJobTitle(models.Model):
    _inherit = "hr.job.seniority.title"
    
    slack_channel = fields.Char(string='Slack Channel')
    
    
class HrJobTemplate(models.Model):
    _inherit = "hr.job.template"
    
    slack_channel = fields.Char(string='Slack Channel')

