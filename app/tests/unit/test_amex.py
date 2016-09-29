import unittest

from app.utils import validate_uk_postcode

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
            self.assertTrue(validate_uk_postcode(p))

        for p in bad_postcodes:
            self.assertFalse(validate_uk_postcode(p))


if __name__ == '__main__':
    unittest.main()