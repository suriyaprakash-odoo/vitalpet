# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo.tools.translate import _
from odoo.tools import email_split
from odoo.exceptions import UserError

from odoo import api, fields, models


_logger = logging.getLogger(__name__)

# welcome email sent to portal users
# (note that calling '_' has no effect except exporting those strings for translation)


def extract_email(email):
    """ extract the email address from a user-friendly email address """
    addresses = email_split(email)
    return addresses[0] if addresses else ''


class PortalWizard(models.TransientModel):
    """
        A wizard to manage the creation/removal of portal users.
    """

    _inherit = 'portal.wizard'
    _description = 'Portal Access Management'


    @api.onchange('portal_id')
    def onchange_portal_id(self):
        # for each partner, determine corresponding portal.wizard.user records
        if self.env.context.get('active_model') == 'res.partner':
            partner_ids = self.env.context.get('active_ids', [])
            contact_ids = set()
            user_changes = []
            for partner in self.env['res.partner'].sudo().browse(partner_ids):
                contact_partners = partner.child_ids or [partner]
                for contact in contact_partners:
                    # make sure that each contact appears at most once in the list
                    if contact.id not in contact_ids:
                        contact_ids.add(contact.id)
                        in_portal = False
                        if contact.user_ids:
                            in_portal = self.portal_id in contact.user_ids[0].groups_id
                        user_changes.append((0, 0, {
                            'model_name': 'res.partner',
                            'partner_id': contact.id,
                            'email': contact.email,
                            'in_portal': in_portal,
                        }))
            self.user_ids = user_changes

        if self.env.context.get('active_model') == 'hr.employee':
            employee_ids = self.env.context.get('active_ids', [])
            emp_contact_ids = set()
            user_changes = []
            for employee in self.env['hr.employee'].sudo().browse(employee_ids):
                contact_employee = [employee]
                for emp_contact in contact_employee:
                    # make sure that each contact appears at most once in the list
                    if emp_contact.id not in emp_contact_ids:
                        emp_contact_ids.add(emp_contact.id)
                        in_portal = False
                        if emp_contact.user_id:
                            in_portal = self.portal_id in emp_contact.user_id.groups_id
                        user_changes.append((0, 0, {
                            'model_name': 'hr.employee',
                            'employee_id': emp_contact.id,
                            'email': emp_contact.work_email,
                            'in_portal': in_portal,
                        }))
            self.user_ids = user_changes

    @api.multi
    def action_apply(self):
        if self.env.context.get('active_model') == 'res.partner':
            self.ensure_one()
            self.user_ids.action_apply()
            return {'type': 'ir.actions.act_window_close'}
        if self.env.context.get('active_model') == 'hr.employee':
            self.ensure_one()
            self.user_ids.action_apply()
            return {'type': 'ir.actions.act_window_close'}


