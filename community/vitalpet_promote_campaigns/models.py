# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date
from dateutil.relativedelta import relativedelta
import datetime
from dateutil import parser
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

try:
    from twilio.rest import Client
except ImportError as err:
    _logger.debug(err)

class promote_carecategory(models.Model):
    _name = 'promote.carecategory'
    _order = 'name desc'

    display_name = fields.Char('Display Name')
    name = fields.Char('Name')
    next_category_id = fields.Many2one('promote.carecategory', 'Next Care_category', help='this carecategroy will apply if maximum age is set')
    age_minimum = fields.Integer('Age Minimum')
    age_maximum = fields.Integer('Age Maximum')
    species_id = fields.Many2one('pims.patient.species','Species')
    include_in_RC = fields.Boolean('Include In Report Card')
    sequence = fields.Integer('Sequence', default=5)

class promote_carecategory_conditions(models.Model):
    _name = 'promote.carecategory.conditions'

    care_category_id = fields.Many2one('promote.carecategory','Care Category', ondelete='cascade')
    Indicator = fields.Selection([ ('red', 'Red'), ('yellow', 'Yellow'), ('green', 'Green') ] , 'Indicator')
    condition = fields.Selection([ ('expired', 'Expired'), ('expires_in3months', 'Expires within 3 months'), ('current', 'Current') ] , 'Condition')
    null_condition = fields.Boolean('Null Condition')
    message = fields.Html('Message')
    min_age =fields.Integer('Minimum age',related='care_category_id.age_minimum')
    max_age =fields.Integer('Maximum age',related='care_category_id.age_maximum')


class care_standard_line(models.Model):
    _name = 'promote.carestandard.line'

    company_id = fields.Many2one('res.company', 'Company')
    frequency = fields.Integer('Frequency', required=True, default=12)
    product_id = fields.Many2one('product.template','Product')
    min_age = fields.Float('Minimum Age')
    max_age = fields.Float('Maximum Age')
    species_id = fields.Many2one('pims.patient.species','Species', help='The Specy is coming directly from Care Category .', related='care_category_id.species_id', store=True)
    care_category_id = fields.Many2one('promote.carecategory', 'Care Category')


    @api.constrains('min_age','max_age')
    def _check_min_max_age(self):

        #for record in self:
            if self.max_age <= self.min_age:

                raise ValidationError("The Maximum Age should be Greater than Minimum Age.")

class product_template(models.Model):
    _inherit = 'product.template'

    care_standard_ids = fields.One2many('promote.carestandard.line', 'product_id', 'Care Standard Lines')

