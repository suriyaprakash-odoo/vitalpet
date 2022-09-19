from odoo import api, fields, models, _



class CrossoveredBudgetLines(models.Model):
    _inherit = "crossovered.budget.lines"

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        result = super(CrossoveredBudgetLines, self).read_group(domain, fields, groupby, offset, limit=limit,orderby=orderby,lazy=True)
        res = result
        cusRes=[]
        for re in reversed(res):
            practical_amount=theoritical_amount=percentage=i=0
            for line in self.env['crossovered.budget.lines'].search(re['__domain']):
                practical_amount+=line.practical_amount
                theoritical_amount+=line.theoritical_amount
                percentage+=line.percentage
                i+=1
            re['practical_amount'] = practical_amount    
            re['theoritical_amount'] = theoritical_amount    
            re['percentage'] = percentage/i if i>0 else 0            
                
            cusRes.append(re)
        return cusRes