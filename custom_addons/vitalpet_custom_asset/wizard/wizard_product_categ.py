from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ProductCategoryWizard(models.TransientModel):
    _name = 'product.category.wizard'

    product_category_id = fields.Many2one('product.category', 'Category')
# 
    @api.multi
    def confirm(self):
        context = dict(self._context)
        context['product_category_id'] = self.product_category_id.id  
        rows = self.env['account.asset.category'].browse(self.env.context.get('active_ids'))
        product_asset_field = self.env['ir.model.fields'].search([('name', '=', 'asset_category_id'),('model', '=', 'product.template')])
        category_asset_field = self.env['ir.model.fields'].search([('name', '=', 'asset_category_pro_id'),('model', '=', 'product.category')])
        for rec in  rows:             
            if rec:
                ir_property = self.env['ir.property'].search([
                        ('name', '=', 'asset_category_pro_id'),
                        ('company_id', '=', rec.company_id.id),
                        ('fields_id', '=', category_asset_field.id),
                        ('value_reference', '=', 'account.asset.category,'+str(rec.id))
                    ])
                if ir_property:
                    return {
                        'name': ('Assign to product'),
                        'view_type': 'form',
                        'view_mode': 'form',
                        'res_model': 'assign.product.category.warning',
                        'view_id': self.env.ref('vitalpet_custom_asset.assign_product_category_warnig_form').id,
                        'type': 'ir.actions.act_window',
                        'context': context,
                        'target': 'new'
                    }
                else:
                    self.env['ir.property'].create({
                            'name': 'asset_category_pro_id',
                            'company_id':rec.company_id.id,
                            'type':'many2one',
                            'fields_id':category_asset_field.id,
                            'res_id': 'product.category,'+str(self.product_category_id.id),
                            'value_reference':'account.asset.category,'+str(rec.id)
                        });
                    products = self.env['product.product'].search([('categ_id', '=', self.product_category_id.id)])
                    for product in products:
                        self.env['ir.property'].create({
                            'name': 'asset_category_id',
                            'company_id':rec.company_id.id,
                            'type':'many2one',
                            'fields_id':product_asset_field.id,
                            'res_id': 'product.template,'+str(product.id),
                            'value_reference':'account.asset.category,'+str(rec.id)
                        });
        tid = context['active_ids']
        for loop in tid:
            asset_obj = self.env['account.asset.category'].search([('id','=',loop)])
            asset_obj.assinged = True
        return True
    

class AssignProductCategoryWarning(models.TransientModel):
    _name = 'assign.product.category.warning' 
    
    def continue_to_assign(self):        
        product_category_id = self.env.context.get('product_category_id')
        if product_category_id:
            product_new_category_id =  product_category_id   
        rows = self.env['account.asset.category'].browse(self.env.context.get('active_ids'))
        product_asset_field = self.env['ir.model.fields'].search([('name', '=', 'asset_category_id'),('model', '=', 'product.template')])
        category_asset_field = self.env['ir.model.fields'].search([('name', '=', 'asset_category_pro_id'),('model', '=', 'product.category')])
        for rec in  rows:             
            if rec:
                ir_property = self.env['ir.property'].search([
                        ('name', '=', 'asset_category_pro_id'),
                        ('company_id', '=', rec.company_id.id),
                        ('fields_id', '=', category_asset_field.id),
                        ('value_reference', '=', 'account.asset.category,'+str(rec.id))
                    ])
                if ir_property:
                    if product_category_id==False:
                        split_product_category_id = ir_property.res_id.split(',')
                        if split_product_category_id:
                            product_new_category_id = int(split_product_category_id[1])
                        ir_property. unlink()
                        rec.assinged = False
                    else:
                        rec.assinged = True                    
                        ir_property.write({'res_id':'product.category,'+str(product_category_id)})
                else:
                    self.env['ir.property'].create({
                            'name': 'asset_category_pro_id',
                            'company_id':rec.company_id.id,
                            'type':'many2one',
                            'fields_id':category_asset_field.id,
                            'res_id': 'product.category,'+str(product_category_id),
                            'value_reference':'account.asset.category,'+str(rec.id)
                        });
                    rec.assinged = True
                products = self.env['product.template'].search([('categ_id', '=', product_new_category_id)])
                for product in products:
                    print product
                    ir_property_product = self.env['ir.property'].search([
                        ('name', '=', 'asset_category_id'),
                        ('company_id', '=', rec.company_id.id),
                        ('fields_id', '=', product_asset_field.id),
                        ('value_reference', '=', 'account.asset.category,'+str(rec.id)),
                        ('res_id', '=', 'product.template,'+str(product.id))])
                    if ir_property_product:
                        if product_category_id==False:
                            ir_property_product. unlink()
                        else:
                            ir_property_product.write({'res_id':'product.template,'+str(product.id)})
                    else:
                        self.env['ir.property'].create({
                            'name': 'asset_category_id',
                            'company_id':rec.company_id.id,
                            'type':'many2one',
                            'fields_id':product_asset_field.id,
                            'res_id': 'product.template,'+str(product.id),
                            'value_reference':'account.asset.category,'+str(rec.id)
                        });
    
    