class campaign_reportcard(models.Model):
    _name = 'promote.campaigns.reportcard'

    _sql_constraints = [
         ('UNIQUE pet_id', 'unique(pet_id)', 'Every Pet should have only one Report Card.'),
     ]

    rating = fields.Integer('Rating', compute='compute_rating', store=True)

    @api.one
    @api.depends('reportcard_lines','reportcard_lines.status')
    def compute_rating(self):
        line_rating=[]
        for reportcard_line in self.reportcard_lines:
            if reportcard_line.status == 'green':
                line_rating.append(5)
            elif reportcard_line.status == 'yellow':
                line_rating.append(3)
            elif reportcard_line.status == 'red':
                line_rating.append(1)
        if line_rating:
            self.rating= round( float(sum(line_rating)) / len(line_rating) )

    company_id = fields.Many2one('res.company', 'Company', related='pet_id.company_id',store=True)
    petowner_id = fields.Many2one('res.partner','Pet Owner', domain=[('is_petowner','=',True)],store=True, related='pet_id.parent_id')
    pet_id = fields.Many2one('res.partner', 'Pet', domain=[('is_pet','=',True)], ondelete='cascade' , required=True)
    species_id = fields.Many2one('pims.patient.species','Species', related='pet_id.species_id',store=True)
    breed_id = fields.Many2one('pims.patient.species.breed','Breed', related='pet_id.breed_id',store=True)
    pet_age = fields.Float('Pet Age', related='pet_id.calculated_age',store=True)
    pet_lastvisit_date = fields.Date('Last Visit', related='pet_id.pims_lastvisit_date')
    report_card = fields.Char('Report Card Link', size=1024)
    html_reportcard_link = fields.Char('HTML Report Card', size=1024, compute='compute_html_reportcard_link')
    last_refresh = fields.Date('Last Refresh')
    last_view = fields.Date('Last View')
    days_since_viewed = fields.Integer('Days Since viewed')
    send = fields.Boolean('Send via SMS', default=False)

    editable = fields.Boolean('Editable')
    reportcard_lines = fields.One2many('promote.campaigns.reportcard.line', 'reportcard_id', 'Report Card Lines')

    planned_refresh_date = fields.Date('Next Planned Refresh Date')

    @api.one
    def compute_html_reportcard_link(self):
        self.html_reportcard_link = 'http://dj.vitalpet.net/petowner/' + str(self.petowner_id.id)

    @api.multi
    def toggle_editable(self):
        self.editable = not(self.editable)

    @api.multi
    def reportcard_createlinks(self):
        print 'start reportcard_createlinks :', self.ids, self
        for reportcard_id in self.ids:
            print 'reportcard_id :', reportcard_id
            pdf_result = self.env['report'].get_pdf([reportcard_id], 'vitalpet_promote_campaigns.report_card_pet')

            reportcard_link = '/vitalpet_promote/static/ReportCard_'+ "%06d" % (reportcard_id,) + '.pdf'
            self.browse([reportcard_id]).write( {'report_card': reportcard_link})
            with open('/opt/odoo/vitalpet/' + reportcard_link, "wb") as pdf_file:
                pdf_file.write(bytes(pdf_result))

    @api.multi
    def reportcard_send_sms(self):
        print 'start reportcard_send_sms :', self.ids, self
        send = self.send
        if ( send != False):
            self.send = False
        else:
            self.send = True


#         account_sid_param = self.env['ir.config_parameter'].search([('key','=','odoo_cenit.twilio.account_sid')])
#         print 'account_sid', self.env['ir.config_parameter'].search([('key','=','odoo_cenit.twilio.account_sid')])
#         auth_token_param = self.env['ir.config_parameter'].search([('key','=','odoo_cenit.twilio.auth_token')])
#         client = Client(account_sid_param.value, auth_token_param.value)
#
#         twilio_account_phonenumber = '+14094228075'
#
#         for reportcard_obj in self:
#             client_phonenumber = reportcard_obj.petowner_id.phone
#             message_body = "This is an important Update on your pet health status. https://vetzip10stage.vitalpet.net" + reportcard_obj.report_card.replace('_', '%5F')
#
#             message = client.api.account.messages.create(from_= twilio_account_phonenumber , to= client_phonenumber, body=message_body)
#
#             print 'message sid : ', message.sid


