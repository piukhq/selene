import unittest
from unittest import mock

from app import utils
from app.utils import validate_headers, save_blob


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


if __name__ == '__main__':
    unittest.main()
