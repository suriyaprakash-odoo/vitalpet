from odoo import api, fields, models


class LogsApproval(models.Model):
    _name="logs.approval"
    
    name= fields.Many2one("res.users",string='Approved By')
    reason= fields.Char("Reason")
#     html= fields.Html("Values to Approve",compute="_compute_fields_list")
    
    
#     @api.multi
#     def _compute_fields_list(self):
#             self.html="""<table>
#                                 <tr>
#                                     <td>Contract Wage</td>
#                                     <td>Hourly</td>
#                                 </tr>
#                         </table>
#             """
# 
#     
    @api.multi
    def confirm_approval(self):
         
        active_id = self.env.context.get('active_id')
        
        contract_id = self.env["hr.contract"].search([('id','=',active_id)])
#         contract_job_id = self.env["hr.contract.job"].search([()])
#         print contract_job_id.job_id.id,"menuuuuuu"
        reason_id = self.reason
        approved_id = self.name.id
        if contract_id:
            log_ids = self.env["hr.contract.line.log"].search([('is_approved','=',False),('contract_log_line_id','=',contract_id.id)])
            for log_id in log_ids:
                log_id.write({'reason':reason_id,'approved_by':approved_id,'is_approved':True})
                
                if log_id.field=='Payout Delay':
                    contract_id.write({'is_approved_hr':True,'payout_delay':int(log_id.change_value)})
                    
                if log_id.field=='Wage':
                    contract_id.write({'is_approved_hr':True,'wage':float(log_id.change_value )})
                       
                if log_id.field=='Pay Type':
                    contract_id.write({'is_approved_hr':True,'salary_computation_method':(log_id.change_value )}) 
                    
                if log_id.field=='Schedule Pay':
                    contract_id.write({'is_approved_hr':True,'schedule_pay':(log_id.change_value )}) 
                    
                if log_id.field=='Trial Period Start Date':
                    contract_id.write({'is_approved_hr':True,'trial_date_start':(log_id.change_value )})
                    
                if log_id.field=='Trial Period End Date':
                    contract_id.write({'is_approved_hr':True,'trial_date_end':(log_id.change_value )})  
                
                if log_id.field=='Duration Start':
                    contract_id.write({'is_approved_hr':True,'date_start':(log_id.change_value )})  
                    
                if log_id.field=='Duration End':
                    contract_id.write({'is_approved_hr':True,'date_end':(log_id.change_value )}) 
                    
                if log_id.field=='Contract Type':
                    contract_id.write({'is_approved_hr':True,'type_id':( self.env['hr.contract.type'].search([('name','=',log_id.change_value)]).id)})                     
                     
                if log_id.field=='Draw type':
                    contract_id.write({'is_approved_hr':True,'draw_type_id':( self.env['hr.contract.draw.type'].search([('code','=',log_id.change_value)]).id)})
                                           
                if log_id.field=='Leave Plan':
                    contract_id.write({'is_approved_hr':True,'leave_holiday_plan':( self.env['hr.contract.leave.holiday.plan'].search([('name','=',log_id.change_value)]).id)}) 
#                 print log_id
#                 print log_id.change_value
#                 print self.env['hr.contract.job'].search([('name','=',log_id.change_value)])
#                 if log_id.field=='Job':
#                         for job in self.env['hr.contract.job'].search([('name','=',log_id.change_value)]):
#                         contract_id.write({'is_approved_hr':True,'contract_job_ids':[(0,0,{'job_id':job.id,'seniority_id':job.seniority_id.id,'is_main_job':job.is_main_job})]})    
                if log_id.field=='Job seniority title':
                    line_id=self.env['hr.contract.job'].search([('seniority_id.name','=',log_id.original_value),('contract_id','=',active_id),('is_main_job','=',True)])
                    if line_id:                    
                        seniority_id=self.env['hr.job.seniority.title'].search([('name','=',log_id.change_value)])
                        if seniority_id:
                            line_id.write({'seniority_id':seniority_id.id})
                            contract_id.write({'is_approved_hr':True,'job_seniority_title':seniority_id.id}) 
                            
                if log_id.field=='Job':
                    line_id=self.env['hr.contract.job'].search([('job_id.name','=',log_id.original_value),('contract_id','=',active_id),('is_main_job','=',True)])
                    if line_id:                    
                        job_id=self.env['hr.job'].search([('name','=',log_id.change_value)])
                        if job_id:
                            line_id.write({'job_id':job_id.id})
                            contract_id.write({'is_approved_hr':True,'job_id':job_id.id})     
                                   
                if log_id.field=='Hourly Rate':
                    line_id=self.env['hr.contract.job'].search([('contract_id.contract_job_ids.hourly_rate_class_id.line_ids.rate','=',log_id.original_value),('contract_id','=',active_id),('is_main_job','=',True)])
                    if line_id:                    
                        hourly_rate_class_id=self.env['hr.hourly.rate.class'].search([('line_ids.rate','=',log_id.change_value)])
                        if hourly_rate_class_id:
                            line_id.write({'hourly_rate_class_id':hourly_rate_class_id.id})
                                                        
        return {'type': 'ir.actions.act_window_close'}