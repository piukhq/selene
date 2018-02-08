import os
import json
import settings
import httpretty

from flask import url_for
from flask_testing import TestCase
from unittest import mock

from app import create_app
from app.utils import csv_to_list_json, init_folders


class MockClient(mock.Mock):
    @staticmethod
    def execute(_):
        result = mock.MagicMock()
        result.current_rows = list()
        return result


class TestViews(TestCase):
    SQLALCHEMY_DATABASE_URI = 'test'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    EREBUS_URL = 'http://test.url/test'
    WRITE_FOLDER = os.path.join(settings.WRITE_FOLDER, 'test')

    def create_app(self):
        return create_app(self, )

    def setUp(self):
        settings.WRITE_FOLDER = self.WRITE_FOLDER
        settings.EREBUS_URL = self.EREBUS_URL
        init_folders()

    def tearDown(self):
        # shutil.rmtree(self.WRITE_FOLDER)
        pass

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

    @httpretty.activate
    @mock.patch('app.cassandra_operations.Client')
    def test_load_to_cassandra(self, client):
        client.side_effect = MockClient()
        httpretty.register_uri(httpretty.POST, settings.EREBUS_URL,
                               body='{"success": true}',
                               content_type="application/json")

        headers = {'Content-Type': "application/json", 'Authorization': settings.SERVICE_TOKEN}
        filename = os.path.join(settings.APP_DIR, 'app', 'tests', 'fixture', 'test_load_cassandra.json')
        with open(filename, 'r') as f:
            file = f.read()

        payload = dict(user_id='1', user_name='test', data=json.loads(file))
        response = self.client.post(url_for('cassandra_ops'), data=json.dumps(payload), headers=headers)

        self.assert200(response)

        payload['data'] = {"merchant": "test"}

        response = self.client.post(url_for('cassandra_ops'), data=json.dumps(payload), headers=headers)

        self.assert200(response)

        response = self.client.post(url_for('cassandra_ops'), data=json.dumps(payload),
                                    content_type="application/json")

        self.assert401(response)

    @mock.patch('app.cassandra_operations.Client')
    def test_cassandra_scheme_providers(self, client):
        client.side_effect = MockClient()
        response = self.client.get(url_for('get_providers'), content_type="application/json")
        self.assert200(response)
