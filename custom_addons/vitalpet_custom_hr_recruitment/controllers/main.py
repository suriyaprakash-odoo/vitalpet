import base64
import json
import pytz

from datetime import datetime
from psycopg2 import IntegrityError
from urlparse import urljoin

from odoo import http
from odoo.http import request
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.translate import _
from odoo.exceptions import ValidationError
from odoo.addons.base.ir.ir_qweb.fields import nl2br
# from recaptcha.client import captcha

from odoo.addons.website.models.website import slug
from odoo.addons.web.controllers.main import WebClient, Binary, Home

    
class Website_new(Home):
    
    
    @http.route('/applicant/welcome_page', type='http', auth="public", website=True)
    def page_new(self):
        applicant=request.env['hr.applicant'].sudo().search([('id','=', request.session.form_builder_id)]);
        applicant.ensure_one()
        
        if not applicant.response_id:
            response = applicant.env['survey.user_input'].sudo().create({'survey_id': applicant.job_id.application_survey_id.id, 'partner_id': applicant.partner_id.id})
            applicant.response_id = response.id
        else:
            response = applicant.response_id
        token = response.token
        trail = "/%s" % token if token else ""
        
        base_url = request.env['ir.config_parameter'].get_param('web.base.url')            
        url=urljoin(base_url, "survey/fill/%s" % (slug(applicant.job_id.application_survey_id)))+"/"+str(token)        
        return request.redirect(url)


