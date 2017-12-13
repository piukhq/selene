import unittest
from app.import_mids import validate_row_data


class TestImportMids(unittest.TestCase):
    def test_validate_row_data(self):
        test_row = {
            'Postcode': '',
            'Partner Name': '',
            'Town/City': '',
            'Action': ''
        }
        validated, _, bad_postcode = validate_row_data(test_row)
        self.assertEqual(False, validated)
        self.assertEqual(True, bad_postcode)

        test_row = {
            'Postcode': '',
            'Partner Name': 'Valid',
            'Town/City': 'Valid',
            'Action': 'V'
        }
        validated, _, _ = validate_row_data(test_row)
        self.assertEqual(True, validated)


if __name__ == '__main__':
    unittest.main()
