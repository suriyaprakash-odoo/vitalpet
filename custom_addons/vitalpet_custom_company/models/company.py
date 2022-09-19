from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, RedirectWarning, ValidationError
from odoo.http import request
import odoo


class Http(models.AbstractModel):
    _inherit = 'ir.http'
     
#     def session_info(self):
#         user = request.env.user
#         display_switch_company_menu = user.has_group('base.group_multi_company') and len(user.company_ids) > 1
#         version_info = odoo.service.common.exp_version()
#         lst_code = []
#         for comp in user.company_ids:
#             if comp.code:
#                 lst_code.append((comp.id,'[ '+ str(str(comp.code or '') + ' ] - ' + str(comp.name))))
#             else:
#                 lst_code.append((comp.id,str(comp.name)))                        
#         if user.company_id.code:
#             code = (user.company_id.id, '[ ' + str(user.company_id.code or '') + '] - ' + str(user.company_id.name))
#         else:
#             code = (user.company_id.id, str(user.company_id.name))
#               
#         return {
#             "session_id": request.session.sid,
#             "uid": request.session.uid,
#             "is_admin": request.env.user.has_group('base.group_system'),
#             "is_superuser": request.env.user._is_superuser(),
#             "user_context": request.session.get_context() if request.session.uid else {},
#             "db": request.session.db,
#             "server_version": version_info.get('server_version'),
#             "server_version_info": version_info.get('server_version_info'),
#             "name": user.name,
#             "username": user.login,
#             "company_id": request.env.user.company_id.id if request.session.uid else None,
#             "partner_id": request.env.user.partner_id.id if request.session.uid and request.env.user.partner_id else None, 
#             "user_companies": {'current_company': code, 'allowed_companies':lst_code} if display_switch_company_menu else False,
#             "currencies": self.get_currencies(),
#         }
