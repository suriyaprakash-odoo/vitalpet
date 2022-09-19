# -*- coding: utf-8 -*-

from datetime import datetime
import difflib
import lxml
import random

from odoo import tools
from odoo import SUPERUSER_ID
from odoo.addons.website.models.website import slug
from odoo import models, fields
from odoo.tools.translate import _

class BlogTag(models.Model):
    _inherit = 'promote.tag'
    _order = 'id ASC'


class BlogPost(models.Model):

            _inherit = 'promote.post'

            body_html = fields.Html('HTML Dynamic Post', sanitize=False)
            video_link = fields.Char('Video URL')


            company_id = fields.Many2one('res.company', 'Company', required=True)
            birdeye_id = fields.Char('BirdEye ID')
            #tags_ids = fields.Many2many('promote.tag', 'tags_relation','blog_post_id','blog_tag_id', 'Post Tags')
        #News Blog
            #title = fields.Char("Post Title")
            short_text =fields.Text("Short Text")
            # content = fields.Text("Content")
        #Adoptions and New Blog
            image = fields.Binary("Image")
            petname = fields.Char('Pet Name')
            city = fields.Char('City')
            age = fields.Integer('Age')
            breed = fields.Char('Breed')
            sex = fields.Selection([('male', 'Male'),('Male', 'Female')])
            weight = fields.Float('Weight')

        #Photos
            caption = fields.Char('Caption')

        #Promotions
            promotion_title = fields.Char('Promotion Title')
            explanation = fields.Char('Explanation')

        #Services
            service = fields.Char('Service')

        #Testimonials
            quote = fields.Char('Quote')
            reviewer_name = fields.Char('Reviewer Name')
            rating = fields.Integer('Rating')
            date_of_review = fields.Date('Date of Review')
            source_url = fields.Char('Source URL')
            reviewer_hometown = fields.Char('Reviewer Hometown')
            source_of_review = fields.Char('Source of Review')
            news_date = fields.Date('News Date')
            expiration_date = fields.Date('Expiration Date')
            state = fields.Selection([('Draft', 'Draft'),('Adopted', 'Adopted'),('Available', 'Available')], default='Draft',string='Status')
            sequence = fields.Integer('Sequence')
            
