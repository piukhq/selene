import arrow
import unittest
import app.controller
from unittest.mock import patch


class TestControllerFile(unittest.TestCase):
    @patch('app.agents.amex.Amex.write_to_file')
    @patch('app.agents.visa.Visa.write_to_file')
    def test_write_to_file(self, mock_write_to_file1, mock_write_to_file2):
        mock_write_to_file1.return_value = True
        mock_write_to_file2.return_value = True
        app.controller.export(True)
        assert mock_write_to_file1.called
        assert mock_write_to_file2.called

    def test_output_write_to_file(self):
        app.controller.export(True)
        self.assertTrue(True)

    def test_sequential_file_number(self):
        file_number = app.controller.sequential_file_number()
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
        app.controller.insert_file_log(log)
        self.assertTrue(True)
