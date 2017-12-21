from os.path import join
import settings

from unittest import TestCase, mock
from app.agents.amex import upload_sftp


class MockSftp:
    hostkeys = None

    def CnOpts(self):
        return self

    def Connection(self, url, username, password, cnopts):
        return self

    def put(self):
        pass


class TestAmexUtils(TestCase):

    @mock.patch('app.agents.amex.pysftp')
    def test_upload_sftp(self, sftp):
        sftp.side_effect = MockSftp
        path = join(settings.APP_DIR, 'app', 'tests', 'fixture')
        try:
            upload_sftp('test', 'test', 'test', path, 'test')

        except Exception as e:
            self.fail('TestAmex upload_sftp failed: {}'.format(e))