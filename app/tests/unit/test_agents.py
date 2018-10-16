import arrow
import xlrd
from io import BytesIO

import os

import pandas as pd
from flask_testing import TestCase
from unittest import mock
from werkzeug.datastructures import FileStorage

import settings
from app import create_app
from app.agents.amex import Amex
from app.agents.mastercard import MasterCard
from app.agents.register import PROVIDERS_MAP
from app.agents.visa import Visa


class TestAmex(TestCase):
    TESTING = True
    UPLOADED_FILES_DEST = 'test'

    NAME = 'amex'
    MIDS_COL_NAME = Amex.mids_col_name

    def create_app(self):
        return create_app()

    @classmethod
    def setUpClass(cls):
        test_mids_file = os.path.join(settings.APP_DIR, 'app/tests/fixture/test_import_mids.csv')
        test_mids_output_file = os.path.join(settings.APP_DIR,
                                             'app/tests/fixture/output/CHINGS_AXP_MER_REG_20181011_111442.txt')

        cols_to_drop = [provider.mids_col_name for name, provider in PROVIDERS_MAP.items() if name != cls.NAME]

        with open(test_mids_file) as f:
            bytes_content = BytesIO(f.read().encode())
            file = FileStorage(bytes_content)
            df = pd.read_csv(file, dtype={PROVIDERS_MAP[cls.NAME].mids_col_name: str, 'Scheme ID': str})
            cls.df = df.drop(cols_to_drop, axis=1)

        with open(test_mids_output_file) as f:
            cls.expected_file = f.read()

    def setUp(self):
        timestamp = arrow.utcnow().format('DDMMYY_hhmmssSSS')
        self.instance = Amex(self.df, timestamp)

    @mock.patch('app.agents.amex.save_blob')
    @mock.patch('app.agents.amex.Sequence', autospec=True)
    def test_export(self, mock_sequence, mock_save):
        mock_sequence.query.filter.return_value.first.return_value.get_seq_number.return_value = 0

        self.instance.export()
        file_content = self.instance.file.get_detail()

        self.assertTrue(mock_sequence.query.filter.return_value.first.return_value.get_seq_number.called)
        self.assertTrue(mock_save.called)
        self.assertEqual(self.expected_file, file_content)


class TestMasterCard(TestCase):
    TESTING = True
    UPLOADED_FILES_DEST = 'test'

    NAME = 'mc'
    MIDS_COL_NAME = MasterCard.mids_col_name

    def create_app(self):
        return create_app()

    @classmethod
    def setUpClass(cls):
        test_mids_file = os.path.join(settings.APP_DIR, 'app/tests/fixture/test_import_mids.csv')
        test_mids_output_file = os.path.join(settings.APP_DIR,
                                             'app/tests/fixture/output/MAS_INPUT_BINK.csv')
        test_handback_file = os.path.join(settings.APP_DIR, 'app/tests/fixture/test_handback.csv')

        cols_to_drop = [provider.mids_col_name for name, provider in PROVIDERS_MAP.items() if name != cls.NAME]

        with open(test_mids_file) as f:
            bytes_content = BytesIO(f.read().encode())
            file = FileStorage(bytes_content)
            df = pd.read_csv(file, dtype={PROVIDERS_MAP[cls.NAME].mids_col_name: str, 'Scheme ID': str})
            cls.df = df.drop(cols_to_drop, axis=1)

        with open(test_mids_output_file) as f:
            cls.expected_export_file = f.read()

        with open(test_handback_file) as f:
            bytes_content = BytesIO(f.read().encode())
            file = FileStorage(bytes_content)
            dataframe_with_footer = pd.read_csv(file, sep='|', header=None, skiprows=1, dtype={23: str})
            cls.handback_df = dataframe_with_footer.iloc[:-1]

    def setUp(self):
        timestamp = arrow.utcnow().format('DDMMYY_hhmmssSSS')
        self.instance = MasterCard(self.df, timestamp)

    @mock.patch('app.agents.mastercard.save_blob')
    def test_export(self, mock_save):
        self.instance.export()
        file_content = self.instance.file.getvalue()

        self.assertTrue(mock_save.called)
        self.assertEqual(self.expected_export_file.split('\n')[1:], file_content.split('\r\n')[1:])

    def test_handback_file_processing(self):
        timestamp = arrow.utcnow().format('DDMMYY_hhmmssSSS')
        instance = MasterCard(self.handback_df, timestamp, handback=True)

        messages = instance.process_handback_file()

        self.assertEqual(messages, [['MasterCard - Total rows - 13', 'Invalid MIDs: 3 - Rows: [0, 12, 8]',
                                     'Total duplicates: 0', 'MasterCard MIDs exported: 10']])


class TestVisa(TestCase):
    TESTING = True
    UPLOADED_FILES_DEST = 'test'

    NAME = 'visa'
    MIDS_COL_NAME = Visa.mids_col_name

    def create_app(self):
        return create_app()

    @classmethod
    def setUpClass(cls):
        test_mids_file = os.path.join(settings.APP_DIR, 'app/tests/fixture/test_import_mids.csv')
        test_mids_output_file = os.path.join(settings.APP_DIR,
                                             'app/tests/fixture/output/CAID_BinkTest_LoyaltyAngels_20181011.xlsx')

        cols_to_drop = [provider.mids_col_name for name, provider in PROVIDERS_MAP.items() if name != cls.NAME]

        with open(test_mids_file) as f:
            bytes_content = BytesIO(f.read().encode())
            file = FileStorage(bytes_content)
            df = pd.read_csv(file, dtype={PROVIDERS_MAP[cls.NAME].mids_col_name: str, 'Scheme ID': str})
            cls.df = df.drop(cols_to_drop, axis=1)

        workbook = xlrd.open_workbook(test_mids_output_file)
        sheet = workbook.sheet_by_index(0)

        cls.expected_file = []
        for rowx in range(sheet.nrows):
            cls.expected_file.append(sheet.row_values(rowx))

    def setUp(self):
        timestamp = arrow.utcnow().format('DDMMYY_hhmmssSSS')
        self.instance = Visa(self.df, timestamp)

    @mock.patch('app.agents.visa.save_blob')
    def test_export(self, mock_save):
        self.instance.export()

        ws = self.instance.file.active

        rows = []
        for row in ws:
            cells = []
            for cell in row:
                cells.append(cell.value)

            rows.append(cells)

        self.assertTrue(mock_save.called)
        self.assertEqual(self.expected_file, rows)
