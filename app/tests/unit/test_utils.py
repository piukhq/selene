from io import BytesIO

import os

import unittest
from unittest import mock
from unittest.mock import MagicMock
from werkzeug.datastructures import FileStorage

import settings
from app import utils
from app.utils import validate_headers, save_blob
from app.views import process_mids_file


class TestUtils(unittest.TestCase):

    def test_uk_postcode_validator(self):
        good_postcodes = [
            'S64 5UZ',
            'N5 7PY',
            'U31 9FJ',
            'HD3 4YJ',
            'YO22 5QL',
            'EX15 1NQ',
            'GU52 6ZB',
            'RH5 6LJ',
            'B20 3HG',
            'BN14 0TQ',
        ]

        bad_postcodes = [
            'A123456',
            'B99_L;',
            'password',
        ]

        for p in good_postcodes:
            self.assertTrue(utils.validate_uk_postcode(p))

        for p in bad_postcodes:
            self.assertFalse(utils.validate_uk_postcode(p))

    def test_validate_headers_success(self):
        expected_headers = ['Partner Name', 'American Express MIDs', 'MasterCard MIDs', 'Visa MIDs',
                            'Address (Building Name/Number, Street)', 'Postcode', 'Town/City', 'County/State',
                            'Country', 'Action', 'Scheme', 'Scheme ID']

        is_valid, invalid_headers, missing_headers = validate_headers(expected_headers)

        self.assertTrue(is_valid)
        self.assertEqual(invalid_headers, [])
        self.assertEqual(missing_headers, [])

    def test_validate_headers_invalid_headers(self):
        extra_header = ['Partner Name', 'American Express MIDs', 'MasterCard MIDs', 'Visa MIDs',
                        'Address (Building Name/Number, Street)', 'Postcode', 'Town/City', 'County/State',
                        'Country', 'Action', 'Scheme', 'Scheme ID', 'Extra Column']

        is_valid, invalid_headers, missing_headers = validate_headers(extra_header)

        self.assertFalse(is_valid)
        self.assertEqual(invalid_headers, ['Extra Column'])
        self.assertEqual(missing_headers, [])

    def test_validate_headers_missing_headers(self):
        missing_header = ['American Express MIDs', 'MasterCard MIDs', 'Visa MIDs',
                          'Address (Building Name/Number, Street)', 'Postcode', 'Town/City', 'County/State',
                          'Country', 'Action']

        is_valid, invalid_headers, missing_headers = validate_headers(missing_header)

        self.assertFalse(is_valid)
        self.assertEqual(invalid_headers, [])
        self.assertEqual(missing_headers, ['Partner Name', 'Scheme', 'Scheme ID'])

    @mock.patch('app.utils.bbs', autospec=True)
    def test_save_blob_with_text_calls_correct_function(self, mock_blob_storage):
        text = 'Text to store'
        container = 'some-container'
        filename = 'name.csv'
        path = '/some_path'

        save_blob(text, container, filename, content_type='text', path=path)

        self.assertTrue(mock_blob_storage.create_blob_from_text.called)
        self.assertFalse(mock_blob_storage.create_blob_from_bytes.called)

        args, kwargs = mock_blob_storage.create_blob_from_text.call_args_list[0]
        kwarg_tuples = kwargs.items()

        self.assertIn(('blob_name', 'some_path/name.csv'), kwarg_tuples)
        self.assertIn(('container_name', 'some-container'), kwarg_tuples)
        self.assertIn(('text', 'Text to store'), kwarg_tuples)

    @mock.patch('app.utils.bbs', autospec=True)
    def test_save_blob_with_bytes_calls_correct_function(self, mock_blob_storage):
        text = b''
        container = 'some-container'
        filename = 'name.csv'
        path = '/some_path'

        save_blob(text, container, filename, content_type='bytes', path=path)

        self.assertTrue(mock_blob_storage.create_blob_from_bytes.called)
        self.assertFalse(mock_blob_storage.create_blob_from_text.called)

        args, kwargs = mock_blob_storage.create_blob_from_bytes.call_args_list[0]
        kwarg_tuples = kwargs.items()

        self.assertIn(('blob_name', 'some_path/name.csv'), kwarg_tuples)
        self.assertIn(('container_name', 'some-container'), kwarg_tuples)
        self.assertIn(('blob', b''), kwarg_tuples)


class TestProcessMidsFile(unittest.TestCase):
    amex = MagicMock(autospec=True)
    amex.mids_col_name = 'American Express MIDs'
    amex_msg = 'Processed mids info for amex'
    amex.return_value.create_messages.return_value = amex_msg

    mc = MagicMock(autospec=True)
    mc.mids_col_name = 'MasterCard MIDs'
    mc_msg = 'Processed mids info for mc'
    mc.return_value.create_messages.return_value = mc_msg

    visa = MagicMock(autospec=True)
    visa.mids_col_name = 'Visa MIDs'
    visa_msg = 'Processed mids info for visa'
    visa.return_value.create_messages.return_value = visa_msg

    provider_map = {
        'amex': amex,
        'mc': mc,
        'visa': visa
    }

    def setUp(self):
        self.test_mids_file_path = os.path.join(settings.APP_DIR, 'app/tests/fixture/test_import_mids.csv')
        self.test_handback_file_path = os.path.join(settings.APP_DIR, 'app/tests/fixture/test_handback.csv')

    @mock.patch.dict('app.views.PROVIDERS_MAP', **provider_map, clear=True)
    def test_process_mids_success(self):
        with open(self.test_mids_file_path) as f:
            bytes_content = BytesIO(f.read().encode())
            file = FileStorage(bytes_content)

            messages = process_mids_file(file)

            self.assertEqual(messages, [self.amex_msg, self.mc_msg, self.visa_msg])
            self.assertTrue(self.visa.return_value.export.called)
            self.assertTrue(self.visa.return_value.write_transaction_matched_csv.called)
            self.assertTrue(self.mc.return_value.export.called)
            self.assertTrue(self.mc.return_value.write_transaction_matched_csv.called)
            self.assertTrue(self.amex.return_value.export.called)
            self.assertTrue(self.amex.return_value.write_transaction_matched_csv.called)

    def test_process_mids_fails_with_invalid_csv(self):
        bytes_content = BytesIO(b'a,b,c,d\n1,2,3,4')
        file = FileStorage(bytes_content)

        with self.assertRaises(ValueError) as e:
            process_mids_file(file)

        self.assertIn("Invalid headers: ['a', 'b', 'c', 'd']", e.exception.args[0].strip())
        self.assertIn("Missing headers: ['Partner Name', 'American Express MIDs', 'MasterCard MIDs', 'Visa MIDs', "
                      "'Address (Building Name/Number, Street)', 'Postcode', 'Town/City', 'County/State', "
                      "'Country', 'Action', 'Scheme', 'Scheme ID']",
                      e.exception.args[0].strip())
        self.assertFalse(self.visa.return_value.export.called)
        self.assertFalse(self.mc.return_value.export.called)
        self.assertFalse(self.amex.return_value.export.called)

    @mock.patch('app.views.MasterCard', autospec=True)
    def test_handback_file_is_recognised(self, mock_mc):
        msg = 'File processing info'
        mock_mc.return_value.process_handback_file.return_value = msg

        with open(self.test_handback_file_path) as f:
            bytes_content = BytesIO(f.read().encode())
            file = FileStorage(bytes_content)

            messages = process_mids_file(file)

        self.assertTrue(mock_mc.return_value.process_handback_file.called)
        self.assertEqual(messages, msg)


if __name__ == '__main__':
    unittest.main()
