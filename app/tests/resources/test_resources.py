import os
import json
import shutil
import settings

from flask_testing import TestCase
from unittest import mock

from app import create_app
from app.utils import csv_to_list_json, init_folders


class TestViews(TestCase):
    SQLALCHEMY_DATABASE_URI = 'test'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    def create_app(self):
        return create_app(self, )

    def setUp(self):
        self.old_write = settings.WRITE_FOLDER
        settings.WRITE_FOLDER = settings.APP_DIR
        init_folders()

    def tearDown(self):
        settings.WRITE_FOLDER = self.old_write

    @mock.patch('app.agents.amex.get_next_file_number')
    def test_import_mids(self, next_sequence):
        next_sequence.return_value = 1
        response = self.client.post("/mids/import_mids", data="test wrong content", content_type="application/json")
        self.assert500(response)

        file = csv_to_list_json(settings.APP_DIR + "/app/tests/fixture/test_import_mids.csv")
        response = self.client.post("/mids/import_mids", data=json.dumps(file), content_type="application/json")

        self.assert200(response)

    def test_mastercard_handback(self):
        response = self.client.post("/mids/mastercard_handback", data="test wrong content",
                                    content_type="application/json")
        self.assert500(response)

        file = csv_to_list_json(settings.APP_DIR + "/app/tests/fixture/test_handback.csv")
        response = self.client.post("/mids/mastercard_handback", data=json.dumps(file), content_type="application/json")

        self.assert200(response)

    def test_handback_duplicates(self):
        response = self.client.post("/mids/handback_duplicates", data="test wrong content",
                                    content_type="application/json")
        self.assert500(response)

        file = csv_to_list_json(settings.APP_DIR + "/app/tests/fixture/test_handback_duplicates.csv")
        response = self.client.post("/mids/handback_duplicates", data=json.dumps(file), content_type="application/json")

        self.assert200(response)

        file = csv_to_list_json(settings.APP_DIR + "/app/tests/fixture/test_handback.csv")
        response = self.client.post("/mids/handback_duplicates", data=json.dumps(file), content_type="application/json")

        self.assert200(response)

    def test_wipe_output_folders(self):
        response = self.client.get('/mids/wipe_folders')
        self.assert200(response)

        shutil.rmtree(os.path.join(settings.WRITE_FOLDER, 'merchants'))

        response = self.client.get('/mids/wipe_folders')
        self.assert500(response)
