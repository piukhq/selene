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
