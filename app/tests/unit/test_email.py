import os
import settings

from unittest import TestCase, mock
from app.email import send_email


class TestEmail(TestCase):

    @mock.patch('smtplib.SMTP', autospec=True)
    def test_send_email(self, fake_smtp):
        fake_smtp.has_extn.return_value = True

        test_file = os.path.join(settings.APP_DIR, 'app', 'tests', 'fixture', 'test_handback.csv')
        try:
            send_email('test', 'test', 'test', test_file)

        except Exception as e:
            self.fail('TestEmail fail: {}'.format(e))
