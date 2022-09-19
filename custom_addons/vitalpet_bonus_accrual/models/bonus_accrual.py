from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError

class HrContractJob(models.Model):
    _inherit = 'hr.contract.job'

    is_bonus = fields.Boolean("Bonus")


class Bonus(models.Model):
    _name = "bonus.accrual"
    
    _rec_name = 'production_tag_id'
    contract_id = fields.Many2one("hr.contract", string='Contract')
    production_tag_id = fields.Many2one("hr.production.tag", string='Tag')
    job_id = fields.Many2one("hr.job","Job")
    is_bonus = fields.Boolean("Include", default=True)
    deduct_draw = fields.Boolean(related="production_tag_id.deduct_draw")


class Contract(models.Model):
    _inherit = 'hr.contract'

    staff_bonus_ids = fields.One2many("bonus.accrual", 'contract_id', string='Staff Bonus')

    @api.multi
    def get_bonus_lines(self):
        self.ensure_one()
        line_vals = []

        if self.staff_bonus_ids:
            self.staff_bonus_ids.unlink()

        if self.contract_job_ids:
            for line in self.contract_job_ids.filtered(lambda s: s.is_bonus):
                for job in line.job_id.production_type_ids:
                    vals = {
                        'job_id':line.job_id.id,
                        'production_tag_id': job.id,
                        'rate_id':job.rate
                    }
                    line_vals.append((0, 0, vals))
        self.write({'staff_bonus_ids':line_vals})
