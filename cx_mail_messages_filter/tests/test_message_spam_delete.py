###################################################################################
#
#    Copyright (C) 2020 Cetmix OÜ
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU LESSER GENERAL PUBLIC LICENSE as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###################################################################################

from .common import MailMessagesFilterCommon


class TestMessageSpamDelete(MailMessagesFilterCommon):
    """
    TEST 1 : Message mark spam and delete (unlink_pro)
        [Mark spam]
        - message mark read
        - message is spam
        [Delete]
        - message is deleted

    TEST 2 : Message move to trash and mark spam
        [Move to trash]
        - message active is False
        - message delete date is not False
        [Mark spam]
        - message active is False
        - message delete date is False
        - message spam date is not False
        - author active is False

    TEST 3 : Create conversation and two messages.
    Mark spam conversation messages. Unmark spam
        [Move to trash]
        - conversation active is True
        [Mark spam]
        - conversation active is False
        [Unmark spam]
        - conversation active is True
    """

    def setUp(self):
        super().setUp()
        mail_message_obj = self.env["mail.message"]
        cetmix_conversation_obj = self.env["cetmix.conversation"]

        self.mail_message_test_1 = mail_message_obj.create(
            {
                "subject": "Test Message #1",
                "body": "Test no html message",
                "email_from": self.res_partner_bob.email,
                "author_id": self.res_partner_bob.id,
            }
        )

        self.cetmix_conversation_test_1 = cetmix_conversation_obj.create(
            {
                "name": "Test Conversation #1",
                "active": True,
                "author_id": self.res_partner_bob.id,
            }
        )

        self.mail_message_conversation_test_1 = mail_message_obj.create(
            {
                "res_id": self.cetmix_conversation_test_1.id,
                "model": cetmix_conversation_obj._name,
                "reply_to": "test.reply1@example.com",
                "email_from": "test.from1@example.com",
                "body": "mail message conversation test 1",
            }
        )

        self.mail_message_conversation_test_2 = mail_message_obj.create(
            {
                "res_id": self.cetmix_conversation_test_1.id,
                "model": cetmix_conversation_obj._name,
                "reply_to": "test.reply2@example.com",
                "email_from": "test.from2@example.com",
                "body": "mail message conversation test 2",
            }
        )

    def test_mark_spam_and_delete(self):
        self.mail_message_test_1.mark_spam()
        self.assertFalse(
            self.mail_message_test_1.active, msg="Message must be archived"
        )
        self.assertTrue(self.mail_message_test_1.spam_date, msg="Spam date must be set")

        self.mail_message_test_1.unlink_pro()
        message_not_found = self.env["mail.message"].search(
            [("id", "=", self.mail_message_test_1.id)]
        )
        self.assertFalse(message_not_found, msg="Recordset must be empty")

    def test_msg_trash_and_mark_spam(self):
        self.mail_message_test_1.unlink_pro()
        self.assertFalse(self.mail_message_test_1.active, msg="Message must be active")
        self.assertTrue(
            self.mail_message_test_1.delete_date, msg="Delete date must be set"
        )

        self.mail_message_test_1.mark_spam()
        self.assertFalse(
            self.mail_message_test_1.active, msg="Message must be archived"
        )
        self.assertFalse(
            self.mail_message_test_1.delete_date, msg="Delete date must not be set"
        )
        self.assertTrue(self.mail_message_test_1.spam_date, msg="Spam date must be set")
        self.assertFalse(
            self.mail_message_test_1.author_id.active,
            msg="Messages author must be archived",
        )

    def test_conversation_spam(self):
        self.mail_message_conversation_test_1.unlink_pro()
        self.assertTrue(
            self.cetmix_conversation_test_1.active, msg="Conversation must be active"
        )

        self.mail_message_conversation_test_2.mark_spam()
        self.assertFalse(
            self.cetmix_conversation_test_1.active, msg="Conversation must be archived"
        )

        self.mail_message_conversation_test_2.unmark_spam()
        self.assertTrue(
            self.cetmix_conversation_test_1.active, msg="Conversation must be active"
        )
