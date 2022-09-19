from odoo import fields, models, api, _

class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line' 
        
    contact_id = fields.Many2one('res.partner', string='Contact', readonly=False)
    
    @api.onchange('contact_id')
    def onchange_timesheet_field(self): 
        res = {'domain': {
        'contact_id': "[('id', '!=', False)]",
        }}
        if self.task_id.partner_ids:
            jrl_ids = self.task_id.partner_ids.ids
            res['domain']['contact_id'] = "[('id', 'in', %s)]" % jrl_ids
        elif self.issue_id.task_id.partner_ids:
            jrl_ids = self.issue_id.task_id.partner_ids.ids
            res['domain']['contact_id'] = "[('id', '=', %s)]" % jrl_ids
        elif self.issue_id.partner_id.id:
            jrl_ids = self.issue_id.partner_id.id
            res['domain']['contact_id'] = "[('id', '=', %s)]" % jrl_ids
        return res