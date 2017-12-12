import os
import unittest

from app.utils import validate_uk_postcode, list_json_to_dict_json, empty_folder
from settings import APP_DIR


class TestUtils(unittest.TestCase):
    relative_path = "/app/tests/unit/test_dir"
    full_path = APP_DIR + relative_path

    def setUp(self):
        os.makedirs(self.full_path, exist_ok=True)

    def tearDown(self):
        os.rmdir(self.full_path)

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
            self.assertTrue(validate_uk_postcode(p))

        for p in bad_postcodes:
            self.assertFalse(validate_uk_postcode(p))

    def test_empty_folder(self):
        open(self.full_path + "/test_file.txt", "w").close()
        self.assertTrue(os.listdir(self.full_path))

        empty_folder(self.relative_path)
        self.assertTrue(not os.listdir(self.full_path))

    def test_list_json_to_dict_json(self):
        input_file = [
            ['Header1', 'Header2', 'Header3'],
            ['value1_row1', 'value2_row1', 'value3_row1'],
            ['value1_row2', 'value2_row2', 'value3_row2']
        ]

        expected = [
            {'Header1': 'value1_row1', 'Header2': 'value2_row1', 'Header3': 'value3_row1'},
            {'Header1': 'value1_row2', 'Header2': 'value2_row2', 'Header3': 'value3_row2'}
        ]

        output = list_json_to_dict_json(input_file)

        self.assertEqual(expected, output)


if __name__ == '__main__':
    unittest.main()
