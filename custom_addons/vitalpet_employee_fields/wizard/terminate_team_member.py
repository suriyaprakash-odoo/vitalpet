from odoo import api, fields, models, _
from datetime import datetime
from dateutil import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
import dateutil.parser

class TerminateMember(models.TransientModel):

    _name = "terminate.member"
    _description = "Employee Terminate Details"
    _rec_name = "termination_date"
    
    termination_date = fields.Date(string="Termination Date", required=True)
    termination_type = fields.Many2one('termination.type',related="termination_reason.termination_type", string='Termination Type', required=True)
    termination_reason = fields.Many2one('termination.reason', string='Termination Reason', required=True)
    rehire_eligible = fields.Boolean(string='Eligible for Rehire?')
    cobra_eligible = fields.Boolean(string='Cobra eligible?')
    paid_through_date = fields.Date(string="Paid Through Date", required=True)

    @api.multi
    def terminate_ok(self): 
        hr_br = self.env['hr.employee'].browse(self.env.context['active_id'])
        data = self.read()[0]
        hr_br.write({
            'termination_date': data['termination_date'],
            'paid_through_date': data['paid_through_date'],
            'termination_type': data['termination_type'] and data['termination_type'][0],
            'termination_reason': data['termination_reason'] and data['termination_reason'][0],
            'rehire_eligible': data['rehire_eligible'],
            'cobra_eligible':data['cobra_eligible'],
            })
        if hr_br.contract_ids:
            for contract in hr_br.contract_ids:
                if data['termination_date']:
                    initial_date = dateutil.parser.parse(data['termination_date']).date()
                    end_date = dateutil.parser.parse(data['paid_through_date']).date()
                    termination_reason = self.termination_reason.id
                    termination_type = self.termination_type.id
                    contract.write({'date_end': end_date.strftime(DEFAULT_SERVER_DATE_FORMAT),'date_start': initial_date.strftime(DEFAULT_SERVER_DATE_FORMAT),
                                    'reason':termination_reason,'type':termination_type,'change_date':contract.date_end
                                    })
        return True
            
        
    