class reportcard_line(models.Model):
    _name = 'promote.campaigns.reportcard.line'
    _order = 'sequence asc'

    name = fields.Char('Sequence', related='care_category_id.display_name', store=True)

    reportcard_id = fields.Many2one('promote.campaigns.reportcard', 'Report Card', ondelete='cascade', required=True)
    pet_id = fields.Many2one('res.partner', 'Pet', related='reportcard_id.pet_id', store=True)

    status = fields.Selection([ ('red', 'Red'), ('yellow', 'Yellow'), ('green', 'Green') ] , 'Status')
    care_category_id = fields.Many2one('promote.carecategory', 'Care Category', ondelete='cascade', required=True)
    message = fields.Html('Message')
    sequence = fields.Integer('Sequence', related='care_category_id.sequence', store=True)

    #dates for changing indicators and delete (when age bigger than max_age)
    delete_date = fields.Date('Delete Date')
    yellow_date = fields.Date('Yellow indicator Date')
    red_date = fields.Date('Red indicator Date')
    transaction_id = fields.Many2one('pims.client.transaction', 'Last Transaction for this Report Card Line')


    @api.one
    def yellow_reportcard_line(self):
        #Lets search for current carecategory condition
        conditions = self.env['promote.carecategory.conditions'].search([('condition', '=', 'expires_in3months'),('care_category_id', '=', self.care_category_id.id)], limit=1)
        ###can be optimized using select instead of search

        if not conditions:
            _logger.warning("no care category condition applies to this case: %s with condition 'expires in 3months'", self.care_category_id.name)
            return False

        self.write({
                    'status' : 'yellow',
                    'message': conditions[0].message,
                    #'delete_date': datetime.datetime.strptime(self.pet_idx_birthday, "%Y-%m-%d") + relativedelta(years=int(default_condition.max_age)) if self.x_birthday and default_condition.max_age else False,
                    #DELETE DATE IS ALREADY SET IN DEFAULTS
                               })

    @api.one
    def red_reportcard_line(self):
        #Lets search for current carecategory condition
        conditions = self.env['promote.carecategory.conditions'].search([('condition', '=', 'expired'),('care_category_id', '=', self.care_category_id.id)], limit=1)
        ###can be optimized using select instead of search

        if not conditions:
            _logger.warning("no care category condition applies to this case: %s with condition 'expires in 3months'", self.care_category_id.name)
            return False

        self.write({
                    'status' : 'red',
                    'message': conditions[0].message,
                    #'delete_date': datetime.datetime.strptime(self.pet_idx_birthday, "%Y-%m-%d") + relativedelta(years=int(default_condition.max_age)) if self.x_birthday and default_condition.max_age else False,
                    #DELETE DATE IS ALREADY SET IN DEFAULTS
                               })

    @api.multi
    def delete_reportcard_line(self):
        for record in self:
            _logger.info('updating ReportCard Line; Carecategory %s Condition no more met', record.care_category_id.name )
            
            if record.transaction_id:
                return record.transaction_id.update_reportcard_oncreate_transaction()
            else:
                #in this case the reportcard is coming from default (Null conditions)
                if not(record.care_category_id.next_category_id):
                    _logger.error("No next carecategory defined for this : carecategory ID %s", record.care_category_id.id)
                    return False
                    
                default_condition = self.env['promote.carecategory.conditions'].search([('care_category_id', '=', record.care_category_id.next_category_id.id),('null_condition', '=', True),('min_age', '<=', record.pet_id.calculated_age), '|' , ('max_age', '=', 0) , ('max_age', '>=', record.pet_id.calculated_age)])
                if default_condition:
                    record.write( {
                                    'reportcard_id': record.reportcard_id.id,
                                    'status': default_condition.Indicator,
                                    'care_category_id': default_condition.care_category_id.id,
                                    'message': default_condition.message,
                                    'delete_date': datetime.datetime.strptime(record.pet_id.x_birthday, "%Y-%m-%d") + relativedelta(years=int(default_condition.max_age)) if self.x_birthday and default_condition.max_age else False,
                                                                         })
                    _logger.info('this reportcard %s was updated to new carecategory %s', record.id, record.care_category_id.name)
                
                else:
                    _logger.error("no default carecategory condition applies to this case: carecategory ID %s with Null condition", record.care_category_id.next_category_id.id)
                    return False



