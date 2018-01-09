import os
import shutil
import unittest
import settings

from app import utils
from app.agents.mastercard import MasterCard


class TestUtils(unittest.TestCase):
    path = os.path.join(settings.WRITE_FOLDER, 'app', 'tests', 'unit', 'test_dir')

    def setUp(self):
        os.makedirs(self.path, exist_ok=True)
        self.old_write_folder = settings.WRITE_FOLDER
        settings.WRITE_FOLDER = self.path

    def tearDown(self):
        shutil.rmtree(self.path)
        settings.WRITE_FOLDER = self.old_write_folder

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

    def test_get_agent(self):
        with self.assertRaises(KeyError):
            utils.get_agent('test_error')

        result = utils.get_agent('mastercard')
        self.assertTrue(isinstance(result, MasterCard))

    def test_wipe_output_folders(self):
        path = os.path.join(self.path, 'merchants')
        os.makedirs(path, exist_ok=True)

        for folder in ['visa', 'amex', 'mastercard']:
            os.makedirs(os.path.join(path, folder), exist_ok=True)

        path = os.path.join(path, 'visa')
        open(path + "/test_file.txt", "w").close()
        os.makedirs(os.path.join(path, 'test_folder'), exist_ok=True)

        self.assertTrue(os.listdir(path))

        utils.wipe_output_folders()
        self.assertFalse(os.listdir(path))

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

        output = utils.list_json_to_dict_json(input_file)

        self.assertEqual(expected, output)

    def test_format_json_input(self):
        file = [
            {'test': 'good'},
            {'test': 'still good'}
        ]
        result = utils.format_json_input(file)
        self.assertEqual(file, result)


if __name__ == '__main__':
    unittest.main()
