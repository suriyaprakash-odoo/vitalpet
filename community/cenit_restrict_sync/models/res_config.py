from odoo import models, fields,api
from odoo.exceptions import Warning
from datetime import datetime

class IrCron(models.Model):
    _inherit = 'ir.cron'
    
    month_number = fields.Integer('Nbre of Month Number',help="Nbre of month to start the sync.")
    start_date = fields.Date('Start Date', compute='_compute_start_end_dates', help="Start date to start the sync.")
    end_date = fields.Date('End Date', compute='_compute_start_end_dates', help="End date to start the sync.")
    
    @api.depends('month_number')
    @api.one
    def _compute_start_end_dates(self):
        if self.month_number:
            today = datetime.today()
            start_date =  today.replace(month=(-1)*self.month_number)
            self.start_date = start_date.strftime("%Y-%m-%d")
            self.end_date = today.strftime("%Y-%m-%d")
            
    
class CenitConfigSettings(models.TransientModel):
    _name = 'cenit.config.settings'
    _description = 'Cenit Sync Configuration'
    _inherit = 'res.config.settings'
    
    backend_id = fields.Many2one('pims.practice', 'Practice', domain=[('syncdata', '=', True)])
    
    
    sync_providers = fields.Boolean('Auto sync providers?')
    sync_provider_interval_number = fields.Integer('Sync Provider Interval Number',help="Repeat every x.")
    sync_provider_interval_type = fields.Selection( [('minutes', 'Minutes'),
            ('hours','Hours'), ('work_days','Work Days'), ('days', 'Days'),('weeks', 'Weeks'), ('months', 'Months')], 'Import Customer groups')
    sync_provider_next_execution = fields.Datetime('Next Execution', help='Next execution time')
    sync_provider_month_number = fields.Integer('Nbre of Month Number',help="Nbre of month to start the sync.")
    
    sync_guarantors = fields.Boolean('Auto sync pet owners?')
    sync_guarantors_interval_number = fields.Integer('Pet Owner Interval Number',help="Repeat every x.")
    sync_guarantors_interval_type = fields.Selection( [('minutes', 'Minutes'),
            ('hours','Hours'), ('work_days','Work Days'), ('days', 'Days'),('weeks', 'Weeks'), ('months', 'Months')], 'Import Customer groups')
    sync_guarantors_next_execution = fields.Datetime('Next Execution', help='Next execution time')
    sync_guarantors_month_number = fields.Integer('Nbre of Month Number',help="Nbre of month to start the sync.")
    
    sync_patients = fields.Boolean('Auto sync pets?')
    sync_patients_interval_number = fields.Integer('Sync pets Interval Number',help="Repeat every x.")
    sync_patients_interval_type = fields.Selection( [('minutes', 'Minutes'),
            ('hours','Hours'), ('work_days','Work Days'), ('days', 'Days'),('weeks', 'Weeks'), ('months', 'Months')], 'Import Customer groups')
    sync_patients_next_execution = fields.Datetime('Next Execution', help='Next execution time')
    sync_patients_month_number = fields.Integer('Nbre of Month Number',help="Nbre of month to start the sync.")
    
    sync_products = fields.Boolean('Auto Sync products?')
    sync_products_interval_number = fields.Integer('Sync products Interval Number',help="Repeat every x.")
    sync_products_interval_type = fields.Selection( [('minutes', 'Minutes'),
            ('hours','Hours'), ('work_days','Work Days'), ('days', 'Days'),('weeks', 'Weeks'), ('months', 'Months')], 'Import Customer groups')
    sync_products_next_execution = fields.Datetime('Next Execution', help='Next execution time')
    sync_products_month_number = fields.Integer('Nbre of Month Number',help="Nbre of month to start the sync.")
    
    sync_reminders = fields.Boolean('Auto sync reminders?')
    sync_reminders_interval_number = fields.Integer('Sync Reminders Interval Number',help="Repeat every x.")
    sync_reminders_interval_type = fields.Selection( [('minutes', 'Minutes'),
            ('hours','Hours'), ('work_days','Work Days'), ('days', 'Days'),('weeks', 'Weeks'), ('months', 'Months')], 'Import Customer groups')
    sync_reminders_next_execution = fields.Datetime('Next Execution', help='Next execution time')
    sync_reminders_month_number = fields.Integer('Nbre of Month Number',help="Nbre of month to start the sync.")
    
    sync_procedures = fields.Boolean('Auto sync procedures?')
    sync_procedures_interval_number = fields.Integer('Sync Procedures Interval Number',help="Repeat every x.")
    sync_procedures_interval_type = fields.Selection( [('minutes', 'Minutes'),
            ('hours','Hours'), ('work_days','Work Days'), ('days', 'Days'),('weeks', 'Weeks'), ('months', 'Months')], 'Import Customer groups')
    sync_procedures_next_execution = fields.Datetime('Next Execution', help='Next execution time')
    sync_procedures_month_number = fields.Integer('Nbre of Month Number',help="Nbre of month to start the sync.")
    
    sync_product_orders = fields.Boolean('Auto Sync product orders?')
    sync_product_orders_interval_number = fields.Integer('Sync product orders Interval Number',help="Repeat every x.")
    sync_product_orders_interval_type = fields.Selection( [('minutes', 'Minutes'),
            ('hours','Hours'), ('work_days','Work Days'), ('days', 'Days'),('weeks', 'Weeks'), ('months', 'Months')], 'Import Customer groups')
    sync_product_orders_next_execution = fields.Datetime('Next Execution', help='Next execution time')
    sync_product_orders_month_number = fields.Integer('Nbre of Month Number',help="Nbre of month to start the sync.")
    
    sync_transactions = fields.Boolean('Auto Sync transactions?')
    sync_transactions_interval_number = fields.Integer('Sync transactions Interval Number',help="Repeat every x.")
    sync_transactions_interval_type = fields.Selection( [('minutes', 'Minutes'),
            ('hours','Hours'), ('work_days','Work Days'), ('days', 'Days'),('weeks', 'Weeks'), ('months', 'Months')], 'Import Customer groups')
    sync_transactions_next_execution = fields.Datetime('Next Execution', help='Next execution time')
    sync_transactions_month_number = fields.Integer('Nbre of Month Number',help="Nbre of month to start the sync.")
    
    @api.onchange('backend_id')
    def onchange_backend_id(self):
        backend = self.backend_id
        if backend :
            
            sync_providers_cron_exist = self.env.ref('cenit_restrict_sync.ir_cron_sync_providers_backend_%d'%(backend.id),raise_if_not_found=False)
            if sync_providers_cron_exist and sync_providers_cron_exist.active:
                self.sync_providers = True
                self.sync_provider_interval_number = sync_providers_cron_exist.interval_number or False
                self.sync_provider_interval_type = sync_providers_cron_exist.interval_type or False
                self.sync_provider_next_execution = sync_providers_cron_exist.nextcall or False
                self.sync_provider_month_number = sync_providers_cron_exist.month_number or False
            else :
                self.sync_providers = False
            
            sync_guarantors_cron_exist = self.env.ref('cenit_restrict_sync.ir_cron_sync_guarantors_backend_%d'%(backend.id),raise_if_not_found=False)
            if sync_guarantors_cron_exist and sync_guarantors_cron_exist.active:
                self.sync_guarantors = True
                self.sync_guarantors_interval_number = sync_guarantors_cron_exist.interval_number or False
                self.sync_guarantors_interval_type = sync_guarantors_cron_exist.interval_type or False
                self.sync_guarantors_next_execution = sync_guarantors_cron_exist.nextcall or False
                self.sync_guarantors_month_number = sync_guarantors_cron_exist.month_number or False
            else :
                self.sync_guarantors = False
            
            sync_patients_cron_exist = self.env.ref('cenit_restrict_sync.ir_cron_sync_patients_backend_%d'%(backend.id),raise_if_not_found=False)
            if sync_patients_cron_exist and sync_patients_cron_exist.active:
                self.sync_patients = True
                self.sync_patients_interval_number = sync_patients_cron_exist.interval_number or False
                self.sync_patients_interval_type = sync_patients_cron_exist.interval_type or False
                self.sync_patients_next_execution = sync_patients_cron_exist.nextcall or False
                self.sync_patients_month_number = sync_patients_cron_exist.month_number or False
            else :
                self.sync_patients = False
            
            sync_products_cron_exist = self.env.ref('cenit_restrict_sync.ir_cron_sync_products_backend_%d'%(backend.id),raise_if_not_found=False)
            if sync_products_cron_exist and sync_products_cron_exist.active:
                self.sync_products = True
                self.sync_products_interval_number = sync_products_cron_exist.interval_number or False
                self.sync_products_interval_type = sync_products_cron_exist.interval_type or False
                self.sync_products_next_execution = sync_products_cron_exist.nextcall or False
                self.sync_products_month_number = sync_products_cron_exist.month_number or False
            else :
                self.sync_products = False
                
            sync_reminders_cron_exist = self.env.ref('cenit_restrict_sync.ir_cron_sync_reminders_backend_%d'%(backend.id),raise_if_not_found=False)
            if sync_reminders_cron_exist and sync_reminders_cron_exist.active:
                self.sync_reminders = True
                self.sync_reminders_interval_number = sync_reminders_cron_exist.interval_number or False
                self.sync_reminders_interval_type = sync_reminders_cron_exist.interval_type or False
                self.sync_reminders_next_execution = sync_reminders_cron_exist.nextcall or False
                self.sync_reminders_month_number = sync_reminders_cron_exist.month_number or False
            else :
                self.sync_reminders = False         
                
            sync_procedures_cron_exist = self.env.ref('cenit_restrict_sync.ir_cron_sync_procedures_backend_%d'%(backend.id),raise_if_not_found=False)
            if sync_procedures_cron_exist and sync_procedures_cron_exist.active:
                self.sync_procedures = True
                self.sync_procedures_interval_number = sync_procedures_cron_exist.interval_number or False
                self.sync_procedures_interval_type = sync_procedures_cron_exist.interval_type or False
                self.sync_procedures_next_execution = sync_procedures_cron_exist.nextcall or False
                self.sync_procedures_month_number = sync_procedures_cron_exist.month_number or False
            else :
                self.sync_procedures = False
            
            sync_product_orders_cron_exist = self.env.ref('cenit_restrict_sync.ir_cron_sync_product_orders_backend_%d'%(backend.id),raise_if_not_found=False)
            if sync_product_orders_cron_exist and sync_product_orders_cron_exist.active:
                self.sync_product_orders = True
                self.sync_product_orders_interval_number = sync_product_orders_cron_exist.interval_number or False
                self.sync_product_orders_interval_type = sync_product_orders_cron_exist.interval_type or False
                self.sync_product_orders_next_execution = sync_product_orders_cron_exist.nextcall or False
                self.sync_product_orders_month_number = sync_product_orders_cron_exist.month_number or False
            else :
                self.sync_product_orders = False
            
            sync_transactions_cron_exist = self.env.ref('cenit_restrict_sync.ir_cron_sync_transactions_backend_%d'%(backend.id),raise_if_not_found=False)
            if sync_transactions_cron_exist and sync_transactions_cron_exist.active:
                self.sync_transactions = True
                self.sync_transactions_interval_number = sync_transactions_cron_exist.interval_number or False
                self.sync_transactions_interval_type = sync_transactions_cron_exist.interval_type or False
                self.sync_transactions_next_execution = sync_transactions_cron_exist.nextcall or False
                self.sync_transactions_month_number = sync_transactions_cron_exist.month_number or False
            else :
                self.sync_transactions = False
            
        
    @api.multi    
    def synchronize_metadata(self):
        backend = self.backend_id
        if backend :
            backend.synchronize_metadata()
            
    @api.multi
    def sync_guarantor(self):
        website = self.website_id
        if website :
            website.write({'sync_guarantors_from_date':self.sync_guarantors_from_date})
            website.sync_guarantors()
            self.sync_guarantors_from_date = website.sync_guarantors_from_date
    
    @api.multi
    def import_orders(self):  
        storeview = self.storeview_id
        if storeview :
            storeview.write({'import_orders_from_date':self.import_orders_from_date})
            storeview.sync_reminders()    
            self.import_orders_from_date = storeview.import_orders_from_date

    @api.multi
    def execute(self):
        backend = self.backend_id
        values = {}
        res = super(CenitConfigSettings,self).execute()
        if backend:
            
            values['sync_providers'] = self.sync_providers or False
            values['sync_guarantors']=self.sync_guarantors or False
            values['sync_patients']=self.sync_patients or False            
            values['sync_products']=self.sync_products or False
            values['sync_reminders']=self.sync_reminders or False
            values['sync_procedures']=self.sync_procedures or False  
            values['sync_product_orders']=self.sync_product_orders or False   
            values['sync_transactions']=self.sync_transactions or False             
            self.setup_sync_providers(backend)
            self.setup_sync_guarantors(backend)
            self.setup_sync_patients(backend)
            self.setup_sync_products(backend)
            self.setup_sync_reminders(backend)
            self.setup_sync_procedures(backend)
            self.setup_sync_product_orders(backend)
            self.setup_sync_transactions(backend)
            
            backend.write(values)
        return res    
    
    @api.multi   
    def setup_sync_providers(self,backend):
        if self.sync_providers:
            cron_exist = self.env.ref('cenit_restrict_sync.ir_cron_sync_providers_backend_%d'%(backend.id),raise_if_not_found=False)
            vals = {
                    'active' : True,
                    'interval_number':self.sync_provider_interval_number,
                    'interval_type':self.sync_provider_interval_type,
                    'nextcall':self.sync_provider_next_execution,
                    'month_number':self.sync_provider_month_number,
                    'args':"[[('id','=',%d)]]"%(backend.id)
                    }
                    
            if cron_exist:
                #vals.update({'name' : cron_exist.name})
                cron_exist.write(vals)
            else:
                sync_providers_cron = self.env.ref('cenit_restrict_sync.ir_cron_sync_providers',raise_if_not_found=False)
                if not sync_providers_cron:
                    raise Warning('Core settings of Cenit are deleted, please upgrade Vitalpet module  to back this settings..')
                
                name = 'Cenit - '+backend.name + ' : Sync Providers'
                vals.update({'name' : name})
                new_cron = sync_providers_cron.copy(default=vals)
                self.env['ir.model.data'].create({'module':'cenit_restrict_sync',
                                                  'name':'ir_cron_sync_providers_backend_%d'%(backend.id),
                                                  'model': 'ir.cron',
                                                  'res_id' : new_cron.id,
                                                  'noupdate' : True
                                                  })
        else:
            cron_exist = self.env.ref('cenit_restrict_sync.ir_cron_sync_providers_backend_%d'%(backend.id),raise_if_not_found=False)
            if cron_exist:
                cron_exist.write({'active':False})
        return True
    
    @api.multi   
    def setup_sync_guarantors(self,backend):
        if self.sync_guarantors:
            cron_exist = self.env.ref('cenit_restrict_sync.ir_cron_sync_guarantors_backend_%d'%(backend.id),raise_if_not_found=False)
            vals = {
                    'active' : True,
                    'interval_number':self.sync_guarantors_interval_number,
                    'interval_type':self.sync_guarantors_interval_type,
                    'nextcall':self.sync_guarantors_next_execution,
                    'month_number':self.sync_guarantors_month_number,
                    'args':"[[('id','=',%d)]]"%(backend.id)
                    }
                    
            if cron_exist:
                cron_exist.write(vals)
            else:
                sync_guarantors_cron = self.env.ref('cenit_restrict_sync.ir_cron_sync_guarantors',raise_if_not_found=False)
                if not sync_guarantors_cron:
                    raise Warning('Core settings of Cenit are deleted, please upgrade Vitalpet module  to back this settings..')
                
                name = 'Cenit - '+backend.name + ' : Sync Pet Owners'
                vals.update({'name' : name})
                new_cron = sync_guarantors_cron.copy(default=vals)
                self.env['ir.model.data'].create({'module':'cenit_restrict_sync',
                                                  'name':'ir_cron_sync_guarantors_backend_%d'%(backend.id),
                                                  'model': 'ir.cron',
                                                  'res_id' : new_cron.id,
                                                  'noupdate' : True
                                                  })
        else:
            cron_exist = self.env.ref('cenit_restrict_sync.ir_cron_sync_guarantors_backend_%d'%(backend.id),raise_if_not_found=False)
            if cron_exist:
                cron_exist.write({'active':False})
        return True
    
    @api.multi   
    def setup_sync_patients(self,backend):
        if self.sync_patients:
            cron_exist = self.env.ref('cenit_restrict_sync.ir_cron_sync_patients_backend_%d'%(backend.id),raise_if_not_found=False)
            vals = {
                    'active' : True,
                    'interval_number':self.sync_patients_interval_number,
                    'interval_type':self.sync_patients_interval_type,
                    'nextcall':self.sync_patients_next_execution,
                    'month_number':self.sync_patients_month_number,
                    'args':"[[('id','=',%d)]]"%(backend.id)
                    }
                    
            if cron_exist:
                cron_exist.write(vals)
            else:
                sync_patients_cron = self.env.ref('cenit_restrict_sync.ir_cron_sync_patients',raise_if_not_found=False)
                if not sync_patients_cron:
                    raise Warning('Core settings of Cenit are deleted, please upgrade Vitalpet module  to back this settings..')
                
                name = 'Cenit - '+backend.name + ' : Sync Pets'
                vals.update({'name' : name})
                new_cron = sync_patients_cron.copy(default=vals)
                self.env['ir.model.data'].create({'module':'cenit_restrict_sync',
                                                  'name':'ir_cron_sync_patients_backend_%d'%(backend.id),
                                                  'model': 'ir.cron',
                                                  'res_id' : new_cron.id,
                                                  'noupdate' : True
                                                  })
        else:
            cron_exist = self.env.ref('cenit_restrict_sync.ir_cron_sync_patients_backend_%d'%(backend.id),raise_if_not_found=False)
            if cron_exist:
                cron_exist.write({'active':False})
        return True
    
    @api.multi   
    def setup_sync_products(self,backend):
        if self.sync_products:
            cron_exist = self.env.ref('cenit_restrict_sync.ir_cron_sync_products_backend_%d'%(backend.id),raise_if_not_found=False)
            vals = {
                    'active' : True,
                    'interval_number':self.sync_products_interval_number,
                    'interval_type':self.sync_products_interval_type,
                    'nextcall':self.sync_products_next_execution,
                    'month_number':self.sync_products_month_number,
                    'args':"[[('id','=',%d)]]"%(backend.id)
                    }
                    
            if cron_exist:
                cron_exist.write(vals)
            else:
                sync_products_cron = self.env.ref('cenit_restrict_sync.ir_cron_sync_products',raise_if_not_found=False)
                if not sync_products_cron:
                    raise Warning('Core settings of Cenit are deleted, please upgrade Vitalpet module  to back this settings..')
                
                name = 'Cenit - '+backend.name + ' : Sync Products'
                vals.update({'name' : name})
                new_cron = sync_products_cron.copy(default=vals)
                self.env['ir.model.data'].create({'module':'cenit_restrict_sync',
                                                  'name':'ir_cron_sync_products_backend_%d'%(backend.id),
                                                  'model': 'ir.cron',
                                                  'res_id' : new_cron.id,
                                                  'noupdate' : True
                                                  })
        else:
            cron_exist = self.env.ref('cenit_restrict_sync.ir_cron_sync_products_backend_%d'%(backend.id),raise_if_not_found=False)
            if cron_exist:
                cron_exist.write({'active':False})
        return True
    
    
    @api.multi   
    def setup_sync_reminders(self,backend):
        if self.sync_reminders:
            cron_exist = self.env.ref('cenit_restrict_sync.ir_cron_sync_reminders_backend_%d'%(backend.id),raise_if_not_found=False)
            vals = {
                    'active' : True,
                    'interval_number':self.sync_reminders_interval_number,
                    'interval_type':self.sync_reminders_interval_type,
                    'nextcall':self.sync_reminders_next_execution,
                    'month_number':self.sync_reminders_month_number,
                    'args':"[[('id','=',%d)]]"%(backend.id)
                    }
                    
            if cron_exist:
                cron_exist.write(vals)
            else:
                sync_reminders_cron = self.env.ref('cenit_restrict_sync.ir_cron_sync_reminders',raise_if_not_found=False)
                if not sync_reminders_cron:
                    raise Warning('Core settings of Cenit are deleted, please upgrade Vitalpet module  to back this settings..')
                
                name = 'Cenit - '+backend.name + ' : Sync Reminders'
                vals.update({'name' : name})
                new_cron = sync_reminders_cron.copy(default=vals)
                self.env['ir.model.data'].create({'module':'cenit_restrict_sync',
                                                  'name':'ir_cron_sync_reminders_backend_%d'%(backend.id),
                                                  'model': 'ir.cron',
                                                  'res_id' : new_cron.id,
                                                  'noupdate' : True
                                                  })
        else:
            cron_exist = self.env.ref('cenit_restrict_sync.ir_cron_sync_reminders_backend_%d'%(backend.id),raise_if_not_found=False)
            if cron_exist:
                cron_exist.write({'active':False})
        return True
    
    @api.multi   
    def setup_sync_procedures(self,backend):
        if self.sync_procedures:
            cron_exist = self.env.ref('cenit_restrict_sync.ir_cron_sync_procedures_backend_%d'%(backend.id),raise_if_not_found=False)
            vals = {
                    'active' : True,
                    'interval_number':self.sync_procedures_interval_number,
                    'interval_type':self.sync_procedures_interval_type,
                    'nextcall':self.sync_procedures_next_execution,
                    'month_number':self.sync_procedures_month_number,
                    'args':"[[('id','=',%d)]]"%(backend.id)
                    }
                    
            if cron_exist:
                cron_exist.write(vals)
            else:
                sync_procedures_cron = self.env.ref('cenit_restrict_sync.ir_cron_sync_procedures',raise_if_not_found=False)
                if not sync_procedures_cron:
                    raise Warning('Core settings of Cenit are deleted, please upgrade Vitalpet module  to back this settings..')
                
                name = 'Cenit - '+backend.name + ' : Sync Procedures'
                vals.update({'name' : name})
                new_cron = sync_procedures_cron.copy(default=vals)
                self.env['ir.model.data'].create({'module':'cenit_restrict_sync',
                                                  'name':'ir_cron_sync_procedures_backend_%d'%(backend.id),
                                                  'model': 'ir.cron',
                                                  'res_id' : new_cron.id,
                                                  'noupdate' : True
                                                  })
        else:
            cron_exist = self.env.ref('cenit_restrict_sync.ir_cron_sync_procedures_backend_%d'%(backend.id),raise_if_not_found=False)
            if cron_exist:
                cron_exist.write({'active':False})
        return True
    
    @api.multi   
    def setup_sync_product_orders(self,backend):
        if self.sync_product_orders:
            cron_exist = self.env.ref('cenit_restrict_sync.ir_cron_sync_product_orders_backend_%d'%(backend.id),raise_if_not_found=False)
            vals = {
                    'active' : True,
                    'interval_number':self.sync_product_orders_interval_number,
                    'interval_type':self.sync_product_orders_interval_type,
                    'nextcall':self.sync_product_orders_next_execution,
                    'month_number':self.sync_product_orders_month_number,
                    'args':"[[('id','=',%d)]]"%(backend.id)
                    }
                    
            if cron_exist:
                cron_exist.write(vals)
            else:
                sync_product_orders_cron = self.env.ref('cenit_restrict_sync.ir_cron_sync_product_orders',raise_if_not_found=False)
                if not sync_product_orders_cron:
                    raise Warning('Core settings of Cenit are deleted, please upgrade Vitalpet module  to back this settings..')
                
                name = 'Cenit - '+backend.name + ' : Sync Product Orderss'
                vals.update({'name' : name})
                new_cron = sync_product_orders_cron.copy(default=vals)
                self.env['ir.model.data'].create({'module':'cenit_restrict_sync',
                                                  'name':'ir_cron_sync_product_orders_backend_%d'%(backend.id),
                                                  'model': 'ir.cron',
                                                  'res_id' : new_cron.id,
                                                  'noupdate' : True
                                                  })
        else:
            cron_exist = self.env.ref('cenit_restrict_sync.ir_cron_sync_product_orders_backend_%d'%(backend.id),raise_if_not_found=False)
            if cron_exist:
                cron_exist.write({'active':False})
        return True
    
    @api.multi   
    def setup_sync_transactions(self,backend):
        if self.sync_transactions:
            cron_exist = self.env.ref('cenit_restrict_sync.ir_cron_sync_transactions_backend_%d'%(backend.id),raise_if_not_found=False)
            vals = {
                    'active' : True,
                    'interval_number':self.sync_transactions_interval_number,
                    'interval_type':self.sync_transactions_interval_type,
                    'nextcall':self.sync_transactions_next_execution,
                    'month_number':self.sync_transactions_month_number,
                    'args':"[[('id','=',%d)]]"%(backend.id)
                    }
                    
            if cron_exist:
                cron_exist.write(vals)
            else:
                sync_transactions_cron = self.env.ref('cenit_restrict_sync.ir_cron_sync_transactions',raise_if_not_found=False)
                if not sync_transactions_cron:
                    raise Warning('Core settings of Cenit are deleted, please upgrade Vitalpet module  to back this settings..')
                
                name = 'Cenit - '+backend.name + ' : Sync Transactions'
                vals.update({'name' : name})
                new_cron = sync_transactions_cron.copy(default=vals)
                self.env['ir.model.data'].create({'module':'cenit_restrict_sync',
                                                  'name':'ir_cron_sync_transactions_backend_%d'%(backend.id),
                                                  'model': 'ir.cron',
                                                  'res_id' : new_cron.id,
                                                  'noupdate' : True
                                                  })
        else:
            cron_exist = self.env.ref('cenit_restrict_sync.ir_cron_sync_transactions_backend_%d'%(backend.id),raise_if_not_found=False)
            if cron_exist:
                cron_exist.write({'active':False})
        return True
    
       
    @api.multi   
    def run_sync_providers(self):
        if self.sync_providers:
            cron_exist = self.env.ref('cenit_restrict_sync.ir_cron_sync_providers_backend_%d'%(self.backend_id.id),raise_if_not_found=False)
            return cron_exist.method_direct_trigger()
    
    @api.multi   
    def run_sync_guarantors(self):
        if self.sync_guarantors:
            cron_exist = self.env.ref('cenit_restrict_sync.ir_cron_sync_guarantors_backend_%d'%(self.backend_id.id),raise_if_not_found=False)
            return cron_exist.method_direct_trigger()
    
    @api.multi   
    def run_sync_patients(self):
        if self.sync_patients:
            cron_exist = self.env.ref('cenit_restrict_sync.ir_cron_sync_patients_backend_%d'%(self.backend_id.id),raise_if_not_found=False)
            return cron_exist.method_direct_trigger()
    
    @api.multi   
    def run_sync_products(self):
        if self.sync_products:
            cron_exist = self.env.ref('cenit_restrict_sync.ir_cron_sync_products_backend_%d'%(self.backend_id.id),raise_if_not_found=False)
            return cron_exist.method_direct_trigger()
    
    
    @api.multi   
    def run_sync_reminders(self):
        if self.sync_reminders:
            cron_exist = self.env.ref('cenit_restrict_sync.ir_cron_sync_reminders_backend_%d'%(self.backend_id.id),raise_if_not_found=False)
            return cron_exist.method_direct_trigger()
        
    @api.multi   
    def run_sync_procedures(self):
        if self.sync_procedures:
            cron_exist = self.env.ref('cenit_restrict_sync.ir_cron_sync_procedures_backend_%d'%(self.backend_id.id),raise_if_not_found=False)
            return cron_exist.method_direct_trigger()
    
    @api.multi   
    def run_sync_product_orders(self):
        if self.sync_product_orders:
            cron_exist = self.env.ref('cenit_restrict_sync.ir_cron_sync_product_orders_backend_%d'%(self.backend_id.id),raise_if_not_found=False)
            return cron_exist.method_direct_trigger()
    
    @api.multi   
    def run_sync_transactions(self):
        if self.sync_transactions:
            cron_exist = self.env.ref('cenit_restrict_sync.ir_cron_sync_transactions_backend_%d'%(self.backend_id.id),raise_if_not_found=False)
            return cron_exist.method_direct_trigger()
        