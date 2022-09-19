# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class WizardInterCompanyValidate(models.TransientModel):

    _name = "wizard.intercompany.validate"
    _description = "Intercompany Validate"

    
    @api.multi
    def action_yes(self):
        payroll_import = self.env['gl.payroll.import'].search([('id','=',self.env.context['active_id'])])
        payroll_import.create_journal()
        return True

        