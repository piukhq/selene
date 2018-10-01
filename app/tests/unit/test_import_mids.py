import arrow
import os

from flask_testing import TestCase
import pandas as pd
from unittest import mock

import settings
from app import create_app
from app.agents.new_amex import Amex
from app.agents.register import PROVIDERS_MAP


class TestImport(TestCase):
    TESTING = True

    def create_app(self):
        return create_app(self, )


class TestBaseProvider(TestCase):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'test'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOADED_FILES_DEST = 'test'

    test_file = os.path.join(settings.APP_DIR, 'app/tests/fixture/test_import_mids.csv')

    def create_app(self):
        return create_app(self, )

    def setUp(self):
        datatype_conversion = {agent_class.col_name: str for agent_class in PROVIDERS_MAP.values()}
        datatype_conversion.update({'Scheme ID': str})

        self.timestamp = arrow.utcnow().format('DDMMYY_hhmmssSSS')
        self.df = pd.read_csv(self.test_file, dtype=datatype_conversion)

        self.provider_class = Amex

    @mock.patch.object(Amex, '_remove_duplicate_mids')
    @mock.patch.object(Amex, '_remove_invalid_postcode_rows')
    def test_removes_null_rows(self, mock_remove_postcodes, mock_remove_duplicates):
        agent_instance = self.provider_class(self.df, self.timestamp)

        self.assertTrue(mock_remove_duplicates.called)
        self.assertTrue(mock_remove_postcodes.called)

        self.assertEqual(agent_instance.initial_row_count, 12)
        self.assertEqual(agent_instance.invalid_row_count, 3)
        self.assertEqual(agent_instance.valid_rows_count, 9)
        self.assertEqual(len(agent_instance.df.index), 9)

    @mock.patch.object(Amex, '_remove_null_rows')
    @mock.patch.object(Amex, '_remove_invalid_postcode_rows')
    def test_removes_duplicate_mids(self, mock_remove_postcodes, mock_remove_null):
        agent_instance = self.provider_class(self.df, self.timestamp)

        self.assertTrue(mock_remove_null.called)
        self.assertTrue(mock_remove_postcodes.called)

        self.assertEqual(agent_instance.initial_row_count, 12)
        self.assertEqual(agent_instance.valid_rows_count, 10)
        self.assertEqual(agent_instance.duplicates_count, 2)

    @mock.patch.object(Amex, '_remove_null_rows')
    @mock.patch.object(Amex, '_remove_duplicate_mids')
    def test_removes_invalid_postcode_rows(self, mock_remove_duplicates, mock_remove_null):
        agent_instance = self.provider_class(self.df, self.timestamp)

        self.assertTrue(mock_remove_null.called)
        self.assertTrue(mock_remove_duplicates.called)

        self.assertEqual(agent_instance.initial_row_count, 12)
        self.assertEqual(agent_instance.valid_rows_count, 9)
        self.assertEqual(agent_instance.invalid_row_count, 3)

    def test_clean(self):
        agent_instance = self.provider_class(self.df, self.timestamp)

        self.assertEqual(agent_instance.initial_row_count, 12)
        self.assertEqual(agent_instance.valid_rows_count, 7)
        self.assertEqual(agent_instance.invalid_row_count, 3)
        self.assertEqual(agent_instance.duplicates_count, 2)
