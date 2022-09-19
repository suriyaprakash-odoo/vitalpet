from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ContractEnhancementWizard(models.TransientModel):
    _name = 'contract.enhancement.wizard'