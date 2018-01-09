import os
import json
import shutil
import settings

from flask_testing import TestCase
from unittest import mock

from app import create_app
from app.utils import csv_to_list_json, init_folders
from app.cassandra_operations import CassandraOperations
from app.resources import (api, LoadToCassandra, ImportMids, MastercardHandback, WipeOutputFolders,
                           FindDuplicatesInHandback)


class MockClient(mock.Mock):
    @staticmethod
    def insert(table, rows):
        pass


class TestViews(TestCase):
    SQLALCHEMY_DATABASE_URI = 'test'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    def create_app(self):
        return create_app(self, )

    def setUp(self):
        self.old_write = settings.WRITE_FOLDER
        settings.WRITE_FOLDER = os.path.join(settings.APP_DIR, 'test')
        init_folders()

    def tearDown(self):
        shutil.rmtree(settings.WRITE_FOLDER)
        settings.WRITE_FOLDER = self.old_write

    @mock.patch('app.agents.amex.get_next_file_number')
    def test_import_mids(self, next_sequence):
        next_sequence.return_value = 1
        response = self.client.post(api.url_for(ImportMids), data="test wrong content", content_type="application/json")
        self.assert500(response)

        file = csv_to_list_json(settings.APP_DIR + "/app/tests/fixture/test_import_mids.csv")
        response = self.client.post(api.url_for(ImportMids), data=json.dumps(file), content_type="application/json")

        self.assert200(response)

    def test_mastercard_handback(self):
        response = self.client.post(api.url_for(MastercardHandback), data="test wrong content",
                                    content_type="application/json")
        self.assert500(response)

        file = csv_to_list_json(settings.APP_DIR + "/app/tests/fixture/test_handback.csv")
        response = self.client.post(api.url_for(MastercardHandback), data=json.dumps(file),
                                    content_type="application/json")

        self.assert200(response)

    def test_handback_duplicates(self):
        response = self.client.post(api.url_for(FindDuplicatesInHandback), data="test wrong content",
                                    content_type="application/json")
        self.assert500(response)

        file = csv_to_list_json(settings.APP_DIR + "/app/tests/fixture/test_handback_duplicates.csv")
        response = self.client.post(api.url_for(FindDuplicatesInHandback), data=json.dumps(file),
                                    content_type="application/json")

        self.assert200(response)

        file = csv_to_list_json(settings.APP_DIR + "/app/tests/fixture/test_handback.csv")
        response = self.client.post(api.url_for(FindDuplicatesInHandback), data=json.dumps(file),
                                    content_type="application/json")

        self.assert200(response)

    def test_wipe_output_folders(self):
        response = self.client.get(api.url_for(WipeOutputFolders))
        self.assert200(response)

        shutil.rmtree(os.path.join(settings.WRITE_FOLDER, 'merchants'))

        response = self.client.get(api.url_for(WipeOutputFolders))
        self.assert500(response)

    def test_load_to_cassandra(self):
        filename = os.path.join(settings.APP_DIR, 'app', 'tests', 'fixture', 'test_load_cassandra.json')
        with open(filename, 'r') as f:
            file = f.read()

        with mock.patch.object(CassandraOperations, 'client', MockClient):
            response = self.client.post(api.url_for(LoadToCassandra), data=file, content_type="application/json")

            self.assert200(response)

            wrong_data = json.loads(file)
            wrong_data[0].pop(5)

            response = self.client.post(api.url_for(LoadToCassandra), data=json.dumps(wrong_data),
                                        content_type="application/json")

            self.assertIn('ValueError', response.json.get('error'))

        wrong_type_data = "wrong data"
        response = self.client.post(api.url_for(LoadToCassandra), data=wrong_type_data, content_type="application/json")

        self.assert500(response)
