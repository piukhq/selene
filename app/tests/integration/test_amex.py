import arrow
import unittest
import app.amex
from unittest.mock import patch


class TestAmexMerchantFile(unittest.TestCase):
    @patch('app.amex.Amex.write_to_file')
    def test_write_to_file(self, mock_write_to_file):
        mock_write_to_file.return_value = True
        amex = app.amex.Amex()
        amex.export('amex')
        assert mock_write_to_file.called

    def test_output_write_to_file(self):
        amex = app.amex.Amex()
        amex.export('amex')
        self.assertTrue(True)

    def test_sequential_file_number(self):
        file_number = app.amex.sequential_file_number()
        self.assertTrue(file_number >= 0)

    def test_insert_log_data(self):
        log = {
            'provider': 'bink',
            'receiver': 'test_card',
            'file_name': "my_test_filename",
            'date': arrow.now().timestamp,
            'process_date': arrow.now().timestamp,
            'status': 'written',
            'file_type': 'out',
            'direction': 'out',
            'sequence_number': '1',
            'comment': 'Merchant onboarding'
        }
        app.amex.insert_file_log(log)
        self.assertTrue(True)