class ResPartner(models.Model):
    _inherit = 'res.partner'

    reportcard_id = fields.Many2one('promote.campaigns.reportcard', 'Report Card', store=True)
    planned_reportcard_refresh_date = fields.Date('Report Card Refresh Date', compute='edit_reportcard',store=True)

    @api.one
    def create_empty_reportcard(self):
        reportcard = self.env["promote.campaigns.reportcard"].create({'pet_id': self.id, 'company_id': self.company_id.id })
        _logger.info('created empty reportcard for : %s, %s', self.name, self.id)
        self.reportcard_id = reportcard
        _logger.info('associated reportcard id : %s', self.reportcard_id.id)
        return self.reportcard_create_default_lines()


    @api.multi
    def reportcard_create_default_lines(self):
        default_conditions = self.env['promote.carecategory.conditions'].search([('null_condition', '=', True),('min_age', '<=', self.calculated_age), '|' , ('max_age', '=', 0) , ('max_age', '>=', self.calculated_age)])
        for default_condition in default_conditions:
            if self.reportcard_id:
                self.env['promote.campaigns.reportcard.line'].create( { 'reportcard_id': self.reportcard_id.id,
                                                                        'status': default_condition.Indicator,
                                                                        'care_category_id': default_condition.care_category_id.id,
                                                                        'message': default_condition.message,
                                                                        'delete_date': datetime.datetime.strptime(self.x_birthday, "%Y-%m-%d") + relativedelta(years=int(default_condition.max_age)) if self.x_birthday and default_condition.max_age else False,
                                                                         })
            else:
                _logger.warning('this pet doesnt have reportcard_id : %s', self.name)

    @api.one
    #@api.depends('is_pet','active','transaction_ids', 'firstname')
    def edit_reportcard(self):
        if not(self.is_pet) or not(self.active):
            return True
        else :
            print self.reportcard_id.id, 'report card id'
            if (self.reportcard_id):
                reportcard = self.reportcard_id
                for reportcard_line in self.reportcard_id.reportcard_lines:
                    reportcard_line.unlink()
            else:
                print 'before create report card'
                reportcard = self.env["promote.campaigns.reportcard"].create({'pet_id': self.id, 'company_id': self.company_id.id })
                print 'after create report card'
            self.reportcard_id = reportcard
            default_conditions = self.env['promote.carecategory.conditions'].search([('null_condition', '=', True),('min_age', '<=', self.calculated_age),('max_age', '>=', self.calculated_age)])
            for default_condition in default_conditions:
                    self.reportcard_id.write({ 'reportcard_lines' :[(0, 0, {'status':default_condition.Indicator,'care_category_id': default_condition.care_category_id.id,'message': default_condition.message})]})

            #if no master condition else:

            add_reportcard_line = True

            if self.transaction_ids:
                for transaction in self.transaction_ids:
                        frequency = 12
                        nxt_planned_date = parser.parse(self.reportcard_id.planned_refresh_date) if self.reportcard_id.planned_refresh_date else False
                        for care_standard in transaction.product_id.care_standard_ids:
                            if not(care_standard.care_category_id and care_standard.care_category_id.include_in_RC):
                                if not(care_standard.max_age) or (care_standard.min_age <= self.calculated_age <= care_standard.max_age):
                                    if (care_standard.company_id == transaction.company_id) :
                                        frequency = care_standard.frequency
                                        print 'frequency with company', frequency
                                        break
                                    if not(care_standard.company_id):
                                        frequency = care_standard.frequency
                                        print 'frequency with no company', frequency

                            for reportcard_line in self.reportcard_id.reportcard_lines:
                                if ( reportcard_line.care_category_id == care_standard.care_category_id ):

                                    if ((datetime.datetime.today() - relativedelta(months=frequency -3)) < parser.parse(transaction.transaction_date)): #code green
                                        reportcard_line.status = 'green'
                                        conditions = self.env['promote.carecategory.conditions'].search([('null_condition', '=', False),('condition', '=', 'current'),('care_category_id', '=', care_standard.care_category_id.id)], limit=1)
                                        if conditions:
                                            reportcard_line.message = conditions[0].message
                                            nxt_planned_date = parser.parse(transaction.transaction_date) + relativedelta(months=frequency -3)

                                    if ((datetime.datetime.today() - relativedelta(months=frequency -3)) > parser.parse(transaction.transaction_date) > (datetime.datetime.today() - relativedelta(months=frequency))): #code yellow
                                        reportcard_line.status = 'yellow'
                                        conditions = self.env['promote.carecategory.conditions'].search([('null_condition', '=', False),('condition', '=', 'expires_in3months'),('care_category_id', '=', care_standard.care_category_id.id)], limit=1)
                                        if conditions:
                                            reportcard_line.message = conditions[0].message
                                            nxt_planned_date = parser.parse(transaction.transaction_date) + relativedelta(months=frequency)

                                    if ((datetime.datetime.today() - relativedelta(months=frequency)) > parser.parse(transaction.transaction_date) ): #code red
                                        reportcard_line.status = 'red'
                                        conditions = self.env['promote.carecategory.conditions'].search([('null_condition', '=', False),('condition', '=', 'expired'),('care_category_id', '=', care_standard.care_category_id.id)], limit=1)
                                        if conditions:
                                            reportcard_line.message = conditions[0].message

                                    add_reportcard_line=False
                                    print 'add_reportcard line is False'
                                    print 'transaction', transaction
                                    try:
                                        self.reportcard_id.planned_refresh_date = min( filter(None, [nxt_planned_date ,  parser.parse(self.reportcard_id.planned_refresh_date) if self.reportcard_id.planned_refresh_date else False]) )
                                        self.planned_reportcard_refresh_date = self.reportcard_id.planned_refresh_date
                                    except:
                                        pass
                                    break

                            if add_reportcard_line:
                                reportcard_line_id = self.env['promote.campaigns.reportcard.line'].create({'pet_id':self.id, 'care_category_id':care_standard.care_category_id.id, 'reportcard_id': reportcard.id})

                                if ((datetime.datetime.today() - relativedelta(months=frequency -3)) < parser.parse(transaction.transaction_date)): #code green
                                        reportcard_line_id.status = 'green'
                                        conditions = self.env['promote.carecategory.conditions'].search([('null_condition', '=', False),('condition', '=', 'green'),('care_category_id', '=', care_standard.care_category_id.id)], limit=1)

                                        if conditions:
                                            reportcard_line_id.message = conditions[0].message
                                            nxt_planned_date = parser.parse(transaction.transaction_date) + relativedelta(months=frequency -3)

                                if ((datetime.datetime.today() - relativedelta(months=frequency -3)) > parser.parse(transaction.transaction_date) > (datetime.datetime.today() - relativedelta(months=frequency))): #code yellow
                                        reportcard_line_id.status = 'yellow'
                                        conditions = self.env['promote.carecategory.conditions'].search([('null_condition', '=', False),('Indicator', '=', 'yellow'),('care_category_id', '=', care_standard.care_category_id.id)], limit=1)
                                        if conditions:
                                            reportcard_line_id.message = conditions[0].message
                                            nxt_planned_date = parser.parse(transaction.transaction_date) + relativedelta(months=frequency)

                                if ((datetime.datetime.today() - relativedelta(months=frequency)) > parser.parse(transaction.transaction_date) ): #code red
                                        reportcard_line_id.status = 'red'
                                        conditions = self.env['promote.carecategory.conditions'].search([('null_condition', '=', False),('Indicator', '=', 'red'),('care_category_id', '=', care_standard.care_category_id.id)], limit=1)
                                        if conditions:
                                            reportcard_line_id.message = conditions[0].message

                                try:
                                    self.reportcard_id.planned_refresh_date = min( filter(None, [nxt_planned_date ,  parser.parse(self.reportcard_id.planned_refresh_date)  if self.reportcard_id.planned_refresh_date else False]) )
                                    self.planned_reportcard_refresh_date = self.reportcard_id.planned_refresh_date
                                except:
                                    pass
                                break


    def create_empty_reportcard_cron(self):
        self._cr.execute("select id from Res_Partner WHERE is_pet=True AND reportcard_id is Null AND active=True LIMIT 2000")
        pets = self.env.cr.fetchall()
        _logger.info('found %s reportcard', len(pets))
        counter=1
        for pet in pets:
            self.env['res.partner'].browse(pet[0]).create_empty_reportcard()
            counter += 1
            if counter >100:
                self.env.cr.commit()
                _logger.info('100 default reportcards committed')
                counter=1
        _logger.info('finished creating empty report cards')
        return True

    @api.multi
    def reportcard_create_default_lines_cron(self):
        #self._cr.execute("select id from Res_Partner WHERE is_pet=True AND reportcard_id is Null AND active=True")
        _logger.info('seaching for empty_rc')
        empty_reportcards = self.env['promote.campaigns.reportcard'].search([('rating','=', 0)], limit=20000)
        counter=1
        for empty_rc in empty_reportcards:
            if not empty_rc.pet_id.reportcard_id:
                empty_rc.pet_id.write({'reportcard_id': empty_rc.id})
            empty_rc.pet_id.reportcard_create_default_lines()
            _logger.info('completed empty_rc for: %s', empty_rc.pet_id.name)
            counter += 1
            if counter >100:
                self.env.cr.commit()
                _logger.info('100 empty RC committed')
                counter=1


    def edit_reportcard_cron(self):
        #pets = self.env['res.partner'].search([('is_pet','=',True),('planned_reportcard_refresh_date','in', [ date.today(), False] ),])
        self._cr.execute("select id from Res_Partner WHERE is_pet=True AND reportcard_id is Null AND active=True limit 5000")
        pets = self.env.cr.fetchall()
        counter=0
        for pet in pets:
            self.env['res.partner'].browse(pet[0]).edit_reportcard()
            counter += 1
            if counter >100:
                self.env.cr.commit()
                counter=0

        _logger.info('finished creating report cards')
        return True

