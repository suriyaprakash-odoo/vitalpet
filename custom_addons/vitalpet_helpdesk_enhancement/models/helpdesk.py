from odoo import fields, models, api, _
import datetime

class HelpDesk(models.Model):
    _inherit = 'helpdesk.tag'  
  
    helpdesk_team = fields.Many2one('helpdesk.team', string='Help Desk Team', store=True)
    assinged_to = fields.Many2one('res.users',string='Assigned To')
    is_attachment_required = fields.Boolean(string='Attachment')
    

class HelpdeskResolution(models.Model):
    _name = 'helpdesk.resolution'
    
    start_date= fields.Datetime(string='Start Date')
    end_date= fields.Datetime(string='End Date')
    helpdesk_id=fields.Many2one('helpdesk.ticket','Helpdesk')
    
class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'
    
        
#     def _default_user_id(self):
#         team_id = self._context.get('default_team_id')
#         if not team_id:
#             team_id = self.env['res.users'].search([('id', 'in', self.team_id.member_ids.ids)]).ids
#         if not team_id:
#             team_id = self.env['helpdesk.team'].search([], limit=1).id
#         return team_id
#     
    tag_form = fields.Many2one('helpdesk.tag',string='Tag')
    user_id = fields.Many2one('res.users', string='Assigned to', track_visibility='onchange',  
                              domain=lambda self:[('id', 'in', self.team_id.member_ids.ids)])
    resolution_ids = fields.One2many('helpdesk.resolution','helpdesk_id', string='Tag')
    close_days = fields.Integer(string='Open Time (Days)', compute='_compute_close_days', store=True)
    
       
    @api.onchange('team_id')
    def onchange_team(self):
        if self.team_id:
            print self.team_id.member_ids
            print self.team_id.member_ids.ids
            return {'domain': {'user_id': [('id', 'in', self.team_id.member_ids.ids)]}}
        return {}
    
    @api.model
    def create(self, vals):
        user_id=False        
        if vals.get('tag_form'):
            tag_list=self.env['helpdesk.tag'].sudo().search([('id','=',vals['tag_form'])])            
            if tag_list:
                vals['tag_ids']=[[6, False, [tag_list.id]]]
                if tag_list.helpdesk_team:
                    vals['team_id']=tag_list.helpdesk_team.id
                    
                if tag_list.assinged_to:
                    user_id=tag_list.assinged_to.id

        res=super(HelpdeskTicket, self).create(vals)        
        if user_id:
            res.user_id=user_id
        if res.partner_email or res.partner_name:
            user_id=self.env['res.users'].sudo().search(['|',('name','=',res.partner_name),('login','=',res.partner_email)])
            res.company_id=user_id.company_id.id            
        return res
        
    @api.multi
    def write(self, vals):
        stage=self.stage_id.name
        if 'stage_id' in vals:
            if stage=='Resolution Recommended':
                print self.env['helpdesk.resolution'].search([('helpdesk_id','=',self.id),('end_date','=',False)])
                self.env['helpdesk.resolution'].search([('helpdesk_id','=',self.id),('end_date','=',False)]).end_date=datetime.datetime.now()                
        res=super(HelpdeskTicket, self).write(vals)
        if 'stage_id' in vals:
            if self.stage_id.name=='Resolution Recommended':
                self.env['helpdesk.resolution'].create({
                        'start_date':datetime.datetime.now(),
                        'helpdesk_id':self.id
                            })                
        return res
    
    @api.depends('close_date')
    def _compute_close_hours(self):
        for ticket in self:
            time_difference = datetime.datetime.now() - fields.Datetime.from_string(ticket.create_date)
            close_hours=0
            for res in ticket.resolution_ids:
                res_diff=fields.Datetime.from_string(res.end_date)-fields.Datetime.from_string(res.start_date)
                close_hours+=(res_diff.seconds) / 3600 + res_diff.days * 24
            print close_hours, (time_difference.seconds) / 3600 + time_difference.days * 24
            ticket.close_hours = ((time_difference.seconds) / 3600 + time_difference.days * 24)-close_hours
    
    @api.depends('close_date')
    def _compute_close_days(self):
        for ticket in self:
            time_difference = datetime.datetime.now() - fields.Datetime.from_string(ticket.create_date)
            close_days=0
            for res in ticket.resolution_ids:
                res_diff=fields.Datetime.from_string(res.end_date)-fields.Datetime.from_string(res.start_date)
                close_days+=res_diff.days
            ticket.close_days = time_difference.days-close_days
            
    @api.multi
    def reminder_email_user(self):
        for line in self.search([('stage_id.is_close', '=', False)]):
            template_id = self.env.ref('vitalpet_helpdesk_enhancement.reminder_email_user')
            if template_id:
                template_id.send_mail(line.id, force_send=True)
                    
    @api.multi
    def reminder_email_customer(self):
        for line in self.search([('stage_id.name', '=', 'Resolution Recommended')]):
            template_id = self.env.ref('vitalpet_helpdesk_enhancement.reminder_email_customer')
            if template_id:
                template_id.send_mail(line.id, force_send=True)
                    