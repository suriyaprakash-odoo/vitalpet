# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
#from odoo import models
from odoo import api, fields, models, _

class MypracticeDashboard(models.Model):
    _inherit = "mypractice.dashboard"


class HrOnboarding(models.Model):
    _inherit = "hr.employee.onboarding"

