import json

from flask_testing import TestCase
from unittest import mock

from app import create_app
from app.utils import csv_to_list_json
from settings import APP_DIR


class TestViews(TestCase):
    def create_app(self):
        self.SQLALCHEMY_DATABASE_URI = 'test'
        self.SQLALCHEMY_TRACK_MODIFICATIONS = False
        return create_app(self, )

    @mock.patch('app.agents.amex.get_next_file_number')
    def test_import_mids(self, next_sequence):
        next_sequence.return_value = 1
        response = self.client.post("/mids/import_mids", data="test wrong content", content_type="application/json")
        self.assert500(response)

        file = csv_to_list_json(APP_DIR + "/app/tests/fixture/test_import_mids.csv")
        response = self.client.post("/mids/import_mids", data=json.dumps(file), content_type="application/json")

        self.assert200(response)

    def test_mastercard_handback(self):
        response = self.client.post("/mids/mastercard_handback", data="test wrong content",
                                    content_type="application/json")
        self.assert500(response)

        file = csv_to_list_json(APP_DIR + "/app/tests/fixture/test_handback.csv")
        response = self.client.post("/mids/mastercard_handback", data=json.dumps(file), content_type="application/json")

        self.assert200(response)

    def test_handback_duplicates(self):
        response = self.client.post("/mids/handback_duplicates", data="test wrong content",
                                    content_type="application/json")
        self.assert500(response)

        file = csv_to_list_json(APP_DIR + "/app/tests/fixture/test_handback_duplicates.csv")
        response = self.client.post("/mids/handback_duplicates", data=json.dumps(file), content_type="application/json")

        self.assert200(response)

    def test_csv_to_json(self):

        with open(APP_DIR + "/app/tests/fixture/test_import_mids.csv", 'rb') as file:
            data = dict(file=file)
            response = self.client.post("/csv_to_json", data=data, content_type='multipart/form-data')

        expected = csv_to_list_json(APP_DIR + "/app/tests/fixture/test_import_mids.csv")
        result = response.json.get('result')

        self.assertEqual(expected, result)
