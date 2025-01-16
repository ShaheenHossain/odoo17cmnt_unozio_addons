from odoo import api, fields, models
from odoo.exceptions import UserError


class MailMail(models.Model):

    _inherit = 'mail.mail'

    not_sent = fields.Boolean(compute='_compute_not_sent', default=True, store=False, help='This field used in tests, odoo check '
                                                                             'only for not created email, but this '
                                                                             'module allow to create mail.mail '
                                                                             'just exclude it from send() function')

    @api.depends('not_sent')
    def _compute_not_sent(self):
        for mail in self:
            mail.not_sent = mail.not_sent

    def send(self, auto_commit=False, raise_exception=False):
        """
        Exclude mails that not in active whitelist Outgoing Mail Server.
        :param auto_commit:
        :param raise_exception:
        :return:
        """

        # pylint: disable= inconsistent-return-statements

        def can_sent_email(email, whitelist_emails):
            for mail in whitelist_emails:
                if mail in email:
                    return True

        active_server_ids = self.env['ir.mail_server'].search([('active', '=', True), ('enable_whitelist', '=', True)])
        whitelist_emails = active_server_ids.mail_whitelist_ids.filtered(lambda f: f.enabled).mapped('name')
        if active_server_ids:
            for mail in self:
                if mail.email_to:
                    if not can_sent_email(mail.email_to, whitelist_emails):
                        mail.not_sent = False  # Used for testing, detail description in field
                        self -= mail
                else:
                    for partner in mail.mail_message_id.partner_ids:
                        if not can_sent_email(partner.email, whitelist_emails):
                            mail.not_sent = False  # Used for testing, detail description in field
                            self -= mail

        res = super().send(auto_commit, raise_exception)
        return res
