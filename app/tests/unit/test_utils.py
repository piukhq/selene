import os
import shutil
import unittest
import settings

from app import utils


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


if __name__ == '__main__':
    unittest.main()
