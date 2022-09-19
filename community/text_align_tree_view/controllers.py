# -*- coding: utf-8 -*-
from openerp import http

# class TextAlignTreeView(http.Controller):
#     @http.route('/text_align_tree_view/text_align_tree_view/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/text_align_tree_view/text_align_tree_view/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('text_align_tree_view.listing', {
#             'root': '/text_align_tree_view/text_align_tree_view',
#             'objects': http.request.env['text_align_tree_view.text_align_tree_view'].search([]),
#         })

#     @http.route('/text_align_tree_view/text_align_tree_view/objects/<model("text_align_tree_view.text_align_tree_view"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('text_align_tree_view.object', {
#             'object': obj
#         })