class PortalWizardUser(models.TransientModel):
    """
        A model to configure users in the portal wizard.
    """

    _inherit = 'portal.wizard.user'
    _description = 'Portal User Config'

    model_name = fields.Char('Model Name') 
    partner_id = fields.Many2one('res.partner', string='Contact', ondelete='cascade', required=False, readonly=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', ondelete='cascade', readonly=True)

    @api.multi
    def get_error_messages(self):
        
            emails = []
            partners_error_empty = self.env['res.partner']
            partners_error_emails = self.env['res.partner']
            partners_error_user = self.env['res.partner']

            for wizard_user in self.with_context(active_test=False).filtered(lambda w: w.in_portal and not w.partner_id.user_ids):
                email = extract_email(wizard_user.email)
                if not email:
                    partners_error_empty |= wizard_user.partner_id
                elif email in emails:
                    partners_error_emails |= wizard_user.partner_id
                user = self.env['res.users'].sudo().with_context(active_test=False).search([('login', '=', email)])
                if user:
                    partners_error_user |= wizard_user.partner_id
                emails.append(email)

            error_msg = []
            if partners_error_empty:
                error_msg.append("%s\n- %s" % (_("Some contacts don't have a valid email: "),
                                    '\n- '.join(partners_error_empty.mapped('display_name'))))
            if partners_error_emails:
                error_msg.append("%s\n- %s" % (_("Several contacts have the same email: "),
                                    '\n- '.join(partners_error_emails.mapped('email'))))
            if partners_error_user:
                error_msg.append("%s\n- %s" % (_("Some contacts have the same email as an existing portal user:"),
                                    '\n- '.join(['%s <%s>' % (p.display_name, p.email) for p in partners_error_user])))
            if error_msg:
                error_msg.append(_("To resolve this error, you can: \n"
                    "- Correct the emails of the relevant contacts\n"
                    "- Grant access only to contacts with unique emails"))
            return error_msg

    @api.multi
    def action_apply(self):
        if self.env.context.get('active_model') == 'res.partner':

            self.env['res.partner'].check_access_rights('write')
            """ From selected partners, add corresponding users to chosen portal group. It either granted
                existing user, or create new one (and add it to the group).
            """
            error_msg = self.get_error_messages()
            if error_msg:
                raise UserError("\n\n".join(error_msg))

            for wizard_user in self.sudo().with_context(active_test=False):
                group_portal = wizard_user.wizard_id.portal_id
                if not group_portal.is_portal:
                    raise UserError('Not a portal: ' + group_portal.name)
                user = wizard_user.partner_id.user_ids[0] if wizard_user.partner_id.user_ids else None
                # update partner email, if a new one was introduced
                if wizard_user.partner_id.email != wizard_user.email:
                    wizard_user.partner_id.write({'email': wizard_user.email})
                # add portal group to relative user of selected partners
                if wizard_user.in_portal:
                    user_portal = None
                    # create a user if necessary, and make sure it is in the portal group
                    if not user:
                        if wizard_user.partner_id.company_id:
                            company_id = wizard_user.partner_id.company_id.id
                        else:
                            company_id = self.env['res.company']._company_default_get('res.users')
                        user_portal = wizard_user.sudo().with_context(company_id=company_id)._create_user()
                        print user_portal, 'uuuuuuuuuuuuuuuu'
                    else:
                        user_portal = user
                    wizard_user.write({'user_id': user_portal.id})
                    if not wizard_user.user_id.active or group_portal not in wizard_user.user_id.groups_id:
                        wizard_user.user_id.write({'active': True, 'groups_id': [(4, group_portal.id)]})
                        # prepare for the signup process
                        wizard_user.user_id.partner_id.signup_prepare()
                        wizard_user._send_email()
                    wizard_user.refresh()
                else:
                    # remove the user (if it exists) from the portal group
                    if user and group_portal in user.groups_id:
                        # if user belongs to portal only, deactivate it
                        if len(user.groups_id) <= 1:
                            user.write({'groups_id': [(3, group_portal.id)], 'active': False})
                        else:
                            user.write({'groups_id': [(3, group_portal.id)]})

        if self.env.context.get('active_model') == 'hr.employee':
            self.env['res.partner'].check_access_rights('write')
            """ From selected partners, add corresponding users to chosen portal group. It either granted
                existing user, or create new one (and add it to the group).
            """
            error_msg = self.get_error_messages()
            if error_msg:
                raise UserError("\n\n".join(error_msg))

            for wizard_user in self.sudo().with_context(active_test=False):
                group_portal = wizard_user.wizard_id.portal_id
                if not group_portal.is_portal:
                    raise UserError('Not a portal: ' + group_portal.name)
                user = wizard_user.employee_id.user_id if wizard_user.employee_id.user_id else None
                # update partner email, if a new one was introduced
                if wizard_user.employee_id.work_email != wizard_user.email:
                    wizard_user.employee_id.write({'work_email': wizard_user.email})
                # add portal group to relative user of selected partners
                if wizard_user.in_portal:
                    user_portal = None
                    # create a user if necessary, and make sure it is in the portal group
                    if not user:
                        if wizard_user.employee_id.company_id:
                            company_id = wizard_user.employee_id.company_id.id
                        else:
                            company_id = self.env['res.company']._company_default_get('res.users')
                        print company_id
                        user_portal = wizard_user.sudo().with_context(company_id=company_id)._create_user()
                        print user_portal, 'iiiiii'
                    else:
                        user_portal = user
                    wizard_user.write({'user_id': user_portal.id})
                    if not wizard_user.user_id.active or group_portal not in wizard_user.user_id.groups_id:
                        wizard_user.user_id.write({'active': True, 'groups_id': [(4, group_portal.id)]})
                        # prepare for the signup process
                        wizard_user.user_id.partner_id.signup_prepare()
                        wizard_user._send_email()
                    wizard_user.refresh()
                else:
                    # remove the user (if it exists) from the portal group
                    if user and group_portal in user.groups_id:
                        # if user belongs to portal only, deactivate it
                        if len(user.groups_id) <= 1:
                            user.write({'groups_id': [(3, group_portal.id)], 'active': False})
                        else:
                            user.write({'groups_id': [(3, group_portal.id)]})

    @api.multi
    def _create_user(self):
        """ create a new user for wizard_user.partner_id
            :returns record of res.users
        """
        #res = super(PortalWizardUser, self)._create_user()

        if self.env.context.get('active_model') == 'res.partner':
            company_id = self.env.context.get('company_id')
            return self.env['res.users'].with_context(no_reset_password=True).create({
                'email': extract_email(self.email),
                'login': extract_email(self.email),
                'partner_id': self.partner_id.id,
                'company_id': company_id,
                'company_ids': [(6, 0, [company_id])],
                'groups_id': [(6, 0, [])],
            })


        if self.env.context.get('active_model') == 'hr.employee':
            company_id = self.env.context.get('company_id')
            customer = self.env['res.partner'].sudo().create({'name': self.employee_id.name, 'customer':False})
            return self.env['res.users'].with_context(no_reset_password=True).create({
                'email': extract_email(self.email),
                'login': extract_email(self.email),
                'partner_id': customer.id,
                'company_id': company_id,
                'company_ids': [(6, 0, [company_id])],
                'groups_id': [(6, 0, [])],
            })

    
    @api.multi
    def _send_email(self):
        """ send notification email to a new portal user """
        if self.env.context.get('active_model') == 'res.partner':
            if not self.env.user.email:
                raise UserError(_('You must have an email address in your User Preferences to send emails.'))

            # determine subject and body in the portal user's language
            template = self.env.ref('portal.mail_template_data_portal_welcome')
            for wizard_line in self:
                lang = wizard_line.user_id.lang
                partner = wizard_line.user_id.partner_id

                portal_url = partner.with_context(signup_force_type_in_url='', lang=lang)._get_signup_url_for_action()[partner.id]
                partner.signup_prepare()

                if template:
                    template.with_context(dbname=self._cr.dbname, portal_url=portal_url, lang=lang).send_mail(wizard_line.id, force_send=True)
                else:
                    _logger.warning("No email template found for sending email to the portal user")


        if self.env.context.get('active_model') == 'hr.employee':
            if not self.env.user.email:
                raise UserError(_('You must have an email address in your User Preferences to send emails.'))

            # determine subject and body in the portal user's language
            template = self.env.ref('portal.mail_template_data_portal_welcome')
            for wizard_line in self:
                lang = wizard_line.user_id.lang
                partner = wizard_line.user_id.partner_id

                portal_url = partner.with_context(signup_force_type_in_url='', lang=lang)._get_signup_url_for_action()[partner.id]
                partner.signup_prepare()

                if template:
                    template.with_context(dbname=self._cr.dbname, portal_url=portal_url, lang=lang).send_mail(wizard_line.id, force_send=True)
                else:
                    _logger.warning("No email template found for sending email to the portal user")

            return True
