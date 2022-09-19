# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models


class PlannerOnboarding(models.Model):

    _inherit = 'web.planner'

    @api.model
    def _get_planner_application(self):
        planner = super(PlannerOnboarding, self)._get_planner_application()
        planner.append(['planner_onboarding', 'Onboarding Planner'])
        return planner
        