class WebsiteForm(http.Controller):

    # Check and insert values from the form on the model <model>
    @http.route('/website_form/<string:model_name>', type='http', auth="public", methods=['POST'], website=True)
    def website_form(self, model_name, **kwargs):
        if model_name!='hr.applicant':
            
            model_record = request.env['ir.model'].search([('model', '=', model_name), ('website_form_access', '=', True)])
            if not model_record:
                return json.dumps(False)
    
            try:
                data = self.extract_data(model_record, request.params)
            # If we encounter an issue while extracting data
            except ValidationError, e:
                # I couldn't find a cleaner way to pass data to an exception
                return json.dumps({'error_fields' : e.args[0]})
    
            try:
                id_record = self.insert_record(request, model_record, data['record'], data['custom'], data.get('meta'))
                if id_record:
                    self.insert_attachment(model_record, id_record, data['attachments'])
    
            # Some fields have additional SQL constraints that we can't check generically
            # Ex: crm.lead.probability which is a float between 0 and 1
            # TODO: How to get the name of the erroneous field ?
            except IntegrityError:
                return json.dumps(False)
    
            request.session['form_builder_model'] = model_record.name
            request.session['form_builder_id']    = id_record
    
            return json.dumps({'id': id_record})
        
        else:

            model_record = request.env['ir.model'].search([('model', '=', model_name), ('website_form_access', '=', True)])
            
            secret_key = "6LdNeiQUAAAAAO76-DjeBx-b7hbblB15b_q-bBuD"
            if secret_key:
                if not model_record:
                    return json.dumps(False)
                try:
                    data = self.extract_data(model_record, request.params)              
                    print data
                # If we encounter an issue while extracting data
                except ValidationError, e:
                    # I couldn't find a cleaner way to pass data to an exception
                    return json.dumps({'error_fields' : e.args[0]})
                #Custom start
                #print model_name
                # #if model_name=="hr.applicant"
                
                
                # if 'g-recaptcha-response' in kwargs.keys():
                #     response = captcha.submit(
                #         '',
                #         kwargs['g-recaptcha-response'],
                #         secret_key,
                #         'http://127.0.0.1:1010/jobs',
                #     )
              
                #     if not response.is_valid:
                #         print "1"
                #     else:
                #         return json.dumps(False)
                # else:                
                #     return json.dumps(False)
                #Custom end
                try:
                    # data['record']['description']=''  
                    id_record = self.insert_record(request, model_record, data['record'], data['custom'], data.get('meta'))
                    if id_record:
                        self.insert_attachment(model_record, id_record, data['attachments'])
                    
                # Some fields have additional SQL constraints that we can't check generically
                # Ex: crm.lead.probability which is a float between 0 and 1
                # TODO: How to get the name of the erroneous field ?
                except IntegrityError:
                    print 232132111
                    return json.dumps(False)
                
                request.session['form_builder_model'] = model_record.name
                request.session['form_builder_id']    = id_record
                return json.dumps({'id': id_record})

    # Constants string to make custom info and metadata readable on a text field

    _custom_label = "%s\n___________\n\n" % _("Custom infos")  # Title for custom fields
    _meta_label = "%s\n________\n\n" % _("Metadata")  # Title for meta data

    # Dict of dynamically called filters following type of field to be fault tolerent

    def identity(self, field_label, field_input):
        return field_input

    def integer(self, field_label, field_input):
        return int(field_input)

    def floating(self, field_label, field_input):
        return float(field_input)

    def boolean(self, field_label, field_input):
        return bool(field_input)

    def date(self, field_label, field_input):
        lang = request.env['ir.qweb.field'].user_lang()
        return datetime.strptime(field_input, lang.date_format).strftime(DEFAULT_SERVER_DATE_FORMAT)

    def datetime(self, field_label, field_input):
        lang = request.env['ir.qweb.field'].user_lang()
        strftime_format = (u"%s %s" % (lang.date_format, lang.time_format))
        user_tz = pytz.timezone(request.context.get('tz') or request.env.user.tz or 'UTC')
        dt = user_tz.localize(datetime.strptime(field_input, strftime_format)).astimezone(pytz.utc)
        return dt.strftime(DEFAULT_SERVER_DATETIME_FORMAT)

    def binary(self, field_label, field_input):
        return base64.b64encode(field_input.read())

    def one2many(self, field_label, field_input):
        return [int(i) for i in field_input.split(',')]

    def many2many(self, field_label, field_input, *args):
        return [(args[0] if args else (6,0)) + (self.one2many(field_label, field_input),)]

    _input_filters = {
        'char': identity,
        'text': identity,
        'html': identity,
        'date': date,
        'datetime': datetime,
        'many2one': integer,
        'one2many': one2many,
        'many2many':many2many,
        'selection': identity,
        'boolean': boolean,
        'integer': integer,
        'float': floating,
        'binary': binary,
    }


    # Extract all data sent by the form and sort its on several properties
    def extract_data(self, model, values):

        data = {
            'record': {},        # Values to create record
            'attachments': [],  # Attached files
            'custom': '',        # Custom fields values
        }

        authorized_fields = model.sudo()._get_form_writable_fields()
        error_fields = []


        for field_name, field_value in values.items():
            # If the value of the field if a file
            if hasattr(field_value, 'filename'):
                # Undo file upload field name indexing
                field_name = field_name.rsplit('[', 1)[0]

                # If it's an actual binary field, convert the input file
                # If it's not, we'll use attachments instead
                if field_name in authorized_fields and authorized_fields[field_name]['type'] == 'binary':
                    data['record'][field_name] = base64.b64encode(field_value.read())
                else:
                    field_value.field_name = field_name
                    data['attachments'].append(field_value)

            # If it's a known field
            elif field_name in authorized_fields:
                try:
                    input_filter = self._input_filters[authorized_fields[field_name]['type']]
                    data['record'][field_name] = input_filter(self, field_name, field_value)
                except ValueError:
                    error_fields.append(field_name)

            # If it's a custom field
            elif field_name != 'context':
                data['custom'] += "%s : %s\n" % (field_name.decode('utf-8'), field_value)

        # Add metadata if enabled
        environ = request.httprequest.headers.environ
        if(request.website.website_form_enable_metadata):
            data['meta'] += "%s : %s\n%s : %s\n%s : %s\n%s : %s\n" % (
                "IP"                , environ.get("REMOTE_ADDR"),
                "USER_AGENT"        , environ.get("HTTP_USER_AGENT"),
                "ACCEPT_LANGUAGE"   , environ.get("HTTP_ACCEPT_LANGUAGE"),
                "REFERER"           , environ.get("HTTP_REFERER")
            )

        # This function can be defined on any model to provide
        # a model-specific filtering of the record values
        # Example:
        # def website_form_input_filter(self, values):
        #     values['name'] = '%s\'s Application' % values['partner_name']
        #     return values
        dest_model = request.env[model.model]
        if hasattr(dest_model, "website_form_input_filter"):
            data['record'] = dest_model.website_form_input_filter(request, data['record'])

        missing_required_fields = [label for label, field in authorized_fields.iteritems() if field['required'] and not label in data['record']]
        if any(error_fields):
            raise ValidationError(error_fields + missing_required_fields)

        return data

    def insert_record(self, request, model, values, custom, meta=None):
        record = request.env[model.model].sudo().create(values)

        if custom or meta:
            default_field = model.website_form_default_field_id
            default_field_data = values.get(default_field.name, '')