class pims_transaction(models.Model):
    _inherit= 'pims.client.transaction'


    @api.one
    def update_reportcard_oncreate_transaction(self):
        _logger.info('Start Updating reportcard for transaction %s', self.id)

        #checks compliance of the transaction pet_id, product_id,
        if not self.pet_id:
            _logger.Error('This transaction doesnt have a pet: %s, %s', self.name, self.id)
            return False

        if not self.product_id:
            _logger.Error('This transaction product doesnt have a product: %s, %s', self.name, self.id)
            return False

        if not self.product_id.care_standard_ids:
            _logger.Warning('This transaction product doesnt have carestandard lines: %s, %s', self.product_id.name, self.product_id.id)
            return False

        #Lets take the fraquency from carestandard first (12 is default)
        frequency = 12
        for care_standard in self.product_id.care_standard_ids:
            if (care_standard.care_category_id and care_standard.care_category_id.include_in_RC):
                                if not(care_standard.max_age) or (care_standard.min_age <= self.calculated_age <= care_standard.max_age):
                                    if (care_standard.company_id == self.company_id) :
                                        frequency = care_standard.frequency
                                        carecategory_id = care_standard.care_category_id.id
                                        _logger.info('frequency and carecategory with company: %s, %s', frequency, care_standard.care_category_id.name )
                                        break
                                    if not(care_standard.company_id):
                                        frequency = care_standard.frequency
                                        carecategory_id = care_standard.care_category_id.id
                                        _logger.info('default frequency and carecategory (with no company): %s, %s', frequency, care_standard.care_category_id.name )

        #Lets search for current carecategory condition
        conditions = self.env['promote.carecategory.conditions'].search([('null_condition', '=', False),('condition', '=', 'current'),('care_category_id', '=', carecategory_id)], limit=1)
        ###can be optimized using select instead of search
        if not conditions:
            _logger.warning("no care category condition applies to this case: carecateogy ID %s with condition 'current'", carecategory_id)
            return False

        add_reportcard_line = True

        for reportcard_line in self.pet_id.reportcard_lines:
        ###maybe its better to use select or search instead of looping over the Reportcard Lines
            if reportcard_line.care_category_id.id == carecategory_id:
                reportcard_line.write({
                        'status' : 'green',
                        'message': conditions[0].message,
                        'yellow_date': datetime.datetime.strptime(self.transaction_date, "%Y-%m-%d") + relativedelta(months=frequency -3),
                        'red_date': datetime.datetime.strptime(self.transaction_date, "%Y-%m-%d") + relativedelta(months=frequency),
                        'transaction_id' : self.id,
                        #'delete_date': datetime.datetime.strptime(self.pet_idx_birthday, "%Y-%m-%d") + relativedelta(years=int(default_condition.max_age)) if self.x_birthday and default_condition.max_age else False,
                        #DELETE DATE IS ALREADY SET IN DEFAULTS
                               })

                add_reportcard_line=False
                _logger.info('Reportcard line was Updated')
                break

        #if no reportcard_line already exists a new reportcard line should be created
        if add_reportcard_line:
            reportcard_line_id = self.env['promote.campaigns.reportcard.line'].create({
                                        'care_category_id' : carecategory_id,
                                        'reportcard_id' : self.pet_id.reportcard_id.id,
                                        'status' : 'green',
                                        'message': conditions[0].message,
                                        'yellow_date': datetime.datetime.strptime(self.transaction_date, "%Y-%m-%d") + relativedelta(months=frequency -3),
                                        'red_date': datetime.datetime.strptime(self.transaction_date, "%Y-%m-%d") + relativedelta(months=frequency),
                                        'transaction_id': self.id ,
                                                                                    })
            _logger.info('Reportcard line was Created with ID : %s', reportcard_line_id)
