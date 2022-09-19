# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import json
import werkzeug
import itertools
import pytz
import babel.dates
from collections import OrderedDict

from odoo import http, fields, _
from odoo.addons.website.controllers.main import QueryURL
from odoo.addons.website.models.website import slug, unslug
from odoo.exceptions import UserError
from odoo.http import request
from odoo.tools import html2plaintext


class WebsitePromote(http.Controller):
    _blog_post_per_page = 20
    _post_comment_per_page = 10

    def nav_list(self, blog=None):
        dom = blog and [('blog_id', '=', blog.id)] or []
        if not request.env.user.has_group('website.group_website_designer'):
            dom += [('post_date', '<=', fields.Datetime.now())]
        groups = request.env['promote.post']._read_group_raw(
            dom,
            ['name', 'post_date'],
            groupby=["post_date"], orderby="post_date desc")
        for group in groups:
            (r, label) = group['post_date']
            start, end = r.split('/')
            group['post_date'] = label
            group['date_begin'] = start
            group['date_end'] = end

            locale = request.context.get('lang') or 'en_US'
            start = pytz.UTC.localize(fields.Datetime.from_string(start))
            tzinfo = pytz.timezone(request.context.get('tz', 'utc') or 'utc')

            group['month'] = babel.dates.format_datetime(start, format='MMMM', tzinfo=tzinfo, locale=locale)
            group['year'] = babel.dates.format_datetime(start, format='YYYY', tzinfo=tzinfo, locale=locale)

        return OrderedDict((year, [m for m in months]) for year, months in itertools.groupby(groups, lambda g: g['year']))

    def _to_date(self, dt):
        # TODO remove me in master/saas-14
        return fields.Date.from_string(dt)

    @http.route([
        '/promote',
        '/promote/page/<int:page>',
    ], type='http', auth="public", website=True)
    def blogs(self, page=1, **post):
        Blog = request.env['promote.blog']
        blogs = Blog.search([], limit=2)
        if len(blogs) == 1:
            return werkzeug.utils.redirect('/promote/%s' % slug(blogs[0]), code=302)

        BlogPost = request.env['promote.post']
        total = BlogPost.search([], count=True)

        pager = request.website.pager(
            url='/promote',
            total=total,
            page=page,
            step=self._blog_post_per_page,
        )
        posts = BlogPost.search([], offset=(page - 1) * self._blog_post_per_page, limit=self._blog_post_per_page)
        blog_url = QueryURL('', ['blog', 'tag'])
        return request.render("vitalpet_promote.latest_blogs", {
            'posts': posts,
            'pager': pager,
            'blog_url': blog_url,
        })

    @http.route([
        '/promote/<model("promote.blog"):blog>',
        '/promote/<model("promote.blog"):blog>/page/<int:page>',
        '/promote/<model("promote.blog"):blog>/tag/<string:tag>',
        '/promote/<model("promote.blog"):blog>/tag/<string:tag>/page/<int:page>',
    ], type='http', auth="public", website=True)
    def blog(self, blog=None, tag=None, page=1, **opt):
        """ Prepare all values to display the blog.

        :return dict values: values for the templates, containing

         - 'blog': current blog
         - 'blogs': all blogs for navigation
         - 'pager': pager of posts
         - 'active_tag_ids' :  list of active tag ids,
         - 'tags_list' : function to built the comma-separated tag list ids (for the url),
         - 'tags': all tags, for navigation
         - 'state_info': state of published/unpublished filter
         - 'nav_list': a dict [year][month] for archives navigation
         - 'date': date_begin optional parameter, used in archives navigation
         - 'blog_url': help object to create URLs
        """
        date_begin, date_end, state = opt.get('date_begin'), opt.get('date_end'), opt.get('state')
        published_count, unpublished_count = 0, 0

        BlogPost = request.env['promote.post']

        Blog = request.env['promote.blog']
        blogs = Blog.search([], order="create_date asc")

        # build the domain for blog post to display
        domain = []
        # retrocompatibility to accept tag as slug
        active_tag_ids = tag and map(int, [unslug(t)[1] for t in tag.split(',')]) or []
        if active_tag_ids:
            domain += [('tag_ids', 'in', active_tag_ids)]
        if blog:
            domain += [('blog_id', '=', blog.id)]
        if date_begin and date_end:
            domain += [("post_date", ">=", date_begin), ("post_date", "<=", date_end)]

        if request.env.user.has_group('website.group_website_designer'):
            count_domain = domain + [("website_published", "=", True), ("post_date", "<=", fields.Datetime.now())]
            published_count = BlogPost.search_count(count_domain)
            unpublished_count = BlogPost.search_count(domain) - published_count

            if state == "published":
                domain += [("website_published", "=", True), ("post_date", "<=", fields.Datetime.now())]
            elif state == "unpublished":
                domain += ['|', ("website_published", "=", False), ("post_date", ">", fields.Datetime.now())]
        else:
            domain += [("post_date", "<=", fields.Datetime.now())]

        blog_url = QueryURL('', ['blog', 'tag'], blog=blog, tag=tag, date_begin=date_begin, date_end=date_end)

        blog_posts = BlogPost.search(domain, order="post_date desc")
        print 'blog_posts 1', len(blog_posts)
        pager = request.website.pager(
            url=request.httprequest.path.partition('/page/')[0],
            total=len(blog_posts),
            page=page,
            step=self._blog_post_per_page,
            url_args=opt,
        )
        pager_begin = (page - 1) * self._blog_post_per_page
        pager_end = page * self._blog_post_per_page
        blog_posts = blog_posts[pager_begin:pager_end]
        print 'blog_posts 2', len(blog_posts)

        all_tags = blog.all_tags()[blog.id]

        # function to create the string list of tag ids, and toggle a given one.
        # used in the 'Tags Cloud' template.
        def tags_list(tag_ids, current_tag):
            tag_ids = list(tag_ids) # required to avoid using the same list
            if current_tag in tag_ids:
                tag_ids.remove(current_tag)
            else:
                tag_ids.append(current_tag)
            tag_ids = request.env['promote.tag'].browse(tag_ids).exists()
            return ','.join(map(slug, tag_ids))
        values = {
            'blog': blog,
            'blogs': blogs,
            'main_object': blog,
            'tags': all_tags,
            'state_info': {"state": state, "published": published_count, "unpublished": unpublished_count},
            'active_tag_ids': active_tag_ids,
            'tags_list' : tags_list,
            'blog_posts': blog_posts,
            'blog_posts_cover_properties': [json.loads(b.cover_properties) for b in blog_posts],
            'pager': pager,
            'nav_list': self.nav_list(blog),
            'blog_url': blog_url,
            'date': date_begin,
        }
        response = request.render("vitalpet_promote.blog_post_short", values)
        return response

    @http.route(['/promote/<model("promote.blog"):blog>/feed'], type='http', auth="public")
    def blog_feed(self, blog, limit='15'):
        v = {}
        v['blog'] = blog
        v['base_url'] = request.env['ir.config_parameter'].get_param('web.base.url')
        v['posts'] = request.env['promote.post'].search([('blog_id','=', blog.id)],
            limit=min(int(limit), 50),
            order="post_date DESC")
        v['html2plaintext'] = html2plaintext
        r = request.render("vitalpet_promote.blog_feed", v, headers=[('Content-Type', 'application/atom+xml')])
        return r

    @http.route([
            '''/promote/<model("promote.blog"):blog>/post/<model("promote.post", "[('blog_id','=',blog[0])]"):promote_post>''',
    ], type='http', auth="public", website=True)
    def promote_post(self, blog, promote_post, tag_id=None, page=1, enable_editor=None, **post):
        """ Prepare all values to display the blog.

        :return dict values: values for the templates, containing

         - 'promote_post': browse of the current post
         - 'blog': browse of the current blog
         - 'blogs': list of browse records of blogs
         - 'tag': current tag, if tag_id in parameters
         - 'tags': all tags, for tag-based navigation
         - 'pager': a pager on the comments
         - 'nav_list': a dict [year][month] for archives navigation
         - 'next_post': next blog post, to direct the user towards the next interesting post
        """
        BlogPost = request.env['promote.post']
        date_begin, date_end = post.get('date_begin'), post.get('date_end')

        pager_url = "/blogpost/%s" % promote_post.id

        pager = request.website.pager(
            url=pager_url,
            total=len(promote_post.website_message_ids),
            page=page,
            step=self._post_comment_per_page,
            scope=7
        )
        pager_begin = (page - 1) * self._post_comment_per_page
        pager_end = page * self._post_comment_per_page
        comments = promote_post.website_message_ids[pager_begin:pager_end]

        tag = None
        if tag_id:
            tag = request.env['promote.tag'].browse(int(tag_id))
        blog_url = QueryURL('', ['blog', 'tag'], blog=promote_post.blog_id, tag=tag, date_begin=date_begin, date_end=date_end)

        if not promote_post.blog_id.id == blog.id:
            return request.redirect("/promote/%s/post/%s" % (slug(promote_post.blog_id), slug(promote_post)))

        tags = request.env['promote.tag'].search([])

        # Find next Post
        all_post = BlogPost.search([('blog_id', '=', blog.id)])
        if not request.env.user.has_group('website.group_website_designer'):
            all_post = all_post.filtered(lambda r: r.post_date <= fields.Datetime.now())

        if promote_post not in all_post:
            return request.redirect("/promote/%s" % (slug(promote_post.blog_id)))

        # should always return at least the current post
        all_post_ids = all_post.ids
        current_blog_post_index = all_post_ids.index(promote_post.id)
        nb_posts = len(all_post_ids)
        next_post_id = all_post_ids[(current_blog_post_index + 1) % nb_posts] if nb_posts > 1 else None
        next_post = next_post_id and BlogPost.browse(next_post_id) or False

        values = {
            'tags': tags,
            'tag': tag,
            'blog': blog,
            'promote_post': promote_post,
            'blog_post_cover_properties': json.loads(promote_post.cover_properties),
            'main_object': promote_post,
            'nav_list': self.nav_list(blog),
            'enable_editor': enable_editor,
            'next_post': next_post,
            'next_post_cover_properties': json.loads(next_post.cover_properties) if next_post else {},
            'date': date_begin,
            'blog_url': blog_url,
            'pager': pager,
            'comments': comments,
        }
        response = request.render("vitalpet_promote.blog_post_complete", values)

        request.session[request.session.sid] = request.session.get(request.session.sid, [])
        if not (promote_post.id in request.session[request.session.sid]):
            request.session[request.session.sid].append(promote_post.id)
            # Increase counter
            promote_post.sudo().write({
                'visits': promote_post.visits+1,
            })
        return response

    def _blog_post_message(self, blog_post_id, message_content, **post):
        BlogPost = request.env['promote.post']
        # for now, only portal and user can post comment on blog post.
        if request.env.user.id == request.website.user_id.id:
            raise UserError(_('Public user cannot post comments on blog post.'))
        # get the partner of the current user
        partner_id = request.env.user.partner_id.id

        message = BlogPost.message_post(
            int(blog_post_id),
            body=message_content,
            message_type='comment',
            subtype='mt_comment',
            author_id=partner_id,
            path=post.get('path', False),
        )
        return message.id

    def _get_discussion_detail(self, ids, publish=False, **post):
        values = []
        for message in request.env['mail.message'].sudo().browse(ids):
            values.append({
                "id": message.id,
                "author_name": message.author_id.name,
                "author_image": message.author_id.image and \
                    ("data:image/png;base64,%s" % message.author_id.image) or \
                    '/vitalpet_promote/static/src/img/anonymous.png',
                "date": message.date,
                'body': html2plaintext(message.body),
                'website_published' : message.website_published,
                'publish' : publish,
            })
        return values

    @http.route(['/promote/post_discussion'], type='json', auth="public", website=True)
    def post_discussion(self, blog_post_id, **post):
        publish = request.env.user.has_group('website.group_website_publisher')
        message_id = self._blog_post_message(blog_post_id, post.get('comment'), **post)
        return self._get_discussion_detail([message_id], publish, **post)

    @http.route('/promote/<int:blog_id>/post/new', type='http', auth="public", website=True)
    def blog_post_create(self, blog_id, **post):
        new_blog_post = request.env['promote.post'].create({
            'blog_id': blog_id,
            'website_published': False,
        })
        return werkzeug.utils.redirect("/promote/%s/post/%s?enable_editor=1" % (slug(new_blog_post.blog_id), slug(new_blog_post)))

    @http.route('/promote/post_duplicate', type='http', auth="public", website=True, methods=['POST'])
    def blog_post_copy(self, blog_post_id, **post):
        """ Duplicate a blog.

        :param blog_post_id: id of the blog post currently browsed.

        :return redirect to the new blog created
        """
        new_blog_post = request.env['promote.post'].with_context(mail_create_nosubscribe=True).browse(int(blog_post_id)).copy()
        return werkzeug.utils.redirect("/promote/%s/post/%s?enable_editor=1" % (slug(new_blog_post.blog_id), slug(new_blog_post)))

    @http.route('/promote/post_get_discussion/', type='json', auth="public", website=True)
    def discussion(self, post_id=0, path=None, count=False, **post):
        domain = [('res_id', '=', int(post_id)), ('model', '=', 'promote.post'), ('path', '=', path)]
        #check current user belongs to website publisher group
        publish = request.env.user.has_group('website.group_website_publisher')
        if not publish:
            domain.append(('website_published', '=', True))
        messages = request.env['mail.message'].sudo().search(domain, count=count)
        if count:
            return messages.ids
        return self._get_discussion_detail(messages.ids, publish, **post)

    @http.route('/promote/post_get_discussions/', type='json', auth="public", website=True)
    def discussions(self, post_id=0, paths=None, count=False, **post):
        ret = []
        for path in paths:
            result = self.discussion(post_id=post_id, path=path, count=count, **post)
            ret.append({"path": path, "val": result})
        return ret

    @http.route('/promote/post_change_background', type='json', auth="public", website=True)
    def change_bg(self, post_id=0, cover_properties={}, **post):
        if not post_id:
            return False
        return request.env['promote.post'].browse(int(post_id)).write({'cover_properties': json.dumps(cover_properties)})

    @http.route('/promote/get_user/', type='json', auth="public", website=True)
    def get_user(self, **post):
        return [False if request.session.uid else True]