#             custom_content = (default_field_data + "\n\n" if default_field_data else '') \
#                            + (self._custom_label + custom + "\n\n" if custom else '') \
#                            + (self._meta_label + meta if meta else '')
                           
            custom_content=""
            # If there is a default field configured for this model, use it.
            # If there isn't, put the custom data in a message instead
            if default_field.name:
                if default_field.ttype == 'html' or model.model == 'mail.mail':
                    custom_content = nl2br(custom_content)
                record.update({default_field.name: custom_content})
            else:
                values = {
                    'body': nl2br(custom_content),
                    'model': model.model,
                    'message_type': 'comment',
                    'no_auto_thread': False,
                    'res_id': record.id,
                }
                mail_id = request.env['mail.message'].sudo().create(values)

        return record.id

    # Link all files attached on the form
    def insert_attachment(self, model, id_record, files):
        orphan_attachment_ids = []
        record = model.env[model.model].browse(id_record)
        authorized_fields = model.sudo()._get_form_writable_fields()
        for file in files:
            custom_field = file.field_name not in authorized_fields
            attachment_value = {
                'name': file.field_name if custom_field else file.filename,
                'datas': base64.encodestring(file.read()),
                'datas_fname': file.filename,
                'res_model': model.model,
                'res_id': record.id,
            }
            attachment_id = request.env['ir.attachment'].sudo().create(attachment_value)
            if attachment_id and not custom_field:
                record.sudo()[file.field_name] = [(4, attachment_id.id)]
            else:
                orphan_attachment_ids.append(attachment_id.id)

        # If some attachments didn't match a field on the model,
        # we create a mail.message to link them to the record
        if orphan_attachment_ids:
            if model.model != 'mail.mail':
                values = {
                    'body': _('<p>Attached files : </p>'),
                    'model': model.model,
                    'message_type': 'comment',
                    'no_auto_thread': False,
                    'res_id': id_record,
                    'attachment_ids': [(6, 0, orphan_attachment_ids)],
                }
                mail_id = request.env['mail.message'].sudo().create(values)
        else:
            # If the model is mail.mail then we have no other choice but to
            # attach the custom binary field files on the attachment_ids field.
            for attachment_id_id in orphan_attachment_ids:
                record.attachment_ids = [(4, attachment_id_id)]




