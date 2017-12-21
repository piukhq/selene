import os
import smtplib
import settings

from unittest import TestCase, mock
from app.email import send_email


class FakeSmtp:
    def __init__(self, host, port):
        pass

    @staticmethod
    def set_debuglevel(_):
        pass

    @staticmethod
    def ehlo():
        pass

    @staticmethod
    def has_extn(_):
        return True

    @staticmethod
    def starttls():
        pass

    @staticmethod
    def login(username, password):
        pass

    @staticmethod
    def sendmail(username, to_email, msg):
        pass

    @staticmethod
    def quit():
        pass


class TestEmail(TestCase):

    @mock.patch.object(smtplib, 'SMTP', FakeSmtp)
    def test_send_email(self):
        test_file = os.path.join(settings.APP_DIR, 'app', 'tests', 'fixture', 'test_handback.csv')
        try:
            send_email('test', 'test', 'test', test_file)

        except Exception as e:
            self.fail('TestEmail fail: {}'.format(e))
