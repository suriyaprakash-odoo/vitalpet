# -*- coding: utf-8 -*-
from odoo.osv import expression
from odoo import api, fields, models, _


class PimsPractice(models.Model):
    _inherit = 'pims.practice'
    
    
    name = fields.Char('Flow Name')
            
    @api.model
    def _scheduler_sync_providers(self, domain):
        if domain is None:
            domain = []
        practice = self.search(domain, limit=1)
        if practice:
            practice_ids = practice.global_practice_id.split('-')
            office_id = practice_ids[0]
            practice_id = practice.global_practice_id[len(office_id)+1:]
            trigger = self.env['flow.trigger'].create({'name':'providers',
                                                       'action': 'load',
                                                       'office_id': office_id,
                                                       'practice_id': practice_id,
                                                       'user_id': self.env.user.id})
            
            
    @api.model
    def _scheduler_sync_guarantors(self, domain):
        if domain is None:
            domain = []
        practice = self.search(domain, limit=1)
        if practice:
            practice_ids = practice.global_practice_id.split('-')
            office_id = practice_ids[0]
            practice_id = practice.global_practice_id[len(office_id)+1:]
            trigger = self.env['flow.trigger'].create({'name':'guarantors',
                                                       'action': 'load',
                                                       'office_id': office_id,
                                                       'practice_id': practice_id,
                                                       'user_id': self.env.user.id})
            
    @api.model
    def _scheduler_sync_patients(self, domain):
        if domain is None:
            domain = []
        practice = self.search(domain, limit=1)
        if practice:
            practice_ids = practice.global_practice_id.split('-')
            office_id = practice_ids[0]
            practice_id = practice.global_practice_id[len(office_id)+1:]
            trigger = self.env['flow.trigger'].create({'name':'patients',
                                                       'action': 'load',
                                                       'office_id': office_id,
                                                       'practice_id': practice_id,
                                                       'user_id': self.env.user.id})
    @api.model
    def _scheduler_sync_reminders(self, domain):
        if domain is None:
            domain = []
        practice = self.search(domain, limit=1)
        if practice:
            practice_ids = practice.global_practice_id.split('-')
            office_id = practice_ids[0]
            practice_id = practice.global_practice_id[len(office_id)+1:]
            trigger = self.env['flow.trigger'].create({'name':'reminders',
                                                       'action': 'load',
                                                       'office_id': office_id,
                                                       'practice_id': practice_id,
                                                       'user_id': self.env.user.id})
    @api.model
    def _scheduler_sync_products(self, domain):
        if domain is None:
            domain = []
        practice = self.search(domain, limit=1)
        if practice:
            practice_ids = practice.global_practice_id.split('-')
            office_id = practice_ids[0]
            practice_id = practice.global_practice_id[len(office_id)+1:]
            trigger = self.env['flow.trigger'].create({'name':'products',
                                                       'action': 'load',
                                                       'office_id': office_id,
                                                       'practice_id': practice_id,
                                                       'user_id': self.env.user.id})
    @api.model
    def _scheduler_sync_procedures(self, domain):
        if domain is None:
            domain = []
        practice = self.search(domain, limit=1)
        if practice:
            practice_ids = practice.global_practice_id.split('-')
            office_id = practice_ids[0]
            practice_id = practice.global_practice_id[len(office_id)+1:]
            trigger = self.env['flow.trigger'].create({'name':'procedures',
                                                       'action': 'load',
                                                       'office_id': office_id,
                                                       'practice_id': practice_id,
                                                       'user_id': self.env.user.id})
            
    @api.model
    def _scheduler_sync_product_orders(self, domain):
        if domain is None:
            domain = []
        practice = self.search(domain, limit=1)
        if practice:
            practice_ids = practice.global_practice_id.split('-')
            office_id = practice_ids[0]
            practice_id = practice.global_practice_id[len(office_id)+1:]
            trigger = self.env['flow.trigger'].create({'name':'productorders',
                                                       'action': 'load',
                                                       'office_id': office_id,
                                                       'practice_id': practice_id,
                                                       'user_id': self.env.user.id})
            
            
    @api.model
    def _scheduler_sync_transactions(self, domain):
        if domain is None:
            domain = []
        practice = self.search(domain, limit=1)
        if practice:
            practice_ids = practice.global_practice_id.split('-')
            office_id = practice_ids[0]
            practice_id = practice.global_practice_id[len(office_id)+1:]
            trigger = self.env['flow.trigger'].create({'name':'transactions',
                                                       'action': 'load',
                                                       'office_id': office_id,
                                                       'practice_id': practice_id,
                                                       'user_id': self.env.user.id})
   
            