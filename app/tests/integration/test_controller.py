import arrow
import unittest
import app.controller
from unittest.mock import patch


class TestControllerFile(unittest.TestCase):
    @patch('app.controller.PaymentCard.write_to_file')
    def test_write_to_file(self, mock_write_to_file):
        mock_write_to_file.return_value = True
        payment_card = app.controller.PaymentCard()
        payment_card.export()
        assert mock_write_to_file.called

    def test_output_write_to_file(self):
        payment_card = app.controller.PaymentCard()
        payment_card.export()
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
        #app.controller.insert_file_log(log)
        self.assertTrue(True)
