from odoo import Command
from odoo.tests import tagged, Form
from odoo.tests.common import users
from odoo.tools import mute_logger
from odoo.addons.mail.tests.test_mail_composer import TestMailComposer


@tagged('mail_composer')
class TestMailComposerForm(TestMailComposer):
    """ Test mail composer form view usage. """

    @classmethod
    def setUpClass(cls):
        super(TestMailComposerForm, cls).setUpClass()

        cls.user_employee.write({'groups_id': [
            (4, cls.env.ref('base.group_private_addresses').id),
            (4, cls.env.ref('base.group_partner_manager').id),
        ]})
        cls.partner_classic = cls.env['res.partner'].create([
            {
                'email': 'not.private@test.example.com',
                'phone': '0032455778899',
                'name': 'Classic Customer',
                'type': 'contact',
            }
        ])

    def enable_whitelist(self):
        if not self.mail_server_global.enable_whitelist:
            self.mail_server_global.enable_whitelist = True

    def add_email_to_whitelist(self, email: str, enabled: bool):
        self.mail_server_global.write({
            'mail_whitelist_ids': [
                Command.create({
                    'name': email,
                    'enabled': enabled,
                }),
            ]
        })

    def prepare_form_view(self):
        partner_classic = self.partner_classic.with_env(self.env)
        test_record = self.test_record.with_env(self.env)

        form = Form(self.env['mail.compose.message'].with_context(**{
            'default_partner_ids': partner_classic.ids,
            'default_model': test_record._name,
            'default_res_id': test_record.id,
        }))
        form.body = '<p>Hello</p>'
        saved_form = form.save()
        return saved_form

    def test_01_empty_whitelist(self):
        """ Test usage of partner to send email """
        self.enable_whitelist()
        saved_form = self.prepare_form_view()

        with self.mock_mail_gateway():
            saved_form._action_send_mail()

        message = self.test_record.message_ids[0]
        self.assertFalse(message.mail_ids.not_sent)

    def test_02_email_added_to_whitelist(self):
        """ Test usage of partner to send email """
        self.enable_whitelist()
        self.add_email_to_whitelist(email=self.partner_classic.email, enabled=True)
        saved_form = self.prepare_form_view()

        with self.mock_mail_gateway():
            saved_form._action_send_mail()

        message = self.test_record.message_ids[0]
        self.assertFalse(message.mail_ids.not_sent)

    def test_03_email_domain_added_to_whitelist(self):
        """ Test usage of partner to send email """
        self.enable_whitelist()
        self.add_email_to_whitelist(email='@test.example.com', enabled=True)
        saved_form = self.prepare_form_view()

        with self.mock_mail_gateway():
            saved_form._action_send_mail()

        message = self.test_record.message_ids[0]
        self.assertFalse(message.mail_ids.not_sent)
