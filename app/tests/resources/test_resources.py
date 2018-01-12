import os
import json
import shutil
import settings

from flask import url_for
from flask_testing import TestCase
from unittest import mock

from app import create_app
from app.utils import csv_to_list_json, init_folders


class MockClient(mock.Mock):
    @staticmethod
    def execute(_):
        result = mock.Mock()
        result.current_rows = list()
        return result


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

        file = csv_to_list_json(settings.APP_DIR + "/app/tests/fixture/test_import_mids.csv")
        response = self.client.post(url_for('import_mids'), data=json.dumps(file), content_type="application/json")

        self.assert200(response)

    def test_mastercard_handback(self):
        file = csv_to_list_json(settings.APP_DIR + "/app/tests/fixture/test_handback.csv")
        response = self.client.post(url_for('mastercard_handback'), data=json.dumps(file),
                                    content_type="application/json")

        self.assert200(response)

    def test_handback_duplicates(self):
        file = csv_to_list_json(settings.APP_DIR + "/app/tests/fixture/test_handback_duplicates.csv")
        response = self.client.post(url_for('handback_duplicates'), data=json.dumps(file),
                                    content_type="application/json")

        self.assert200(response)

        file = csv_to_list_json(settings.APP_DIR + "/app/tests/fixture/test_handback.csv")
        response = self.client.post(url_for('handback_duplicates'), data=json.dumps(file),
                                    content_type="application/json")

        self.assert200(response)

    def test_wipe_output_folders(self):
        response = self.client.get(url_for('wipe_folders'))
        self.assert200(response)

        shutil.rmtree(os.path.join(settings.WRITE_FOLDER, 'merchants'))

        response = self.client.get(url_for('wipe_folders'))
        self.assert500(response)

    @mock.patch('app.cassandra_operations.Client')
    def test_load_to_cassandra(self, client):
        client.side_effect = MockClient()

        headers = {'Content-Type': "application/json", 'Authorization': settings.SERVICE_TOKEN}
        filename = os.path.join(settings.APP_DIR, 'app', 'tests', 'fixture', 'test_load_cassandra.json')
        with open(filename, 'r') as f:
            file = f.read()

        response = self.client.post(url_for('cassandra_ops'), data=file, headers=headers)

        self.assert200(response)

        merchant = json.dumps({"merchant": "test"})
        response = self.client.post(url_for('cassandra_ops'), data=merchant, headers=headers)

        self.assert200(response)

        response = self.client.post(url_for('cassandra_ops'), data=merchant,
                                    content_type="application/json")

        self.assert401(response)

    @mock.patch('app.cassandra_operations.Client')
    def test_cassandra_scheme_providers(self, client):
        client.side_effect = MockClient()
        response = self.client.get(url_for('get_providers'), content_type="application/json")
        self.assert200(response)