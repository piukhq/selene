from os.path import join
import settings

from unittest import TestCase, mock
from app.agents.amex import upload_sftp


class MockLftp:
    def __init__(self, *args, **kwargs):
        pass


class TestAmexUtils(TestCase):

    @mock.patch('app.agents.amex.cmd.lftp')
    def test_upload_sftp(self, sftp):
        sftp.side_effect = MockLftp
        path = join(settings.APP_DIR, 'app', 'tests', 'fixture')
        try:
            upload_sftp('test', 'test', 'test', path, 'test')

        except Exception as e:
            self.fail('TestAmex upload_sftp failed: {}'.format(e))
