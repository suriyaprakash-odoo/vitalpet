from odoo import fields, models, api, _


class Partner(models.Model):
    _inherit = "res.partner"
    
#     is_petowner=fields.Boolean(string="Is Pet Owner")
    is_applicant=fields.Boolean(string="Is Applicant")
#     is_pet=fields.Boolean(string="Is Pet")
#     last_name=fields.Char("Last Name")
    
    
#     @api.multi
#     def name_get(self):
#         result = []
#         for line in self:
#             if line.last_name:
#                 result.append((line.id, (line.name+" "+line.last_name or '')))
#             else:
#                 result.append((line.id, (line.name or '')))
#         return result

class Employee(models.Model):
    _inherit = "hr.employee"
    
#     last_name=fields.Char("Last Name")
#     
#     @api.multi
#     def name_get(self):
#         result = []
#         for line in self:
#             if line.last_name:
#                 result.append((line.id, (line.name+" "+line.last_name or '')))
#             else:
#                 result.append((line.id, (line.name or '')))
#         return result


    
    