class WebsiteHrRecruitment(http.Controller):
    @http.route([
        '/jobs',
        '/jobs/country/<model("res.country"):country>',
        '/jobs/department/<model("hr.department"):department>',
        '/jobs/country/<model("res.country"):country>/department/<model("hr.department"):department>',
        '/jobs/office/<int:office_id>',
        '/jobs/country/<model("res.country"):country>/office/<int:office_id>',
        '/jobs/department/<model("hr.department"):department>/office/<int:office_id>',
        '/jobs/country/<model("res.country"):country>/department/<model("hr.department"):department>/office/<int:office_id>',
    ], type='http', auth="public", website=True)
    def jobs(self, country=None, department=None, office_id=None, **kwargs):
        env = request.env(context=dict(request.env.context, show_address=True, no_tag_br=True))
        Country = env['res.country']
        Jobs = env['hr.job']
        Templates = env['hr.job.template']

        # List jobs available to current UID
        job_ids = Jobs.search([], order="website_published desc,no_of_recruitment desc").ids
        job_templates = Templates.search([('active_state', '=', True)]).ids
        # Browse jobs as superuser, because address is restricted
        jobs = Jobs.sudo().browse(job_ids)
        templates = Templates.sudo().browse(job_templates)
        
        # Default search by user country
        if not (country or department or office_id or kwargs.get('all_countries')):
            country_code = request.session['geoip'].get('country_code')
            if country_code:
                countries_ = Country.search([('code', '=', country_code)])
                country = countries_[0] if countries_ else None
                if not any(j for j in jobs if j.address_id and j.address_id.country_id == country):
                    country = False

        # Filter job / office for country
        if country and not kwargs.get('all_countries'):
            jobs = [j for j in jobs if j.address_id is None or j.address_id.country_id and j.address_id.country_id.id == country.id]
            offices = set(j.address_id for j in jobs if j.address_id is None or j.address_id.country_id and j.address_id.country_id.id == country.id)
        else:
            offices = set(j.address_id for j in jobs if j.address_id)

        # Deduce departments and countries offices of those jobs
        departments = set(j.department_id for j in jobs if j.department_id)
        countries = set(o.country_id for o in offices if o.country_id)

        if department:
            jobs = (j for j in jobs if j.department_id and j.department_id.id == department.id)
        if office_id and office_id in map(lambda x: x.id, offices):
            jobs = (j for j in jobs if j.address_id and j.address_id.id == office_id)
        else:
            office_id = False
        print jobs
        print templates


        return request.render("website_hr_recruitment.index", {
            'jobs': jobs,
            'job_templates': templates,
            'countries': countries,
            'departments': departments,
            'offices': offices,
            'country_id': country,
            'department_id': department,
            'office_id': office_id,
        })



    @http.route([
        '/jobs/search/<model("hr.job.template"):job>',        
    ], type='http', auth="public", website=True)
    def jobs_search(self, job, **kwargs):
        env = request.env(context=dict(request.env.context, show_address=True, no_tag_br=True))
 
        Country = env['res.country']
        Jobs = env['hr.job']
 
        # List jobs available to current UID
        job_ids = Jobs.search([]).ids
        jobs = Jobs.sudo().browse(job_ids)
        
        
        # Render page
        return request.render("vitalpet_custom_hr_recruitment.index_temp", {
            'jobs': jobs,
            'template_id': job.id,
        })
        

    @http.route('/jobs/detail/<model("hr.job"):job>', type='http', auth="public", website=True)
    def jobs_detail(self, job, **kwargs):
        return request.render("website_hr_recruitment.detail", {
            'job': job.sudo(),
            'main_object': job.sudo(),
        })

    @http.route(['/jobs/apply/<model("hr.job"):job>','/jobs/apply/<model("hr.job"):job>/<string:city>'], type='http', auth="public", website=True)
    def jobs_apply(self, job, city='', **kwargs):
        error = {}
        default = {}
        env = request.env(context=dict(request.env.context, show_address=True, no_tag_br=True)) 
        States = env['res.country.state']
 
        # List jobs available to current UID
        state_ids = States.sudo().search([('country_id' , '=' , 235)]).ids
        state = States.sudo().browse(state_ids)
        if 'website_hr_recruitment_error' in request.session:
            error = request.session.pop('website_hr_recruitment_error')
            default = request.session.pop('website_hr_recruitment_default')
        
        over_write_city = request.env['over_write.city'].sudo().search([('job_temp_id', '=', job.id), ('city_wizard', '=', city)])
        
        return request.render("website_hr_recruitment.apply", {
            'job': job,
            'error': error,
            'default': default,
            'states': state,
            'over_write_city':over_write_city or False
        })
        

