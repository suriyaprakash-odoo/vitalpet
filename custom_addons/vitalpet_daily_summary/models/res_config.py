from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp

class idmove_line(models.Model):
    _name = 'idmove.line'

    name = fields.Char(string='Name', required=True)
    incomedep_ref_id = fields.Many2one('sales.summary', 'ID Ref#')
    amount_total = fields.Float(string='Amount')
    debit = fields.Float('Debit', digits=dp.get_precision('Account'))
    credit = fields.Float('Credit', digits=dp.get_precision('Account'))
    account_id = fields.Many2one('account.account', 'Account', required=True, ondelete="cascade",
                                  domain=[('type', '<>', 'view'), ('type', '<>', 'closed')], index=2)
    partner_id = fields.Many2one('res.partner', 'Partner', index=1, ondelete='restrict')
    date_maturity = fields.Date('Due date', index=True, help="This field is used for payable and receivable journal entries. You can put the limit date for the payment of this line.")
    tax_amount = fields.Float('Tax/Base Amount', digits=dp.get_precision('Account'), index=True, help="If the Tax account is a tax code account, this field will contain the taxed amount.If the tax account is base tax code, " \
                                    "this field will contain the basic amount(without tax).")
    amount_currency = fields.Float('Amount Currency',  help="The amount expressed in an optional other currency if it is a multi-currency entry.", digits=dp.get_precision('Account'))
    state = fields.Selection([('draft', 'Unbalanced'), ('valid', 'Balanced')], 'Status', readonly=True, copy=False, default='draft')
    analytic_account_id= fields.Many2one('account.analytic.account', 'Analytic Account')
    company_id = fields.Many2one('res.company', 'Company')
    product_id = fields.Many2one('product.product', 'Product')
    journal_id = fields.Many2one('account.journal', 'Journal')
    group_code = fields.Many2one('sale.summary.group',string='Group Code')
    is_group = fields.Boolean(string='Group')
    service_id = fields.Many2one('sale.summary.config', 'Service')

idmove_line()


class SaleSummaryConfig(models.Model):
    _name = 'sale.summary.config'

    field_label = fields.Selection([('Income','Income'),('Payments','Payments'),('Adjustment','Adjustment'),('Discounts','Discounts'),('Accounts Receivable','Accounts Receivable'),('Metrics','Metrics ')],string='Category')
    category_id = fields.Many2one('ir.model.fields',string='Sales Summary')
    name = fields.Char(compute='get_name', string='Field Name')
    product_id = fields.Many2one('product.product', string='Product Name', required=False)
    product_categ = fields.Many2one('product.category', string='Product Category', required=False)
    desc = fields.Char(string='Reference')
    account_income_id = fields.Char(string='Account', required=False)
    opposite_ac = fields.Char(string='Opposite Account')
    journal_id = fields.Char(string='Journal', required=False)
    debit = fields.Selection([('negative','IF NEGATIVE'),('positive','IF POSITIVE')], required=True)
    credit = fields.Selection([('negative','IF NEGATIVE'),('positive','IF POSITIVE')], required=True)
    # is_active = fields.Boolean(string='Active')
    group_code = fields.Many2one('sale.summary.group',string='Group Code')
    is_group = fields.Boolean(string='Group')
    #reference = fields.Char('Reference')


    def get_name(self):
        if self.category_id:
            self.name = self.category_id.name
        else:
            self.name = ''



    @api.onchange('debit')
    def onchange_debit(self):
        if self.debit == 'negative':
            self.credit = 'positive'
        if self.debit == 'positive':
            self.credit = 'negative'


    @api.onchange('credit')
    def onchange_credit(self):
        if self.credit == 'negative':
            self.debit = 'positive'
        if self.credit == 'positive':
            self.debit = 'negative'


    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.product_categ = self.product_id.categ_id
            self.account_income_id = self.product_id.property_account_income_id.id
            #self.account_expense_id = self.product_id.property_account_expense_id.id


    @api.onchange('product_categ')
    def onchange_product_categ(self):
        if self.product_categ:
            self.account_income_id = self.product_categ.property_account_income_categ_id.id


    @api.model
    def create(self, vals):
        res = super(SaleSummaryConfig, self).create(vals)
        res.name = res.category_id.name
        return res


    # @api.model
    # def write(self, vals):
    #     res = super(SaleSummaryConfig, self).write(vals)
    #     res.name = res.category_id.name
    #     return res



SaleSummaryConfig()


class SaleSummaryGrouping(models.Model):
    _name = 'sale.summary.group'

    name = fields.Char(string='Name')
    code = fields.Char(string='Code')

SaleSummaryGrouping()



class SummaryDashboardGrouping(models.Model):
    _name = 'summary.dashboard.group'

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code')
    group_dashboard = fields.Selection([('missing_practice','Missing reports by Practice'),('draft_balanced','Draft - Balanced but not validated'),('draft_imbalanced','Draft - Imbalanced'),('unbalanced_journal','Unbalanced journal entries'),('practice_kpi','Practice performance (key KPIs)')],'Grouping', required=True)

SummaryDashboardGrouping()







class IrModelFields(models.Model):
    _inherit = 'ir.model.fields'
    

    helper = fields.Char('Helper')
    notes = fields.Text('Notes')
    limit = fields.Integer('Limit')
    client_context = fields.Char('Client Context')

    @api.multi
    def name_get(self):
        res = []
        for field in self:
            res.append((field.id, '%s' % (field.field_description)))
        return res

IrModelFields()
    

class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.multi
    @api.depends('product_variant_ids.summary_count')
    def _summary_count(self):
        for product in self:
            product.summary_count = sum([p.summary_count for p in product.product_variant_ids])

    @api.multi
    def action_view_voucher(self):
        self.ensure_one()
        action = self.env.ref('sales_summary.action_product_voucher_list')
        product_ids = self.product_variant_ids.ids
        print product_ids[0]
        return {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'view_type': action.view_type,
            'view_mode': action.view_mode,
            'target': action.target,
            'context': "{'default_product_id': " + str(product_ids[0]) + "}",
            'res_model': action.res_model,
            'domain': [('product_id.product_tmpl_id', '=', self.id)],
        }

    summary_count = fields.Integer(compute='_summary_count', string='# Sales')
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
